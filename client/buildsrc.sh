#!/bin/sh
set -e
rm -f dist/mc_twitchext_src.zip
zip dist/mc_twitchext_src.zip *.py */*.py
zip -g -j dist/mc_twitchext_src.zip ../requirements.txt ../assets/icon.ico