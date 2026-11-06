#define MyAppName "ATS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Harman"
#define MyAppExeName "ATS.exe"

[Setup]
AppId={{A8D7A5C8-7F16-49A0-8B72-ATS001}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}

DefaultDirName={autopf}\ATS
DefaultGroupName=ATS

OutputDir=installer
OutputBaseFilename=ATS_Setup

Compression=lzma
SolidCompression=yes

WizardStyle=modern

SetupIconFile=assets\icon.ico

UninstallDisplayIcon={app}\ATS.exe

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"

[Files]
Source: "dist\ATS\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ATS"; Filename: "{app}\ATS.exe"
Name: "{autodesktop}\ATS"; Filename: "{app}\ATS.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ATS.exe"; Description: "Iniciar ATS"; Flags: nowait postinstall skipifsilent