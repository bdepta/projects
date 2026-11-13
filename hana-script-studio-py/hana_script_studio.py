#!/usr/bin/env python3
"""HANA Script Studio (Python edition).

A small desktop app for working with SAP HANA SQL scripts (SAP Note 1969700,
"SQL Statement Collection"): pick a folder, filter scripts by a word, keep several
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
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Optional

APP_NAME = "HANA Script Studio"
EXTENSIONS = (".txt", ".sql")
MAX_INDEXED_BYTES = 4 * 1024 * 1024

# ---------------------------------------------------------------------------
# Logic (no GUI): everything below is covered by test_hana_script_studio.py
# ---------------------------------------------------------------------------


def find_modification_section(text: str) -> Optional[tuple[int, int]]:
    """Return the zero-based inclusive (first_line, last_line) of the modification section.

    It starts at the first line containing "Modification section" and ends on the line
    before the line containing "Internal section" (or on the last line if there is none).
    """
    if not text:
        return None
    lines = text.split("\n")
    start = -1
    for i, line in enumerate(lines):
        low = line.lower()
        if start < 0:
            if "modification section" in low:
                start = i
        elif "internal section" in low:
            return start, max(start, i - 1)
    return None if start < 0 else (start, len(lines) - 1)


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


@dataclass
class ScriptEntry:
    """A script file found in the library folder."""

    path: str
    root: str
    content: Optional[str] = field(default=None, repr=False)  # lower-cased, for search

    def __post_init__(self) -> None:
        self.file_name = os.path.basename(self.path)
        rel = os.path.dirname(os.path.relpath(self.path, self.root))
        self.folder = "" if rel == "." else rel
        stem = os.path.splitext(self.file_name)[0]
        self.prefix = "HANA_" if stem.upper().startswith("HANA_") else ""
        rest = stem[len(self.prefix):]
        self.version = ""
        i = rest.rfind("_")
        if i > 0 and i + 1 < len(rest) and rest[i + 1].isdigit():
            self.version = rest[i + 1:]
            rest = rest[:i]
        self.base_name = rest
        self.lower_name = self.file_name.lower()


def _load_content(entry: ScriptEntry) -> None:
    try:
        if os.path.getsize(entry.path) <= MAX_INDEXED_BYTES:
            entry.content = read_text_file(entry.path)[0].lower()
    except OSError:
        pass


class ScriptLibrary:
    """All scripts of a folder, with their content kept in memory for instant search."""

    def __init__(self, root: str, entries: list[ScriptEntry]) -> None:
        self.root = root
        self.entries = entries

    @classmethod
    def load(cls, root: str) -> "ScriptLibrary":
        if not os.path.isdir(root):
            raise FileNotFoundError(root)
        entries: list[ScriptEntry] = []
        for dirpath, _dirs, files in os.walk(root):
            for name in files:
                if name.lower().endswith(EXTENSIONS):
                    entries.append(ScriptEntry(os.path.join(dirpath, name), root))
        entries.sort(key=lambda e: e.lower_name)
        with ThreadPoolExecutor(max_workers=min(8, (os.cpu_count() or 2) * 2)) as pool:
            list(pool.map(_load_content, entries))
        return cls(root, entries)

    def search(self, query: str, name_only: bool = False) -> list[ScriptEntry]:
        """Entries whose name (and content, unless name_only) contain every word of query."""
        words = query.lower().split()
        if not words:
            return list(self.entries)
        out = []
        for e in self.entries:
            for w in words:
                if w in e.lower_name or (not name_only and e.content is not None and w in e.content):
                    continue
                break
            else:
                out.append(e)
        return out


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
    name_only: bool = False

    @classmethod
    def load(cls, path: Optional[str] = None) -> "Settings":
        try:
            with open(path or settings_path(), encoding="utf-8") as f:
                data = json.load(f)
            known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**known)
        except (OSError, ValueError, TypeError):
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
        shell="#1B2A3A", shell2="#26384B", shell_fg="#EAF0F6", shell_dim="#93A6B9",
        accent="#0A6ED1", accent_ink="#FFFFFF", accent_soft="#E3EEFB",
        bg="#EEF1F4", panel="#FFFFFF", panel2="#F7F8FA", line="#D8DEE5", fg="#1B2A3A", dim="#617083",
        edit="#E9730C", edit_bg="#FFEBD6", kw="#0A57B8", str="#1F7A44", num="#B5471F", cmt="#7B8794",
    ),
    "dark": dict(
        shell="#0C1520", shell2="#18283A", shell_fg="#EAF0F6", shell_dim="#7F93A7",
        accent="#5AA6F5", accent_ink="#06182B", accent_soft="#16304F",
        bg="#111A25", panel="#182231", panel2="#142030", line="#2A3949", fg="#E4EAF0", dim="#92A3B5",
        edit="#F29A4A", edit_bg="#3F2A14", kw="#82BBFF", str="#6ED29A", num="#F29B88", cmt="#7F8E9D",
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
iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAOPklEQVR42uWbeYxd1X3HP+fc+/Z58+Z5vDB47GGM
F5aAwUwNgwiFOLSiElhAp6KiAkdqaICipIlaVVERTmlaBSkhJKQkBUQINEIepSIBnI1gBxtjwDZ4N16YxfbYHo9n
eTNvvfeeX/+4773ZPTM2OLY50tU83TnnnvP7nt92fuf3U0yhiYhqbkY3NaEANm/erDgL2jXXXCMAzSBNYJRS8olO
ICJaRCzOkSYilojoyfS1J9pxQCulPIBVGzZEFlTXXhGw9KWWUrMNBDHmT0utBlCOCB1G2HMk3bVNKZUuAcEEHDEu
AI8++qhWShnA27hj72XVlYkvh0OB5bFwuL6qMoI623Yd6BvIMS0Ta9/f1vnaif6eZ5RSH5Y4uEjL5FkeYPXq1aHd
LR3fOXaiPyuDzYiIc5Y+prTIY939zt6Woz9Ys2ZNBcCqVausKRH/x/e2z2k51PnuEMIdEfGMMWKMnHXNGBHjL8wM
BaO1o2vb2i07F0wKhEeLxG/cuLW2raPro+K3C0ORPVdaEYyCiMjBo93tm3fsmz90g4epkJLCu7wZtXfv3tD0mlmv
zK2pXgg4AgE460R+wqaUAn/tbu2s5JyqROLV9bt3x4co99GmA2Db7pbvlHbenHP7PgYnDHKxbN/b9pOhtI6S+3c/
3LXwyPHegoi45yLbT4CDe7yn37y3s+XqofpAA6xdu1YDxOOVD14wPREoWpVzju1PJhGATK+qUPGw/VWApqYm3w8Q
EaWUclet2hAJB+y7RASllOb8a5aIEA6Hbluz5oMqpVSviCjd3NysAeZfOutzVVWVtUopmawbeS614kabmdXJaYnq
yoaSEdBNTU0KwLL15VXxCIB3fnF/2SwAmGjIlkA4eHnprS6d6Gxbz1bD+p5n9A/5aWlqR/kBoIN8VppSwTEAQPjs
NBkLgM9ksyeCyZjhjKG1GldFioARGSZ51jgQm1F9fTnVSk1KBxkBEUFOcfykAFCApdUURAusCWYv4amVv9ixmmdk
XKCHjudk4ycJhD3eTioFvVmPLe3Z8i6KQENdlIqQHuYqlvp39DnsOZLDthSeQMhSLK2PYhdB9ASs4qD9nXk+OJjl
YI9D3jVURSwWzAzRcFGUqog17LtDiS/tR3t3gS3tWdq6C2QKhoqQxcUzgjTURZkZt0f1nxIARgRLKT48mGHZ4/vQ
IY0IiBE+eOQSrqqNDFucJ4KtFL/a1scDz7YRiNs4BcP0ygD7HruUqoiFawRbK95vy/Ct147y1r4B+jPecNVrKeYk
A6xonMY3b51FOKDL85SI+agzz8pfHeG3u/rpSbswNM6jFbMSNk1Lqlh5Ww3VMWsUiFMSAVsrdEj7Oy7gGjkpogFr
sH9GQSyky1xia8XLm3q57/k2Cq4hGrZIxm1fb/i0YwSODbg89soR3tqf5pcP1BMPW3hF8NbuHeDOH7fQ0+8SiVhU
VYzYaYG+rOGp33eyZu8Av374YmqTgZNygp5QCcrw5+Tu5uj+pTHbD+f40gttKA2JmL/wnn6XVM4j7xh6BjxSOY+Q
rUkmA/xxe4p//r+Osq440udw93OtpHIeibiN1tA74NKb8cf3pj16Mx62DcmqADvbs3z5pYNlDpNT4YBPxgf3/37/
zePkcoZE3MbxBM8TvnbLTO5aUkUsqGnpKvD4746xpT1LLKSJVwV4eVMv//IXM5k/I8Qz609w7ESBqsoAjhHyBeHe
xmpWNE4jEbU42ufww7VdvLGrHyusqErYvLE7xcbWNI31MTwjYyr0KQMgIx5G/B7eV7At/3+b2jLogM9wmZzHnUuS
PNE0u9z36jkRbpgfY/4ju+jtd9EBjRlweefjNPNnhFh/II2yfeWbyRuW1kd5YcXcwcnmRLjl0jgLH91N65EcVtjC
S7m8uWeAxvoYIp8QB1iqaB7V6HdjKRuFQgTyrkGpYqBBKXLu8Ch1wRNmVNisfvhiutMuQUvhuMIVtREA8q6UgdZK
UXBlmIIruIKlofn+i+jocQgGFI4jLJgV9tc4jhKYMgA5R8g5Mkyx+BreX8RIP8IrKs6aRIB9R/OIQDSs+d3Ofu57
oZ0HbqzmitkRYkGfO264ODbmvBdVB1lnBAQiQcW2Q1luf/pjvr5sJkvmRkgUTWfD3CjMHe8weBoASBHFpmdaCVhq
uB9Q/J3OGyJFk1eCoPRzReM01m5PoaO+aQoFFT/bcIKfv9dD/fQgV86O0Dgvys0L4yyZGynvqta+Bbnvumn8bP0J
jAhKQTioeW1bite3p6irDnLFhWGurY9x88IKri+CWHAF21IntVxT5oCjKRcZR6CUGj1ZyYm699ppvNua4enfd6JD
FtGgIllh4wm0niiw72iOX7zfQyisWbYozn8sr+HqOZGyJfnCogoeu/NCHvlFBwQUsZAmGbMw4jtgrccLvPpBH3ZA
0zgvysrbavjCoooJLdeUD0O5giE/zlMoyvl4HPTfd9fy/N9fxBUXhskUDD0pl1TaReGbxmSljW0pVm/v44bH9/L6
jhRa+T6/Efi3W2fxysPzaKyPUnCFnpRL34CLEaiMWiQrbcJBxbr9ab74xH6effsEWp3cfNtTNWnLr0pQFbGGiUBJ
HxzoyvNeS4ZgQI22HOJ7jCsap3HP0iTvtmR4+0Cad1vSbD2cpaWrgAjEwppEzCadN6z4aTtbH1lETSKAMYIrsHxx
guWLE2xqy7B+f5qNLWm2Hsqy/3gB1zXEIhaVEQvHEx78+SGW1kW5sjZy+mZQFV3e7/31hcybHhqzz/++18P63a1E
gnbZMEr5UDUYlwlYihvmx7hhvi+r/TnDprYM332jk9/sTBEOamIhTVevw8ubevn6shmjFt9QF6WhLgrMIOsYth7K
8aO1x3l5Uy+hAARtRTbr8dyGbp78m9mfnBnsyxo8M5YVUKQLZljsyTNCPKT5za4U//naMSqiFumCYcHMEM/+3Rzy
RdMVD2tuXlTBTQsrWPztj9jVkaMi7J/mWrry7D6a4/4XD1IRtsh7hmTU5sUVc7G0r3MiAc119VGuq6/jWL/LG7v6
qYxaKEux52iueIz/pPwA7VsDNQSAkoUYyWGl956BdTtT6JiF8eCtvQM8eGM1S+ZGT26qxFes4YBm/Z5+CGgf4Lzh
3muTLF+cOFns7/TjAacdiFeQdQyN9TGmzwyRdQwBrcgVDE3/08pjt9fQOC9GKKA43OPwxB+Os+twlkhIlz3J+uog
9dVBFtRGONhdIBzUFAKa+186yJE+l2WXVPji0u/y7NsneHPPANFwcbwnLLrAd4SMAW2dYQCUUmQLwrSYxb3XJvne
68dITgtgBxTtvQ73PNdKImYTtBS9WQ/HEWIRjVaKnGOojAfKu/zQn0/nay8eJDxNY1mKvpzHAy+1E4/ZhG1FKmfI
5z2iEQutfLFUtuLea5MndYT0RBEeW6thj5pCf0srtPZF4Vu31fDFqxL09Dg4rhALat8PMEKmYIgGNckKCwX+CbFg
eOru2cybHsQ1wj/eNIN7bqymt9sh5xj/1FgMfGQKhpCtSMZtLA2ZvJDud/mvOy6koS7qxzdOxRV2PMEdcOl1dPls
7J7EqOYcv/8J7ctpd/HAoICKkObVB+fx2OqjPL+hmyO9hcFghho8TVkBzdK6KP9+ew1/eVkcI0U/XuClL9VxdW2E
p9Z20Xqi4IeYRoxXtuLymjDfvHUWf/tnSYzIuKG3cQEoDbjsgjDPf6W+7PqKCBdVh0axVKn/LZfGef6heQQDCtcT
IkFNtOjji0A4oPj28hr+adkM3j6QZkdHjmMpl4LnW4u6aj+kdV19dFRIq3Sj/41bZnL/56t5+0CarYdyHOlzyLk+
B82pCrJkboTrL44RsFRx/ARqcdOmTQGAnfsOrhySCvPp3VF7k7t1d73x3k92/Jj9HBGRXQcOfb94X2jbE3l+3ggP
whpLD4gpxxKHZc0psJUq26bSMVqM8blXxtYjuhRdlrEtixjjh8XRo+yeKobuJxvNtidUgpOJLRdv07Ua3+EY9d3T
vOf8pLI2T2Mdg6cB9/BWxHh+Xo58yjdsSiEiKG1hz148ai1nDoAioanmh8iu+wkqGCmLwqd/uamRQpbI5/+ByqYf
lVzGMwmA+IvwHPI7XkMcA1YBjHdmANAW4hh/7rueRFmnntVzigAoEIOyAlTe9STpP3wXLBt1hi6YBQWeS2zZN3zi
xZT10JkTgeKEocV3EFp8x5/2ivc0UpoGATCnqEXE+ByhOHMZBuW55JSIH3poHwTAEue00T+TqTXq1CfUMkirLlVb
eI7XISNuc86nNoQkcV3TUQagublZALKOuzs1kAOwzstsGX9XdbbgqYLj7Sy91U1NTQbAKvRt7e5NHSnl051v9Jfy
H493dfcV+jPvl9SBVkrJmjVr7IaGhkwuV/hlMcvanH8sgKeUIpPL//r66z/XLSKWUsrPCL3pppsMQH8h91Rnd7/H
mdXpZ4D7BUD19GdJD2SfBGgeo5MFsHVP2w/L6fLnT7Z4QURkx772F4fSOjIkZkRESy74rx8f6twFBBS45wEbuECg
9fDxtlSer4qIXrlypYzHKhpgw+Yd8w8e7W4fLJw493hhaMnM4c6eznc277lyKI3jtlIhwTtb9i9o7ejaMaJSzBhj
zspKClMsnCoFnkTEK9YL7V+35aPFAKsmW/xZAmH1xo2VH7Uee7qzu38ozd5ZXDZXDqR1pzKyr73zp2vWbJo+Uu4n
dZEytNjwgx0HllYm4l8JhwJ/laiMz4qFzs4q2kzB0NeX6srknd8OpLM/vuqSuvUjaZnSTdLI0tl129qSiZB1TSBg
XabE1IIE/9QOgy/QyjGYDs/IrrxnbW64ZHbXEHmX0y6mPp+Lp9UUP6yKoJ+tJRXCFMvn/x/KOz4SZm/u9wAAAABJ
RU5ErkJggg==
"""


def _first_font(candidates: tuple[str, ...], default: str) -> str:
    have = {f.lower(): f for f in tkfont.families()}
    for c in candidates:
        if c.lower() in have:
            return have[c.lower()]
    return default


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

        self.gutter = tk.Canvas(self, width=48, highlightthickness=0, bd=0)
        self.text = tk.Text(
            self, wrap="none", undo=True, maxundo=-1, font=font, bd=0, highlightthickness=0,
            padx=8, pady=6, spacing1=1, spacing3=1, tabs=(font.measure("  "),), cursor="xterm",
        )
        self.rail = tk.Canvas(self, width=12, highlightthickness=0, bd=0, cursor="hand2")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.text.xview)
        self.text.configure(yscrollcommand=self._on_yscroll, xscrollcommand=self.hsb.set)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.gutter.grid(row=0, column=0, sticky="ns")
        self.text.grid(row=0, column=1, sticky="nsew")
        self.rail.grid(row=0, column=2, sticky="ns", pady=8)
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
            bg=p["panel"], fg=p["fg"], insertbackground=p["fg"], selectbackground=p["accent_soft"],
            selectforeground=p["fg"], inactiveselectbackground=p["accent_soft"],
        )
        self.gutter.configure(bg=p["panel"])
        self.rail.configure(bg=p["panel"])
        t = self.text
        t.tag_configure("kw", foreground=p["kw"])
        t.tag_configure("str", foreground=p["str"])
        t.tag_configure("num", foreground=p["num"])
        t.tag_configure("cmt", foreground=p["cmt"])
        t.tag_configure("section", background=p["edit_bg"])
        t.tag_configure("flash", background=p["accent_soft"])
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
        self.text.yview(f"{max(a - 2, 1)}.0")
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
        starts = [0]
        for m in re.finditer("\n", text):
            starts.append(m.end())

        def idx(off: int) -> str:
            line = bisect.bisect_right(starts, off) - 1
            return f"{line + 1}.{off - starts[line]}"

        comments = [(m.start(), m.end()) for m in COMMENT_RE.finditer(text)]
        cstarts = [c[0] for c in comments]

        def in_comment(off: int) -> bool:
            i = bisect.bisect_right(cstarts, off) - 1
            return i >= 0 and off < comments[i][1]

        for m in TOKEN_RE.finditer(text):
            if in_comment(m.start()):
                continue
            t.tag_add(m.lastgroup, idx(m.start()), idx(m.end()))
        for s, e in comments:
            t.tag_add("cmt", idx(s), idx(e))

    # -- gutter and rail ----------------------------------------------------
    def _on_yscroll(self, first, last) -> None:
        self.vsb.set(first, last)
        self._schedule_gutter()

    def _schedule_gutter(self) -> None:
        if self._gutter_job is None:
            self._gutter_job = self.after_idle(self._draw_gutter)

    def _draw_gutter(self) -> None:
        self._gutter_job = None
        c, t, p = self.gutter, self.text, self.p
        total = int(t.index("end-1c").split(".")[0])
        width = self.font.measure("0") * max(3, len(str(total))) + 22
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
                c.create_rectangle(width - 4, y, width, y + h, fill=p["edit"], width=0)
            c.create_text(width - 12, y + h / 2, text=str(ln), anchor="e", fill=p["cmt"], font=self.font)
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
        c.create_rectangle(3, 0, 9, h - 1, fill=p["panel2"], outline=p["line"])
        y0 = a / total * (h - 2)
        y1 = max(y0 + 4, (b + 1) / total * (h - 2))
        c.create_rectangle(3, y0, 9, y1, fill=p["edit"], width=0)


class StartDialog(tk.Toplevel if tk else object):  # type: ignore[misc]
    """Asks for the scripts folder. Result is stored in self.result (None if cancelled)."""

    def __init__(self, master, palette: dict, ui_font, initial: str):
        super().__init__(master)
        p = palette
        self.result: Optional[str] = None
        self.title("Select scripts folder")
        self.configure(bg=p["panel"])
        self.resizable(False, False)
        self.transient(master)

        tk.Label(self, text="Select the folder with your SAP HANA SQL scripts", bg=p["panel"], fg=p["fg"],
                 font=(ui_font, 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(18, 4))
        tk.Label(self, text="All .txt and .sql files in it and its subfolders will be loaded.", bg=p["panel"],
                 fg=p["dim"], font=(ui_font, 10)).grid(row=1, column=0, columnspan=2, sticky="w", padx=20)

        self.var = tk.StringVar(value=initial)
        self.entry = tk.Entry(self, textvariable=self.var, width=62, relief="flat", bg=p["bg"], fg=p["fg"],
                              insertbackground=p["fg"], highlightthickness=1, highlightbackground=p["line"],
                              highlightcolor=p["accent"], font=(ui_font, 10))
        self.entry.grid(row=2, column=0, sticky="ew", padx=(20, 8), pady=14, ipady=5)
        browse = tk.Button(self, text="Browse…", command=self._browse, relief="flat", bg=p["panel"], fg=p["fg"],
                           highlightthickness=1, highlightbackground=p["line"], padx=12, pady=4, font=(ui_font, 10))
        browse.grid(row=2, column=1, padx=(0, 20))

        self.error = tk.Label(self, text="", bg=p["panel"], fg=p["edit"], font=(ui_font, 10), anchor="w")
        self.error.grid(row=3, column=0, columnspan=2, sticky="ew", padx=20)

        bar = tk.Frame(self, bg=p["bg"])
        bar.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        tk.Button(bar, text="Quit", command=self._cancel, relief="flat", bg=p["panel"], fg=p["fg"],
                  highlightthickness=1, highlightbackground=p["line"], padx=14, pady=4,
                  font=(ui_font, 10)).pack(side="right", padx=(8, 16), pady=12)
        tk.Button(bar, text="Open", command=self._ok, relief="flat", bg=p["accent"], fg=p["accent_ink"],
                  activebackground=p["accent"], activeforeground=p["accent_ink"], padx=18, pady=4,
                  font=(ui_font, 10, "bold")).pack(side="right", pady=12)

        self.bind("<Return>", lambda _e: self._ok())
        self.bind("<Escape>", lambda _e: self._cancel())
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.update_idletasks()
        x = master.winfo_rootx() + max(0, (master.winfo_width() - self.winfo_reqwidth()) // 2)
        y = master.winfo_rooty() + max(0, (master.winfo_height() - self.winfo_reqheight()) // 3)
        self.geometry(f"+{x}+{y}")
        self.entry.focus_set()
        self.entry.select_range(0, "end")
        self.grab_set()

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


class Tab:
    def __init__(self, doc: ScriptDocument, entry: ScriptEntry, editor: CodeEditor):
        self.doc, self.entry, self.editor = doc, entry, editor
        self.frame = self.dot = self.title = self.close = self.bar = None


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
        self._rows: dict[str, ScriptEntry] = {}
        self._search_job = None
        self._toast_job = None
        self._load_queue: queue.Queue = queue.Queue()
        self._suppress_select = False

        self.title(APP_NAME)
        self.geometry("1240x780")
        self.minsize(860, 520)
        try:
            self._icon = tk.PhotoImage(data=base64.b64decode("".join(ICON_PNG_B64.split())))
            self.iconphoto(True, self._icon)
        except tk.TclError:
            pass

        self.ui_font = _first_font(("Segoe UI", "SF Pro Text", "Noto Sans", "DejaVu Sans"), "TkDefaultFont")
        mono = _first_font(("Cascadia Mono", "Consolas", "Menlo", "DejaVu Sans Mono", "Liberation Mono"), "TkFixedFont")
        self.mono = tkfont.Font(family=mono, size=11)

        self._build()
        self.apply_theme()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind_all("<Control-s>", lambda _e: self.save_current())
        self.bind_all("<Control-w>", lambda _e: self.close_tab(self.current) if self.current else None)
        self.bind_all("<Control-f>", self._focus_search)
        self.after(60, self.startup)

    # ------------------------------------------------------------------ UI
    def _build(self) -> None:
        f = lambda size=10, weight="normal": (self.ui_font, size, weight)  # noqa: E731
        self.configure(bg="#000000")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # app bar
        self.appbar = tk.Frame(self, height=40)
        self.appbar.grid(row=0, column=0, sticky="ew")
        self.appbar.grid_propagate(False)
        self.appbar.grid_columnconfigure(2, weight=1)
        self.logo = tk.Canvas(self.appbar, width=22, height=16, highlightthickness=0, bd=0)
        self.logo.grid(row=0, column=0, padx=(14, 8), pady=12)
        self.logo.create_polygon(0, 0, 22, 0, 13.5, 15, 0, 15, tags="logo")
        self.app_title = tk.Label(self.appbar, text=APP_NAME, font=f(11, "bold"))
        self.app_title.grid(row=0, column=1)
        self.folder_label = tk.Label(self.appbar, text="", font=f(9), anchor="e")
        self.folder_label.grid(row=0, column=2, sticky="e", padx=10)
        self.theme_btn = tk.Button(self.appbar, command=self.toggle_theme, relief="flat", bd=0, padx=10, pady=3, font=f(9))
        self.theme_btn.grid(row=0, column=3, padx=3)
        self.folder_btn = tk.Button(self.appbar, text="Change folder", command=self.change_folder, relief="flat", bd=0,
                                    padx=10, pady=3, font=f(9))
        self.folder_btn.grid(row=0, column=4, padx=(3, 10))

        # body
        self.body = tk.Frame(self)
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(1, weight=1)

        self.side = tk.Frame(self.body, width=320)
        self.side.grid(row=0, column=0, sticky="ns")
        self.side.grid_propagate(False)
        self.side.grid_rowconfigure(4, weight=1)
        self.side.grid_columnconfigure(0, weight=1)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._schedule_search())
        self.search_caption = tk.Label(self.side, text="Search scripts by name or content", font=f(9), anchor="w")
        self.search_caption.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))
        self.search = tk.Entry(self.side, textvariable=self.search_var, relief="flat", font=f(10))
        self.search.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 6), ipady=6)
        self.name_only = tk.BooleanVar(value=self.settings.name_only)
        self.name_only.trace_add("write", lambda *_: self._on_name_only())
        self.name_only_cb = tk.Checkbutton(self.side, text="Match file names only", variable=self.name_only,
                                           relief="flat", bd=0, font=f(9), anchor="w", highlightthickness=0)
        self.name_only_cb.grid(row=2, column=0, sticky="w", padx=10)
        self.count_label = tk.Label(self.side, text="", font=f(9), anchor="w")
        self.count_label.grid(row=3, column=0, sticky="ew", padx=12, pady=(6, 6))

        self.listwrap = tk.Frame(self.side)
        self.listwrap.grid(row=4, column=0, sticky="nsew")
        self.listwrap.grid_rowconfigure(0, weight=1)
        self.listwrap.grid_columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(self.listwrap, columns=("name", "ver"), show="", selectmode="browse",
                                 style="Scripts.Treeview")
        self.tree.column("name", stretch=True, width=210)
        self.tree.column("ver", stretch=False, width=80, anchor="e")
        self.tree_sb = ttk.Scrollbar(self.listwrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_sb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree_sb.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.empty_label = tk.Label(self.listwrap, text="", font=f(10), wraplength=270, justify="left")

        # editor area
        self.right = tk.Frame(self.body)
        self.right.grid(row=0, column=1, sticky="nsew")
        self.right.grid_rowconfigure(2, weight=1)
        self.right.grid_columnconfigure(0, weight=1)
        self.tabstrip = tk.Frame(self.right)
        self.tabstrip.grid(row=0, column=0, sticky="ew")

        self.actions = tk.Frame(self.right)
        self.actions.grid(row=1, column=0, sticky="ew")
        self.jump_btn = tk.Button(self.actions, text="Go to modification section", command=self.jump, relief="flat",
                                  bd=0, padx=12, pady=5, font=f(10, "bold"))
        self.reset_btn = tk.Button(self.actions, text="Reset to original", command=self.reset, relief="flat", padx=12,
                                   pady=4, font=f(10))
        self.copy_btn = tk.Button(self.actions, text="Copy script", command=self.copy, relief="flat", padx=12, pady=4,
                                  font=f(10))
        self.jump_btn.pack(side="left", padx=(12, 10), pady=8)
        self.reset_btn.pack(side="left", padx=(0, 6), pady=8)
        self.copy_btn.pack(side="left", pady=8)
        self.section_label = tk.Label(self.actions, text="", font=f(9))
        self.section_label.pack(side="right", padx=14)
        self.section_swatch = tk.Frame(self.actions, width=11, height=11, highlightthickness=1)
        self.section_swatch.pack(side="right")

        self.editor_host = tk.Frame(self.right)
        self.editor_host.grid(row=2, column=0, sticky="nsew")
        self.editor_host.grid_rowconfigure(0, weight=1)
        self.editor_host.grid_columnconfigure(0, weight=1)
        self.empty_state = tk.Frame(self.editor_host)
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.empty_title = tk.Label(self.empty_state, text="Open a script to start", font=f(14, "bold"))
        self.empty_text = tk.Label(self.empty_state, text="Pick a script from the list on the left. You can keep several "
                                   "scripts open in tabs.", font=f(10), wraplength=340, justify="center")
        self.empty_title.place(relx=0.5, rely=0.42, anchor="center")
        self.empty_text.place(relx=0.5, rely=0.48, anchor="n")
        self.toast = tk.Label(self.editor_host, text="", font=f(10), padx=14, pady=8)

        # status bar
        self.status = tk.Frame(self)
        self.status.grid(row=2, column=0, sticky="ew")
        self.pos_label = tk.Label(self.status, text="Ln 1, Col 1", font=f(9))
        self.state_label = tk.Label(self.status, text="No changes", font=f(9))
        tk.Label(self.status, text="UTF-8", font=f(9)).pack(side="left", padx=(14, 18), pady=4)
        tk.Label(self.status, text="SQL", font=f(9)).pack(side="left", pady=4)
        self.pos_label.pack(side="left", padx=18, pady=4)
        self.state_label.pack(side="right", padx=14, pady=4)
        self._status_children = list(self.status.winfo_children())

        self._set_actions_enabled(False)

    # --------------------------------------------------------------- theme
    def apply_theme(self) -> None:
        p = self.p
        self.configure(bg=p["bg"])
        for w in (self.appbar,):
            w.configure(bg=p["shell"])
        self.logo.configure(bg=p["shell"])
        self.logo.itemconfigure("logo", fill=p["accent"], outline=p["accent"])
        self.app_title.configure(bg=p["shell"], fg=p["shell_fg"])
        self.folder_label.configure(bg=p["shell"], fg=p["shell_dim"])
        for b in (self.theme_btn, self.folder_btn):
            b.configure(bg=p["shell2"], fg=p["shell_fg"], activebackground="#34506B", activeforeground=p["shell_fg"])
        self.theme_btn.configure(text="Dark theme" if self.settings.theme == "light" else "Light theme")

        self.body.configure(bg=p["bg"])
        self.side.configure(bg=p["panel2"])
        self.listwrap.configure(bg=p["panel2"])
        self.search.configure(bg=p["panel"], fg=p["fg"], insertbackground=p["fg"], highlightthickness=1,
                              highlightbackground=p["line"], highlightcolor=p["accent"])
        self.name_only_cb.configure(bg=p["panel2"], fg=p["fg"], activebackground=p["panel2"], activeforeground=p["fg"],
                                    selectcolor=p["panel"])
        self.count_label.configure(bg=p["panel2"], fg=p["dim"])
        self.search_caption.configure(bg=p["panel2"], fg=p["dim"])
        self.empty_label.configure(bg=p["panel2"], fg=p["dim"])

        self.right.configure(bg=p["panel"])
        self.tabstrip.configure(bg=p["bg"])
        self.actions.configure(bg=p["panel"], highlightthickness=0)
        self.jump_btn.configure(bg=p["accent"], fg=p["accent_ink"], activebackground=p["accent"],
                                activeforeground=p["accent_ink"], disabledforeground=p["accent_ink"])
        for b in (self.reset_btn, self.copy_btn):
            b.configure(bg=p["panel"], fg=p["fg"], activebackground=p["bg"], activeforeground=p["fg"],
                        highlightthickness=1, highlightbackground=p["line"], disabledforeground=p["dim"])
        self.section_label.configure(bg=p["panel"], fg=p["dim"])
        self.section_swatch.configure(bg=p["edit_bg"], highlightbackground=p["edit"])
        self.editor_host.configure(bg=p["panel"])
        self.empty_state.configure(bg=p["panel"])
        self.empty_title.configure(bg=p["panel"], fg=p["fg"])
        self.empty_text.configure(bg=p["panel"], fg=p["dim"])
        self.toast.configure(bg=p["shell"], fg=p["shell_fg"])
        self.status.configure(bg=p["shell2"])
        for w in self._status_children:
            w.configure(bg=p["shell2"], fg=p["shell_dim"])
        self._update_state_label()

        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("Scripts.Treeview", background=p["panel2"], fieldbackground=p["panel2"], foreground=p["fg"],
                     borderwidth=0, rowheight=26, font=(self.ui_font, 10))
        st.map("Scripts.Treeview", background=[("selected", p["panel"])], foreground=[("selected", p["accent"])])
        st.layout("Scripts.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        st.configure("Vertical.TScrollbar", background=p["line"], troughcolor=p["panel2"], bordercolor=p["panel2"],
                     arrowcolor=p["dim"], lightcolor=p["line"], darkcolor=p["line"])
        st.configure("Horizontal.TScrollbar", background=p["line"], troughcolor=p["panel2"], bordercolor=p["panel2"],
                     arrowcolor=p["dim"], lightcolor=p["line"], darkcolor=p["line"])
        for name in ("Vertical.TScrollbar", "Horizontal.TScrollbar"):
            st.map(name, background=[("disabled", p["line"]), ("active", p["dim"]), ("!active", p["line"])])
        for t in self.tabs:
            t.editor.set_palette(p)
        self._style_jump_button()
        self._render_tabs()
        self._refresh_list_marks()

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
        dlg = StartDialog(self, self.p, self.ui_font, self.settings.last_folder)
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
        self._clear_list()
        self.library = None

        def work() -> None:
            try:
                self._load_queue.put((path, ScriptLibrary.load(path), None))
            except Exception as ex:  # noqa: BLE001 - reported to the user
                self._load_queue.put((path, None, ex))

        threading.Thread(target=work, daemon=True).start()
        self.after(40, self._poll_load)

    def _poll_load(self) -> None:
        try:
            path, lib, err = self._load_queue.get_nowait()
        except queue.Empty:
            self.after(40, self._poll_load)
            return
        if err is not None:
            self.count_label.configure(text=f"Cannot read this folder: {err}")
            return
        self.library = lib
        self._apply_filter()

    # -------------------------------------------------------------- search
    def _focus_search(self, _e=None):
        self.search.focus_set()
        self.search.select_range(0, "end")
        return "break"

    def _schedule_search(self) -> None:
        if self._search_job:
            self.after_cancel(self._search_job)
        self._search_job = self.after(150, self._apply_filter)

    def _on_name_only(self) -> None:
        self.settings.name_only = bool(self.name_only.get())
        self.settings.save()
        self._apply_filter()

    def _clear_list(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self._rows.clear()

    def _row_text(self, e: ScriptEntry) -> str:
        mod = any(t.entry is e and t.doc.is_modified for t in self.tabs)
        name = e.base_name + (f"   {e.folder}" if e.folder else "")
        return ("● " if mod else "") + name

    def _apply_filter(self) -> None:
        self._search_job = None
        if self.library is None:
            return
        hits = self.library.search(self.search_var.get(), bool(self.name_only.get()))
        self._clear_list()
        for e in hits:
            self.tree.insert("", "end", iid=e.path, values=(self._row_text(e), e.version))
            self._rows[e.path] = e
        total = len(self.library.entries)
        self.count_label.configure(text=f"{len(hits):,} of {total:,} scripts")
        if hits:
            self.empty_label.place_forget()
        else:
            self.empty_label.configure(text="No .txt or .sql files found in this folder. Use Change folder to pick "
                                       "another one." if total == 0 else "No scripts match your search.")
            self.empty_label.place(x=12, y=14)
        if self.current and self.current.entry.path in self._rows:
            self._select_row(self.current.entry.path)

    def _select_row(self, path: str) -> None:
        self._suppress_select = True
        try:
            self.tree.selection_set(path)
            self.tree.see(path)
        finally:
            self.after_idle(lambda: setattr(self, "_suppress_select", False))

    def _refresh_list_marks(self) -> None:
        for path, e in self._rows.items():
            self.tree.set(path, "name", self._row_text(e))

    def _on_select(self, _e=None) -> None:
        if self._suppress_select:
            return
        sel = self.tree.selection()
        if sel and sel[0] in self._rows:
            self.open_script(self._rows[sel[0]])

    # ---------------------------------------------------------------- tabs
    def open_script(self, entry: ScriptEntry) -> None:
        for t in self.tabs:
            if t.entry.path == entry.path:
                self.select_tab(t)
                return
        try:
            doc = ScriptDocument(entry.path)
        except OSError as ex:
            self.show_toast(f"Cannot open {entry.file_name}: {ex.strerror or ex}")
            return
        editor = CodeEditor(self.editor_host, doc, self.p, self.mono, self._on_editor_change, self._on_cursor)
        tab = Tab(doc, entry, editor)
        self.tabs.append(tab)
        self.select_tab(tab)

    def select_tab(self, tab: Optional[Tab]) -> None:
        self.current = tab
        for t in self.tabs:
            t.editor.grid_forget()
        self.empty_state.grid_forget()
        if tab is None:
            self.empty_state.grid(row=0, column=0, sticky="nsew")
        else:
            tab.editor.grid(row=0, column=0, sticky="nsew")
            tab.editor.text.focus_set()
            self._select_row(tab.entry.path) if tab.entry.path in self._rows else self.tree.selection_set(())
        self._set_actions_enabled(tab is not None)
        self._render_tabs()
        self._update_section_info()
        self._update_state_label()
        if tab:
            self._on_cursor(tab.editor)

    def _render_tabs(self) -> None:
        p = self.p
        for w in self.tabstrip.winfo_children():
            w.destroy()
        self.tabstrip.configure(bg=p["bg"])
        tk.Frame(self.tabstrip, height=6, bg=p["bg"]).pack(side="top", fill="x")
        row = tk.Frame(self.tabstrip, bg=p["bg"])
        row.pack(side="top", fill="x", padx=(8, 0))
        for t in self.tabs:
            sel = t is self.current
            bg = p["panel"] if sel else p["bg"]
            fg = p["fg"] if sel else p["dim"]
            box = tk.Frame(row, bg=bg)
            box.pack(side="left", padx=(0, 2))
            tk.Frame(box, height=2, bg=p["accent"] if sel else bg).pack(side="top", fill="x")
            inner = tk.Frame(box, bg=bg)
            inner.pack(side="top")
            title = tk.Label(inner, text=self._tab_title(t), bg=bg, fg=fg, font=(self.ui_font, 10), padx=10, pady=5)
            title.pack(side="left")
            dot = tk.Label(inner, text="●" if t.doc.is_modified else " ", bg=bg, fg=p["edit"], font=(self.ui_font, 8))
            dot.pack(side="left")
            close = tk.Label(inner, text="✕", bg=bg, fg=p["dim"], font=(self.ui_font, 8), padx=6, cursor="hand2")
            close.pack(side="left", padx=(0, 4))
            close.bind("<Enter>", lambda _e, c=close: c.configure(fg=p["fg"]))
            close.bind("<Leave>", lambda _e, c=close: c.configure(fg=p["dim"]))
            close.bind("<Button-1>", lambda _e, tab=t: self.close_tab(tab))
            for w in (box, inner, title, dot):
                w.bind("<Button-1>", lambda _e, tab=t: self.select_tab(tab))
                w.bind("<Button-2>", lambda _e, tab=t: self.close_tab(tab))
                w.bind("<Button-3>", lambda e, tab=t: self._tab_menu(e, tab))
            t.title, t.dot, t.close, t.frame = title, dot, close, box
        tk.Frame(self.tabstrip, height=1, bg=p["line"]).pack(side="bottom", fill="x")

    def _tab_title(self, t: Tab) -> str:
        return os.path.splitext(t.doc.name)[0].replace("_2.00.040+", "")

    def _tab_menu(self, event, tab: Tab) -> None:
        m = tk.Menu(self, tearoff=0)
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
        tab.editor.destroy()
        if self.current is tab:
            self.select_tab(self.tabs[min(i, len(self.tabs) - 1)] if self.tabs else None)
        else:
            self._render_tabs()
        self._refresh_list_marks()
        return True

    def _close_all_tabs(self) -> bool:
        for t in list(self.tabs):
            if not self.close_tab(t):
                return False
        return True

    # ------------------------------------------------------------- actions
    def _set_actions_enabled(self, on: bool) -> None:
        state = "normal" if on else "disabled"
        for b in (self.jump_btn, self.reset_btn, self.copy_btn):
            b.configure(state=state)
        self._style_jump_button()

    def _style_jump_button(self) -> None:
        p = self.p
        if str(self.jump_btn.cget("state")) == "disabled":
            self.jump_btn.configure(bg=p["line"], fg=p["dim"], disabledforeground=p["dim"])
        else:
            self.jump_btn.configure(bg=p["accent"], fg=p["accent_ink"])

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
        self._render_tabs()
        self._refresh_list_marks()
        self._update_state_label()
        return True

    def save_current(self):
        if self.current and self._save_tab(self.current):
            self.show_toast("Saved to disk")
        return "break"

    # ----------------------------------------------------------- callbacks
    def _on_editor_change(self, editor: CodeEditor) -> None:
        if self.current and self.current.editor is editor:
            self._update_section_info()
            self._update_state_label()
        self._render_tabs()
        self._refresh_list_marks()

    def _on_cursor(self, editor: CodeEditor) -> None:
        if self.current and self.current.editor is editor:
            line, col = editor.text.index("insert").split(".")
            self.pos_label.configure(text=f"Ln {line}, Col {int(col) + 1}")

    def _update_section_info(self) -> None:
        if not self.current:
            self.section_label.configure(text="")
            self.jump_btn.configure(state="disabled")
            self._style_jump_button()
            return
        s = self.current.editor.section
        self.section_label.configure(
            text=f"Modification section: lines {s[0] + 1}–{s[1] + 1}" if s else "No modification section in this script")
        self.jump_btn.configure(state="normal" if s else "disabled")
        self._style_jump_button()

    def _update_state_label(self) -> None:
        mod = bool(self.current and self.current.doc.is_modified)
        self.state_label.configure(text="Modified (not saved)" if mod else "No changes",
                                   fg="#FFB070" if mod else self.p["shell_dim"])

    def show_toast(self, text: str) -> None:
        self.toast.configure(text=text)
        self.toast.place(relx=1.0, rely=1.0, x=-24, y=-16, anchor="se")
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
    App().mainloop()


if __name__ == "__main__":
    main()
