#!/usr/bin/env python

import sys
import subprocess
import os
import re
import time
import json
from datetime import datetime
from threading import Thread

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QProgressBar, QLabel, QListWidget,
    QStackedWidget, QDialog, QColorDialog, QFormLayout, QScrollArea,
    QSystemTrayIcon, QMenu, QCheckBox, QSpinBox, QLineEdit, QTreeWidget,
    QTreeWidgetItem, QGroupBox, QMessageBox, QTabWidget, QListWidgetItem,
    QFrame, QComboBox, QSlider, QFontComboBox, QSplitter, QStatusBar
)
from PySide6.QtCore import QProcess, Qt, QSettings, Signal, QObject, QTimer, QEvent, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPalette, QColor, QIcon, QAction, QFont, QPixmap, QPainter, QBrush, QLinearGradient

# --- Configuration ---
PACMAN_LOG = "/var/log/pacman.log"
CHECKUPDATES_CMD = "/usr/bin/checkupdates"
YAY_CMD = "/usr/bin/yay"
PACMAN_CMD = "/usr/bin/pacman"
PKEXEC_CMD = "/usr/bin/pkexec"
SUDO_CMD = "/usr/bin/sudo"
ZENITY_CMD = "/usr/bin/zenity"
TERMINAL_CMD = "foot"
TERMINAL_EXEC_FLAG = "-e"

# Add new configuration
UPDATE_HISTORY_FILE = os.path.expanduser("~/.config/MyOrg/update_history.json")
IGNORED_PACKAGES_FILE = os.path.expanduser("~/.config/MyOrg/ignored_packages.json")

# Ensure config directory exists
os.makedirs(os.path.dirname(UPDATE_HISTORY_FILE), exist_ok=True)

# --- Enhanced Theme Presets ---
THEME_PRESETS = {
    "Dark Professional": {
        "window_bg": "#1e1e2e",
        "text_fg": "#cdd6f4",
        "button_bg": "#313244",
        "button_fg": "#cdd6f4",
        "list_bg": "#313244",
        "progress_bar_bg": "#45475a",
        "progress_bar_chunk": "#89b4fa",
        "accent": "#89b4fa",
        "secondary_bg": "#11111b",
        "border": "#45475a",
        "success": "#a6e3a1",
        "warning": "#f9e2af",
        "error": "#f38ba8"
    },
    "Nord Aurora": {
        "window_bg": "#2e3440",
        "text_fg": "#eceff4",
        "button_bg": "#3b4252",
        "button_fg": "#eceff4",
        "list_bg": "#3b4252",
        "progress_bar_bg": "#4c566a",
        "progress_bar_chunk": "#88c0d0",
        "accent": "#88c0d0",
        "secondary_bg": "#2e3440",
        "border": "#4c566a",
        "success": "#a3be8c",
        "warning": "#ebcb8b",
        "error": "#bf616a"
    },
    "Dracula": {
        "window_bg": "#282a36",
        "text_fg": "#f8f8f2",
        "button_bg": "#44475a",
        "button_fg": "#f8f8f2",
        "list_bg": "#44475a",
        "progress_bar_bg": "#6272a4",
        "progress_bar_chunk": "#bd93f9",
        "accent": "#bd93f9",
        "secondary_bg": "#282a36",
        "border": "#6272a4",
        "success": "#50fa7b",
        "warning": "#f1fa8c",
        "error": "#ff5555"
    },
    "Monokai": {
        "window_bg": "#272822",
        "text_fg": "#f8f8f2",
        "button_bg": "#3e3d32",
        "button_fg": "#f8f8f2",
        "list_bg": "#3e3d32",
        "progress_bar_bg": "#49483e",
        "progress_bar_chunk": "#66d9ef",
        "accent": "#66d9ef",
        "secondary_bg": "#272822",
        "border": "#49483e",
        "success": "#a6e22e",
        "warning": "#fd971f",
        "error": "#f92672"
    },
    "Gruvbox": {
        "window_bg": "#282828",
        "text_fg": "#ebdbb2",
        "button_bg": "#3c3836",
        "button_fg": "#ebdbb2",
        "list_bg": "#3c3836",
        "progress_bar_bg": "#504945",
        "progress_bar_chunk": "#83a598",
        "accent": "#83a598",
        "secondary_bg": "#282828",
        "border": "#504945",
        "success": "#b8bb26",
        "warning": "#fabd2f",
        "error": "#fb4934"
    },
    "Tokyo Night": {
        "window_bg": "#1a1b26",
        "text_fg": "#c0caf5",
        "button_bg": "#24283b",
        "button_fg": "#c0caf5",
        "list_bg": "#24283b",
        "progress_bar_bg": "#414868",
        "progress_bar_chunk": "#7dcfff",
        "accent": "#7dcfff",
        "secondary_bg": "#1a1b26",
        "border": "#414868",
        "success": "#9ece6a",
        "warning": "#e0af68",
        "error": "#f7768e"
    },
    "One Dark": {
        "window_bg": "#282c34",
        "text_fg": "#abb2bf",
        "button_bg": "#3e4451",
        "button_fg": "#abb2bf",
        "list_bg": "#3e4451",
        "progress_bar_bg": "#5c6370",
        "progress_bar_chunk": "#61afef",
        "accent": "#61afef",
        "secondary_bg": "#282c34",
        "border": "#5c6370",
        "success": "#98c379",
        "warning": "#e5c07b",
        "error": "#e06c75"
    },
    "Solarized Dark": {
        "window_bg": "#002b36",
        "text_fg": "#93a1a1",
        "button_bg": "#073642",
        "button_fg": "#93a1a1",
        "list_bg": "#073642",
        "progress_bar_bg": "#586e75",
        "progress_bar_chunk": "#2aa198",
        "accent": "#2aa198",
        "secondary_bg": "#002b36",
        "border": "#586e75",
        "success": "#859900",
        "warning": "#b58900",
        "error": "#dc322f"
    },
    "Material Dark": {
        "window_bg": "#121212",
        "text_fg": "#ffffff",
        "button_bg": "#1e1e1e",
        "button_fg": "#ffffff",
        "list_bg": "#1e1e1e",
        "progress_bar_bg": "#333333",
        "progress_bar_chunk": "#6200ea",
        "accent": "#6200ea",
        "secondary_bg": "#121212",
        "border": "#333333",
        "success": "#00c853",
        "warning": "#ff9800",
        "error": "#f44336"
    },
    "Cyberpunk": {
        "window_bg": "#0d0d0d",
        "text_fg": "#00ff9f",
        "button_bg": "#1a1a1a",
        "button_fg": "#00ff9f",
        "list_bg": "#1a1a1a",
        "progress_bar_bg": "#333333",
        "progress_bar_chunk": "#ff073a",
        "accent": "#ff073a",
        "secondary_bg": "#0d0d0d",
        "border": "#333333",
        "success": "#39ff14",
        "warning": "#ffff00",
        "error": "#ff073a"
    }
}

# --- Helper Functions ---
def get_color_setting(settings, key, default_color):
    color_str = settings.value(key, default_color)
    return QColor(color_str)

def check_polkit_agent():
    """Check if a polkit agent is running"""
    try:
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
        
        if not os.environ.get('DISPLAY'):
            return False
            
        return False
    except:
        return False

def load_update_history():
    """Load update history from JSON file"""
    try:
        if os.path.exists(UPDATE_HISTORY_FILE):
            with open(UPDATE_HISTORY_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_update_history(history):
    """Save update history to JSON file"""
    try:
        with open(UPDATE_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Failed to save history: {e}")

def load_ignored_packages():
    """Load ignored packages list"""
    try:
        if os.path.exists(IGNORED_PACKAGES_FILE):
            with open(IGNORED_PACKAGES_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_ignored_packages(packages):
    """Save ignored packages list"""
    try:
        with open(IGNORED_PACKAGES_FILE, 'w') as f:
            json.dump(packages, f, indent=2)
    except Exception as e:
        print(f"Failed to save ignored packages: {e}")

# --- Auth Worker ---
class AuthWorker(QObject):
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self, use_zenity=True):
        super().__init__()
        self.use_zenity = use_zenity
    
    def run(self):
        try:
            if self.use_zenity and os.path.exists(ZENITY_CMD):
                result = subprocess.run(
                    [ZENITY_CMD, '--password', '--title=Arch Update GUI Authentication'],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    password = result.stdout.strip()
                    
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
                self.error.emit("Zenity not available")
                self.finished.emit(False)
                
        except subprocess.TimeoutExpired:
            self.error.emit("Authentication timed out")
            self.finished.emit(False)
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(False)

# --- Custom Events ---
class YayFinishedEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, returncode, error=None):
        super().__init__(self.EVENT_TYPE)
        self.returncode = returncode
        self.error = error

class SearchCompleteEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    
    def __init__(self, packages):
        super().__init__(self.EVENT_TYPE)
        self.packages = packages

# --- Beautiful Card Widget ---
class CardWidget(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
            layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)

# --- Beautiful Status Card ---
class StatusCard(CardWidget):
    def __init__(self, parent=None):
        super().__init__("System Status", parent)
        
        self.status_icon = QLabel("◉")
        self.status_icon.setStyleSheet("font-size: 28px; color: #89b4fa;")
        self.status_label = QLabel("Ready to check for updates")
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 13px;")
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_icon)
        status_layout.addWidget(self.status_label, 1)
        status_layout.addStretch()
        
        self.content_layout.addLayout(status_layout)
        
        # Progress section with beautiful styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.08);
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #56b06c, stop:1 #4a9d60);
                border-radius: 5px;
            }
        """)
        self.content_layout.addWidget(self.progress_bar)

# --- Beautiful Package Card ---
class PackageCard(CardWidget):
    def __init__(self, parent=None):
        super().__init__("Available Updates", parent)
        
        self.package_list = QListWidget()
        self.package_list.setStyleSheet("""
            QListWidget {
                border: none;
                background: transparent;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 6px;
                margin-bottom: 2px;
            }
            QListWidget::item:selected {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        self.content_layout.addWidget(self.package_list)
        
        # Stats
        self.stats_label = QLabel("0 updates available")
        self.stats_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); font-size: 12px;")
        self.content_layout.addWidget(self.stats_label)

# --- Beautiful Action Buttons ---
class ActionButton(QPushButton):
    def __init__(self, text, icon_text="", primary=False, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(45)
        self.setMinimumWidth(120)
        self.setCursor(Qt.PointingHandCursor)
        
        if primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #56b06c, stop:1 #4a9d60);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #66c07c, stop:1 #5aad70);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4a9d60, stop:1 #3e8d54);
                }
                QPushButton:disabled {
                    background: #555555;
                    color: #888888;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 255, 255, 0.08);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 8px;
                    font-size: 14px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.15);
                    border-color: rgba(255, 255, 255, 0.25);
                }
                QPushButton:pressed {
                    background: rgba(255, 255, 255, 0.2);
                }
                QPushButton:disabled {
                    background: rgba(255, 255, 255, 0.03);
                    color: #666666;
                    border-color: rgba(255, 255, 255, 0.05);
                }
            """)
        
        if icon_text:
            self.setText(f"{icon_text}  {text}")
        else:
            self.setText(text)

# --- Main Application Window ---
class UpdateAppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arch Update GUI")
        self.setGeometry(100, 100, 900, 700)
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
        
        has_polkit = check_polkit_agent()
        self.use_terminal_sudo = not has_polkit

        # Setup system tray
        self.setup_system_tray()
        
        # Setup auto-check timer
        self.auto_check_timer = QTimer(self)
        self.auto_check_timer.timeout.connect(self.auto_check_updates)
        self.setup_auto_check_timer()

        # --- Beautiful Main Layout ---
        self.setup_beautiful_ui()
        
        # --- QProcess Setup (MUST BE BEFORE add_enhanced_menus) ---
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        
        # Add menu bar with enhanced features
        self.add_enhanced_menus()
        
        self.apply_styles()
        self.restore_window_state()
        self.show()
        
        # Check on startup if enabled
        if self.settings.value("auto_check_startup", False, type=bool):
            QTimer.singleShot(2000, self.check_for_updates)
    
    def setup_beautiful_ui(self):
        """Setup the beautiful, modern UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- Top Header ---
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Arch Update Manager")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin-bottom: 5px;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Top buttons
        self.view_log_button = ActionButton("View Log", "▤")  # Changed from emoji
        self.view_log_button.clicked.connect(self.show_log_page)
        header_layout.addWidget(self.view_log_button)
        
        self.settings_button = ActionButton("Settings", "⚙")  # Changed from emoji
        self.settings_button.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_button)
        
        main_layout.addLayout(header_layout)
        
        # --- Main Content Splitter ---
        splitter = QSplitter(Qt.Vertical)
        
        # Top section - Status and Packages
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(20)
        
        # Status card
        self.status_card = StatusCard()
        top_layout.addWidget(self.status_card, 1)
        
        # Package card
        self.package_card = PackageCard()
        top_layout.addWidget(self.package_card, 1)
        
        splitter.addWidget(top_widget)
        
        # Bottom section - Progress and Actions
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(15)
        
        # Progress section
        progress_card = CardWidget("Update Progress")
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.scroll_widget = QWidget()
        self.package_progress_layout = QVBoxLayout(self.scroll_widget)
        self.package_progress_layout.setContentsMargins(0, 0, 0, 0)
        self.package_progress_layout.setSpacing(8)
        self.package_progress_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_widget)
        progress_card.content_layout.addWidget(self.scroll_area)
        
        bottom_layout.addWidget(progress_card)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        self.check_button = ActionButton("Check for Updates", "⌕", primary=True)  # Changed from emoji
        self.check_button.clicked.connect(self.check_for_updates)
        actions_layout.addWidget(self.check_button)
        
        self.update_button = ActionButton("Run Updates", "▶", primary=True)  # Changed from emoji
        self.update_button.clicked.connect(self.run_updates)
        self.update_button.setEnabled(False)
        actions_layout.addWidget(self.update_button)
        
        actions_layout.addStretch()
        
        self.clean_cache_button = ActionButton("Clean Cache", "⌫")  # Changed from emoji
        self.clean_cache_button.clicked.connect(self.clean_cache)
        actions_layout.addWidget(self.clean_cache_button)
        
        bottom_layout.addLayout(actions_layout)
        
        splitter.addWidget(bottom_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 500])
        main_layout.addWidget(splitter)
        
        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: rgba(255, 255, 255, 0.05);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                padding: 5px;
            }
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # --- Log Page (Hidden by default) ---
        self.log_page_widget = QWidget()
        log_layout = QVBoxLayout(self.log_page_widget)
        
        log_header = QHBoxLayout()
        log_title = QLabel("Update Log")
        log_title.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        log_header.addWidget(log_title)
        log_header.addStretch()
        
        back_button = ActionButton("Back to Main", "←")  # Changed from emoji
        back_button.clicked.connect(self.show_main_page)
        log_header.addWidget(back_button)
        
        log_layout.addLayout(log_header)
        
        self.log_textview = QTextEdit()
        self.log_textview.setReadOnly(True)
        self.log_textview.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.3);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 10px;
                font-family: 'Monospace';
                font-size: 12px;
            }
        """)
        log_layout.addWidget(self.log_textview)
        
        # Store reference for page switching
        self.main_page_widget = central_widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.main_page_widget)
        self.stacked_widget.addWidget(self.log_page_widget)
        
        # Replace central widget
        self.setCentralWidget(self.stacked_widget)

    def setup_system_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("system-software-update"))
        
        tray_menu = QMenu()
        
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        check_action = QAction("Check for Updates", self)
        check_action.triggered.connect(self.check_for_updates)
        tray_menu.addAction(check_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def setup_auto_check_timer(self):
        self.auto_check_timer.stop()
        
        if self.settings.value("auto_check_enabled", False, type=bool):
            interval_hours = self.settings.value("auto_check_interval", 6, type=int)
            interval_ms = interval_hours * 60 * 60 * 1000
            self.auto_check_timer.start(interval_ms)
    
    def auto_check_updates(self):
        self.tray_icon.showMessage(
            "Arch Update",
            "Checking for updates...",
            QSystemTrayIcon.Information,
            2000
        )
        self.check_for_updates()
    
    def add_enhanced_menus(self):
        menubar = self.menuBar()
        tools_menu = menubar.addMenu("Tools")
        
        search_action = QAction("Search Packages", self)
        search_action.triggered.connect(self.open_package_search)
        tools_menu.addAction(search_action)
        
        ignored_action = QAction("Manage Ignored Packages", self)
        ignored_action.triggered.connect(self.open_ignored_packages)
        tools_menu.addAction(ignored_action)
        
        history_action = QAction("Update History", self)
        history_action.triggered.connect(self.open_update_history)
        tools_menu.addAction(history_action)
        
        tools_menu.addSeparator()
        
        rollback_action = QAction("Rollback Last Update", self)
        rollback_action.triggered.connect(self.rollback_update)
        tools_menu.addAction(rollback_action)
    
    def open_package_search(self):
        dialog = PackageSearchDialog(self)
        dialog.exec()
    
    def open_ignored_packages(self):
        dialog = IgnoredPackagesDialog(self)
        dialog.exec()
    
    def open_update_history(self):
        dialog = UpdateHistoryDialog(self)
        dialog.exec()
    
    def rollback_update(self):
        reply = QMessageBox.question(
            self,
            "Rollback Update",
            "This will downgrade recently updated packages.\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if TERMINAL_EXEC_FLAG:
                    cmd = [TERMINAL_CMD, TERMINAL_EXEC_FLAG, 'bash', '-c',
                           f'echo "Rolling back packages..." && '
                           f'{SUDO_CMD} pacman -U /var/cache/pacman/pkg/*.pkg.tar.* && '
                           f'echo "Rollback complete. Press Enter..." && read']
                else:
                    cmd = [TERMINAL_CMD, 'bash', '-c',
                           f'echo "Rolling back packages..." && '
                           f'{SUDO_CMD} pacman -U /var/cache/pacman/pkg/*.pkg.tar.* && '
                           f'echo "Rollback complete. Press Enter..." && read']
                
                subprocess.Popen(cmd)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Rollback failed: {str(e)}")
    
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMinimized() and self.settings.value("minimize_to_tray", True, type=bool):
                self.hide()
                event.ignore()
                return
        super().changeEvent(event)
    
    def closeEvent(self, event):
        self.settings.setValue("window/geometry", self.saveGeometry())
        
        if self.settings.value("minimize_to_tray", True, type=bool):
            event.ignore()
            self.hide()
        else:
            event.accept()
    
    def open_settings(self):
        dialog = BeautifulSettingsDialog(self.settings, self)
        dialog.exec()
    
    def record_update_history(self, update_type, package_count, status):
        history = load_update_history()
        entry = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': update_type,
            'package_count': package_count,
            'status': status
        }
        history.append(entry)
        
        if len(history) > 100:
            history = history[-100:]
        
        save_update_history(history)
    
    def filter_ignored_packages(self):
        ignored = load_ignored_packages()
        if ignored:
            self.pending_pacman = [pkg for pkg in self.pending_pacman 
                                  if not any(pkg.startswith(ign) for ign in ignored)]
            self.pending_aur = [pkg for pkg in self.pending_aur 
                               if not any(pkg.startswith(ign) for ign in ignored)]
    
    def finalize_update(self):
        self.status_card.status_icon.setText("✓")
        self.status_card.status_label.setText("Updates complete!")
        self.status_card.progress_bar.setVisible(False)
        
        self.update_log_content += self.parse_pacman_log(self.start_timestamp)
        self.update_log_content += f"\nUpdate run finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        self.set_buttons_enabled(True)
        self.update_button.setEnabled(False)
        self.authenticated = False
        
        total_packages = len(self.pending_pacman) + len(self.pending_aur)
        self.record_update_history("Full Update", total_packages, "Success")
        
        try:
            subprocess.Popen(['notify-send', 'Arch Update', 'System update completed successfully!'])
        except:
            pass
        
        self.tray_icon.showMessage(
            "Arch Update",
            f"Successfully updated {total_packages} packages!",
            QSystemTrayIcon.Information,
            5000
        )
    
    def process_started(self):
        pname = self.current_process or "(unknown)"
        msg = f"⚙ Process started: {pname}"
        self.status_card.status_icon.setText("◉")
        self.status_card.status_label.setText(msg)
        self.status_bar.showMessage(msg)
        
        self.update_log_content += msg + "\n"
        try:
            self.log_textview.insertPlainText(msg + "\n")
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass
        
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
        self.status_card.status_icon.setText("✗")
        self.status_card.status_label.setText(msg)
        self.status_bar.showMessage(msg)
        
        self.update_log_content += msg + "\n"
        try:
            self.log_textview.insertPlainText(msg + "\n")
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass
        
        self.status_card.progress_bar.setVisible(False)
        self.set_buttons_enabled(True)
        
        try:
            subprocess.Popen(['notify-send', '-u', 'critical', 'Arch Update Error', msg])
        except:
            pass

    def restore_window_state(self):
        geometry = self.settings.value("window/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(900, 700)

    def apply_styles(self):
        """Apply beautiful theme styling"""
        theme_name = self.settings.value("current_theme", "Dark Professional")
        if theme_name in THEME_PRESETS:
            theme = THEME_PRESETS[theme_name]
        else:
            theme = THEME_PRESETS["Dark Professional"]
        
        # Apply gradient background
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(theme["window_bg"]))
        gradient.setColorAt(1, QColor(theme["secondary_bg"]))
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme["window_bg"]}, stop:1 {theme["secondary_bg"]});
                color: {theme["text_fg"]};
            }}
            
            CardWidget {{
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid {theme["border"]};
                border-radius: 12px;
                color: {theme["text_fg"]};
            }}
            
            QLabel {{
                color: {theme["text_fg"]};
            }}
            
            QListWidget {{
                background: rgba(0, 0, 0, 0.2);
                color: {theme["text_fg"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                selection-background-color: {theme["accent"]};
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            
            QMenuBar {{
                background: rgba(0, 0, 0, 0.2);
                border-bottom: 1px solid {theme["border"]};
                color: {theme["text_fg"]};
            }}
            
            QMenuBar::item {{
                background: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background: {theme["accent"]};
            }}
            
            QMenu {{
                background: {theme["window_bg"]};
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                color: {theme["text_fg"]};
            }}
            
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background: {theme["accent"]};
            }}
        """)
        
        # Update status bar
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background: rgba(0, 0, 0, 0.1);
                border-top: 1px solid {theme["border"]};
                color: {theme["text_fg"]};
                padding: 5px 10px;
            }}
        """)

    def show_main_page(self):
        self.stacked_widget.setCurrentWidget(self.main_page_widget)

    def show_log_page(self):
        self.log_textview.setPlainText(self.update_log_content if self.update_log_content else "No log yet.")
        self.stacked_widget.setCurrentWidget(self.log_page_widget)

    def clean_cache(self):
        reply = subprocess.run(['which', 'paccache'], capture_output=True)
        if reply.returncode != 0:
            QMessageBox.warning(self, "Error", "paccache not found. Install pacman-contrib.")
            return
        
        self.status_card.status_icon.setText("⌫")
        self.status_card.status_label.setText("Cleaning package cache...")
        
        try:
            result = subprocess.run([PKEXEC_CMD, 'paccache', '-rk1'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                self.status_card.status_icon.setText("✓")
                self.status_card.status_label.setText("Cache cleaned successfully!")
                self.update_log_content += f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Cache cleaned\n"
                self.update_log_content += result.stdout
                try:
                    subprocess.Popen(['notify-send', 'Arch Update', 'Package cache cleaned!'])
                except:
                    pass
            else:
                self.status_card.status_icon.setText("✗")
                self.status_card.status_label.setText("Failed to clean cache.")
                self.update_log_content += f"Cache clean failed: {result.stderr}\n"
        except subprocess.TimeoutExpired:
            self.status_card.status_icon.setText("⏱")
            self.status_card.status_label.setText("Cache cleaning timed out")
        except Exception as e:
            self.status_card.status_icon.setText("✗")
            self.status_card.status_label.setText(f"Error: {str(e)}")

    def clear_package_progress(self):
        for widget_dict in self.package_widgets.values():
            widget_dict['container'].setParent(None)
            widget_dict['container'].deleteLater()
        self.package_widgets.clear()
        self.current_package = None

    def add_package_progress(self, package_name):
        if package_name in self.package_widgets:
            return
        
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 8, 10, 8)
        
        label = QLabel(package_name)
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(label, 1)
        
        progress = QProgressBar()
        progress.setRange(0, 0)
        progress.setTextVisible(True)
        progress.setFixedHeight(25)
        progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 4px;
                background: rgba(0, 0, 0, 0.2);
                text-align: center;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 3px;
            }
        """)
        layout.addWidget(progress, 2)
        
        status_label = QLabel("Waiting...")
        status_label.setStyleSheet("font-size: 12px; color: rgba(255, 255, 255, 0.8);")
        layout.addWidget(status_label)
        
        insert_pos = self.package_progress_layout.count() - 1
        self.package_progress_layout.insertWidget(insert_pos, container)
        
        self.package_widgets[package_name] = {
            'container': container,
            'label': label,
            'progress': progress,
            'status': status_label
        }
        
        return self.package_widgets[package_name]

    def update_package_progress(self, package_name, progress_value=None, status_text=None):
        if package_name not in self.package_widgets:
            self.add_package_progress(package_name)
        
        widget_dict = self.package_widgets[package_name]
        
        if progress_value is not None:
            if progress_value < 0:
                widget_dict['progress'].setRange(0, 0)
            else:
                widget_dict['progress'].setRange(0, 100)
                widget_dict['progress'].setValue(progress_value)
        
        if status_text is not None:
            widget_dict['status'].setText(status_text)

    def set_buttons_enabled(self, enabled):
        self.check_button.setEnabled(enabled)
        has_pending_updates = bool(self.pending_pacman or self.pending_aur)
        self.update_button.setEnabled(enabled and has_pending_updates and self.authenticated)
    
    def check_for_updates(self):
        self.set_buttons_enabled(False)
        self.authenticated = False
        
        self.status_card.status_icon.setText("⌕")
        self.status_card.status_label.setText("Authentication required...")
        self.status_bar.showMessage("Authentication required...")
        
        auth_msg = f"Update check started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        auth_msg += "Requesting authentication...\n"
        self.update_log_content = auth_msg
        
        try:
            subprocess.Popen(['notify-send', 'Arch Update', 'Authentication required for update check...'])
        except:
            pass
        
        zenity_available = os.path.exists(ZENITY_CMD)
        
        if zenity_available:
            self.status_card.status_label.setText("Enter password in dialog...")
            self.update_log_content += "Opening password dialog...\n"
            
            self.auth_worker = AuthWorker(use_zenity=True)
            self.auth_thread = Thread(target=self.auth_worker.run)
            self.auth_worker.finished.connect(self.on_auth_finished)
            self.auth_worker.error.connect(self.on_auth_error)
            self.auth_thread.start()
        else:
            self.status_card.status_icon.setText("✗")
            self.status_card.status_label.setText("Zenity not found!")
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
            self.status_card.status_icon.setText("◉")
            self.status_card.status_label.setText("Authenticated. Checking official packages...")
            self.status_bar.showMessage("Authenticated. Checking for updates...")
            self.update_log_content += "Authentication successful.\n"
            
            self.package_card.package_list.clear()
            self.package_card.stats_label.setText("Checking for updates...")
            
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
        self.status_card.status_icon.setText("✗")
        self.status_card.status_label.setText(f"Authentication failed: {error_msg}")
        self.status_bar.showMessage(f"Authentication failed: {error_msg}")
        self.update_log_content += f"Authentication failed: {error_msg}\n"
        try:
            subprocess.Popen(['notify-send', '-u', 'critical', 'Arch Update', 
                            f'Authentication failed: {error_msg}'])
        except:
            pass

    def run_updates(self):
        if not self.authenticated:
            QMessageBox.warning(self, "Authentication Required", 
                              "Please check for updates first to authenticate.")
            return
        
        self.set_buttons_enabled(False)
        
        self.status_card.status_icon.setText("▶")
        self.status_card.status_label.setText("Preparing update...")
        self.status_card.progress_bar.setVisible(True)
        self.status_card.progress_bar.setRange(0, 0)
        
        self.clear_package_progress()
        
        for pkg_line in self.pending_pacman:
            pkg_name = pkg_line.split()[0] if pkg_line else "unknown"
            self.add_package_progress(pkg_name)
        
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
            QMessageBox.warning(self, "Process Running", "A process is already running!")
            return

        lock_file = "/var/lib/pacman/db.lck"
        if os.path.exists(lock_file):
            try:
                result = subprocess.run(['pgrep', '-x', 'pacman|checkupdates'], 
                                      capture_output=True, shell=True)
                if result.returncode != 0:
                    remove_result = subprocess.run([SUDO_CMD, 'rm', '-f', lock_file],
                                                  capture_output=True, timeout=5)
                    if remove_result.returncode == 0:
                        self.update_log_content += "Removed stale database lock\n"
                        self.status_card.status_label.setText("Removed stale lock, preparing update...")
            except Exception as e:
                self.update_log_content += f"Could not check/remove lock: {str(e)}\n"

        self.status_card.status_label.setText("Waiting for database lock to clear...")
        self.update_log_content += "Waiting for database lock to clear...\n"
        QTimer.singleShot(3000, self.start_pacman_update)

    def start_pacman_update(self):
        """Start the actual pacman update after ensuring database is unlocked"""
        self.status_card.status_label.setText("Starting Pacman update...")
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
        self.status_card.status_label.setText("Starting AUR update in terminal...")
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
        if isinstance(e, YayFinishedEvent):
            self.handle_yay_finished(e.returncode, e.error)
            return True
        elif isinstance(e, SearchCompleteEvent):
            self.handle_search_complete(e.packages)
            return True
        return super().event(e)

    def handle_yay_finished(self, returncode, error=None):
        if returncode == 0:
            self.update_log_content += "AUR update process finished.\n"
            
            for pkg_line in self.pending_aur:
                pkg_name = pkg_line.split()[0] if pkg_line else "unknown"
                if pkg_name in self.package_widgets:
                    self.update_package_progress(pkg_name, 100, "✓ Complete")
            
            self.finalize_update()
        else:
            if error:
                self.status_card.status_icon.setText("✗")
                self.status_card.status_label.setText(f"AUR Update error: {error}")
                self.update_log_content += f"AUR update error: {error}\n"
            else:
                self.status_card.status_icon.setText("✗")
                self.status_card.status_label.setText(f"AUR Update failed (Code: {returncode}).")
                self.update_log_content += f"AUR update failed (Code: {returncode}).\n"
            self.set_buttons_enabled(True)

    def handle_search_complete(self, packages):
        self.search_results_list.clear()
        for name, version, repo, desc in packages:
            item = QTreeWidgetItem([name, version, repo, desc])
            self.search_results_list.addTopLevelItem(item)

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
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
            lines = data.split('\n')
            for line in lines:
                upgrade_match = re.search(r'upgrading\s+([^\s]+)', line, re.IGNORECASE)
                install_match = re.search(r'installing\s+([^\s]+)', line, re.IGNORECASE)
                
                if upgrade_match:
                    pkg_name = upgrade_match.group(1)
                    if self.current_package != pkg_name:
                        if self.current_package:
                            self.update_package_progress(self.current_package, 100, "✓ Complete")
                        self.current_package = pkg_name
                        self.update_package_progress(pkg_name, -1, "Upgrading...")
                    self.status_card.status_label.setText(f"Upgrading {pkg_name}...")
                    self.status_bar.showMessage(f"Upgrading {pkg_name}...")
                
                elif install_match:
                    pkg_name = install_match.group(1)
                    if self.current_package != pkg_name:
                        if self.current_package:
                            self.update_package_progress(self.current_package, 100, "✓ Complete")
                        self.current_package = pkg_name
                        self.update_package_progress(pkg_name, -1, "Installing...")
                    self.status_card.status_label.setText(f"Installing {pkg_name}...")
                    self.status_bar.showMessage(f"Installing {pkg_name}...")
                
                download_match = re.search(r'downloading\s+([^\s]+)', line, re.IGNORECASE)
                if download_match and self.current_package:
                    self.update_package_progress(self.current_package, -1, "Downloading...")
                
                percent_match = re.search(r'(\d+)%', line)
                if percent_match and self.current_package:
                    percent = int(percent_match.group(1))
                    self.update_package_progress(self.current_package, percent, f"{percent}%")
            
            if "downloading" in data.lower():
                self.status_card.status_label.setText("Downloading packages...")
            elif "checking" in data.lower():
                self.status_card.status_label.setText("Checking packages...")
            elif "resolving" in data.lower():
                self.status_card.status_label.setText("Resolving dependencies...")
            elif "loading" in data.lower():
                self.status_card.status_label.setText("Loading package files...")

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        error_msg = f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {data}"
        self.update_log_content += error_msg
        try:
            self.log_textview.insertPlainText(error_msg)
            self.log_textview.ensureCursorVisible()
        except Exception:
            pass
        if self.current_process == "pacman_update":
            if "authentication failed" in data.lower() or "not authorized" in data.lower():
                self.status_card.status_icon.setText("✗")
                self.status_card.status_label.setText("Authentication failed. Update cancelled.")
                self.status_card.progress_bar.setVisible(False)
                self.set_buttons_enabled(True)
                self.current_process = None
            elif self.process.exitStatus() == QProcess.NormalExit and self.process.exitCode() != 0:
                self.status_card.status_icon.setText("✗")
                self.status_card.status_label.setText("Pacman update failed. Check log.")
                self.status_card.progress_bar.setVisible(False)
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
            self.status_card.status_icon.setText("✗")
            self.status_card.status_label.setText(f"Process crashed: {process_name}")
            self.status_bar.showMessage(f"Process crashed: {process_name}")
            self.set_buttons_enabled(True)
            return

        if process_name == "checkupdates":
            if exitCode == 0:
                self.status_card.status_label.setText("Checking AUR packages...")
                self.status_bar.showMessage("Checking AUR packages...")
                self.current_process = "yay_check"
                self.process.start(YAY_CMD, ["-Qua"])
            else:
                self.status_card.status_icon.setText("✗")
                self.status_card.status_label.setText("Failed to check official updates.")
                self.status_bar.showMessage("Failed to check official updates.")
                self.set_buttons_enabled(True)
                self.authenticated = False

        elif process_name == "yay_check":
            if exitCode == 0:
                self.package_card.package_list.clear()
                
                self.filter_ignored_packages()
                
                if self.pending_pacman:
                    self.package_card.package_list.addItem("━━━ Official Packages ━━━")
                    for pkg in self.pending_pacman:
                        item = QListWidgetItem(f"📦 {pkg}")
                        item.setToolTip("Official repository package")
                        self.package_card.package_list.addItem(item)
                
                if self.pending_aur:
                    if self.pending_pacman:
                        self.package_card.package_list.addItem("")
                    self.package_card.package_list.addItem("━━━ AUR Packages ━━━")
                    for pkg in self.pending_aur:
                        item = QListWidgetItem(f"🎯 {pkg}")
                        item.setToolTip("AUR package")
                        self.package_card.package_list.addItem(item)

                if not self.pending_pacman and not self.pending_aur:
                    self.status_card.status_icon.setText("✓")
                    self.status_card.status_label.setText("System is up to date!")
                    self.package_card.stats_label.setText("0 updates available")
                    self.status_bar.showMessage("System is up to date!")
                    self.authenticated = False
                    try:
                        subprocess.Popen(['notify-send', 'Arch Update', 'System is up to date!'])
                    except:
                        pass
                    
                    self.tray_icon.showMessage(
                        "Arch Update",
                        "System is up to date!",
                        QSystemTrayIcon.Information,
                        3000
                    )
                else:
                    count = len(self.pending_pacman) + len(self.pending_aur)
                    self.status_card.status_icon.setText("▣")
                    self.status_card.status_label.setText(f"{count} update(s) available!")
                    self.package_card.stats_label.setText(f"{count} updates available")
                    self.status_bar.showMessage(f"{count} updates available!")
                    try:
                        subprocess.Popen(['notify-send', 'Arch Update', f'{count} updates available!'])
                    except:
                        pass
                    
                    self.tray_icon.showMessage(
                        "Arch Update",
                        f"{count} updates available!",
                        QSystemTrayIcon.Information,
                        5000
                    )
            else:
                self.status_card.status_icon.setText("✗")
                self.status_card.status_label.setText("Failed to check AUR updates.")
                self.status_bar.showMessage("Failed to check AUR updates.")

            self.set_buttons_enabled(True)

        elif process_name == "pacman_update":
            if exitCode == 0:
                self.status_card.status_label.setText("Pacman update successful. Proceeding to AUR...")
                self.status_card.progress_bar.setRange(0, 100)
                self.status_card.progress_bar.setValue(100)
                self.update_log_content += "Pacman update successful.\n"
                if self.pending_aur:
                    self.run_yay_update()
                else:
                    self.finalize_update()
            else:
                if exitStatus != QProcess.CrashExit:
                    self.status_card.status_icon.setText("✗")
                    self.status_card.status_label.setText("Pacman update failed. Check log.")
                    self.status_bar.showMessage("Pacman update failed.")
                self.update_log_content += f"Pacman update failed (Code: {exitCode}).\n"
                self.status_card.progress_bar.setVisible(False)
                self.set_buttons_enabled(True)
                self.authenticated = False

def parse_pacman_log(start_epoch):
    """Parse pacman log for recent updates"""
    updated_lines = []
    try:
        with open(PACMAN_LOG, 'r') as f:
            for line in f:
                if "[ALPM]" in line and ("upgraded" in line or "installed" in line):
                    match = re.match(r'\[(.*?)\]', line)
                    if match:
                        log_time_str = match.group(1)
                        try:
                            log_dt_naive = datetime.strptime(log_time_str.split('+')[0], '%Y-%m-%dT%H:%M:%S')
                            log_epoch = time.mktime(log_dt_naive.timetuple())

                            if log_epoch >= start_epoch:
                                action_part = line.split("] [ALPM] ")[1].strip()
                                updated_lines.append(f" - {action_part}")
                        except ValueError:
                            if time.time() > start_epoch:
                                action_part = line.split("] [ALPM] ")[1].strip()
                                updated_lines.append(f" - {action_part} (time parse failed)")
                            continue
    except FileNotFoundError:
        return "Error: Could not open pacman log file.\n"
    except Exception as e:
        return f"Error parsing pacman log: {e}\n"

    if updated_lines:
        return "Packages updated/installed in this session:\n" + "\n".join(updated_lines) + "\n"
    else:
        return "No package changes recorded in pacman log for this session.\n"

# Make parse_pacman_log a method of UpdateAppWindow
UpdateAppWindow.parse_pacman_log = lambda self, start_epoch: parse_pacman_log(start_epoch)

# --- Beautiful Settings Dialog ---
class BeautifulSettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 650)
        
        # Get current theme for styling
        theme_name = self.settings.value("current_theme", "Dark Professional")
        current_theme = theme_name  # Define it here before use
        if theme_name in THEME_PRESETS:
            theme = THEME_PRESETS[theme_name]
        else:
            theme = THEME_PRESETS["Dark Professional"]
        
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme["window_bg"]}, stop:1 {theme["secondary_bg"]});
                color: {theme["text_fg"]};
            }}
            QLabel {{ color: {theme["text_fg"]}; }}
            QTabWidget::pane {{
                border: 1px solid {theme["border"]};
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.2);
            }}
            QTabBar::tab {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid {theme["border"]};
                border-radius: 6px;
                padding: 8px 16px;
                margin-right: 2px;
                color: {theme["text_fg"]};
            }}
            QTabBar::tab:selected {{
                background: {theme["accent"]};
                color: {theme["window_bg"]};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme["border"]};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: {theme["text_fg"]};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QComboBox {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                padding: 5px;
                color: {theme["text_fg"]};
            }}
            QComboBox QAbstractItemView {{
                background: {theme["list_bg"]};
                color: {theme["text_fg"]};
                selection-background-color: {theme["accent"]};
            }}
            QSpinBox, QLineEdit {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                padding: 5px;
                color: {theme["text_fg"]};
            }}
            QCheckBox {{
                color: {theme["text_fg"]};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid {theme["border"]};
                background: rgba(255, 255, 255, 0.1);
            }}
            QCheckBox::indicator:checked {{
                background: {theme["accent"]};
                border-color: {theme["accent"]};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        header = QLabel("⚙ Settings")
        header.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        tabs = QTabWidget()
        
        # Appearance Tab
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        appearance_layout.setContentsMargins(15, 15, 15, 15)
        
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QVBoxLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEME_PRESETS.keys())
        self.theme_combo.setCurrentText(current_theme)
        self.theme_combo.currentTextChanged.connect(self.preview_theme)
        theme_layout.addWidget(self.theme_combo)
        
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        theme_layout.addWidget(preview_label)
        
        self.preview_frame = QFrame()
        self.preview_frame.setFixedHeight(80)
        theme_layout.addWidget(self.preview_frame)
        
        theme_group.setLayout(theme_layout)
        appearance_layout.addWidget(theme_group)
        
        font_group = QGroupBox("Typography")
        font_layout = QFormLayout()
        
        self.font_family = QFontComboBox()
        current_font = self.settings.value("font_family", "Sans Serif")
        self.font_family.setCurrentFont(QFont(current_font))
        font_layout.addRow("Font Family:", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(self.settings.value("font_size", 10, type=int))
        font_layout.addRow("Font Size:", self.font_size)
        
        font_group.setLayout(font_layout)
        appearance_layout.addWidget(font_group)
        
        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "Appearance")
        
        # Updates Tab
        updates_tab = QWidget()
        updates_layout = QVBoxLayout(updates_tab)
        updates_layout.setContentsMargins(15, 15, 15, 15)
        
        auto_group = QGroupBox("Automatic Updates")
        auto_layout = QVBoxLayout()
        
        self.check_startup = QCheckBox("Check for updates on application startup")
        self.check_startup.setChecked(self.settings.value("auto_check_startup", False, type=bool))
        auto_layout.addWidget(self.check_startup)
        
        self.scheduled_check = QCheckBox("Enable scheduled update checks")
        self.scheduled_check.setChecked(self.settings.value("auto_check_enabled", False, type=bool))
        auto_layout.addWidget(self.scheduled_check)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Check interval:"))
        self.check_interval = QSpinBox()
        self.check_interval.setRange(1, 24)
        self.check_interval.setValue(self.settings.value("auto_check_interval", 6, type=int))
        interval_layout.addWidget(self.check_interval)
        interval_layout.addWidget(QLabel("hours"))
        interval_layout.addStretch()
        auto_layout.addLayout(interval_layout)
        
        auto_group.setLayout(auto_layout)
        updates_layout.addWidget(auto_group)
        
        behavior_group = QGroupBox("Update Behavior")
        behavior_layout = QVBoxLayout()
        
        self.minimize_tray = QCheckBox("Minimize to system tray when closing")
        self.minimize_tray.setChecked(self.settings.value("minimize_to_tray", True, type=bool))
        behavior_layout.addWidget(self.minimize_tray)
        
        self.show_notifications = QCheckBox("Show desktop notifications")
        self.show_notifications.setChecked(self.settings.value("show_notifications", True, type=bool))
        behavior_layout.addWidget(self.show_notifications)
        
        self.confirm_updates = QCheckBox("Ask for confirmation before updating")
        self.confirm_updates.setChecked(self.settings.value("confirm_updates", False, type=bool))
        behavior_layout.addWidget(self.confirm_updates)
        
        behavior_group.setLayout(behavior_layout)
        updates_layout.addWidget(behavior_group)
        
        updates_layout.addStretch()
        tabs.addTab(updates_tab, "Updates")
        
        # Advanced Tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        advanced_layout.setContentsMargins(15, 15, 15, 15)
        
        terminal_group = QGroupBox("Terminal Settings")
        terminal_layout = QFormLayout()
        
        self.terminal_cmd = QLineEdit()
        self.terminal_cmd.setText(self.settings.value("terminal_cmd", TERMINAL_CMD))
        self.terminal_cmd.setPlaceholderText("e.g., foot, kitty, alacritty")
        terminal_layout.addRow("Terminal Command:", self.terminal_cmd)
        
        self.terminal_flag = QLineEdit()
        self.terminal_flag.setText(self.settings.value("terminal_flag", TERMINAL_EXEC_FLAG))
        self.terminal_flag.setPlaceholderText("e.g., -e, --")
        terminal_layout.addRow("Execute Flag:", self.terminal_flag)
        
        terminal_group.setLayout(terminal_layout)
        advanced_layout.addWidget(terminal_group)
        
        performance_group = QGroupBox("Performance")
        performance_layout = QVBoxLayout()
        
        self.animations_enabled = QCheckBox("Enable UI animations")
        self.animations_enabled.setChecked(self.settings.value("animations_enabled", True, type=bool))
        performance_layout.addWidget(self.animations_enabled)
        
        self.high_dpi = QCheckBox("Enable high DPI scaling")
        self.high_dpi.setChecked(self.settings.value("high_dpi", True, type=bool))
        performance_layout.addWidget(self.high_dpi)
        
        performance_group.setLayout(performance_layout)
        advanced_layout.addWidget(performance_group)
        
        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(tabs)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = ActionButton("Reset", "↺")
        reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addWidget(reset_btn)
        
        apply_btn = ActionButton("Apply", "✓", primary=True)
        apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(apply_btn)
        
        close_btn = ActionButton("Close", "✕")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.preview_theme(current_theme)
    
    def preview_theme(self, theme_name):
        if theme_name in THEME_PRESETS:
            theme = THEME_PRESETS[theme_name]
            self.preview_frame.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {theme["window_bg"]}, stop:1 {theme["secondary_bg"]});
                    border: 2px solid {theme["accent"]};
                    border-radius: 6px;
                }}
            """)
    
    def apply_settings(self):
        self.settings.setValue("current_theme", self.theme_combo.currentText())
        self.settings.setValue("font_family", self.font_family.currentFont().family())
        self.settings.setValue("font_size", self.font_size.value())
        self.settings.setValue("auto_check_startup", self.check_startup.isChecked())
        self.settings.setValue("auto_check_enabled", self.scheduled_check.isChecked())
        self.settings.setValue("auto_check_interval", self.check_interval.value())
        self.settings.setValue("minimize_to_tray", self.minimize_tray.isChecked())
        self.settings.setValue("show_notifications", self.show_notifications.isChecked())
        self.settings.setValue("confirm_updates", self.confirm_updates.isChecked())
        self.settings.setValue("terminal_cmd", self.terminal_cmd.text())
        self.settings.setValue("terminal_flag", self.terminal_flag.text())
        self.settings.setValue("animations_enabled", self.animations_enabled.isChecked())
        self.settings.setValue("high_dpi", self.high_dpi.isChecked())
        
        self.parent().apply_styles()
        self.parent().setup_auto_check_timer()
        
        QMessageBox.information(self, "Settings Applied", "Settings applied successfully!")
        self.accept()
    
    def reset_defaults(self):
        reply = QMessageBox.question(self, "Reset Settings",
            "Reset all settings to defaults?", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.theme_combo.setCurrentText("Dark Professional")
            self.font_family.setCurrentFont(QFont("Sans Serif"))
            self.font_size.setValue(10)
            self.check_startup.setChecked(False)
            self.scheduled_check.setChecked(False)
            self.check_interval.setValue(6)
            self.minimize_tray.setChecked(True)
            self.show_notifications.setChecked(True)
            self.confirm_updates.setChecked(False)
            self.terminal_cmd.setText(TERMINAL_CMD)
            self.terminal_flag.setText(TERMINAL_EXEC_FLAG)

# --- Package Search Dialog ---
class PackageSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Packages")
        self.setMinimumSize(700, 500)
        
        settings = QSettings("MyOrg", "ArchUpdateGUI")
        theme_name = settings.value("current_theme", "Dark Professional")
        theme = THEME_PRESETS.get(theme_name, THEME_PRESETS["Dark Professional"])
        
        self.setStyleSheet(f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {theme["window_bg"]}, stop:1 {theme["secondary_bg"]});
                color: {theme["text_fg"]};
            }}
            QLabel {{ color: {theme["text_fg"]}; }}
            QLineEdit {{
                padding: 10px;
                border: 2px solid {theme["border"]};
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.3);
                color: {theme["text_fg"]};
            }}
            QTreeWidget {{
                border: 2px solid {theme["border"]};
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.2);
                color: {theme["text_fg"]};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter package name...")
        self.search_input.returnPressed.connect(self.search_packages)
        search_layout.addWidget(self.search_input)
        
        search_btn = ActionButton("Search", "⌕", primary=True)
        search_btn.clicked.connect(self.search_packages)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        self.results_list = QTreeWidget()
        self.results_list.setHeaderLabels(["Package", "Version", "Repository", "Description"])
        layout.addWidget(self.results_list)
        
        close_btn = ActionButton("Close", "✕")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def search_packages(self):
        query = self.search_input.text().strip()
        if not query:
            return
        
        self.results_list.clear()
        self.results_list.addTopLevelItem(QTreeWidgetItem(["Searching...", "", "", ""]))
        
        def do_search():
            try:
                result = subprocess.run(['pacman', '-Ss', query], capture_output=True, text=True, timeout=10)
                lines = result.stdout.split('\n')
                packages = []
                
                for i in range(0, len(lines)-1, 2):
                    if lines[i].strip():
                        match = re.match(r'(\S+)/(\S+)\s+(\S+)', lines[i])
                        if match:
                            repo, name, version = match.groups()
                            desc = lines[i+1].strip() if i+1 < len(lines) else ""
                            packages.append((name, version, repo, desc))
                
                QApplication.instance().postEvent(self, SearchCompleteEvent(packages))
            except:
                pass
        
        Thread(target=do_search, daemon=True).start()
    
    def event(self, e):
        if isinstance(e, SearchCompleteEvent):
            self.results_list.clear()
            for name, version, repo, desc in e.packages:
                self.results_list.addTopLevelItem(QTreeWidgetItem([name, version, repo, desc]))
            return True
        return super().event(e)

# --- Update History Dialog ---
class UpdateHistoryDialog(QDialog):
    def __init__(self, parent=None):  # FIXED: was __init__(init__(
        super().__init__(parent)
        self.setWindowTitle("Update History")
        self.setMinimumSize(800, 500)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.history_tree = QTreeWidget()
        self.history_tree.setHeaderLabels(["Date", "Type", "Count", "Status"])
        layout.addWidget(self.history_tree)
        
        self.load_history()
        
        btn_layout = QHBoxLayout()
        refresh_btn = ActionButton("Refresh", "↻")
        refresh_btn.clicked.connect(self.load_history)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        
        close_btn = ActionButton("Close", "✕")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
    
    def load_history(self):
        history = load_update_history()
        self.history_tree.clear()
        for entry in reversed(history):
            status = "✓" if entry.get('status') == 'Success' else "✗"
            self.history_tree.addTopLevelItem(QTreeWidgetItem([
                entry.get('date', ''),
                entry.get('type', ''),
                str(entry.get('package_count', 0)),
                f"{status} {entry.get('status', '')}"
            ]))

# --- Ignored Packages Dialog ---
class IgnoredPackagesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ignored Packages")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("Manage Ignored Packages")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        self.ignored_list = QListWidget()
        self.load_ignored()
        layout.addWidget(self.ignored_list)
        
        btn_layout = QHBoxLayout()
        self.add_input = QLineEdit()
        self.add_input.setPlaceholderText("Package name...")
        btn_layout.addWidget(self.add_input)
        
        add_btn = ActionButton("Add", "+", primary=True)
        add_btn.clicked.connect(self.add_package)
        btn_layout.addWidget(add_btn)
        
        remove_btn = ActionButton("Remove", "-")
        remove_btn.clicked.connect(self.remove_package)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)
        
        close_btn = ActionButton("Close", "✕")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def load_ignored(self):
        packages = load_ignored_packages()
        self.ignored_list.clear()
        for pkg in packages:
            self.ignored_list.addItem(f"▪ {pkg}")
    
    def add_package(self):
        pkg = self.add_input.text().strip()
        if not pkg:
            return
        packages = load_ignored_packages()
        if pkg in packages:
            QMessageBox.warning(self, "Duplicate", f"'{pkg}' already ignored.")
            return
        packages.append(pkg)
        save_ignored_packages(packages)
        self.ignored_list.addItem(f"▪ {pkg}")
        self.add_input.clear()
    
    def remove_package(self):
        current = self.ignored_list.currentItem()
        if not current:
            return
        pkg = current.text().replace("▪ ", "")
        packages = load_ignored_packages()
        if pkg in packages:
            packages.remove(pkg)
            save_ignored_packages(packages)
            self.ignored_list.takeItem(self.ignored_list.row(current))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Arch Update GUI")
    app.setOrganizationName("MyOrg")
    app.setOrganizationDomain("myorg.com")
    
    # Enable high DPI scaling
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    window = UpdateAppWindow()
    sys.exit(app.exec())
