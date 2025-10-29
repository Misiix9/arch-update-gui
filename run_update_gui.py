#!/usr/bin/env python3
"""
Wrapper runner that loads `style.qss` and launches `UpdateAppWindow` from `update_gui.py`
This keeps the original script unchanged and applies a global QSS stylesheet.

The QSS will override the inline styles from update_gui.py's apply_styles() method.
"""
import sys
import os
from PySide6.QtWidgets import QApplication

# Ensure the directory containing this file is on the path so we can import update_gui
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

try:
    import update_gui
except Exception as e:
    print(f"Error importing update_gui: {e}")
    raise

STYLE_PATH = os.path.join(HERE, "style.qss")

def load_stylesheet(app, path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as fh:
                qss_content = fh.read()
                app.setStyleSheet(qss_content)
                return True
        except Exception as e:
            print(f"Failed to load stylesheet: {e}")
            return False
    else:
        print(f"Stylesheet not found at: {path}")
        return False


def main():
    app = QApplication(sys.argv)
    
    # Load QSS before creating window
    load_stylesheet(app, STYLE_PATH)
    
    # Instantiate the window defined in update_gui
    # The QSS will take precedence over inline styles set by apply_styles()
    win = update_gui.UpdateAppWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
