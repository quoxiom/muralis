"""System tray icon for Muralis - Simplified version."""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction
from typing import Optional, Callable


class TrayIcon(QSystemTrayIcon):
    """System tray icon for Muralis."""
    
    def __init__(self, refresh_callback: Optional[Callable] = None):
        """Initialize the system tray icon.
        
        Args:
            refresh_callback: Callback function to call when refresh is requested
        """
        super().__init__()
        
        self.refresh_callback = refresh_callback
        
        # Create icon (using a simple icon for now)
        # TODO: Add proper icon file
        self.setIcon(QIcon.fromTheme("wallpaper"))
        self.setToolTip("Muralis - Wallpaper Manager")
        
        # Create context menu
        self.menu = QMenu()
        
        # Refresh action
        self.refresh_action = QAction("🔄 Refresh Wallpaper", self)
        self.refresh_action.triggered.connect(self._on_refresh)
        self.menu.addAction(self.refresh_action)
        
        self.menu.addSeparator()
        
        # Show action
        self.show_action = QAction("📂 Show Muralis", self)
        self.show_action.triggered.connect(self._show_main_window)
        self.menu.addAction(self.show_action)
        
        self.menu.addSeparator()
        
        # Quit action
        self.quit_action = QAction("🚪 Quit", self)
        self.quit_action.triggered.connect(self._quit_app)
        self.menu.addAction(self.quit_action)
        
        self.setContextMenu(self.menu)
        
        # Connect activation signal (click)
        self.activated.connect(self._on_activated)
        
        # Show the tray icon
        self.show()
    
    def _on_refresh(self):
        """Handle refresh action."""
        if self.refresh_callback:
            self.refresh_callback()
    
    def _show_main_window(self):
        """Show the main window by finding it in the application."""
        # Find the main window from the application
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'MainWindow':
                widget.show()
                widget.raise_()
                widget.activateWindow()
                break
    
    def _quit_app(self):
        """Quit the application."""
        self.hide()
        QApplication.quit()
    
    def _on_activated(self, reason):
        """Handle tray icon activation (click)."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_main_window()
    
    def show_message(self, title: str, message: str, 
                     icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information, 
                     timeout: int = 3000):
        """Show a balloon message from the tray icon."""
        self.showMessage(title, message, icon, timeout)
    
    def update_tooltip(self, text: str):
        """Update the tray icon tooltip."""
        self.setToolTip(f"Muralis - {text}")