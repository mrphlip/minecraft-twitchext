#!/bin/sh
set -e
rm -f dist/mc_twitchext_src.zip
zip dist/mc_twitchext_src.zip *.py */*.py
zip -g -j dist/mc_twitchext_src.zip  ../assets/icon.ico ../assets/data_versions.json ../assets/icon.icns ../Pipfile ../Pipfile.lock
cp dist/mc_twitchext_src.zip ../www/mc_twitchext_src.zip
