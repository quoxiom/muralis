"""Themed message dialogs that match the app's monochrome icon set.

Qt's default QMessageBox icons are the platform's colored icons. These
helpers use the same greyscale SVG set as the rest of the UI so popup
dialogs stay consistent with the theme.
"""

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt

from .icons import make_icon, ICON_IDLE

# Monochrome glyphs shown next to the dialog text.
_ICONS = {
    "info": "info",
    "warning": "warning",
    "critical": "error",
    "question": "about",  # fallback glyph
}


def _box(
    parent, kind: str, title: str, text: str, buttons=QMessageBox.StandardButton.Ok
) -> QMessageBox:
    """Build a QMessageBox whose icon is a greyscale UI glyph."""
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setStandardButtons(buttons)
    icon_name = _ICONS.get(kind, "info")
    box.setIconPixmap(make_icon(icon_name, ICON_IDLE, 32).pixmap(32, 32))
    box.setWindowFlag(Qt.WindowType.Dialog)
    return box


def info(parent, title: str, text: str):
    _box(parent, "info", title, text).exec()


def warning(parent, title: str, text: str):
    _box(parent, "warning", title, text).exec()


def critical(parent, title: str, text: str):
    _box(parent, "critical", title, text).exec()


def confirm(parent, title: str, text: str) -> bool:
    """A Yes/No confirmation; returns True when accepted."""
    box = _box(
        parent,
        "question",
        title,
        text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return bool(box.exec() == QMessageBox.StandardButton.Yes)
