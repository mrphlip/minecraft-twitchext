$ErrorActionPreference = "Stop"
python -m PyInstaller --onefile --name mc_twitchext --windowed --icon ..\assets\icon.ico --add-data "..\assets\icon.ico;." main.py
cd dist
Compress-Archive mc_twitchext.exe mc_twitchext.zip
Copy-Item mc_twitchext.zip ..\..\www\mc_twitchext.zip
