#!/usr/bin/env python3
"""HANA Script Studio (Python edition).

A small desktop app for working with SAP HANA SQL scripts (SAP Note 1969700,
"SQL Statement Collection"): pick a folder, filter scripts by file name, keep several
open in tabs, edit the "Modification section", reset it, copy the script.

Pure standard library (Tkinter). Run:  python hana_script_studio.py
"""
from __future__ import annotations

import base64
import bisect
import json
import os
import queue
import re
import struct
import sys
import tempfile
import threading
from dataclasses import dataclass
from typing import Optional

APP_NAME = "HANA Script Studio"
EXTENSIONS = (".txt", ".sql")

# ---------------------------------------------------------------------------
# Logic (no GUI): everything below is covered by test_hana_script_studio.py
# ---------------------------------------------------------------------------

_FROM_RE = re.compile(r"\bFROM\b", re.I)


def _code_only(line: str, in_block: bool) -> tuple[str, bool]:
    """Return the line without comments and string contents, and whether a /* */ is still open."""
    out: list[str] = []
    i, n = 0, len(line)
    while i < n:
        if in_block:
            j = line.find("*/", i)
            if j < 0:
                return "".join(out), True
            i, in_block = j + 2, False
            out.append(" ")
        elif line.startswith("/*", i):
            in_block, i = True, i + 2
        elif line.startswith("--", i):
            break
        elif line[i] == "'":
            j = i + 1
            while j < n:
                if line[j] == "'":
                    if line[j + 1:j + 2] == "'":
                        j += 2
                        continue
                    break
                j += 1
            out.append("''")
            i = j + 1
        else:
            out.append(line[i])
            i += 1
    return "".join(out), in_block


def find_modification_section(text: str) -> Optional[tuple[int, int]]:
    """Return the zero-based inclusive (first_line, last_line) of the modification section.

    The section starts at the first line containing "Modification section" and ends on the
    line before the first FROM that follows it. FROM inside comments or string literals is
    ignored. If there is no FROM, only the marker line is returned.
    """
    if not text:
        return None
    lines = text.split("\n")
    start = next((i for i, ln in enumerate(lines) if "modification section" in ln.lower()), -1)
    if start < 0:
        return None
    _, in_block = _code_only(lines[start], False)
    for i in range(start + 1, len(lines)):
        code, in_block = _code_only(lines[i], in_block)
        m = _FROM_RE.search(code)
        if m:
            end = i if code[:m.start()].strip() else i - 1
            return start, max(start, end)
    return start, start


def match_spans(name: str, query: str) -> list[tuple[int, int]]:
    """Character ranges of name that match any word of query (case-insensitive, merged)."""
    low = name.lower()
    spans: list[tuple[int, int]] = []
    for word in query.lower().split():
        i = low.find(word)
        while i >= 0:
            spans.append((i, i + len(word)))
            i = low.find(word, i + len(word))
    spans.sort()
    merged: list[tuple[int, int]] = []
    for s, e in spans:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def read_text_file(path: str) -> tuple[str, str, str]:
    """Read a script. Returns (text with \\n newlines, encoding, original newline style)."""
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8", "cp1252"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover - cp1252 rarely fails, latin-1 never does
        enc, text = "latin-1", raw.decode("latin-1")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text.replace("\r\n", "\n").replace("\r", "\n"), enc, newline


class ScriptEntry:
    """A script file found in the library folder."""

    def __init__(self, path: str, root: str) -> None:
        self.path = path
        self.file_name = os.path.basename(path)
        rel = os.path.dirname(os.path.relpath(path, root))
        self.folder = "" if rel == "." else rel
        self.lower_name = self.file_name.lower()
        stem = os.path.splitext(self.file_name)[0]
        self.prefix = "HANA_" if stem.upper().startswith("HANA_") else ""
        rest = stem[len(self.prefix):]
        self.version = ""
        i = rest.rfind("_")
        if i > 0 and i + 1 < len(rest) and rest[i + 1].isdigit():
            self.version = rest[i + 1:]
            rest = rest[:i]
        self.base_name = rest


class ScriptLibrary:
    """All scripts of a folder. Searching is by file name only, so loading is instant."""

    def __init__(self, root: str, entries: list[ScriptEntry]) -> None:
        self.root = root
        self.entries = entries

    @classmethod
    def load(cls, root: str) -> "ScriptLibrary":
        if not os.path.isdir(root):
            raise FileNotFoundError(root)
        entries = [
            ScriptEntry(os.path.join(dirpath, name), root)
            for dirpath, _dirs, files in os.walk(root)
            for name in files
            if name.lower().endswith(EXTENSIONS)
        ]
        entries.sort(key=lambda e: e.lower_name)
        return cls(root, entries)

    def search(self, query: str) -> list[ScriptEntry]:
        """Entries whose file name contains every word of query, ignoring case."""
        words = query.lower().split()
        if not words:
            return list(self.entries)
        return [e for e in self.entries if all(w in e.lower_name for w in words)]


class ScriptDocument:
    """A script open for editing. The file on disk changes only on save()."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.name = os.path.basename(path)
        self.original, self.encoding, self.newline = read_text_file(path)
        self.text = self.original

    @property
    def is_modified(self) -> bool:
        return self.text != self.original

    def reset(self) -> str:
        self.text = self.original
        return self.text

    def save(self) -> None:
        data = self.text.replace("\n", self.newline).encode(self.encoding)
        with open(self.path, "wb") as f:
            f.write(data)
        self.original = self.text


def settings_path() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "HanaScriptStudio", "settings.json")


@dataclass
class Settings:
    last_folder: str = ""
    theme: str = "light"  # light | dark

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Settings":
        try:
            with open(path or settings_path(), encoding="utf-8") as f:
                data = json.load(f)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except (OSError, ValueError, TypeError, AttributeError):
            return cls()

    def save(self, path: Optional[str] = None) -> None:
        path = path or settings_path()
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.__dict__, f, indent=2)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# GUI (Tkinter)
# ---------------------------------------------------------------------------

try:  # tkinter is missing on some Linux installs (apt install python3-tk)
    import tkinter as tk
    import tkinter.font as tkfont
    from tkinter import filedialog, messagebox, ttk
except ImportError:  # pragma: no cover
    tk = None  # type: ignore[assignment]

PALETTES = {
    "light": dict(
        bg="#F7F7F5", panel="#FFFFFF", line="#E6E6E1", hover="#F0F0EC", sel="#EAF2FC",
        fg="#1E2430", dim="#6F7785", faint="#B8BDC6",
        accent="#0A6ED1", accent_hover="#085CB0", accent_ink="#FFFFFF",
        edit="#E9730C", edit_bg="#FFF1E2",
        kw="#0A57B8", str="#1F7A44", num="#B5471F", cmt="#8A93A0",
    ),
    "dark": dict(
        bg="#14171C", panel="#1A1E25", line="#272C35", hover="#222730", sel="#1E2D42",
        fg="#E6E8EC", dim="#8D95A3", faint="#4B525E",
        accent="#5AA6F5", accent_hover="#7BB8F7", accent_ink="#06182B",
        edit="#F29A4A", edit_bg="#3A2A18",
        kw="#82BBFF", str="#6ED29A", num="#F29B88", cmt="#7F8E9D",
    ),
}

KEYWORDS = (
    "SELECT FROM WHERE GROUP BY ORDER HAVING WITH AS AND OR NOT NULL IS IN LIKE BETWEEN CASE WHEN THEN ELSE END "
    "JOIN INNER LEFT RIGHT OUTER FULL ON UNION ALL DISTINCT TOP LIMIT DESC ASC OVER PARTITION CAST COUNT SUM MIN "
    "MAX AVG DUMMY EXISTS INSERT UPDATE DELETE CREATE DROP ALTER TABLE VIEW"
).split()
COMMENT_RE = re.compile(r"/\*.*?\*/|--[^\n]*", re.S)
TOKEN_RE = re.compile(
    r"(?P<str>'(?:[^']|'')*')|(?P<num>\b\d+(?:\.\d+)?\b)|(?P<kw>\b(?:" + "|".join(KEYWORDS) + r")\b)",
    re.I,
)

ICON_PNG_B64 = """
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
RU5ErkJggg==
"""


def _write_ico(png: bytes) -> Optional[str]:
    """Wrap a PNG into a one-image .ico file (Windows needs a real icon file for the taskbar)."""
    try:
        w, h = struct.unpack(">II", png[16:24])
        entry = struct.pack("<BBBBHHII", w % 256, h % 256, 0, 0, 1, 32, len(png), 22)
        path = os.path.join(tempfile.gettempdir(), "HanaScriptStudio.ico")
        with open(path, "wb") as f:
            f.write(struct.pack("<HHH", 0, 1, 1) + entry + png)
        return path
    except (OSError, struct.error):
        return None


def _first_font(candidates: tuple[str, ...], default: str) -> str:
    have = {f.lower(): f for f in tkfont.families()}
    for c in candidates:
        if c.lower() in have:
            return have[c.lower()]
    return default


def _auto_scrollbar(sb, first, last) -> None:
    """Scrollbar callback that hides the bar while everything fits."""
    if float(first) <= 0.0 and float(last) >= 1.0:
        sb.grid_remove()
    else:
        sb.grid()
    sb.set(first, last)


class FlatButton(tk.Label if tk else object):  # type: ignore[misc]
    """A flat, borderless button. kind: "primary" (filled accent) or "ghost" (text only)."""

    def __init__(self, master, text, command, font, kind="ghost", base="panel", padx=12, pady=6):
        super().__init__(master, text=text, font=font, padx=padx, pady=pady, bd=0, cursor="hand2")
        self.command, self.kind, self.base = command, kind, base
        self.enabled, self.hover, self.p = True, False, PALETTES["light"]
        self.bind("<Enter>", lambda _e: self._set_hover(True))
        self.bind("<Leave>", lambda _e: self._set_hover(False))
        self.bind("<Button-1>", self._click)

    def _set_hover(self, on: bool) -> None:
        self.hover = on
        self.paint()

    def _click(self, _e) -> None:
        if self.enabled:
            self.command()

    def set_enabled(self, on: bool) -> None:
        self.enabled = on
        self.configure(cursor="hand2" if on else "arrow")
        self.paint()

    def set_palette(self, p: dict) -> None:
        self.p = p
        self.paint()

    def paint(self) -> None:
        p = self.p
        if self.kind == "primary":
            if not self.enabled:
                bg, fg = p["line"], p["dim"]
            else:
                bg, fg = (p["accent_hover"] if self.hover else p["accent"]), p["accent_ink"]
        else:
            bg = p["hover"] if (self.hover and self.enabled) else p[self.base]
            fg = p["fg"] if self.enabled else p["faint"]
        self.configure(bg=bg, fg=fg)


class CodeEditor(tk.Frame if tk else object):  # type: ignore[misc]
    """Text editor with line numbers, SQL colouring, modification-section band and rail."""

    def __init__(self, master, doc: ScriptDocument, palette: dict, font, on_change, on_cursor):
        super().__init__(master)
        self.doc = doc
        self.on_change = on_change
        self.on_cursor = on_cursor
        self.font = font
        self.section: Optional[tuple[int, int]] = None
        self._hl_job = None
        self._gutter_job = None

        self.gutter = tk.Canvas(self, width=52, highlightthickness=0, bd=0)
        self.text = tk.Text(
            self, wrap="none", undo=True, maxundo=-1, font=font, bd=0, highlightthickness=0,
            padx=14, pady=8, spacing1=2, spacing3=2, tabs=(font.measure("  "),), cursor="xterm",
        )
        self.rail = tk.Canvas(self, width=10, highlightthickness=0, bd=0, cursor="hand2")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.text.yview, style="Thin.Vertical.TScrollbar")
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview, style="Thin.Horizontal.TScrollbar")
        self.text.configure(yscrollcommand=self._on_yscroll, xscrollcommand=lambda f, l: _auto_scrollbar(self.hsb, f, l))

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.gutter.grid(row=0, column=0, sticky="ns")
        self.text.grid(row=0, column=1, sticky="nsew")
        self.rail.grid(row=0, column=2, sticky="ns", pady=10)
        self.vsb.grid(row=0, column=3, sticky="ns")
        self.hsb.grid(row=1, column=0, columnspan=3, sticky="ew")

        self.text.insert("1.0", doc.text)
        self.text.edit_reset()
        self.text.edit_modified(False)
        self.text.bind("<<Modified>>", self._modified)
        for seq in ("<KeyRelease>", "<ButtonRelease-1>"):
            self.text.bind(seq, lambda _e: self.on_cursor(self), add="+")
        self.text.bind("<Control-a>", self._select_all)
        self.text.bind("<Control-y>", lambda _e: (self.text.edit_redo(), "break")[1])
        self.text.bind("<Control-f>", lambda _e: "break")
        self.text.bind("<Configure>", lambda _e: self._schedule_gutter())
        self.rail.bind("<Button-1>", lambda _e: self.jump())
        self.rail.bind("<Configure>", lambda _e: self._draw_rail())

        self.set_palette(palette)
        self.refresh_section()
        self.highlight()

    # -- appearance ---------------------------------------------------------
    def set_palette(self, p: dict) -> None:
        self.p = p
        self.configure(bg=p["panel"])
        self.text.configure(
            bg=p["panel"], fg=p["fg"], insertbackground=p["fg"], selectbackground=p["sel"],
            selectforeground=p["fg"], inactiveselectbackground=p["sel"],
        )
        self.gutter.configure(bg=p["panel"])
        self.rail.configure(bg=p["panel"])
        t = self.text
        t.tag_configure("kw", foreground=p["kw"])
        t.tag_configure("str", foreground=p["str"])
        t.tag_configure("num", foreground=p["num"])
        t.tag_configure("cmt", foreground=p["cmt"])
        t.tag_configure("section", background=p["edit_bg"])
        t.tag_configure("flash", background=p["sel"])
        t.tag_raise("sel")
        self._schedule_gutter()
        self._draw_rail()

    # -- content ------------------------------------------------------------
    def get_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set_text(self, text: str) -> None:
        self.text.edit_separator()
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        self.text.edit_separator()
        self.text.mark_set("insert", "1.0")
        self.text.see("1.0")

    def _modified(self, _e=None) -> None:
        if not self.text.edit_modified():
            return
        self.text.edit_modified(False)
        self.doc.text = self.get_text()
        self.refresh_section()
        self._schedule_highlight()
        self._schedule_gutter()
        self.on_change(self)

    def _select_all(self, _e=None):
        self.text.tag_add("sel", "1.0", "end-1c")
        return "break"

    # -- modification section ----------------------------------------------
    def refresh_section(self) -> None:
        self.section = find_modification_section(self.doc.text)
        self.text.tag_remove("section", "1.0", "end")
        if self.section:
            a, b = self.section
            self.text.tag_add("section", f"{a + 1}.0", f"{b + 2}.0")
        self._draw_rail()

    def jump(self) -> bool:
        if not self.section:
            return False
        a = self.section[0] + 1
        self.text.mark_set("insert", f"{a}.0")
        self.text.yview(f"{max(a - 3, 1)}.0")
        self.text.focus_set()
        self.text.tag_remove("flash", "1.0", "end")
        self.text.tag_add("flash", f"{a}.0", f"{a + 1}.0")
        self.text.tag_raise("flash", "section")
        self.after(700, lambda: self.text.tag_remove("flash", "1.0", "end"))
        self.on_cursor(self)
        return True

    # -- colouring ----------------------------------------------------------
    def _schedule_highlight(self) -> None:
        if self._hl_job:
            self.after_cancel(self._hl_job)
        self._hl_job = self.after(120, self.highlight)

    def highlight(self) -> None:
        self._hl_job = None
        t = self.text
        for tag in ("kw", "str", "num", "cmt"):
            t.tag_remove(tag, "1.0", "end")
        text = self.get_text()
        starts = [0] + [m.end() for m in re.finditer("\n", text)]

        def idx(off: int) -> str:
            line = bisect.bisect_right(starts, off) - 1
            return f"{line + 1}.{off - starts[line]}"

        comments = [(m.start(), m.end()) for m in COMMENT_RE.finditer(text)]
        cstarts = [c[0] for c in comments]

        def in_comment(off: int) -> bool:
            i = bisect.bisect_right(cstarts, off) - 1
            return i >= 0 and off < comments[i][1]

        for m in TOKEN_RE.finditer(text):
            if not in_comment(m.start()):
                t.tag_add(m.lastgroup, idx(m.start()), idx(m.end()))
        for s, e in comments:
            t.tag_add("cmt", idx(s), idx(e))

    # -- gutter and rail ----------------------------------------------------
    def _on_yscroll(self, first, last) -> None:
        _auto_scrollbar(self.vsb, first, last)
        self._schedule_gutter()

    def _schedule_gutter(self) -> None:
        if self._gutter_job is None:
            self._gutter_job = self.after_idle(self._draw_gutter)

    def _draw_gutter(self) -> None:
        self._gutter_job = None
        c, t, p = self.gutter, self.text, self.p
        total = int(t.index("end-1c").split(".")[0])
        width = self.font.measure("0") * max(3, len(str(total))) + 26
        if int(c["width"]) != width:
            c.configure(width=width)
        c.delete("all")
        i = t.index("@0,0")
        prev = None
        while i != prev:
            info = t.dlineinfo(i)
            if info is None:
                break
            y, h = info[1], info[3]
            ln = int(i.split(".")[0])
            if self.section and self.section[0] + 1 <= ln <= self.section[1] + 1:
                c.create_rectangle(width - 6, y, width - 4, y + h, fill=p["edit"], width=0)
            c.create_text(width - 16, y + h / 2, text=str(ln), anchor="e", fill=p["faint"], font=self.font)
            prev = i
            i = t.index(f"{i}+1line")

    def _draw_rail(self) -> None:
        c, p = self.rail, self.p
        c.delete("all")
        h = c.winfo_height()
        if not self.section or h < 20:
            return
        total = int(self.text.index("end-1c").split(".")[0])
        a, b = self.section
        c.create_line(5, 0, 5, h, fill=p["line"])
        y0 = a / total * (h - 2)
        y1 = max(y0 + 4, (b + 1) / total * (h - 2))
        c.create_rectangle(3, y0, 7, y1, fill=p["edit"], width=0)


class StartDialog(tk.Toplevel if tk else object):  # type: ignore[misc]
    """Asks for the scripts folder. Result is stored in self.result (None if cancelled)."""

    def __init__(self, master, palette: dict, fonts: dict, initial: str):
        super().__init__(master)
        p = self.p = palette
        self.result: Optional[str] = None
        self.title("Select scripts folder")
        self.configure(bg=p["panel"])
        self.resizable(False, False)
        self.transient(master)

        tk.Label(self, text="Select your scripts folder", bg=p["panel"], fg=p["fg"], font=fonts["title"]
                 ).grid(row=0, column=0, columnspan=2, sticky="w", padx=24, pady=(22, 2))
        tk.Label(self, text="All .txt and .sql files in it and its subfolders will be listed.", bg=p["panel"],
                 fg=p["dim"], font=fonts["small"]).grid(row=1, column=0, columnspan=2, sticky="w", padx=24)

        self.var = tk.StringVar(value=initial)
        self.entry = tk.Entry(self, textvariable=self.var, width=60, relief="flat", bg=p["bg"], fg=p["fg"],
                              insertbackground=p["fg"], highlightthickness=1, highlightbackground=p["line"],
                              highlightcolor=p["accent"], font=fonts["ui"])
        self.entry.grid(row=2, column=0, sticky="ew", padx=(24, 8), pady=(16, 6), ipady=6)
        browse = FlatButton(self, "Browse…", self._browse, fonts["ui"], base="panel")
        browse.set_palette(p)
        browse.grid(row=2, column=1, padx=(0, 24), pady=(16, 6))

        self.error = tk.Label(self, text=" ", bg=p["panel"], fg=p["edit"], font=fonts["small"], anchor="w")
        self.error.grid(row=3, column=0, columnspan=2, sticky="ew", padx=24)

        bar = tk.Frame(self, bg=p["panel"])
        bar.grid(row=4, column=0, columnspan=2, sticky="e", padx=18, pady=(8, 18))
        quit_btn = FlatButton(bar, "Quit", self._cancel, fonts["ui"], base="panel")
        quit_btn.set_palette(p)
        quit_btn.pack(side="left", padx=(0, 6))
        open_btn = FlatButton(bar, "Open", self._ok, fonts["ui_bold"], kind="primary", padx=22)
        open_btn.set_palette(p)
        open_btn.pack(side="left")

        self.bind("<Return>", lambda _e: self._ok())
        self.bind("<Escape>", lambda _e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.update_idletasks()
        x = master.winfo_rootx() + max(0, (master.winfo_width() - self.winfo_reqwidth()) // 2)
        y = master.winfo_rooty() + max(0, (master.winfo_height() - self.winfo_reqheight()) // 3)
        self.geometry(f"+{x}+{y}")
        self.entry.focus_set()
        self.entry.select_range(0, "end")
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass

    def _browse(self) -> None:
        start = self.var.get() if os.path.isdir(self.var.get()) else os.path.expanduser("~")
        path = filedialog.askdirectory(parent=self, initialdir=start, title="Select the scripts folder")
        if path:
            self.var.set(os.path.normpath(path))

    def _ok(self) -> None:
        path = os.path.expanduser(self.var.get().strip().strip('"'))
        if not path:
            self.error.configure(text="Enter the path to the folder with your scripts.")
        elif not os.path.isdir(path):
            self.error.configure(text="This folder does not exist. Check the path or use Browse.")
        else:
            self.result = os.path.normpath(path)
            self.destroy()

    def _cancel(self) -> None:
        self.result = None
        self.destroy()


class ResultPanel(tk.Frame if tk else object):  # type: ignore[misc]
    """Raw text area for pasting the result of a query next to the script."""

    def __init__(self, master, palette: dict, fonts: dict, mono, on_hide, toast):
        super().__init__(master)
        self.fonts, self.on_hide, self.toast = fonts, on_hide, toast
        self.head = tk.Frame(self)
        self.head.pack(side="top", fill="x")
        self.title = tk.Label(self.head, text="Query result", font=fonts["ui_bold"])
        self.title.pack(side="left", padx=(18, 10), pady=6)
        self.count = tk.Label(self.head, text="Empty", font=fonts["small"])
        self.count.pack(side="left")
        self.buttons = []
        for text, cmd in (("✕", on_hide), ("Clear", self.clear), ("Copy", self.copy), ("Paste", self.paste)):
            b = FlatButton(self.head, text, cmd, fonts["ui"], padx=10, pady=4)
            b.pack(side="right", padx=(0, 4), pady=3)
            self.buttons.append(b)
        self.line = tk.Frame(self, height=1)
        self.line.pack(side="top", fill="x")
        body = tk.Frame(self)
        body.pack(side="top", fill="both", expand=True)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)
        self.body = body
        self.text = tk.Text(body, wrap="none", undo=True, font=mono, bd=0, highlightthickness=0, padx=14, pady=8,
                            spacing1=1, spacing3=1, tabs=(mono.measure("    "),))
        vsb = ttk.Scrollbar(body, orient="vertical", command=self.text.yview, style="Thin.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(body, orient="horizontal", command=self.text.xview, style="Thin.Horizontal.TScrollbar")
        self.text.configure(yscrollcommand=lambda f, l: _auto_scrollbar(vsb, f, l),
                            xscrollcommand=lambda f, l: _auto_scrollbar(hsb, f, l))
        self.text.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.text.bind("<<Modified>>", self._modified)
        self.set_palette(palette)

    def set_palette(self, p: dict) -> None:
        self.configure(bg=p["panel"])
        self.head.configure(bg=p["bg"])
        self.body.configure(bg=p["panel"])
        self.line.configure(bg=p["line"])
        self.title.configure(bg=p["bg"], fg=p["fg"])
        self.count.configure(bg=p["bg"], fg=p["dim"])
        for b in self.buttons:
            b.base = "bg"
            b.set_palette(p)
        self.text.configure(bg=p["panel"], fg=p["fg"], insertbackground=p["fg"], selectbackground=p["sel"],
                            selectforeground=p["fg"], inactiveselectbackground=p["sel"])

    def _modified(self, _e=None) -> None:
        if self.text.edit_modified():
            self.text.edit_modified(False)
            self.update_count()

    def update_count(self) -> None:
        text = self.get_text()
        self.count.configure(text=f"{text.count(chr(10)) + 1:,} lines" if text else "Empty")

    def get_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set_text(self, text: str) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        self.text.edit_reset()
        self.text.see("1.0")
        self.update_count()

    def paste(self) -> None:
        try:
            data = self.clipboard_get()
        except tk.TclError:
            data = ""
        if not data.strip():
            self.toast("Clipboard is empty")
            return
        self.set_text(data.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n"))
        self.toast(f"Pasted {self.count.cget('text')}")

    def copy(self) -> None:
        text = self.get_text()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.toast("Copied the result")

    def clear(self) -> None:
        self.set_text("")


class ScriptView(tk.Frame if tk else object):  # type: ignore[misc]
    """One tab's content: the script editor, with an optional result panel split below it."""

    def __init__(self, master, doc, palette, fonts, mono, on_change, on_cursor, toast):
        super().__init__(master)
        self.paned = tk.PanedWindow(self, orient="vertical", sashwidth=7, sashrelief="flat", bd=0,
                                    sashcursor="sb_v_double_arrow", opaqueresize=True)
        self.paned.pack(fill="both", expand=True)
        self.editor = CodeEditor(self.paned, doc, palette, mono, on_change, on_cursor)
        self.results = ResultPanel(self.paned, palette, fonts, mono, self.hide_results, toast)
        self.paned.add(self.editor, minsize=120, stretch="always")
        self.results_visible = False
        self.set_palette(palette)

    def set_palette(self, p: dict) -> None:
        self.configure(bg=p["panel"])
        self.paned.configure(bg=p["panel"])
        self.editor.set_palette(p)
        self.results.set_palette(p)

    def show_results(self, focus: bool = True) -> None:
        if not self.results_visible:
            self.paned.add(self.results, minsize=90, height=max(160, self.winfo_height() // 3), stretch="never")
            self.results_visible = True
        if focus:
            self.results.text.focus_set()

    def hide_results(self) -> None:
        if self.results_visible:
            self.paned.forget(self.results)
            self.results_visible = False
        self.editor.text.focus_set()
        if self.on_hidden:
            self.on_hidden()

    on_hidden = None


class Tab:
    def __init__(self, doc: ScriptDocument, entry: ScriptEntry, view: "ScriptView"):
        self.doc, self.entry, self.view, self.editor = doc, entry, view, view.editor
        self.shown_mod = False  # modified state last drawn in the tab strip and list


class App(tk.Tk if tk else object):  # type: ignore[misc]
    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings.load()
        if self.settings.theme not in PALETTES:
            self.settings.theme = "light"
        self.p = PALETTES[self.settings.theme]
        self.library: Optional[ScriptLibrary] = None
        self.tabs: list[Tab] = []
        self.current: Optional[Tab] = None
        self._visible: list[ScriptEntry] = []
        self._sel_path: Optional[str] = None
        self._search_job = None
        self._toast_job = None
        self._load_queue: queue.Queue = queue.Queue()
        self._skin: list[tuple] = []
        self._buttons: list[FlatButton] = []
        self._placeholder_on = False

        self.title(APP_NAME)
        self.geometry("1280x800")
        self.minsize(900, 540)
        png = base64.b64decode("".join(ICON_PNG_B64.split()))
        try:
            self._icon = tk.PhotoImage(data=png)
            self.iconphoto(True, self._icon)
        except tk.TclError:
            pass
        if sys.platform == "win32":  # taskbar and title bar icon
            ico = _write_ico(png)
            if ico:
                try:
                    self.iconbitmap(default=ico)
                except tk.TclError:
                    pass

        ui = _first_font(("Segoe UI", "SF Pro Text", "Noto Sans", "DejaVu Sans"), "TkDefaultFont")
        mono = _first_font(("Cascadia Mono", "Consolas", "Menlo", "DejaVu Sans Mono", "Liberation Mono"), "TkFixedFont")
        self.fonts = {
            "ui": tkfont.Font(family=ui, size=10),
            "ui_bold": tkfont.Font(family=ui, size=10, weight="bold"),
            "small": tkfont.Font(family=ui, size=9),
            "title": tkfont.Font(family=ui, size=12, weight="bold"),
            "row": tkfont.Font(family=ui, size=10),
            "row_bold": tkfont.Font(family=ui, size=10, weight="bold"),
        }
        self.mono = tkfont.Font(family=mono, size=11)

        self._build()
        self.apply_theme()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind_all("<Control-s>", lambda _e: self.save_current())
        self.bind_all("<Control-w>", lambda _e: self.close_tab(self.current) if self.current else None)
        self.bind_all("<Control-f>", self._focus_search)
        self.bind_all("<Control-Shift-V>", self.paste_result)
        # tab switching as in Notepad++ (the Text widget has its own bindings for these keys)
        for widget in ("Text", "all"):
            self.bind_class(widget, "<Control-Tab>", lambda _e: self.switch_tab(1))
            self.bind_class(widget, "<Control-Next>", lambda _e: self.switch_tab(1))
            self.bind_class(widget, "<Control-Prior>", lambda _e: self.switch_tab(-1))
            for seq in ("<Control-Shift-Tab>", "<Control-ISO_Left_Tab>"):
                try:
                    self.bind_class(widget, seq, lambda _e: self.switch_tab(-1))
                except tk.TclError:  # keysym unknown on this platform
                    pass
        self.after(60, self.startup)

    # ------------------------------------------------------------------ UI
    def _s(self, widget, **opts):
        """Register widget options that map to palette keys (re-applied on theme change)."""
        self._skin.append((widget, opts))
        return widget

    def _btn(self, parent, text, command, **kw) -> FlatButton:
        b = FlatButton(parent, text, command, kw.pop("font", self.fonts["ui"]), **kw)
        self._buttons.append(b)
        return b

    def _hairline(self, parent, row=None, column=0, columnspan=1, vertical=False):
        f = tk.Frame(parent, width=1 if vertical else 0, height=0 if vertical else 1)
        self._s(f, bg="line")
        return f

    def _build(self) -> None:
        F = self.fonts
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._s(self, bg="bg")

        # top bar
        top = self._s(tk.Frame(self, height=46), bg="bg")
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(2, weight=1)
        self.logo = tk.Canvas(top, width=22, height=16, highlightthickness=0, bd=0)
        self._s(self.logo, bg="bg")
        self.logo.create_polygon(0, 0, 22, 0, 13.5, 15, 0, 15, tags="logo")
        self.logo.grid(row=0, column=0, padx=(18, 8))
        self._s(tk.Label(top, text=APP_NAME, font=F["ui_bold"]), bg="bg", fg="fg").grid(row=0, column=1)
        self.folder_label = self._s(tk.Label(top, text="", font=F["small"], anchor="e"), bg="bg", fg="dim")
        self.folder_label.grid(row=0, column=2, sticky="e", padx=12)
        self.theme_btn = self._btn(top, "Dark", self.toggle_theme, base="bg", padx=10, pady=4)
        self.theme_btn.grid(row=0, column=3)
        self._btn(top, "Change folder", self.change_folder, base="bg", padx=10, pady=4).grid(row=0, column=4, padx=(0, 12))
        self._hairline(self).grid(row=1, column=0, sticky="ew")

        # body: resizable list | editor
        self.paned = self._s(tk.PanedWindow(self, orient="horizontal", sashwidth=7, sashrelief="flat", bd=0,
                                            sashcursor="sb_h_double_arrow", opaqueresize=True), bg="panel")
        self.paned.grid(row=2, column=0, sticky="nsew")

        left = self._s(tk.Frame(self.paned), bg="panel")
        left.grid_rowconfigure(3, weight=1)
        left.grid_columnconfigure(0, weight=1)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._on_search_typed())
        self.search = self._s(tk.Entry(left, textvariable=self.search_var, relief="flat", font=F["ui"],
                                       highlightthickness=1), bg="bg", insertbackground="fg",
                              highlightbackground="line", highlightcolor="accent")
        self.search.grid(row=0, column=0, sticky="ew", padx=(18, 12), pady=(16, 8), ipady=7)
        self.search.bind("<FocusIn>", self._ph_hide)
        self.search.bind("<FocusOut>", self._ph_show)
        self.search.bind("<Down>", lambda _e: (self.list.focus_set(), self._move_selection(1), "break")[2])
        self.count_label = self._s(tk.Label(left, text="", font=F["small"], anchor="w"), bg="panel", fg="dim")
        self.count_label.grid(row=1, column=0, sticky="ew", padx=(20, 12), pady=(0, 6))
        self._hairline(left).grid(row=2, column=0, columnspan=2, sticky="ew")

        wrap = self._s(tk.Frame(left), bg="panel")
        wrap.grid(row=3, column=0, columnspan=2, sticky="nsew")
        wrap.grid_rowconfigure(0, weight=1)
        wrap.grid_columnconfigure(0, weight=1)
        self.list = self._s(tk.Text(wrap, wrap="none", bd=0, highlightthickness=0, relief="flat", cursor="arrow",
                                    font=F["row"], spacing1=6, spacing3=6, padx=14, pady=4, insertwidth=0,
                                    state="disabled", takefocus=True), bg="panel", fg="fg",
                            selectbackground="panel", inactiveselectbackground="panel")
        self.list_vsb = ttk.Scrollbar(wrap, orient="vertical", command=self.list.yview, style="Thin.Vertical.TScrollbar")
        self.list_hsb = ttk.Scrollbar(wrap, orient="horizontal", command=self.list.xview, style="Thin.Horizontal.TScrollbar")
        self.list.configure(yscrollcommand=lambda f, l: _auto_scrollbar(self.list_vsb, f, l),
                            xscrollcommand=lambda f, l: _auto_scrollbar(self.list_hsb, f, l))
        self.list.grid(row=0, column=0, sticky="nsew")
        self.list_vsb.grid(row=0, column=1, sticky="ns")
        self.list_hsb.grid(row=1, column=0, sticky="ew")
        self.empty_label = self._s(tk.Label(wrap, text="", font=F["ui"], wraplength=300, justify="left"), bg="panel", fg="dim")
        self.list.bind("<Button-1>", self._on_list_click)
        self.list.bind("<Control-Button-1>", lambda e: self._on_list_click(e, new_copy=True))
        self.list.bind("<Button-3>", self._on_list_menu)
        self.list.bind("<Control-Return>", lambda _e: (self._open_selected(new_copy=True), "break")[1])
        self.list.bind("<B1-Motion>", lambda _e: "break")
        self.list.bind("<Double-Button-1>", lambda _e: "break")
        self.list.bind("<Up>", lambda _e: (self._move_selection(-1), "break")[1])
        self.list.bind("<Down>", lambda _e: (self._move_selection(1), "break")[1])
        self.list.bind("<Return>", lambda _e: (self._open_selected(), "break")[1])

        right = self._s(tk.Frame(self.paned), bg="panel")
        right.grid_rowconfigure(3, weight=1)
        right.grid_columnconfigure(0, weight=1)
        self.paned.add(left, minsize=260, width=470, stretch="never")
        self.paned.add(right, minsize=460, stretch="always")

        self.tabstrip = self._s(tk.Frame(right), bg="panel")
        self.tabstrip.grid(row=0, column=0, sticky="ew")
        self.actions = self._s(tk.Frame(right), bg="panel")
        self.actions.grid(row=1, column=0, sticky="ew")
        self.jump_btn = self._btn(self.actions, "Go to modification section", self.jump, kind="primary",
                                  font=F["ui_bold"], padx=16, pady=7)
        self.reset_btn = self._btn(self.actions, "Reset to original", self.reset)
        self.copy_btn = self._btn(self.actions, "Copy script", self.copy)
        self.results_btn = self._btn(self.actions, "Results", self.toggle_results)
        self.jump_btn.pack(side="left", padx=(18, 8), pady=12)
        self.reset_btn.pack(side="left", padx=2, pady=12)
        self.copy_btn.pack(side="left", padx=2, pady=12)
        self.results_btn.pack(side="left", padx=(14, 2), pady=12)
        self.section_label = self._s(tk.Label(self.actions, text="", font=F["small"]), bg="panel", fg="dim")
        self.section_label.pack(side="right", padx=18)
        self._hairline(right).grid(row=2, column=0, sticky="ew")

        self.editor_host = self._s(tk.Frame(right), bg="panel")
        self.editor_host.grid(row=3, column=0, sticky="nsew")
        self.editor_host.grid_rowconfigure(0, weight=1)
        self.editor_host.grid_columnconfigure(0, weight=1)
        self.empty_state = self._s(tk.Frame(self.editor_host), bg="panel")
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self._s(tk.Label(self.empty_state, text="Open a script to start", font=F["title"]),
                bg="panel", fg="fg").place(relx=0.5, rely=0.42, anchor="center")
        self._s(tk.Label(self.empty_state, text="Click a script to open it. Ctrl+click opens another copy of a script that is already open.",
                         font=F["ui"]), bg="panel", fg="dim").place(relx=0.5, rely=0.47, anchor="n")
        self.toast = self._s(tk.Label(self.editor_host, text="", font=F["ui"], padx=16, pady=9), bg="fg", fg="panel")

        # status bar
        self._hairline(self).grid(row=3, column=0, sticky="ew")
        status = self._s(tk.Frame(self), bg="bg")
        status.grid(row=4, column=0, sticky="ew")
        for text in ("UTF-8", "SQL"):
            self._s(tk.Label(status, text=text, font=F["small"]), bg="bg", fg="dim").pack(side="left", padx=(18, 0), pady=6)
        self.pos_label = self._s(tk.Label(status, text="Ln 1, Col 1", font=F["small"]), bg="bg", fg="dim")
        self.pos_label.pack(side="left", padx=18, pady=6)
        self.state_label = self._s(tk.Label(status, text="No changes", font=F["small"]), bg="bg", fg="dim")
        self.state_label.pack(side="right", padx=18, pady=6)

        self._set_actions_enabled(False)

    # --------------------------------------------------------------- theme
    def apply_theme(self) -> None:
        p = self.p
        for widget, opts in self._skin:
            widget.configure(**{k: p[v] for k, v in opts.items()})
        for b in self._buttons:
            b.set_palette(p)
        self.logo.itemconfigure("logo", fill=p["accent"], outline=p["accent"])
        self.theme_btn.configure(text="Dark" if self.settings.theme == "light" else "Light")
        self.list.tag_configure("cur", background=p["sel"])
        self.list.tag_configure("match", font=self.fonts["row_bold"], foreground=p["accent"])
        self.list.tag_configure("ext", foreground=p["faint"])
        self.list.tag_configure("folder", foreground=p["dim"], font=self.fonts["small"])
        self.list.tag_configure("dot", foreground=p["edit"])

        st = ttk.Style(self)
        st.theme_use("clam")
        for orient, side in (("Vertical", "ns"), ("Horizontal", "ew")):
            name = f"Thin.{orient}.TScrollbar"
            st.layout(name, [(f"{orient}.Scrollbar.trough", {"sticky": side, "children": [
                (f"{orient}.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})]})])
            st.configure(name, width=9, background=p["line"], troughcolor=p["panel"], bordercolor=p["panel"],
                         lightcolor=p["line"], darkcolor=p["line"], relief="flat", gripcount=0)
            st.map(name, background=[("active", p["faint"]), ("!active", p["line"])])
        for t in self.tabs:
            t.view.set_palette(p)
        self._ph_refresh()
        self._render_list()
        self._render_tabs()
        self._update_state_label()

    def toggle_theme(self) -> None:
        self.settings.theme = "dark" if self.settings.theme == "light" else "light"
        self.p = PALETTES[self.settings.theme]
        self.settings.save()
        self.apply_theme()

    # ------------------------------------------------------------- startup
    def startup(self) -> None:
        self.change_folder(initial=True)

    def change_folder(self, initial: bool = False) -> None:
        if not self._close_all_tabs():
            return
        dlg = StartDialog(self, self.p, self.fonts, self.settings.last_folder)
        self.wait_window(dlg)
        if dlg.result:
            self.load_folder(dlg.result)
        elif initial and self.library is None:
            self.destroy()

    def load_folder(self, path: str) -> None:
        self.settings.last_folder = path
        self.settings.save()
        self.folder_label.configure(text=path)
        self.count_label.configure(text="Loading scripts…")
        self.library = None
        self._visible = []
        self._render_list()

        def work() -> None:
            try:
                self._load_queue.put((ScriptLibrary.load(path), None))
            except Exception as ex:  # noqa: BLE001 - reported to the user
                self._load_queue.put((None, ex))

        threading.Thread(target=work, daemon=True).start()
        self.after(30, self._poll_load)

    def _poll_load(self) -> None:
        try:
            lib, err = self._load_queue.get_nowait()
        except queue.Empty:
            self.after(30, self._poll_load)
            return
        if err is not None:
            self.count_label.configure(text=f"Cannot read this folder: {err}")
            return
        self.library = lib
        self._apply_filter()

    # -------------------------------------------------------------- search
    PLACEHOLDER = "Search scripts by file name"

    def _query(self) -> str:
        return "" if self._placeholder_on else self.search_var.get()

    def _ph_refresh(self) -> None:
        self.search.configure(fg=self.p["faint"] if self._placeholder_on else self.p["fg"])

    def _ph_show(self, _e=None) -> None:
        if not self.search_var.get():
            self._placeholder_on = True
            self.search_var.set(self.PLACEHOLDER)
            self.search.configure(fg=self.p["faint"])

    def _ph_hide(self, _e=None) -> None:
        if self._placeholder_on:
            self._placeholder_on = False
            self.search_var.set("")
            self.search.configure(fg=self.p["fg"])

    def _focus_search(self, _e=None):
        self.search.focus_set()
        self.search.select_range(0, "end")
        return "break"

    def _on_search_typed(self) -> None:
        if self._placeholder_on:
            return
        if self._search_job:
            self.after_cancel(self._search_job)
        self._search_job = self.after(150, self._apply_filter)

    def _apply_filter(self) -> None:
        self._search_job = None
        if self.library is None:
            return
        self._visible = self.library.search(self._query())
        total = len(self.library.entries)
        self.count_label.configure(
            text=f"{total:,} scripts" if not self._query().strip() else f"{len(self._visible):,} of {total:,} scripts")
        self._render_list()

    # ------------------------------------------------------- list rendering
    def _render_list(self) -> None:
        t, query = self.list, self._query()
        mods = {tab.entry.path for tab in self.tabs if tab.doc.is_modified}
        lines, tags = [], []
        for n, e in enumerate(self._visible, start=1):
            name = e.file_name
            row = name
            tags.append(("ext", n, len(os.path.splitext(name)[0]), len(name)))
            for s, en in match_spans(name, query):
                tags.append(("match", n, s, en))
            if e.folder:
                tags.append(("folder", n, len(row) + 3, len(row) + 3 + len(e.folder)))
                row += "   " + e.folder
            if e.path in mods:
                tags.append(("dot", n, len(row) + 2, len(row) + 3))
                row += "  ●"
            lines.append(row)
        t.configure(state="normal")
        t.delete("1.0", "end")
        t.insert("1.0", "\n".join(lines))
        for tag, n, c0, c1 in tags:
            t.tag_add(tag, f"{n}.{c0}", f"{n}.{c1}")
        t.configure(state="disabled")
        self._mark_current()
        if self._visible:
            self.empty_label.place_forget()
        elif self.library is not None:
            self.empty_label.configure(
                text="No .txt or .sql files found in this folder. Use Change folder to pick another one."
                if not self.library.entries else "No scripts match your search.")
            self.empty_label.place(x=16, y=16)

    def _mark_current(self) -> None:
        t = self.list
        t.tag_remove("cur", "1.0", "end")
        for n, e in enumerate(self._visible, start=1):
            if e.path == self._sel_path:
                t.tag_add("cur", f"{n}.0", f"{n + 1}.0")
                t.see(f"{n}.0")
                break

    def _row_entry(self, event) -> Optional[ScriptEntry]:
        n = int(self.list.index(f"@{event.x},{event.y}").split(".")[0])
        return self._visible[n - 1] if 1 <= n <= len(self._visible) else None

    def _on_list_click(self, event, new_copy: bool = False):
        self.list.focus_set()
        entry = self._row_entry(event)
        if entry:
            self._sel_path = entry.path
            self._mark_current()
            self.open_script(entry, new_copy=new_copy)
        return "break"

    def _on_list_menu(self, event):
        entry = self._row_entry(event)
        if entry:
            m = tk.Menu(self, tearoff=0)
            m.add_command(label="Open", command=lambda: self.open_script(entry))
            m.add_command(label="Open in a new tab (another copy)",
                          command=lambda: self.open_script(entry, new_copy=True))
            m.tk_popup(event.x_root, event.y_root)
        return "break"

    def _move_selection(self, delta: int) -> None:
        if not self._visible:
            return
        paths = [e.path for e in self._visible]
        i = paths.index(self._sel_path) if self._sel_path in paths else (-1 if delta > 0 else len(paths))
        self._sel_path = paths[max(0, min(len(paths) - 1, i + delta))]
        self._mark_current()

    def _open_selected(self, new_copy: bool = False) -> None:
        for e in self._visible:
            if e.path == self._sel_path:
                self.open_script(e, new_copy=new_copy)
                return

    # ---------------------------------------------------------------- tabs
    def open_script(self, entry: ScriptEntry, new_copy: bool = False) -> None:
        """Open a script in a tab. If it is already open, switch to it, unless new_copy is set:
        then a second, independent copy opens (handy for trying different parameters)."""
        if not new_copy:
            for t in self.tabs:
                if t.entry.path == entry.path:
                    self.select_tab(t)
                    return
        try:
            doc = ScriptDocument(entry.path)
        except OSError as ex:
            self.show_toast(f"Cannot open {entry.file_name}: {ex.strerror or ex}")
            return
        view = ScriptView(self.editor_host, doc, self.p, self.fonts, self.mono, self._on_editor_change,
                          self._on_cursor, self.show_toast)
        view.on_hidden = self._update_results_button
        tab = Tab(doc, entry, view)
        self.tabs.append(tab)
        self.select_tab(tab)

    def select_tab(self, tab: Optional[Tab]) -> None:
        self.current = tab
        for t in self.tabs:
            t.view.grid_forget()
        self.empty_state.grid_forget()
        if tab is None:
            self.empty_state.grid(row=0, column=0, sticky="nsew")
        else:
            tab.view.grid(row=0, column=0, sticky="nsew")
            tab.editor.text.focus_set()
            self._sel_path = tab.entry.path
            self._mark_current()
        self._set_actions_enabled(tab is not None)
        self._render_tabs(reveal=True)
        self._update_results_button()
        self._update_section_info()
        self._update_state_label()
        if tab:
            self._on_cursor(tab.editor)

    def _tab_labels(self) -> dict:
        """Tab -> text; later copies of the same file get a number: Name (2)."""
        copies: dict[str, int] = {}
        labels = {}
        for t in self.tabs:
            copies[t.entry.path] = n = copies.get(t.entry.path, 0) + 1
            labels[t] = os.path.splitext(t.doc.name)[0] + (f" ({n})" if n > 1 else "")
        return labels

    def _render_tabs(self, reveal: bool = False) -> None:
        """Draw the tab strip. With many tabs it scrolls: arrow buttons, mouse wheel and a
        drop-down list of all open tabs. reveal=True scrolls the current tab into view."""
        p, F = self.p, self.fonts
        old = getattr(self, "_tab_canvas", None)
        x0 = old.xview()[0] if old is not None and old.winfo_exists() else 0.0
        for w in self.tabstrip.winfo_children():
            w.destroy()
        labels = self._tab_labels()

        bar = tk.Frame(self.tabstrip, bg=p["panel"])
        bar.pack(side="top", fill="x", pady=(6, 0))
        ctrl = tk.Frame(bar, bg=p["panel"])
        ctrl.pack(side="right", padx=(0, 8))
        canvas = tk.Canvas(bar, bg=p["panel"], highlightthickness=0, bd=0, xscrollincrement=40, height=36)
        canvas.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self._tab_canvas = canvas
        row = tk.Frame(canvas, bg=p["panel"])
        canvas.create_window((0, 0), window=row, anchor="nw")

        boxes = {}
        for t in self.tabs:
            sel = t is self.current
            box = tk.Frame(row, bg=p["panel"])
            box.pack(side="left", padx=(0, 4))
            boxes[t] = box
            inner = tk.Frame(box, bg=p["panel"])
            inner.pack(side="top")
            title = tk.Label(inner, text=labels[t], bg=p["panel"], fg=p["fg"] if sel else p["dim"],
                             font=F["ui_bold"] if sel else F["ui"], padx=8, pady=7)
            title.pack(side="left")
            dot = tk.Label(inner, text="●" if t.doc.is_modified else " ", bg=p["panel"], fg=p["edit"], font=F["small"])
            dot.pack(side="left")
            close = tk.Label(inner, text="✕", bg=p["panel"], fg=p["dim"] if sel else p["faint"], font=F["small"],
                             padx=6, cursor="hand2")
            close.pack(side="left", padx=(0, 4))
            close.bind("<Enter>", lambda _e, c=close: c.configure(fg=p["fg"]))
            close.bind("<Leave>", lambda _e, c=close, s=sel: c.configure(fg=p["dim"] if s else p["faint"]))
            close.bind("<Button-1>", lambda _e, tab=t: self.close_tab(tab))
            tk.Frame(box, height=2, bg=p["accent"] if sel else p["panel"]).pack(side="top", fill="x")
            for w in (box, inner, title, dot):
                w.bind("<Button-1>", lambda _e, tab=t: self.select_tab(tab))
                w.bind("<Button-2>", lambda _e, tab=t: self.close_tab(tab))
                w.bind("<Button-3>", lambda e, tab=t: self._tab_menu(e, tab))

        # scroll controls (shown only when the tabs do not fit)
        def small_btn(text, command):
            b = FlatButton(ctrl, text, command, F["ui"], padx=8, pady=5)
            b.set_palette(p)
            return b

        left_b = small_btn("◀", lambda: canvas.xview_scroll(-3, "units"))
        right_b = small_btn("▶", lambda: canvas.xview_scroll(3, "units"))
        list_b = small_btn("▾", lambda: self._tab_list_menu(list_b, labels))
        if len(self.tabs) >= 2:
            list_b.pack(side="left")

        def wheel(event):
            step = -1 if (getattr(event, "num", 0) == 4 or getattr(event, "delta", 0) > 0) else 1
            canvas.xview_scroll(step * 3, "units")
            return "break"

        def bind_wheel(w):
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                # a fresh lambda per sequence: Tkinter names Tcl commands after the function,
                # so sharing one function across bindings breaks widget destruction
                w.bind(seq, lambda e: wheel(e))
            for c in w.winfo_children():
                bind_wheel(c)

        bind_wheel(canvas)

        state = {"first": True}

        def layout(_e=None) -> None:
            if not canvas.winfo_exists():
                return
            row.update_idletasks()
            total, h = row.winfo_reqwidth(), row.winfo_reqheight()
            width = canvas.winfo_width()
            canvas.configure(scrollregion=(0, 0, total, h), height=h)
            overflow = total > width > 1
            if overflow and not left_b.winfo_ismapped():
                opts = {"before": list_b} if len(self.tabs) >= 2 else {}
                left_b.pack(side="left", **opts)
                right_b.pack(side="left", **opts)
            elif not overflow and left_b.winfo_ismapped():
                left_b.pack_forget()
                right_b.pack_forget()
            if state["first"] and width > 1:
                state["first"] = False
                cur = boxes.get(self.current)
                if not overflow:
                    canvas.xview_moveto(0)
                elif reveal and cur is not None:
                    left, bx, bw = canvas.canvasx(0), cur.winfo_x(), cur.winfo_reqwidth()
                    if bx < left:
                        canvas.xview_moveto(bx / total)
                    elif bx + bw > left + width:
                        canvas.xview_moveto((bx + bw - width) / total)
                else:
                    canvas.xview_moveto(x0)

        canvas.bind("<Configure>", layout)
        canvas.after_idle(layout)

    def _tab_list_menu(self, anchor, labels: dict) -> None:
        """Drop-down with every open tab, so none can get lost."""
        m = tk.Menu(self, tearoff=0)
        for t in self.tabs:
            text = ("✓  " if t is self.current else "     ") + labels[t] + ("  ●" if t.doc.is_modified else "")
            m.add_command(label=text, command=lambda tab=t: self.select_tab(tab))
        m.tk_popup(anchor.winfo_rootx(), anchor.winfo_rooty() + anchor.winfo_height())

    def _tab_menu(self, event, tab: Tab) -> None:
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="Open another copy", command=lambda: self.open_script(tab.entry, new_copy=True))
        m.add_separator()
        m.add_command(label="Close", command=lambda: self.close_tab(tab))
        m.add_command(label="Close all", command=self._close_all_tabs)
        m.tk_popup(event.x_root, event.y_root)

    def close_tab(self, tab: Optional[Tab]) -> bool:
        if tab is None:
            return True
        if tab.doc.is_modified:
            answer = messagebox.askyesnocancel(
                "Unsaved changes", f"Save changes to {tab.doc.name}?\n\nYour edits will be lost if you don't save them.",
                parent=self)
            if answer is None:
                return False
            if answer and not self._save_tab(tab):
                return False
        i = self.tabs.index(tab)
        self.tabs.remove(tab)
        tab.view.destroy()
        if self.current is tab:
            self.select_tab(self.tabs[min(i, len(self.tabs) - 1)] if self.tabs else None)
        else:
            self._render_tabs()
        self._render_list()
        return True

    def _close_all_tabs(self) -> bool:
        for t in list(self.tabs):
            if not self.close_tab(t):
                return False
        return True

    # ------------------------------------------------------------- actions
    def _set_actions_enabled(self, on: bool) -> None:
        for b in (self.jump_btn, self.reset_btn, self.copy_btn, self.results_btn):
            b.set_enabled(on)

    def toggle_results(self) -> None:
        """Split the screen: show or hide the result area below the script."""
        if not self.current:
            return
        view = self.current.view
        if view.results_visible:
            view.hide_results()
        else:
            view.show_results()
        self._update_results_button()

    def paste_result(self, _e=None):
        """Ctrl+Shift+V: paste the clipboard into the result area of the current script."""
        if self.current:
            self.current.view.show_results(focus=False)
            self.current.view.results.paste()
            self._update_results_button()
        return "break"

    def _update_results_button(self) -> None:
        shown = bool(self.current and self.current.view.results_visible)
        self.results_btn.configure(text="Hide results" if shown else "Results")

    def switch_tab(self, step: int):
        if len(self.tabs) > 1 and self.current in self.tabs:
            self.select_tab(self.tabs[(self.tabs.index(self.current) + step) % len(self.tabs)])
        return "break"

    def jump(self) -> None:
        if self.current and self.current.editor.jump():
            self.show_toast(f"Jumped to line {self.current.editor.section[0] + 1}")

    def reset(self) -> None:
        if self.current:
            self.current.editor.set_text(self.current.doc.original)
            self.show_toast("Restored the original script from disk")

    def copy(self) -> None:
        if not self.current:
            return
        text = self.current.editor.get_text()
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()  # keep the clipboard content after the app closes (Windows/X11)
        self.show_toast(f"Copied the full script ({text.count(chr(10)) + 1} lines)")

    def _save_tab(self, tab: Tab) -> bool:
        try:
            tab.doc.text = tab.editor.get_text()
            tab.doc.save()
        except OSError as ex:
            self.show_toast(f"Cannot save: {ex.strerror or ex}")
            return False
        tab.shown_mod = False
        self._render_tabs()
        self._render_list()
        self._update_state_label()
        return True

    def save_current(self):
        if self.current and self._save_tab(self.current):
            self.show_toast("Saved to disk")
        return "break"

    # ----------------------------------------------------------- callbacks
    def _on_editor_change(self, editor: CodeEditor) -> None:
        tab = next((t for t in self.tabs if t.editor is editor), None)
        if tab is None:
            return
        if tab is self.current:
            self._update_section_info()
            self._update_state_label()
        if tab.doc.is_modified != tab.shown_mod:  # redraw only when the dot appears or disappears
            tab.shown_mod = tab.doc.is_modified
            self._render_tabs()
            self._render_list()

    def _on_cursor(self, editor: CodeEditor) -> None:
        if self.current and self.current.editor is editor:
            line, col = editor.text.index("insert").split(".")
            self.pos_label.configure(text=f"Ln {line}, Col {int(col) + 1}")

    def _update_section_info(self) -> None:
        if not self.current:
            self.section_label.configure(text="")
            self.jump_btn.set_enabled(False)
            return
        s = self.current.editor.section
        self.section_label.configure(
            text=f"Section: lines {s[0] + 1}–{s[1] + 1}" if s else "No modification section")
        self.jump_btn.set_enabled(bool(s))

    def _update_state_label(self) -> None:
        mod = bool(self.current and self.current.doc.is_modified)
        self.state_label.configure(text="Modified, not saved" if mod else "No changes",
                                   fg=self.p["edit"] if mod else self.p["dim"])

    def show_toast(self, text: str) -> None:
        self.toast.configure(text=text)
        self.toast.place(relx=1.0, rely=1.0, x=-28, y=-22, anchor="se")
        if self._toast_job:
            self.after_cancel(self._toast_job)
        self._toast_job = self.after(1800, self.toast.place_forget)

    def on_close(self) -> None:
        if self._close_all_tabs():
            self.destroy()


def main() -> None:
    if tk is None:
        sys.exit("Tkinter is not available. On Debian/Ubuntu install it with: sudo apt install python3-tk")
    if sys.platform == "win32":  # crisp text on high-DPI displays
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # noqa: BLE001
            pass
        try:  # own taskbar group, so Windows shows our icon instead of python.exe's
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("HanaScriptStudio.App")
        except Exception:  # noqa: BLE001
            pass
    app = App()
    app.after(100, app._ph_show)
    app.mainloop()


if __name__ == "__main__":
    main()
