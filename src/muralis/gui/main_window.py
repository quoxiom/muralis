"""Main window for Muralis GUI."""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QStackedWidget,
    QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QAction

from .settings_tab import SettingsTab
from .history_tab import HistoryTab
from .preview_widget import PreviewWidget
from .tray_icon import TrayIcon


class MainWindow(QMainWindow):
    """Main application window for Muralis."""
    
    def __init__(self, parent=None):
        """Initialize the main window."""
        super().__init__(parent)
        
        self.setWindowTitle("Muralis - Smart Wallpaper Manager")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs - pass refresh callback
        self.preview_widget = PreviewWidget(
            refresh_callback=self._refresh_wallpaper,
            parent=self
        )
        self.tab_widget.addTab(self.preview_widget, "🖼️ Preview")
        
        self.settings_tab = SettingsTab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        
        self.history_tab = HistoryTab(
            refresh_callback=self._refresh_wallpaper,
            parent=self
        )
        self.tab_widget.addTab(self.history_tab, "📜 History")
        
        # Info tab placeholder
        info_tab = QLabel(
            "Muralis v0.2.0\n\n"
            "Part of Qutility Suite\n"
            "by Quoxiom\n\n"
            "GitHub: https://github.com/quoxiom/qutility-muralis"
        )
        info_tab.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_tab.setStyleSheet("font-size: 14px; padding: 50px;")
        self.tab_widget.addTab(info_tab, "ℹ️ About")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create system tray icon
        self.tray_icon = TrayIcon(refresh_callback=self._refresh_wallpaper)
        
        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh_preview)
        self.refresh_timer.start(60000)  # Refresh every minute
        
        # Load initial data
        self._load_current_wallpaper()
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        refresh_action = QAction("&Refresh Wallpaper", self)
        refresh_action.triggered.connect(self._refresh_wallpaper)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        show_tray_action = QAction("Show &Tray Icon", self)
        show_tray_action.setCheckable(True)
        show_tray_action.setChecked(True)
        show_tray_action.triggered.connect(self.toggle_tray_icon)
        view_menu.addAction(show_tray_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("&Documentation", self)
        docs_action.triggered.connect(self._show_documentation)
        help_menu.addAction(docs_action)
    
    def _load_current_wallpaper(self):
        """Load and display the current wallpaper."""
        self.preview_widget.load_current_wallpaper()
    
    def _refresh_wallpaper(self):
        """Manually refresh the wallpaper."""
        from muralis.app import MuralisApp
        from pathlib import Path
        
        self.status_bar.showMessage("Updating wallpaper...")
        
        try:
            app = MuralisApp(str(Path.home() / ".config/muralis/config.ini"))
            if app.run_once():
                self.status_bar.showMessage("Wallpaper updated successfully!", 3000)
                self._load_current_wallpaper()
                self.history_tab.refresh_history()
            else:
                self.status_bar.showMessage("Failed to update wallpaper", 3000)
                QMessageBox.warning(self, "Error", "Failed to update wallpaper")
        except Exception as e:
            self.status_bar.showMessage(f"Error: {str(e)}", 5000)
            QMessageBox.critical(self, "Error", f"Failed to update wallpaper:\n{str(e)}")
    
    def _auto_refresh_preview(self):
        """Auto-refresh the preview (not the wallpaper itself)."""
        self.preview_widget.refresh_preview()
    
    def toggle_tray_icon(self, show: bool):
        """Toggle the system tray icon visibility."""
        if show:
            self.tray_icon.show()
        else:
            self.tray_icon.hide()
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Muralis",
            "<h2>Muralis</h2>"
            "<p>Smart Wallpaper Manager for Linux</p>"
            "<p>Version 0.2.0</p>"
            "<p>Part of Qutility Suite by Quoxiom</p>"
            "<p>© 2026 Quoxiom (Qamber Haidry)</p>"
            "<p><a href='https://github.com/quoxiom/qutility-muralis'>GitHub</a></p>"
        )
    
    def _show_documentation(self):
        """Show documentation."""
        QMessageBox.information(
            self,
            "Documentation",
            "Please visit:\n"
            "https://github.com/quoxiom/qutility-muralis/wiki"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Hide to tray instead of quitting
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.show_message(
                "Muralis",
                "Application minimized to system tray"
            )
            event.ignore()
        else:
            event.accept()