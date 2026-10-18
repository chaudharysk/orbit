; Orbit installer (Inno Setup 6). Build dist/Orbit first (packaging/windows/build_exe.py):
;   iscc /DAppVersion=0.1.0 packaging\windows\orbit.iss   ->  dist\OrbitSetup-0.1.0.exe
; Protected program files; remove legacy elevated startup during upgrades.
; Orbit itself runs in the original user's unelevated session.

#ifndef AppVersion
  #define AppVersion "0.1.2"
#endif

[Setup]
AppId={{6E3C7A10-0B7A-4C5E-9D2B-0A1B2C3D4E5F}
AppName=Orbit
AppVersion={#AppVersion}
AppPublisher=Orbit
AppPublisherURL=https://github.com/harsha20599/orbit
AppSupportURL=https://github.com/harsha20599/orbit/issues
DefaultDirName={autopf}\Orbit
UsePreviousAppDir=no
DefaultGroupName=Orbit
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=..\..\dist
OutputBaseFilename=OrbitSetup-{#AppVersion}
SetupIconFile=..\..\build\orbit.ico
UninstallDisplayIcon={app}\Orbit.exe
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=force
RestartApplications=no

[Tasks]
Name: "autostart"; Description: "Start Orbit when I sign in"; Flags: checkedonce
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Files]
Source: "..\..\dist\Orbit\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Orbit"; Filename: "{app}\Orbit.exe"
Name: "{userdesktop}\Orbit"; Filename: "{app}\Orbit.exe"; Tasks: desktopicon

[Run]
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM Orbit.exe /T"; Flags: runhidden waituntilterminated
Filename: "{sys}\schtasks.exe"; Parameters: "/Delete /F /TN Orbit"; Flags: runhidden waituntilterminated
Filename: "{app}\Orbit.exe"; Parameters: "--autostart on"; Description: "Start Orbit now"; Flags: nowait postinstall skipifsilent runasoriginaluser; Tasks: autostart
Filename: "{app}\Orbit.exe"; Parameters: "--autostart off"; Description: "Start Orbit now"; Flags: nowait postinstall skipifsilent runasoriginaluser; Tasks: not autostart

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueName: "Orbit"; Flags: uninsdeletevalue dontcreatekey

[UninstallRun]
; remove the sign-in task (created by Orbit, elevated); harmless if it doesn't exist
Filename: "{sys}\schtasks.exe"; Parameters: "/Delete /F /TN Orbit"; Flags: runhidden; RunOnceId: "OrbitTask"
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM Orbit.exe"; Flags: runhidden; RunOnceId: "OrbitKill"
