$ErrorActionPreference = "Stop"
python -m pipenv sync --dev
python -m pipenv run python -m PyInstaller --onefile --name mc_twitchext --windowed --icon ..\assets\icon.ico --add-data "..\assets\icon.ico;." --add-data "..\assets\data_versions.json;." main.py
cd dist
If (Test-Path mc_twitchext.zip) {
	Remove-Item mc_twitchext.zip
}
Compress-Archive mc_twitchext.exe mc_twitchext.zip
Copy-Item mc_twitchext.zip ..\..\www\mc_twitchext.zip
