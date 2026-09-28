#!/bin/sh
# Build a standalone game folder and zip it with the config for Itch.io.
set -e
PYTHON=.venv/bin/python
NAME="pac-man-$(uname -s | tr 'A-Z' 'a-z')"

rm -rf build dist
$PYTHON -m pip install --quiet pyinstaller
$PYTHON -m PyInstaller --onedir --noconfirm --clean --name pac-man pac-man.py
mv dist/pac-man "dist/$NAME"
cp config.json highscores.json PLAY.txt "dist/$NAME/"
(cd dist && zip -qry "$NAME.zip" "$NAME")
echo "Package ready: dist/$NAME.zip"
