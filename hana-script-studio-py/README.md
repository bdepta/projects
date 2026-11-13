# HANA Script Studio (Python edition)

The same app as the .NET version, in a single Python file with no dependencies. Browse a folder of SAP HANA SQL scripts (for example the "SQL Statement Collection" from SAP Note 1969700), filter them by a word in the file name, keep several open in tabs, change the parameters in the **Modification section**, and copy the finished script to the clipboard. Your original files are never changed until you save them yourself (Ctrl+S).

Only the Python standard library is used (Tkinter). There is nothing to build or install besides Python.

## Files

| File | What it is |
|---|---|
| `hana_script_studio.py` | The whole application |
| `test_hana_script_studio.py` | Tests for the logic (standard `unittest`) |
| `README.md` | This file |

## Installation (Windows)

1. Install Python 3.9 or newer from [python.org/downloads](https://www.python.org/downloads/). Keep the default options (they include Tkinter). Tick **Add python.exe to PATH** in the installer.
2. Download `hana_script_studio.py` (or clone the repository).
3. Start it:

   ```powershell
   python hana_script_studio.py
   ```

   You can also double-click the file if `.py` files are associated with Python.

No `pip install` is needed. To uninstall, delete the file. Settings live in `%APPDATA%\HanaScriptStudio\settings.json`.

**Linux:** Tkinter is a separate package on Debian/Ubuntu: `sudo apt install python3-tk`, then `python3 hana_script_studio.py`. **macOS:** use Python from python.org, which includes Tkinter.

## Usage

1. **Start.** The app asks for the folder with your scripts. The field is pre-filled with the folder you used last time, so you usually just press **Enter**. Use **Browse…** to pick a folder, or type or paste a path. All `.txt` and `.sql` files in the folder and its subfolders are loaded. **Change folder** (top right) opens the same window later.
2. **Search.** Type a word in the search box on the left. The list narrows as you type and shows only scripts whose **file name** contains it. With several words, all of them must appear in the name. The matching part of each name is shown in **bold blue**. Shortcut: **Ctrl+F**. Script contents are not searched.
3. **Open scripts.** The list shows full file names. Drag the thin divider between the list and the editor to make the list wider or narrower. Click a script (or select it with the arrow keys and press Enter) to open it in a new tab. You can keep many scripts open. A dot next to a name (in the tab and in the list) means unsaved changes.
4. **Edit.** Change the script in the editor. The modification section has a soft orange background and an orange mark next to the line numbers. The slim bar at the right edge of the editor shows where the section sits in the file. Click it to jump there.
5. **Buttons above the editor:**
   - **Go to modification section** moves the cursor to the `Modification section` line.
   - **Reset to original** restores the file as it is on disk and discards all edits to that script.
   - **Copy script** copies the whole, current (edited) script to the clipboard. Paste it into the tool where you run your SQL, such as SAP HANA Studio, HANA Cockpit or DBeaver.
6. **Save.** Edits are a working copy only. **Ctrl+S** writes them to the file, keeping its original encoding and line endings. If you close a tab or the window with unsaved changes, the app asks what to do.

Shortcuts: `Ctrl+F` search, `Ctrl+S` save, `Ctrl+W` close tab, `Ctrl+Z` / `Ctrl+Y` undo / redo. A tab also closes with the ✕ or a middle click.

The **Dark theme / Light theme** button in the top right switches the look. The choice is remembered.

### How the modification section is found

The section starts at the line that contains `Modification section` (case-insensitive) and ends on the line before the first `FROM` that follows it, which is where the parameters of the SAP scripts end. A `from` inside a comment or a quoted string does not count. If a script has no `Modification section` marker, the jump button is disabled and the bar above the editor says so.

## Tests

```bash
python -m unittest
```

## Performance notes

- Because only file names are searched, a folder is scanned in a fraction of a second, and filtering runs in memory with a 150 ms delay after each keystroke, so it stays instant for thousands of files.
- A script is read from disk only when you open it.
- Unlike the .NET version, this one has no installer. To get a single `.exe` you can build one yourself with PyInstaller (`pip install pyinstaller`, then `pyinstaller --onefile --windowed hana_script_studio.py`). This creates extra build folders, so delete them afterwards or keep them out of Git.
