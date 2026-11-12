# HANA Script Studio

A fast desktop app for working with SAP HANA SQL scripts, such as the "SQL Statement Collection" from SAP Note 1969700. Browse a folder of scripts, filter them by a word, keep several open in tabs, change the parameters in the **Modification section**, and copy the finished script to the clipboard. Your original files are never changed until you save them yourself (Ctrl+S).

The app is written in C# (.NET 8) with Avalonia UI and the AvaloniaEdit editor. It targets Windows first. The same code can be built for macOS and Linux.

## Installation (Windows)

### Option 1: installer (recommended)

1. Download `HanaScriptStudio-Setup-<version>.exe` (see "Where to get the installer" below).
2. Run it and click through the wizard: **Next → Install → Finish**.
3. The app installs for your Windows account only, so no administrator rights are needed. .NET is bundled, so there is nothing else to install.
4. Start **HANA Script Studio** from the Start menu or the desktop shortcut.

To uninstall: **Settings → Apps → HANA Script Studio → Uninstall**.

The installer is not code-signed, so Windows SmartScreen may show "Unknown publisher". Click **More info → Run anyway**.

### Option 2: portable version

1. Download `HanaScriptStudio-portable-win-x64.zip`.
2. Unzip it to any folder and run `HanaScriptStudio.exe`. No installation is needed.

### Where to get the installer

Either build it yourself on a Windows PC with one command (needs [.NET SDK 8](https://dotnet.microsoft.com/download/dotnet/8.0) and, for the installer, [Inno Setup 6](https://jrsoftware.org/isdl.php)):

```powershell
cd hana-script-studio
.\build-windows.ps1 -Version 1.0.0
```

The files appear in `artifacts\`: `HanaScriptStudio-Setup-1.0.0.exe` and `HanaScriptStudio-portable-win-x64.zip`. Without Inno Setup the script still creates the portable zip, and you can start the app directly from `publish\win-x64\HanaScriptStudio.exe`.

Or use GitHub Actions. The workflow `HANA Script Studio` builds the same files and publishes them as the artifact `HanaScriptStudio-windows` on the **Actions** tab. To get a versioned installer, push a tag such as `hana-v1.0.0`:

```bash
git tag hana-v1.0.0 && git push origin hana-v1.0.0
```

## Usage

1. **First start.** The app asks for the folder that holds your scripts (for example the unpacked SAP collection). Your choice is remembered. Change it later with **Change folder**. All `.txt` and `.sql` files in the folder and its subfolders are loaded.
2. **Search.** Type a word in the search box on the left. The list narrows as you type and looks at file names and script content. With several words, all of them must appear. Tick **Match file names only** to search names only. Shortcut: **Ctrl+F**.
3. **Open scripts.** Click a script in the list to open it in a new tab. You can keep many scripts open. A dot next to the name means unsaved changes.
4. **Edit.** Change the script in the editor. The modification section is highlighted in orange, and the slim bar at the right edge of the editor shows where it sits in the file. Click the bar to jump there.
5. **Buttons above the editor:**
   - **Go to modification section** moves the cursor to the `Modification section` line.
   - **Reset to original** restores the file as it is on disk and discards all edits to that script.
   - **Copy script** copies the whole, current (edited) script to the clipboard. Paste it into the tool where you run your SQL, such as SAP HANA Studio, HANA Cockpit or DBeaver.
6. **Save.** Edits are a working copy only. **Ctrl+S** writes them to the file. If you close a tab or the window with unsaved changes, the app asks what to do.

Shortcuts: `Ctrl+F` search, `Ctrl+S` save, `Ctrl+W` close tab.

The **Theme** button in the top right switches between System, Light and Dark. Settings (last folder, theme) are stored in `%APPDATA%\HanaScriptStudio\settings.json`.

### How the modification section is found

The section starts at the first line that contains `Modification section` (case-insensitive) and ends on the line before the line that contains `Internal section`. If a script has no such section, the jump button is disabled and the bar above the editor says so.

## Building from source

Requirements: [.NET SDK 8](https://dotnet.microsoft.com/download/dotnet/8.0).

```bash
cd hana-script-studio
dotnet test                                # logic tests (section parser, search, reset)
dotnet run --project src/HanaScriptStudio  # run the app

# self-contained build for Windows
dotnet publish src/HanaScriptStudio -c Release -r win-x64 --self-contained -p:DebugType=none -o publish/win-x64
```

On macOS or Linux use `-r osx-arm64`, `-r osx-x64` or `-r linux-x64`. Installers for those systems are not prepared yet.

## Project layout

```
hana-script-studio/
├── src/HanaScriptStudio.Core/   UI-free logic: index and search, section parser, document, settings
├── src/HanaScriptStudio/        Avalonia app: window, SAP-style theme, SQL editor
├── tests/HanaScriptStudio.Core.Tests/   xUnit tests
├── assets/                      app icon (icon.ico, icon.png) and the script that generates it
├── installer/                   Inno Setup installer script
└── build-windows.ps1            one-command Windows build (tests, publish, zip, installer)
```

## Performance notes

- The content of all scripts is read once, in parallel, after you pick a folder. Filtering then runs in memory only, with a short delay (150 ms) after each keystroke.
- The list is virtualized, so thousands of files do not slow down scrolling.
- Files larger than 4 MB appear in the list but are skipped when searching by content.
