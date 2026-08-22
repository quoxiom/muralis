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

# Greyscale icon tint (idle). Active/accent variants come from the theme.
ICON_IDLE = "#9e9e9e"


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


def app_icon(tint: str = "#d4d4d4") -> QIcon:
    """The application icon at multiple sizes (window + taskbar).

    ``tint`` selects the glyph colour so it can be made light or dark to stay
    visible on the current theme's surfaces.
    """
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addPixmap(render_pixmap("muralis", size, tint))
    return icon


def icon_tint_for_theme(colors: dict) -> str:
    """Pick a glyph colour that reads on the theme's window surface.

    Light themes get a dark glyph, dark themes a light glyph, so it is visible
    on both a light taskbar and a dark window.
    """
    try:
        s = colors.get("window", "#ffffff")
        s = s.lstrip("#")
        luminance = (int(s[0:2], 16) * 299
                     + int(s[2:4], 16) * 587
                     + int(s[4:6], 16) * 114) / 1000
        return "#1a1a1a" if luminance > 128 else "#e8e8e8"
    except (ValueError, IndexError):
        return "#d4d4d4"
