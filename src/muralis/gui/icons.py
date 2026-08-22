"""Greyscale SVG icons for the Muralis GUI.

Icons are rendered at runtime from the bundled SVG files and tinted to the
requested color, so the same artwork can be shown muted (idle), bright
(active), or in the theme accent.
"""

from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

ICONS_DIR = Path(__file__).parent / "icons"

# Idle greyscale + active bright + accent variants
ICON_IDLE = "#9e9e9e"
ICON_ACTIVE = "#e8e8e8"
ICON_ACCENT = "#7c6cf6"


def render_pixmap(name: str, size: int = 18, color: str = ICON_IDLE) -> QPixmap:
    """Render an SVG icon to a pixmap and tint every pixel with `color`."""
    renderer = QSvgRenderer(str(ICONS_DIR / f"{name}.svg"))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return pixmap


def make_icon(name: str, color: str = ICON_IDLE, size: int = 18) -> QIcon:
    """Build a QIcon for the named icon at the given color/size."""
    icon = QIcon()
    icon.addPixmap(render_pixmap(name, size, color))
    return icon


def app_icon() -> QIcon:
    """The application icon at multiple sizes (window + tray)."""
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(render_pixmap("muralis", size, "#ffffff"))
    return icon
