"""GUI module for Muralis - Smart Wallpaper Manager.

This module provides the graphical user interface for Muralis,
including the main window, settings, history viewer, preview widget,
and system tray integration.
"""

from .main_window import MainWindow
from .settings_tab import SettingsTab
from .history_tab import HistoryTab
from .preview_widget import PreviewWidget
from .tray_icon import TrayIcon

__all__ = [
    'MainWindow',
    'SettingsTab', 
    'HistoryTab',
    'PreviewWidget',
    'TrayIcon',
]


def run_gui():
    """Launch Muralis GUI application.
    
    This is the main entry point for the GUI. It creates the
    QApplication, main window, and starts the event loop.
    
    Example:
        from muralis.gui import run_gui
        run_gui()
    """
    import sys
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    
    app = QApplication(sys.argv)
    app.setApplicationName("Muralis")
    app.setOrganizationName("Quoxiom")
    app.setApplicationDisplayName("Muralis Wallpaper Manager")
    
    # Enable high DPI scaling for better display on high-resolution screens
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Set application icon (once we have icons)
    # app.setWindowIcon(QIcon(":/icons/muralis.png"))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


# Version of the GUI module
__version__ = "0.2.0"

# Module metadata
__author__ = "Qamber Haidry"
__copyright__ = "Copyright (c) 2026 Quoxiom"
__license__ = "MIT"


if __name__ == "__main__":
    """Run the GUI when this module is executed directly."""
    run_gui()