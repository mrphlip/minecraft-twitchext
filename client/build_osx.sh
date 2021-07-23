#!/bin/sh
set -e
rm -rf dist/mc_twitchext.app  # otherwise we'll get an overwrite warning
python3 -m pipenv sync -d
python3 -m pipenv run python3 -m PyInstaller --onefile --name mc_twitchext --windowed --icon ../assets/icon.icns --add-data ../assets/icon.ico:. main.py
# pyinstaller creates both dist/mc_twitchext (which doesn't work) and dist/mc_twitchext.app (which does)
rm dist/mc_twitchext
# create dmg image
rm -rf build/dmg build/uncompressed.dmg dist/mc_twitchext.dmg
mkdir build/dmg
cp -a dist/mc_twitchext.app build/dmg
hdiutil create build/uncompressed.dmg -ov -volname mc_twitchext -fs HFS+ -srcfolder build/dmg
hdiutil convert build/uncompressed.dmg -format UDZO -o dist/mc_twitchext.dmg
cp dist/mc_twitchext.dmg ../www/mc_twitchext.dmg
