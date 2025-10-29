# Arch Update GUI

A modern, user-friendly graphical interface for managing system updates on Arch Linux and Arch-based distributions.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Platform](https://img.shields.io/badge/platform-Arch%20Linux-blue.svg)

## Features

✨ **Smart Update Management**
- Check for updates from official repositories and AUR
- View detailed package information (current → new versions)
- Desktop notifications for update status
- Real-time update progress with per-package tracking

🎨 **Modern Interface**
- Clean, professional dark theme
- Customizable color scheme
- Live logging with timestamps
- Progress indicators for all operations

🔒 **Secure & Reliable**
- Graphical password prompt (Zenity)
- Secure privilege elevation via sudo
- Database lock detection and handling
- Comprehensive error handling

📦 **Package Management**
- Official repository updates (pacman)
- AUR package updates (yay)
- Package cache cleaning (paccache)
- Detailed update logs

## Screenshots

*Coming soon*

## Supported Operating Systems

- ✅ Arch Linux
- ✅ Manjaro
- ✅ EndeavourOS
- ✅ Garuda Linux
- ✅ ArcoLinux
- ✅ Any Arch-based distribution

**Desktop Environments:** Works on all (KDE Plasma, GNOME, XFCE, i3, Hyprland, etc.)

## Requirements

### System Packages
- Python 3.8 or higher
- PySide6 (Qt6 for Python)
- pacman (comes with Arch)
- checkupdates (pacman-contrib)
- yay (AUR helper)
- zenity (graphical dialogs)
- sudo
- notify-send (libnotify) - optional, for notifications

### Python Packages
- PySide6

## Installation

### Quick Install (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/arch-update-gui.git
cd arch-update-gui
```

2. Run the installer:
```bash
chmod +x install.sh
./install.sh
```

The installer will:
- Install all required dependencies
- Set up the Python virtual environment
- Create a desktop launcher
- Configure the application

### Manual Installation

1. Install system dependencies:
```bash
sudo pacman -S python python-pip python-virtualenv pacman-contrib yay zenity libnotify
```

2. Clone the repository:
```bash
git clone https://github.com/yourusername/arch-update-gui.git
cd arch-update-gui
```

3. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

4. Install Python dependencies:
```bash
pip install PySide6
```

5. Make the script executable:
```bash
chmod +x update_gui.py
```

6. Run the application:
```bash
./update_gui.py
```

### Creating a Desktop Launcher

Create `~/.local/share/applications/arch-update-gui.desktop`:
```desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Arch Update GUI
Comment=Graphical system update manager for Arch Linux
Exec=/home/YOUR_USERNAME/arch-update-gui/venv/bin/python /home/YOUR_USERNAME/arch-update-gui/update_gui.py
Icon=system-software-update
Terminal=false
Categories=System;Settings;PackageManager;
Keywords=update;upgrade;pacman;aur;yay;
```

Replace `YOUR_USERNAME` with your actual username.

## Usage

### First Run

1. Launch the application from your application menu or run:
```bash
./update_gui.py
```

2. Click **"Check for Updates"**
   - A password dialog will appear (zenity)
   - Enter your password to authenticate
   - The app will check for updates from official repos and AUR

3. Review pending updates in the list

4. Click **"Run Updates"** to install updates
   - Official packages are updated via pacman
   - AUR packages are updated via yay (in terminal)

### Main Features

#### Check for Updates
- Click the **"Check for Updates"** button
- Enter your password when prompted
- View the list of pending updates with version numbers

#### Run Updates
- Only enabled after checking for updates
- Updates all official packages automatically
- Opens terminal for AUR package updates (requires user interaction)
- Shows real-time progress for each package

#### Clean Cache
- Click **"Clean Cache"** to remove old package versions
- Keeps one old version of each package
- Frees up disk space in `/var/cache/pacman/pkg/`

#### View Logs
- Click the document icon (top right) to view detailed logs
- See what was installed, upgraded, and any errors
- Logs persist between sessions

#### Customize Colors
- Click the settings icon (top right)
- Choose custom colors for all UI elements
- Click "Apply" to save your theme

## Configuration

Settings are automatically saved to:
```
~/.config/MyOrg/ArchUpdateGUI.conf
```

This includes:
- Window size and position
- Color preferences

## Terminal Configuration

By default, the app uses `foot` terminal for AUR updates. To use a different terminal, edit `update_gui.py`:

```python
# Line ~23
TERMINAL_CMD = "foot"  # Change to: "kitty", "alacritty", "gnome-terminal", etc.
TERMINAL_EXEC_FLAG = "-e"  # For foot/alacritty. Use "" for kitty, or "--" for gnome-terminal
```

Common terminal configurations:
```python
# Kitty
TERMINAL_CMD = "kitty"
TERMINAL_EXEC_FLAG = ""

# Alacritty
TERMINAL_CMD = "alacritty"
TERMINAL_EXEC_FLAG = "-e"

# GNOME Terminal
TERMINAL_CMD = "gnome-terminal"
TERMINAL_EXEC_FLAG = "--"

# Konsole (KDE)
TERMINAL_CMD = "konsole"
TERMINAL_EXEC_FLAG = "-e"
```

## Troubleshooting

### "Zenity not found" error
Install zenity:
```bash
sudo pacman -S zenity
```

### "Database lock" error
The app automatically handles stale locks. If issues persist:
```bash
sudo rm /var/lib/pacman/db.lck
```

### "checkupdates not found"
Install pacman-contrib:
```bash
sudo pacman -S pacman-contrib
```

### "yay not found"
Install yay:
```bash
sudo pacman -S --needed git base-devel
git clone https://aur.archlinux.org/yay.git
cd yay
makepkg -si
```

### Application won't start
Check if PySide6 is installed:
```bash
python -c "import PySide6; print('OK')"
```

If not, install it:
```bash
pip install PySide6
```

### Password prompt not appearing
Make sure zenity is installed and your `$DISPLAY` variable is set:
```bash
echo $DISPLAY  # Should output something like :0 or :1
```

## Development

### Running from Source
```bash
git clone https://github.com/yourusername/arch-update-gui.git
cd arch-update-gui
python -m venv venv
source venv/bin/activate
pip install PySide6
python update_gui.py
```

### Project Structure
```
arch-update-gui/
├── update_gui.py       # Main application
├── FEATURES.md         # Detailed feature list
├── README.md           # This file
├── install.sh          # Installation script
├── LICENSE             # MIT License
└── venv/              # Virtual environment (after setup)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PySide6](https://www.qt.io/qt-for-python) (Qt for Python)
- Uses [pacman](https://www.archlinux.org/pacman/) for system updates
- AUR support via [yay](https://github.com/Jguer/yay)
- Inspired by the Arch Linux community

## Support

If you encounter any issues or have questions:
- Open an issue on [GitHub Issues](https://github.com/misiix9/arch-update-gui/issues)
- Check existing issues for solutions
- Provide detailed information (error messages, system info, logs)

## Roadmap

- [ ] Automatic update checking on startup
- [ ] Scheduled update checks
- [ ] System tray icon
- [ ] Package search and info
- [ ] Rollback functionality
- [ ] Multiple theme presets
- [ ] Package ignoring/holding
- [ ] Update history viewer

## Author

**Onxy**
- GitHub: [@Misiix9](https://github.com/Misiix9)

---

⭐ If you find this project useful, please consider giving it a star on GitHub!
