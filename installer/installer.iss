#define MyAppName "Ktisis"
#define MyAppVersion "2.0"
#define MyAppExeName "start.bat"

[Setup]
AppId={{8F2B1C3A-7D4E-4A9F-9C21-5B6E8D0F1A2C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
; Εγκατάσταση μόνο για τον τρέχοντα χρήστη, χωρίς δικαιώματα διαχειριστή - η
; εφαρμογή είναι ούτως ή άλλως για έναν χρήστη, τοπικά. Αυτό αποφεύγει εντελώς
; το πρόβλημα εγγραφής στο Program Files που είχαμε ξαναδεί.
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\installer_output
OutputBaseFilename=KtisisSetup
SetupIconFile=..\assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Files]
Source: "..\dist\Ktisis\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "start.bat"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\Ktisis.exe"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\Ktisis.exe"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Εκκίνηση του Ktisis"; Flags: postinstall nowait skipifsilent
