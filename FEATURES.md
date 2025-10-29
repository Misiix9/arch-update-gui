# Arch Update GUI - Features

## Main Features

### Update Checking
- **Check for Updates**: Scans both official repositories (via `checkupdates`) and AUR (via `yay -Qua`)
- **Version Information**: Shows package names with old and new versions
- **Update Count**: Displays total number of pending updates
- **Desktop Notifications**: Notifies you when checks start/complete and shows update count

### Update Installation
- **Secure Updates**: Uses `pkexec` for privilege elevation
- **Per-Package Progress**: 
  - Shows each package being updated with its own progress bar
  - Real-time status for each package (Downloading, Installing, Upgrading, Complete)
  - Percentage progress when available from pacman
  - Automatic scrolling as packages are processed
- **Live Logging**: All output is shown in real-time in the log view
- **Dual Update Support**: Handles both official packages (pacman) and AUR packages (yay)
- **Desktop Notifications**: Notifies when updates start, complete, or fail

### Package Cache Cleaning
- **Clean Cache Button**: One-click cache cleaning using `paccache`
- **Smart Cleaning**: Keeps one old version of each package
- **Notification**: Desktop notification when cleaning completes

### Window Management
- **Remember Window Size/Position**: Automatically saves and restores window geometry
- **Persistent Settings**: Color preferences and window state saved between sessions

### Enhanced Logging
- **Timestamped Entries**: All log entries include timestamps
- **Live Updates**: Log view updates in real-time during operations
- **Error Highlighting**: Errors are clearly marked in the log
- **Process Status**: Shows when processes start, finish, and any errors

### User Interface
- **Clean Monochrome Theme**: Professional dark theme with QPalette
- **Customizable Colors**: Settings dialog to customize all UI colors
- **Per-Package Progress View**: See exactly what's being installed/upgraded in real-time
- **Progress Indicators**: Visual feedback for all long-running operations
- **Organized Package List**: Sections for Official and AUR packages during check
- **Status Messages**: Always-visible status label showing current operation

## Keyboard Shortcuts
- **Check Updates**: Click "Check for Updates" button
- **Run Updates**: Click "Run Updates" button (enabled after check finds updates)
- **Clean Cache**: Click "Clean Cache" button
- **View Log**: Click document icon (top right)
- **Settings**: Click settings icon (top right)

## Desktop Notifications
Notifications are sent for:
- Update check started
- Update check completed (shows count)
- System is up to date
- Updates starting
- Pacman update in progress
- Updates completed successfully
- Cache cleaning completed
- Errors (shown as critical notifications)

## Error Handling
- **Process Failures**: Clear error messages if processes fail to start
- **Authentication Failures**: Detects when pkexec authentication is cancelled
- **Timeout Handling**: Handles hung processes gracefully
- **Missing Commands**: Warns if required tools (checkupdates, yay, paccache) are missing

## Log Features
- Real-time output streaming
- Timestamped error messages
- Process start/finish notifications
- Parsed pacman log showing installed/upgraded packages
- Persistent log that survives between sessions

## Configuration Files
- **Settings**: `~/.config/MyOrg/ArchUpdateGUI.conf`
  - Window geometry
  - Color preferences
  
## Requirements
- Python 3
- PySide6
- checkupdates (pacman-contrib package)
- yay (for AUR support)
- pkexec (polkit)
- paccache (pacman-contrib, optional for cache cleaning)
- notify-send (libnotify, optional for desktop notifications)

## Tips
1. The first time you click "Run Updates", a polkit authentication dialog will appear
2. Check the log view to see detailed output of what's happening
3. Desktop notifications work even if the window is minimized
4. The window remembers its size and position between runs
5. Use "Clean Cache" periodically to free up disk space
