[Setup]
AppName=Ktisis
AppVersion=1.0
AppPublisher=Ktisis
DefaultDirName={autopf}\Ktisis
DefaultGroupName=Ktisis
OutputDir=installer_output
OutputBaseFilename=KtisisSetup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\Ktisis.exe

[Tasks]
Name: "desktopicon"; Description: "Δημιουργία εικονιδίου στην Επιφάνεια εργασίας"; GroupDescription: "Πρόσθετες συντομεύσεις:"

[Files]
Source: "dist\Ktisis\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Ktisis"; Filename: "{app}\Run Ktisis.bat"; WorkingDir: "{app}"
Name: "{autodesktop}\Ktisis"; Filename: "{app}\Run Ktisis.bat"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\Run Ktisis.bat"; Description: "Εκκίνηση του Ktisis"; Flags: postinstall skipifsilent nowait
