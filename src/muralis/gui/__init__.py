"""GUI module for Muralis - Smart Wallpaper Manager.

This module provides the graphical user interface for Muralis,
including the main window, settings, history viewer and preview widget.
"""

from .main_window import MainWindow
from .settings_tab import SettingsTab
from .history_tab import HistoryTab
from .preview_widget import PreviewWidget

__all__ = [
    'MainWindow',
    'SettingsTab', 
    'HistoryTab',
    'PreviewWidget',
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
    import configparser
    from pathlib import Path
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPalette, QColor

    from .theme import ThemeManager, DEFAULT_THEME
    from .icons import app_icon

    app = QApplication(sys.argv)
    app.setApplicationName("Muralis")
    app.setOrganizationName("Quoxiom")
    app.setApplicationDisplayName("Muralis")
    app.setWindowIcon(app_icon())

    # Apply the stored theme (or the default) before showing the window
    theme_manager = ThemeManager(app)
    config_path = Path.home() / ".config/muralis/config.ini"
    stored = DEFAULT_THEME
    if config_path.exists():
        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            stored = config.get("gui", "theme", fallback=DEFAULT_THEME)
        except Exception:
            pass
    if not theme_manager.apply(stored):
        theme_manager.apply(DEFAULT_THEME)

    # Dark palette fallback so tooltips / palette-driven widgets match the
    # theme instead of the platform default (the ugly 80s yellow).
    colors = theme_manager.load_colors(stored) or theme_manager.load_colors(DEFAULT_THEME)
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(colors.get("window", "#161616")))
    pal.setColor(QPalette.ColorRole.WindowText, QColor(colors.get("text", "#d4d4d4")))
    pal.setColor(QPalette.ColorRole.Base, QColor(colors.get("input_bg", "#1e1e1e")))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(colors.get("panel", "#1c1c1c")))
    pal.setColor(QPalette.ColorRole.Text, QColor(colors.get("text", "#d4d4d4")))
    pal.setColor(QPalette.ColorRole.Button, QColor(colors.get("btn_bg", "#242424")))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(colors.get("text", "#d4d4d4")))
    pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors.get("tooltip_bg", "#2b2b2b")))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor(colors.get("tooltip_text", "#e6e6e6")))
    pal.setColor(QPalette.ColorRole.Highlight, QColor(colors.get("accent", "#7c6cf6")))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(colors.get("accent_text", "#ffffff")))
    app.setPalette(pal)
    
    # Enable high DPI scaling for better display on high-resolution screens
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Set application icon (once we have icons)
    # app.setWindowIcon(QIcon(":/icons/muralis.png"))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


# Version of the GUI module
__version__ = "0.3.0"

# Module metadata
__author__ = "Qamber Haidry"
__copyright__ = "Copyright (c) 2026 Quoxiom"
__license__ = "MIT"


if __name__ == "__main__":
    """Run the GUI when this module is executed directly."""
    run_gui()