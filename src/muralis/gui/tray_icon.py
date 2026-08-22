"""System tray icon for Muralis - Simplified version."""

from typing import Callable, Optional

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QAction

from muralis.i18n import t
from .icons import app_icon, make_icon, ICON_IDLE


class TrayIcon(QSystemTrayIcon):
    """System tray icon for Muralis.

    The tray menu uses standard QActions with the same greyscale icons as the
    main UI. Standard actions render reliably across desktop environments
    (custom widget rows do not), so the icon sits to the LEFT of the text.
    """

    def __init__(self, refresh_callback: Optional[Callable] = None):
        super().__init__()

        self.refresh_callback = refresh_callback
        self.setIcon(app_icon())
        self.setToolTip(t("gui.tray.tooltip"))

        self.menu = QMenu()
        self.refresh_action = self._add_action(
            t("gui.tray.refresh"), "refresh", self._on_refresh)
        self.menu.addSeparator()
        self.show_action = self._add_action(
            t("gui.tray.show"), "muralis", self._show_main_window)
        self.menu.addSeparator()
        self.quit_action = self._add_action(
            t("gui.tray.quit"), "power", self._quit_app)

        self.setContextMenu(self.menu)
        self.activated.connect(self._on_activated)
        self.show()

    def _add_action(self, text: str, icon_name: str,
                    callback: Callable) -> QAction:
        """Add a standard tray menu action (native rendering, reliable)."""
        action = QAction(text, self)
        action.setIcon(make_icon(icon_name, ICON_IDLE, 16))
        action.triggered.connect(lambda _checked=False: callback())
        self.menu.addAction(action)
        return action

    def _on_refresh(self):
        if self.refresh_callback:
            self.refresh_callback()

    def _show_main_window(self):
        for widget in QApplication.topLevelWidgets():
            if widget.__class__.__name__ == 'MainWindow':
                widget.show()
                widget.raise_()
                widget.activateWindow()
                break

    def _quit_app(self):
        self.hide()
        QApplication.quit()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_main_window()

    def show_message(self, title: str, message: str,
                     icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                     timeout: int = 3000):
        self.showMessage(title, message, icon, timeout)

    def update_tooltip(self, text: str):
        self.setToolTip(f"Muralis - {text}")
