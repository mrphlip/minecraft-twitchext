#!/bin/sh
set -e
python3 -m pipenv sync --dev
python3 -m pipenv run python3 -m PyInstaller --onefile --name mc_twitchext --windowed --add-data ../assets/icon.ico:. --add-data ../assets/data_versions.json:. main.py
cd dist
mv mc_twitchext mc_twitchext.bin
tar cjf mc_twitchext.tar.bz2 mc_twitchext.bin
cp mc_twitchext.tar.bz2 ../../www/mc_twitchext.tar.bz2
