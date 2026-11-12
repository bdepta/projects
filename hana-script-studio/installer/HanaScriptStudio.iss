; Inno Setup script. Build with:  iscc /DAppVersion=1.0.0 installer\HanaScriptStudio.iss
; Expects the self-contained publish output in ..\publish\win-x64

#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{6E1B2B3C-5C0B-4C8A-9E55-3D4E7C5B1A21}
AppName=HANA Script Studio
AppVersion={#AppVersion}
AppPublisher=HANA Script Studio
DefaultDirName={autopf}\HANA Script Studio
DefaultGroupName=HANA Script Studio
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\artifacts
OutputBaseFilename=HanaScriptStudio-Setup-{#AppVersion}
Compression=lzma2/max
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
WizardStyle=modern
UninstallDisplayName=HANA Script Studio
UninstallDisplayIcon={app}\HanaScriptStudio.exe

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: checkedonce

[Files]
Source: "..\publish\win-x64\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\HANA Script Studio"; Filename: "{app}\HanaScriptStudio.exe"
Name: "{autodesktop}\HANA Script Studio"; Filename: "{app}\HanaScriptStudio.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\HanaScriptStudio.exe"; Description: "Launch HANA Script Studio"; Flags: nowait postinstall skipifsilent
