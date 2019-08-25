#!/bin/sh
set -e
python3 -m PyInstaller --onefile --name mc_twitchext --windowed -i ../assets/icon.ico main.py
