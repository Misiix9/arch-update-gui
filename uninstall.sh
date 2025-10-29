#!/bin/bash

# Arch Update GUI Uninstaller

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DESKTOP_FILE="$HOME/.local/share/applications/arch-update-gui.desktop"

echo "Uninstalling Arch Update GUI..."

# Remove desktop launcher
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    echo "Removed desktop launcher"
fi

# Remove virtual environment
if [ -d "$SCRIPT_DIR/venv" ]; then
    rm -rf "$SCRIPT_DIR/venv"
    echo "Removed virtual environment"
fi

# Remove config
CONFIG_DIR="$HOME/.config/MyOrg"
if [ -d "$CONFIG_DIR" ]; then
    read -p "Remove configuration files? (y/n): " remove_config
    if [[ $remove_config == "y" ]]; then
        rm -rf "$CONFIG_DIR"
        echo "Removed configuration"
    fi
fi

echo "Uninstall complete!"
echo "Note: System packages (zenity, pacman-contrib, etc.) were not removed."
