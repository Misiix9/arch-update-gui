#!/usr/bin/env python

import sys
import subprocess
import os
import re
import time
from datetime import datetime
from threading import Thread

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QProgressBar, QLabel, QListWidget,
    QStackedWidget, QDialog, QColorDialog, QFormLayout, QScrollArea
)
from PySide6.QtCore import QProcess, Qt, QSettings, Signal, QObject
from PySide6.QtGui import QPalette, QColor, QIcon

# --- Configuration ---
PACMAN_LOG = "/var/log/pacman.log"
CHECKUPDATES_CMD = "/usr/bin/checkupdates"
YAY_CMD = "/usr/bin/yay"
PACMAN_CMD = "/usr/bin/pacman"
PKEXEC_CMD = "/usr/bin/pkexec"
SUDO_CMD = "/usr/bin/sudo"
ZENITY_CMD = "/usr/bin/zenity"
# Your preferred terminal emulator command (e.g., kitty, foot, alacritty)
# For foot, use: foot -e
# For kitty, use: kitty
# For alacritty, use: alacritty -e
TERMINAL_CMD = "foot"
TERMINAL_EXEC_FLAG = "-e"  # Use -e for foot, alacritty; remove for kitty

# --- Helper Function ---
def get_color_setting(settings, key, default_color):
    color_str = settings.value(key, default_color)
    return QColor(color_str)

def check_polkit_agent():
    """Check if a polkit agent is running"""
    try:
        # Check for common polkit agents more thoroughly
        agents = [
            'polkit-kde-authentication-agent',
            'polkit-gnome-authentication-agent',
            'lxpolkit',
            '/usr/lib/polkit-kde-authentication-agent-1',
            '/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1'
        ]
        
        for agent in agents:
            result = subprocess.run(['pgrep', '-f', agent], 
                                  capture_output=True, timeout=2)
            if result.returncode == 0:
                return True
        
        # Also check if DISPLAY is set (required for GUI polkit)
        if not os.environ.get('DISPLAY'):
            return False
            
        return False
    except:
        return False

# --- Settings Dialog ---
class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Color Settings")
        layout = QFormLayout(self)

        self.color_widgets = {}
        self.color_buttons = {}

        # Define color settings
        color_options = {
            "window_bg": ("Window Background", "#2e2e2e"),
            "text_fg": ("Text Color", "#e0e0e0"),
            "button_bg": ("Button Background", "#4a4a4a"),
            "button_fg": ("Button Text", "#e0e0e0"),
            "list_bg": ("List Background", "#3a3a3a"),
            "progress_bar_bg": ("Progress Bar Background", "#4a4a4a"),
            "progress_bar_chunk": ("Progress Bar Chunk", "#6a9ed4"),
        }

        for key, (label_text, default_color) in color_options.items():
            color = get_color_setting(self.settings, key, default_color)

            color_label = QLabel(f"Current: {color.name()}")
            color_button = QPushButton(label_text)
            color_button.clicked.connect(lambda checked=False, k=key, lbl=color_label: self.choose_color(k, lbl))

            self.color_widgets[key] = color_label
            self.color_buttons[key] = color_button

            layout.addRow(color_button, color_label)

        # Apply and Close buttons
        button_box = QHBoxLayout()
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply_settings)
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_box.addWidget(apply_button)
        button_box.addWidget(close_button)
        layout.addRow(button_box)

        self.load_settings()

    def choose_color(self, key, label):
        current_color = QColor(label.text().split(': ')[1])
        color = QColorDialog.getColor(current_color, self, f"Select {self.color_buttons[key].text()}")
        if color.isValid():
            label.setText(f"Current: {color.name()}")
            # Store temporarily until Apply is hit
            self.settings.setValue(f"temp_{key}", color.name())


    def apply_settings(self):
        # Apply temporary settings to actual settings
        for key in self.color_widgets.keys():
             temp_color = self.settings.value(f"temp_{key}", None)
             if temp_color:
                 self.settings.setValue(key, temp_color)
                 self.settings.remove(f"temp_{key}") # Clean up temp value
        self.parent().apply_styles() # Tell main window to re-apply styles
        self.accept() # Close dialog after applying


    def load_settings(self):
         for key, label in self.color_widgets.items():
              color = get_color_setting(self.settings, key, "#FFFFFF") # Use placeholder default
              label.setText(f"Current: {color.name()}")
              self.settings.remove(f"temp_{key}") # Clear any lingering temp values


# --- Auth Worker for threaded authentication ---
class AuthWorker(QObject):
    finished = Signal(bool)  # Success/failure
    error = Signal(str)  # Error message
    
    def __init__(self, use_zenity=True):
        super().__init__()
        self.use_zenity = use_zenity
    
    def run(self):
        try:
            if self.use_zenity and os.path.exists(ZENITY_CMD):
                # Use zenity for graphical password prompt
                result = subprocess.run(
                    [ZENITY_CMD, '--password', '--title=Arch Update GUI Authentication'],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    password = result.stdout.strip()
                    
                    # Test the password with sudo -S
                    auth_result = subprocess.run(
                        [SUDO_CMD, '-S', '-v'],
                        input=password + '\n',
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if auth_result.returncode == 0:
                        self.finished.emit(True)
                    else:
                        self.error.emit("Incorrect password")
                        self.finished.emit(False)
                else:
                    self.error.emit("Authentication cancelled")
                    self.finished.emit(False)
            else:
                # Fallback to terminal
                self.error.emit("Zenity not available")
                self.finished.emit(False)
                
        except subprocess.TimeoutExpired:
            self.error.emit("Authentication timed out")
            self.finished.emit(False)
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False)

# --- Custom Event for yay completion ---
from PySide6.QtCore import QEvent

class YayFinishedEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, returncode, error=None):
        super().__init__(self.EVENT_TYPE)
        self.returncode = returncode
        self.error = error

# --- Main Application Window ---
class UpdateAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arch Update GUI")
        self.setGeometry(100, 100, 600, 450)
        self.settings = QSettings("MyOrg", "ArchUpdateGUI")

        self.pending_pacman = []
        self.pending_aur = []
        self.update_log_content = ""
        self.start_timestamp = 0
        self.current_process = None
        self.package_widgets = {}
        self.current_package = None
        self.authenticated = False
        self.auth_thread = None
        self.auth_worker = None
        
        # Check for polkit agent
        has_polkit = check_polkit_agent()
        self.use_terminal_sudo = not has_polkit
        
        if self.use_terminal_sudo:
            print("No polkit agent detected, will use zenity/terminal with sudo")
        else:
            print("Polkit agent detected, will use pkexec")

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # --- Stacked Widget for Pages ---
        self.stacked_widget = QStackedWidget()
        self.main_page_widget = QWidget()
        self.log_page_widget = QWidget()

        self.stacked_widget.addWidget(self.main_page_widget)
        self.stacked_widget.addWidget(self.log_page_widget)
        self.main_layout.addWidget(self.stacked_widget)

        # --- Main Page Layout ---
        main_page_layout = QVBoxLayout(self.main_page_widget)

        # Buttons on top right for log/settings
        top_button_layout = QHBoxLayout()
        top_button_layout.addStretch()
        self.view_log_button = QPushButton()
        self.view_log_button.setIcon(QIcon.fromTheme("document-open")) # Use system icon
        self.view_log_button.setToolTip("View Update Log")
        self.view_log_button.clicked.connect(self.show_log_page)
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon.fromTheme("preferences-system")) # Use system icon
        self.settings_button.setToolTip("Settings")
        self.settings_button.clicked.connect(self.open_settings)
        top_button_layout.addWidget(self.view_log_button)
        top_button_layout.addWidget(self.settings_button)
        main_page_layout.addLayout(top_button_layout)


        main_page_layout.addWidget(QLabel("Pending Updates:"))
        
        # Create scroll area for package progress
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.package_progress_layout = QVBoxLayout(self.scroll_widget)
        self.package_progress_layout.addStretch()  # Push items to top
        self.scroll_area.setWidget(self.scroll_widget)
        main_page_layout.addWidget(self.scroll_area)
        
        # Keep list widget for initial check display (hidden during updates)
        self.list_widget_pending = QListWidget()
        self.list_widget_pending.setVisible(True)
        main_page_layout.addWidget(self.list_widget_pending)

        self.status_label = QLabel("Click 'Check for Updates' to begin.")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_page_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        main_page_layout.addWidget(self.progress_bar)

        # --- Bottom Buttons ---
        button_layout = QHBoxLayout()
        button_layout.addStretch() # Push buttons to center
        self.check_button = QPushButton("Check for Updates")
        self.check_button.clicked.connect(self.check_for_updates)
        self.update_button = QPushButton("Run Updates")
        self.update_button.clicked.connect(self.run_updates)
        self.update_button.setEnabled(False)
        self.clean_cache_button = QPushButton("Clean Cache")
        self.clean_cache_button.clicked.connect(self.clean_cache)
        self.clean_cache_button.setToolTip("Clean old package cache (keeps 1 version)")
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.clean_cache_button)
        button_layout.addStretch() # Push buttons to center
        main_page_layout.addLayout(button_layout)

        # --- Log Page Layout ---
        log_page_layout = QVBoxLayout(self.log_page_widget)
        self.log_textview = QTextEdit()
        self.log_textview.setReadOnly(True)
        back_button = QPushButton("Back to Main")
        back_button.clicked.connect(self.show_main_page)
        log_page_layout.addWidget(QLabel("Update Log:"))
        log_page_layout.addWidget(self.log_textview)
        log_page_layout.addWidget(back_button)

        # --- QProcess Setup ---
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        # Extra signals for better feedback
        try:
            self.process.started.connect(self.process_started)
            self.process.errorOccurred.connect(self.handle_qprocess_error)
        except Exception:
            # Older PySide6 versions may not have these signals exposed the same way
            pass

    def process_started(self):
        # Called when a QProcess actually starts
        pname = self.current_process or "(unknown)"
        msg = f"✓ Process started: {pname}"
        self.status_label.setText(msg)
        self.update_log_content += msg + "\n"
        try:
            # show incremental feedback in the log view
            self.log_textview.insertPlainText(msg + "\n")
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass
        
        # Send notification
        if pname == "pacman_update":
            try:
                subprocess.Popen(['notify-send', 'Arch Update', 'Pacman update in progress...'])
            except:
                pass

    def handle_qprocess_error(self, error):
        error_names = {
            0: "FailedToStart",
            1: "Crashed", 
            2: "Timedout",
            3: "WriteError",
            4: "ReadError",
            5: "UnknownError"
        }
        error_name = error_names.get(error, f"Error({error})")
        msg = f"⚠ Process error: {error_name} for {self.current_process}"
        self.status_label.setText(msg)
        self.update_log_content += msg + "\n"
        try:
            self.log_textview.insertPlainText(msg + "\n")
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass
        
        # Re-enable buttons on error
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        
        # Send error notification
        try:
            subprocess.Popen(['notify-send', '-u', 'critical', 'Arch Update Error', msg])
        except:
            pass

        self.apply_styles()
        self.restore_window_state()
        self.show()

    def restore_window_state(self):
        """Restore window size and position from settings"""
        geometry = self.settings.value("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # Default size if no saved state
            self.resize(800, 600)

    def closeEvent(self, event):
        """Save window state when closing"""
        self.settings.setValue("window/geometry", self.saveGeometry())
        event.accept()

    # --- Styling ---
    def apply_styles(self):
        # Basic monochrome theme using QPalette
        palette = QPalette()
        window_bg = get_color_setting(self.settings, "window_bg", "#2e2e2e")
        text_fg = get_color_setting(self.settings, "text_fg", "#e0e0e0")
        button_bg = get_color_setting(self.settings, "button_bg", "#4a4a4a")
        button_fg = get_color_setting(self.settings, "button_fg", "#e0e0e0")
        list_bg = get_color_setting(self.settings, "list_bg", "#3a3a3a")
        progress_bar_bg = get_color_setting(self.settings, "progress_bar_bg", "#4a4a4a")
        progress_bar_chunk = get_color_setting(self.settings, "progress_bar_chunk", "#6a9ed4")


        palette.setColor(QPalette.Window, QColor(window_bg))
        palette.setColor(QPalette.WindowText, QColor(text_fg))
        palette.setColor(QPalette.Base, QColor(list_bg)) # List background
        palette.setColor(QPalette.AlternateBase, QColor("#454545")) # Not directly used here
        palette.setColor(QPalette.ToolTipBase, QColor("#1e1e1e"))
        palette.setColor(QPalette.ToolTipText, QColor(text_fg))
        palette.setColor(QPalette.Text, QColor(text_fg))
        palette.setColor(QPalette.Button, QColor(button_bg))
        palette.setColor(QPalette.ButtonText, QColor(button_fg))
        palette.setColor(QPalette.BrightText, QColor("#ff0000")) # e.g., for highlighting
        palette.setColor(QPalette.Link, QColor("#4a90d9"))
        palette.setColor(QPalette.Highlight, QColor("#4a90d9")) # Item selection
        palette.setColor(QPalette.HighlightedText, QColor("#000000"))

        # Apply palette to the application
        QApplication.setPalette(palette)
        self.setPalette(palette) # Also apply to window

        # Style progress bar specifically
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: {progress_bar_bg};
                color: {text_fg};
            }}
            QProgressBar::chunk {{
                background-color: {progress_bar_chunk};
                width: 10px; /* Adjust chunk width */
                margin: 0.5px;
            }}
        """)

        # Style TextEdit (Log view)
        self.log_textview.setStyleSheet(f"""
            QTextEdit {{
                background-color: {list_bg};
                color: {text_fg};
                border: 1px solid grey;
            }}
        """)
        # Style ListWidget (Pending List)
        self.list_widget_pending.setStyleSheet(f"""
            QListWidget {{
                background-color: {list_bg};
                color: {text_fg};
                border: 1px solid grey;
            }}
        """)

    # --- Page Navigation ---
    def show_main_page(self):
        self.stacked_widget.setCurrentWidget(self.main_page_widget)

    def show_log_page(self):
        self.log_textview.setPlainText(self.update_log_content if self.update_log_content else "No log yet.")
        self.stacked_widget.setCurrentWidget(self.log_page_widget)

    # --- Settings ---
    def open_settings(self):
        dialog = SettingsDialog(self.settings, self)
        dialog.exec()

    def clean_cache(self):
        """Clean package cache using paccache"""
        reply = subprocess.run(['which', 'paccache'], capture_output=True)
        if reply.returncode != 0:
            self.status_label.setText("paccache not found. Install pacman-contrib.")
            try:
                subprocess.Popen(['notify-send', 'Arch Update', 'paccache not found!'])
            except:
                pass
            return
        
        self.status_label.setText("Cleaning package cache...")
        try:
            # Run paccache with pkexec to clean cache (keep 1 old version)
            result = subprocess.run([PKEXEC_CMD, 'paccache', '-rk1'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.status_label.setText("Cache cleaned successfully! ✅")
                self.update_log_content += f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Cache cleaned\n"
                self.update_log_content += result.stdout
                try:
                    subprocess.Popen(['notify-send', 'Arch Update', 'Package cache cleaned!'])
                except:
                    pass
            else:
                self.status_label.setText("Failed to clean cache.")
                self.update_log_content += f"Cache clean failed: {result.stderr}\n"
        except subprocess.TimeoutExpired:
            self.status_label.setText("Cache cleaning timed out")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    # --- Update Logic ---
    def clear_package_progress(self):
        """Clear all package progress widgets"""
        for widget_dict in self.package_widgets.values():
            widget_dict['container'].setParent(None)
            widget_dict['container'].deleteLater()
        self.package_widgets.clear()
        self.current_package = None

    def add_package_progress(self, package_name):
        """Add a new package with progress bar to the UI"""
        if package_name in self.package_widgets:
            return  # Already exists
        
        # Create container widget
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Package label
        label = QLabel(package_name)
        label.setMinimumWidth(200)
        layout.addWidget(label, stretch=1)
        
        # Progress bar
        progress = QProgressBar()
        progress.setRange(0, 0)  # Indeterminate by default
        progress.setTextVisible(True)
        progress.setMaximumHeight(20)
        layout.addWidget(progress, stretch=2)
        
        # Status label
        status_label = QLabel("Waiting...")
        status_label.setMinimumWidth(100)
        layout.addWidget(status_label)
        
        # Insert before the stretch at the end
        insert_pos = self.package_progress_layout.count() - 1
        self.package_progress_layout.insertWidget(insert_pos, container)
        
        # Store references
        self.package_widgets[package_name] = {
            'container': container,
            'label': label,
            'progress': progress,
            'status': status_label
        }
        
        return self.package_widgets[package_name]

    def update_package_progress(self, package_name, progress_value=None, status_text=None):
        """Update progress for a specific package"""
        if package_name not in self.package_widgets:
            self.add_package_progress(package_name)
        
        widget_dict = self.package_widgets[package_name]
        
        if progress_value is not None:
            if progress_value < 0:
                widget_dict['progress'].setRange(0, 0)  # Indeterminate
            else:
                widget_dict['progress'].setRange(0, 100)
                widget_dict['progress'].setValue(progress_value)
        
        if status_text is not None:
            widget_dict['status'].setText(status_text)

    # --- Corrected Function ---
    def set_buttons_enabled(self, enabled):
        self.check_button.setEnabled(enabled)
        # Convert the check for non-empty lists to a boolean
        has_pending_updates = bool(self.pending_pacman or self.pending_aur)
        self.update_button.setEnabled(enabled and has_pending_updates and self.authenticated)
    def check_for_updates(self):
        self.set_buttons_enabled(False)
        self.authenticated = False
        
        self.status_label.setText("Authentication required...")
        auth_msg = f"Update check started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        auth_msg += "Requesting authentication...\n"
        self.update_log_content = auth_msg
        
        try:
            subprocess.Popen(['notify-send', 'Arch Update', 'Authentication required for update check...'])
        except:
            pass
        
        # Check if zenity is available
        zenity_available = os.path.exists(ZENITY_CMD)
        
        if zenity_available:
            self.status_label.setText("Enter password in dialog...")
            self.update_log_content += "Opening password dialog...\n"
            
            # Use threaded authentication to prevent GUI freeze
            self.auth_worker = AuthWorker(use_zenity=True)
            self.auth_thread = Thread(target=self.auth_worker.run)
            self.auth_worker.finished.connect(self.on_auth_finished)
            self.auth_worker.error.connect(self.on_auth_error)
            self.auth_thread.start()
        else:
            # Fallback: show error and suggest installing zenity
            self.status_label.setText("Zenity not found!")
            self.update_log_content += "ERROR: Zenity not found\n"
            self.update_log_content += "Install with: sudo pacman -S zenity\n"
            self.set_buttons_enabled(True)
            try:
                subprocess.Popen(['notify-send', '-u', 'critical', 'Arch Update', 
                                'Zenity required! Install: sudo pacman -S zenity'])
            except:
                pass

    def on_auth_finished(self, success):
        """Called when authentication completes"""
        if success:
            self.authenticated = True
            self.status_label.setText("Authenticated. Checking official packages...")
            self.update_log_content += "Authentication successful.\n"
            
            # Proceed with update check
            self.list_widget_pending.clear()
            self.list_widget_pending.setVisible(True)
            self.scroll_area.setVisible(False)
            self.clear_package_progress()
            self.pending_pacman = []
            self.pending_aur = []
            
            try:
                subprocess.Popen(['notify-send', 'Arch Update', 'Checking for updates...'])
            except:
                pass
            
            self.current_process = "checkupdates"
            self.process.start(CHECKUPDATES_CMD, [])
        else:
            self.set_buttons_enabled(True)

    def on_auth_error(self, error_msg):
        """Called when authentication has an error"""
        self.status_label.setText(f"Authentication failed: {error_msg}")
        self.update_log_content += f"Authentication failed: {error_msg}\n"
        try:
            subprocess.Popen(['notify-send', '-u', 'critical', 'Arch Update', 
                            f'Authentication failed: {error_msg}'])
        except:
            pass

    def run_updates(self):
        if not self.authenticated:
            self.status_label.setText("Please check for updates first to authenticate.")
            try:
                subprocess.Popen(['notify-send', '-u', 'critical', 'Arch Update', 
                                'Authentication required! Click "Check for Updates" first.'])
            except:
                pass
            return
        
        self.set_buttons_enabled(False)
        
        # Switch to package progress view
        self.list_widget_pending.setVisible(False)
        self.scroll_area.setVisible(True)
        self.clear_package_progress()
        
        # Pre-populate with pending packages
        for pkg_line in self.pending_pacman:
            pkg_name = pkg_line.split()[0] if pkg_line else "unknown"
            self.add_package_progress(pkg_name)
        
        self.status_label.setText("Preparing update...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setValue(0)
        start_msg = f"\nUpdate run started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        self.update_log_content += start_msg
        try:
            self.log_textview.insertPlainText(start_msg)
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass
        self.start_timestamp = time.time()

        try:
            subprocess.Popen(['notify-send', 'Arch Update', 'Starting system update...'])
        except:
            pass

        if self.process.state() != QProcess.NotRunning:
            self.status_label.setText("Error: A process is already running!")
            self.update_log_content += "ERROR: Process already running\n"
            self.set_buttons_enabled(True)
            return

        # Check for and remove stale database lock if no pacman is running
        lock_file = "/var/lib/pacman/db.lck"
        if os.path.exists(lock_file):
            try:
                # Check if pacman/checkupdates is actually running
                result = subprocess.run(['pgrep', '-x', 'pacman|checkupdates'], 
                                      capture_output=True, shell=True)
                if result.returncode != 0:  # No pacman/checkupdates running
                    # Try to remove stale lock with sudo
                    remove_result = subprocess.run([SUDO_CMD, 'rm', '-f', lock_file],
                                                  capture_output=True, timeout=5)
                    if remove_result.returncode == 0:
                        self.update_log_content += "Removed stale database lock\n"
                        self.status_label.setText("Removed stale lock, preparing update...")
            except Exception as e:
                self.update_log_content += f"Could not check/remove lock: {str(e)}\n"

        # Give database extra time to unlock
        from PySide6.QtCore import QTimer
        self.status_label.setText("Waiting for database lock to clear...")
        self.update_log_content += "Waiting for database lock to clear...\n"
        QTimer.singleShot(3000, self.start_pacman_update)  # Increased to 3 seconds

    def start_pacman_update(self):
        """Start the actual pacman update after ensuring database is unlocked"""
        self.status_label.setText("Starting Pacman update...")
        auth_msg = "Running update with cached authentication...\n"
        self.update_log_content += auth_msg
        try:
            self.log_textview.insertPlainText(auth_msg)
            self.log_textview.ensureCursorVisible()
        except:
            pass
        
        # Start pacman update with QProcess (non-blocking)
        self.current_process = "pacman_update"
        self.process.start(SUDO_CMD, [PACMAN_CMD, '-Syu', '--noconfirm'])

    def run_yay_update(self):
        self.status_label.setText("Starting AUR update in terminal...")
        self.update_log_content += "\nStarting AUR update (in external terminal)...\n"
        
        for pkg_line in self.pending_aur:
            pkg_name = pkg_line.split()[0] if pkg_line else "unknown"
            self.add_package_progress(pkg_name)
        
        # Run yay in a thread to prevent freezing
        def run_yay():
            try:
                if TERMINAL_EXEC_FLAG:
                    terminal_cmd = [TERMINAL_CMD, TERMINAL_EXEC_FLAG, YAY_CMD, "-Sua"]
                else:
                    terminal_cmd = [TERMINAL_CMD, YAY_CMD, "-Sua"]
                
                result = subprocess.run(terminal_cmd, timeout=600)
                
                # Update UI from main thread
                QApplication.instance().postEvent(self, YayFinishedEvent(result.returncode))
                
            except Exception as e:
                QApplication.instance().postEvent(self, YayFinishedEvent(-1, str(e)))
        
        yay_thread = Thread(target=run_yay)
        yay_thread.daemon = True
        yay_thread.start()

    def event(self, e):
        """Override event handler to catch custom events"""
        if isinstance(e, YayFinishedEvent):
            self.handle_yay_finished(e.returncode, e.error)
            return True
        return super().event(e)

    def handle_yay_finished(self, returncode, error=None):
        """Handle yay completion"""
        if returncode == 0:
            self.update_log_content += "AUR update process finished.\n"
            
            for pkg_line in self.pending_aur:
                pkg_name = pkg_line.split()[0] if pkg_line else "unknown"
                if pkg_name in self.package_widgets:
                    self.update_package_progress(pkg_name, 100, "✓ Complete")
            
            self.finalize_update()
        else:
            if error:
                self.status_label.setText(f"AUR Update error: {error}")
                self.update_log_content += f"AUR update error: {error}\n"
            else:
                self.status_label.setText(f"AUR Update failed (Code: {returncode}).")
                self.update_log_content += f"AUR update failed (Code: {returncode}).\n"
            self.set_buttons_enabled(True)

    def finalize_update(self):
        self.status_label.setText("Parsing update log...")
        self.update_log_content += self.parse_pacman_log(self.start_timestamp)
        self.update_log_content += f"\nUpdate run finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        self.status_label.setText("Updates complete! ✅")
        self.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        self.update_button.setEnabled(False)
        self.authenticated = False  # Reset authentication after update
        
        try:
            subprocess.Popen(['notify-send', 'Arch Update', 'System update completed successfully!'])
        except:
            pass

    def set_buttons_enabled(self, enabled):
        self.check_button.setEnabled(enabled)
        # Only enable update button if authenticated AND has pending updates
        has_pending_updates = bool(self.pending_pacman or self.pending_aur)
        self.update_button.setEnabled(enabled and has_pending_updates and self.authenticated)

    # --- Process Handling ---
    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.update_log_content += data
        try:
            self.log_textview.insertPlainText(data)
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass

        if self.current_process == "checkupdates":
            lines = data.strip().split('\n')
            for line in lines:
                if line:
                    self.pending_pacman.append(line.strip())
        elif self.current_process == "yay_check":
             lines = data.strip().split('\n')
             for line in lines:
                 if line:
                     self.pending_aur.append(line.strip())
        elif self.current_process == "pacman_update":
            # Parse pacman output for package operations
            lines = data.split('\n')
            for line in lines:
                # Look for package installation/upgrade patterns
                # Format: "upgrading package-name (old-ver -> new-ver)"
                # Format: "installing package-name (version)"
                upgrade_match = re.search(r'upgrading\s+([^\s]+)', line, re.IGNORECASE)
                install_match = re.search(r'installing\s+([^\s]+)', line, re.IGNORECASE)
                
                if upgrade_match:
                    pkg_name = upgrade_match.group(1)
                    if self.current_package != pkg_name:
                        # Mark previous package as complete
                        if self.current_package:
                            self.update_package_progress(self.current_package, 100, "✓ Complete")
                        self.current_package = pkg_name
                        self.update_package_progress(pkg_name, -1, "Upgrading...")
                    self.status_label.setText(f"Upgrading {pkg_name}...")
                
                elif install_match:
                    pkg_name = install_match.group(1)
                    if self.current_package != pkg_name:
                        if self.current_package:
                            self.update_package_progress(self.current_package, 100, "✓ Complete")
                        self.current_package = pkg_name
                        self.update_package_progress(pkg_name, -1, "Installing...")
                    self.status_label.setText(f"Installing {pkg_name}...")
                
                # Look for download progress
                download_match = re.search(r'downloading\s+([^\s]+)', line, re.IGNORECASE)
                if download_match and self.current_package:
                    self.update_package_progress(self.current_package, -1, "Downloading...")
                
                # Look for percentage in output
                percent_match = re.search(r'(\d+)%', line)
                if percent_match and self.current_package:
                    percent = int(percent_match.group(1))
                    self.update_package_progress(self.current_package, percent, f"{percent}%")
            
            # Update status messages for general operations
            if "downloading" in data.lower():
                self.status_label.setText("Downloading packages...")
            elif "checking" in data.lower():
                self.status_label.setText("Checking packages...")
            elif "resolving" in data.lower():
                self.status_label.setText("Resolving dependencies...")
            elif "loading" in data.lower():
                self.status_label.setText("Loading package files...")

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        timestamp = datetime.now().strftime('%H:%M:%S')
        # Add errors to log with timestamp
        error_msg = f"[{timestamp}] ERROR: {data}"
        self.update_log_content += error_msg
        try:
            self.log_textview.insertPlainText(error_msg)
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass
        if self.current_process == "pacman_update":
             # Handle password prompt cancellation or other pkexec errors
             if "authentication failed" in data.lower() or "not authorized" in data.lower():
                  self.status_label.setText("Authentication failed. Update cancelled.")
                  self.progress_bar.setVisible(False)
                  self.set_buttons_enabled(True)
                  self.current_process = None
             # Handle other potential errors during pacman execution
             elif self.process.exitStatus() == QProcess.NormalExit and self.process.exitCode() != 0:
                  self.status_label.setText("Pacman update failed. Check log.")
                  self.progress_bar.setVisible(False)
                  self.set_buttons_enabled(True)


    def process_finished(self, exitCode, exitStatus):
        process_name = self.current_process
        self.current_process = None

        if process_name == "pacman_update" and self.current_package:
            self.update_package_progress(self.current_package, 100, "✓ Complete")
            self.current_package = None

        finish_msg = f"Process finished: {process_name} (code={exitCode}, status={exitStatus})\n"
        self.update_log_content += finish_msg
        try:
            self.log_textview.insertPlainText(finish_msg)
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass

        if exitStatus == QProcess.CrashExit:
             self.status_label.setText(f"Process crashed: {process_name}")
             self.update_log_content += f"Process crashed: {process_name}\n"
             self.set_buttons_enabled(True)
             return

        if process_name == "checkupdates":
            if exitCode == 0:
                self.status_label.setText("Checking AUR packages...")
                self.current_process = "yay_check"
                self.process.start(YAY_CMD, ["-Qua"])
            else:
                self.status_label.setText("Failed to check official updates.")
                self.update_log_content += "Failed to check official updates.\n"
                self.set_buttons_enabled(True)
                self.authenticated = False  # Reset on failure

        elif process_name == "yay_check":
             if exitCode == 0:
                self.list_widget_pending.clear()
                if self.pending_pacman:
                    self.list_widget_pending.addItem("━━━ Official Packages ━━━")
                    self.list_widget_pending.addItems(self.pending_pacman)
                if self.pending_aur:
                    self.list_widget_pending.addItem("")
                    self.list_widget_pending.addItem("━━━ AUR Packages ━━━")
                    self.list_widget_pending.addItems(self.pending_aur)

                if not self.pending_pacman and not self.pending_aur:
                    self.status_label.setText("System is up to date. ✅")
                    self.update_log_content += "\nSystem is up to date.\n"
                    self.authenticated = False  # Reset - no updates to run
                    try:
                        subprocess.Popen(['notify-send', 'Arch Update', 'System is up to date!'])
                    except:
                        pass
                else:
                    count = len(self.pending_pacman) + len(self.pending_aur)
                    self.status_label.setText(f"{count} update(s) pending. Ready to update!")
                    self.update_log_content += f"\nFound {len(self.pending_pacman)} official and {len(self.pending_aur)} AUR updates.\n"
                    try:
                        subprocess.Popen(['notify-send', 'Arch Update', f'{count} updates available!'])
                    except:
                        pass
             else:
                  self.status_label.setText("Failed to check AUR updates.")
                  self.update_log_content += "Failed to check AUR updates.\n"

             self.set_buttons_enabled(True)

        elif process_name == "pacman_update":
            if exitCode == 0:
                self.status_label.setText("Pacman update successful. Proceeding to AUR...")
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(100)
                self.update_log_content += "Pacman update successful.\n"
                if self.pending_aur:
                    self.run_yay_update()
                else:
                    self.finalize_update()
            else:
                 if exitStatus != QProcess.CrashExit:
                    self.status_label.setText("Pacman update failed. Check log.")
                 self.update_log_content += f"Pacman update failed (Code: {exitCode}).\n"
                 self.progress_bar.setVisible(False)
                 self.set_buttons_enabled(True)
                 self.authenticated = False

    def parse_pacman_log(self, start_epoch):
        updated_lines = []
        try:
            with open(PACMAN_LOG, 'r') as f:
                for line in f:
                    # Basic check for timestamp and relevant action
                    if "[ALPM]" in line and ("upgraded" in line or "installed" in line):
                        match = re.match(r'\[(.*?)\]', line) # Extract timestamp string
                        if match:
                            log_time_str = match.group(1)
                            # Convert log timestamp format to struct_time, then epoch
                            try:
                                # Example format: 2025-10-22T21:30:00+0100
                                # Need to handle timezone if present, mktime uses local
                                # Simplification: Assume log uses parseable format for strptime
                                log_dt_naive = datetime.strptime(log_time_str.split('+')[0], '%Y-%m-%dT%H:%M:%S')
                                log_epoch = time.mktime(log_dt_naive.timetuple())

                                if log_epoch >= start_epoch:
                                    # Extract relevant part of the log message
                                    action_part = line.split("] [ALPM] ")[1].strip()
                                    updated_lines.append(f" - {action_part}")
                            except ValueError:
                                # Handle cases where timestamp parsing fails
                                if time.time() > start_epoch: # Fallback: include if line occurred recently
                                      action_part = line.split("] [ALPM] ")[1].strip()
                                      updated_lines.append(f" - {action_part} (time parse failed)")
                                continue # Skip lines we can't parse timestamp for
        except FileNotFoundError:
            return "Error: Could not open pacman log file.\n"
        except Exception as e:
            return f"Error parsing pacman log: {e}\n"

        if updated_lines:
            return "Packages updated/installed in this session:\n" + "\n".join(updated_lines) + "\n"
        else:
            return "No package changes recorded in pacman log for this session.\n"


# --- Run Application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings = QSettings("MyOrg", "ArchUpdateGUI")
    
    window = UpdateAppWindow()
    sys.exit(app.exec())
