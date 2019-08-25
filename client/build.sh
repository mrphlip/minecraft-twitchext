#!/bin/sh
set -e
python3 -m PyInstaller --onefile --name mc_twitchext --windowed --icon ../assets/icon.ico --add-data ../assets/icon.ico:. main.py
