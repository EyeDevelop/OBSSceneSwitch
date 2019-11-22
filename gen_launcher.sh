#!/bin/bash

# Check if in the right directory.
if [[ ! -f "screen_daemon.py" ]]; then
    echo "ERROR: Run this script in the repo directory."
    exit 1
fi

if [[ ! -d "$HOME/.local/share/applications" ]]; then
    echo "ERROR: Cannot find user applications folder."
    echo "       Please create ~/.local/share/applications"
    exit 1
fi

# Create a new launcher.
cat << EOF > /tmp/stream-setup.desktop
[Desktop Entry]
Categories=Development;
Comment=Starts OBS and the rest of the stream setup.
Path=$(pwd)
Exec=./start.sh
Icon=/usr/share/icons/hicolor/256x256/apps/com.obsproject.Studio.png
Name=Start Stream Setup
Terminal=true
Type=Application
Version=1.0
EOF


echo "Successfully created desktop entry."
echo "Installing file..."

xdg-desktop-menu install /tmp/stream-setup.desktop && echo "Successfully installed desktop entry!"
