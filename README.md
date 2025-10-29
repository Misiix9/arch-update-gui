# Arch Update GUI

A beautiful, modern graphical user interface for managing Arch Linux system updates with support for both official repositories and AUR packages.

![Arch Update GUI](https://img.shields.io/badge/Python-3.9+-blue.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## Features

### 🎨 Beautiful Modern Interface
- **10 Premium Themes**: Dark Professional, Nord Aurora, Dracula, Monokai, Gruvbox, Tokyo Night, One Dark, Solarized Dark, Material Dark, and Cyberpunk
- **Live Theme Preview**: See theme changes instantly before applying
- **Smooth Animations**: Optional UI animations for a polished experience
- **Responsive Design**: Adapts to different screen sizes with high DPI support
- **Card-based Layout**: Clean, organized interface with gradient backgrounds
- **Unicode Icons**: Cross-platform compatible symbols

### 📦 Update Management
- **Dual Repository Support**: Manage both official Arch repositories and AUR packages
- **Real-time Progress**: Live package-by-package update tracking with progress bars
- **Smart Authentication**: Secure password handling via Zenity dialog with cached sessions
- **Background Checks**: Automatic scheduled update checks (1-24 hour intervals)
- **System Tray Integration**: Minimize to tray with quick access menu
- **Desktop Notifications**: Optional notifications for update status

### 🔧 Advanced Features
- **Package Search**: Quick search across all available packages with repository info
- **Ignored Packages**: Exclude specific packages from updates permanently
- **Update History**: Track all system updates with timestamps and status
- **Rollback Support**: Easy terminal access to package cache for rollbacks
- **Cache Management**: One-click package cache cleaning with paccache
- **Custom Terminal**: Configure your preferred terminal emulator (foot, kitty, alacritty, etc.)

### 📊 Detailed Logging
- **Comprehensive Logs**: Full update process logging with timestamps
- **Pacman Log Parsing**: Automatic extraction of update details from `/var/log/pacman.log`
- **Session History**: Track package installations and upgrades per session
- **Dedicated Log View**: Separate page for viewing full monospace logs
- **Error Tracking**: Detailed error messages and stderr capture

## Requirements

### System Requirements
- **OS**: Arch Linux or Arch-based distribution
- **Python**: 3.9 or higher
- **Display Server**: X11 or Wayland

### Dependencies

#### Python Packages
```bash
sudo pacman -S python-pyside6
```

#### System Utilities
```bash
# Required
sudo pacman -S pacman-contrib zenity

# Optional but recommended
sudo pacman -S yay            # For AUR support
sudo pacman -S libnotify      # For desktop notifications
```

## Installation

### Quick Install
```bash
# Clone or download to your preferred location
cd ~/Documents/scripts/Update

# Make executable
chmod +x update_gui.py

# Run
python update_gui.py
```

### Desktop Entry (Optional)
Create `~/.local/share/applications/arch-update-gui.desktop`:

```ini
[Desktop Entry]
Name=Arch Update GUI
Comment=Graphical update manager for Arch Linux
Exec=python /home/YOUR_USERNAME/Documents/scripts/Update/update_gui.py
Icon=system-software-update
Terminal=false
Type=Application
Categories=System;Settings;PackageManager;
Keywords=update;package;pacman;aur;yay;
```

Replace `YOUR_USERNAME` with your actual username.

## Usage

### First Run
1. Launch the application
2. Click **Settings** (⚙) to configure your preferences
3. Select your preferred theme from 10 options
4. Configure terminal emulator if using custom terminal
5. Enable auto-check or scheduled checks if desired
6. Click **Check for Updates** to authenticate and scan for updates

### Checking for Updates
1. Click **Check for Updates** button
2. Enter your password in the Zenity dialog
3. Wait for official repository scan
4. Wait for AUR package scan
5. Review available updates in the package list (📦 for official, 🎯 for AUR)

### Running Updates
1. After checking for updates, click **Run Updates**
2. Official repository updates run automatically via pacman
3. Monitor real-time progress for each package
4. AUR updates open in your terminal for manual review
5. View completion summary with package counts

### Managing Ignored Packages
1. Go to **Tools** → **Manage Ignored Packages**
2. Type package name in input field
3. Click **Add** (+) button
4. Select package from list and click **Remove** (-) to unignore
5. Changes apply immediately to future update checks

### Viewing History
1. Go to **Tools** → **Update History**
2. Review past updates with dates, types, package counts, and status
3. Click **Refresh** (↻) to reload the list
4. Use **Clear History** (⌫) to reset (confirmation required)
5. History stored in JSON format at `~/.config/MyOrg/update_history.json`

### Package Search
1. Go to **Tools** → **Search Packages**
2. Enter package name in search field
3. Press Enter or click **Search** (⌕)
4. View results in tree format with version and repository info
5. Double-click package for detailed pacman information

### Rollback Updates
1. Go to **Tools** → **Rollback Last Update**
2. Confirm the action
3. Terminal opens with rollback command
4. Follow on-screen instructions to select packages

## Configuration

### Settings Panel (3 Tabs)

#### Appearance Tab
- **Theme Selection**: Choose from 10 premium themes
  - Dark Professional (Catppuccin-inspired)
  - Nord Aurora
  - Dracula
  - Monokai
  - Gruvbox
  - Tokyo Night
  - One Dark
  - Solarized Dark
  - Material Dark
  - Cyberpunk
- **Live Preview**: See theme colors before applying
- **Typography**: Customize font family and size (8-24pt)

#### Updates Tab
- **Auto-Check on Startup**: Check for updates when app launches
- **Scheduled Checks**: Enable periodic background checks (1-24 hours)
- **System Tray**: Minimize to tray instead of closing
- **Notifications**: Toggle desktop notifications
- **Confirmation**: Require confirmation before updating (optional)

#### Advanced Tab
- **Terminal Command**: Set custom terminal (foot, kitty, alacritty, etc.)
- **Execute Flag**: Terminal execution flag (-e, --, etc.)
- **UI Animations**: Enable/disable smooth animations
- **High DPI Scaling**: Toggle high DPI support for 4K displays

### Configuration Files
Settings are stored in:
- `~/.config/MyOrg/ArchUpdateGUI.conf` - Qt settings (QSettings)
- `~/.config/MyOrg/update_history.json` - Update history log
- `~/.config/MyOrg/ignored_packages.json` - Ignored packages list

## Keyboard Shortcuts

- **Enter** in search field: Execute search
- **Esc**: Close dialogs
- **Alt+F4**: Quit application

## System Tray Features

- **Click**: Toggle window visibility
- **Menu Options**:
  - Show Window
  - Check for Updates
  - Quit

## Troubleshooting

### Authentication Issues
**Problem**: "Zenity not found" error  
**Solution**: Install zenity: `sudo pacman -S zenity`

**Problem**: Password dialog doesn't appear  
**Solution**: Ensure you're running in a graphical environment with DISPLAY set

**Problem**: Authentication fails repeatedly  
**Solution**: Verify your password is correct and your user has sudo privileges

### Update Failures
**Problem**: "Database is locked" error  
**Solution**: Close other package managers (pamac, octopi, etc.), or the app will auto-remove stale locks after 3 seconds

**Problem**: AUR updates fail  
**Solution**: Ensure `yay` is installed: `sudo pacman -S yay`

**Problem**: Process crashes during update  
**Solution**: Check the log page for error details; ensure no conflicting processes

### Display Issues
**Problem**: Blurry text on high DPI displays  
**Solution**: Enable "High DPI Scaling" in Settings → Advanced

**Problem**: Theme not applying correctly  
**Solution**: Click **Apply** in settings dialog; restart application if needed

**Problem**: Window too small on startup  
**Solution**: Resize window manually; size is saved automatically on close

### Permission Issues
**Problem**: "Authentication failed" errors  
**Solution**: Verify your user is in the `wheel` group: `groups $USER`

**Problem**: pkexec errors for cache cleaning  
**Solution**: Ensure polkit is installed and configured

## Development

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

## Author

**Onxy**
- GitHub: [@Misiix9](https://github.com/Misiix9)

---

⭐ If you find this project useful, please consider giving it a star on GitHub!
