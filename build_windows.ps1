param(
  [ValidateSet('x64','arm64')][string]$Arch = 'x64',
  [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
$Target = "windows-$Arch"
Write-Host "Building Alterfy+ for $Target"
& $Python -m pip install -r requirements.txt pyinstaller
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
New-Item -ItemType Directory -Force -Path "tools\$Target" | Out-Null
Write-Host 'Place the official VLC runtime, yt-dlp.exe and optional ffmpeg.exe in tools\' $Target
& $Python -m PyInstaller --noconfirm --clean --onedir --windowed --name AlterfyPlus `
  --icon icon.png `
  --add-data "icon.png;." `
  --add-data "portable_manifest.json;." `
  --add-data "tools;tools" `
  main.py
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }
Write-Host "Portable build ready: dist\AlterfyPlus"
