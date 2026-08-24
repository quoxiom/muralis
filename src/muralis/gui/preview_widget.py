"""Wallpaper preview widget for Muralis GUI."""

from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
)

from muralis.i18n import t

MODIFIED_TIME_FORMAT = "%d %b %Y %H:%M:%S"

PREVIEW_SIZE = (800, 450)  # fallback for freshly-downloaded images without a saved size


def _safe_mtime(path: Path) -> float:
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def _provider_name() -> str:
    """Localized label for the configured provider."""
    provider = "bing"
    try:
        from .configview import config_view
        provider = config_view().get("general", "provider", fallback="bing")
    except Exception:
        pass
    localized = t(f"gui.provider.{provider}")
    return provider if localized.startswith("gui.provider") else localized


class PreviewWidget(QWidget):
    """Wallpaper preview: an expanding image with a rich tooltip."""

    def __init__(self, refresh_callback: Optional[Callable] = None, parent=None):
        super().__init__(parent)

        self.refresh_callback = refresh_callback
        self._pixmap: Optional[QPixmap] = None
        self._tooltip = ""

        layout = QVBoxLayout(self)
        # Match the Settings content pane's left indentation so all pages align.
        layout.setContentsMargins(20, 0, 20, 0)

        # Expands in both directions — the sole body of the preview.
        self.preview_label = QLabel()
        self.preview_label.setObjectName("previewImage")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_label.setToolTip("")
        layout.addWidget(self.preview_label, 1)

        # Action buttons (text-only, styled like the rest of the UI). They are
        # placed right-aligned in the page header row by MainWindow._make_page.
        self.refresh_btn = self._make_action_button(t("gui.preview.refresh"))
        self.open_folder_btn = self._make_action_button(
            t("gui.preview.open_folder"))
        self.refresh_btn.clicked.connect(self.request_refresh)
        self.open_folder_btn.clicked.connect(self.open_wallpaper_folder)

    def action_buttons(self) -> list:
        """Return the action buttons for the page header row."""
        return [self.refresh_btn, self.open_folder_btn]

    def _make_action_button(self, label: str) -> QPushButton:
        button = QPushButton(label)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        return button

    def request_refresh(self):
        if self.refresh_callback:
            self.refresh_callback()
        else:
            print("No refresh callback set")

    def load_current_wallpaper(self):
        wallpaper_dir = Path.home() / "Pictures" / "Muralis"
        if wallpaper_dir.exists():
            wallpapers = list(wallpaper_dir.glob("muralis_*.jpg"))
            if wallpapers:
                latest = max(wallpapers, key=_safe_mtime)
                self.display_wallpaper(latest)
                return
        self._pixmap = None
        self.preview_label.setText(t("gui.preview.none_hint"))
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setToolTip("")

    def display_wallpaper(self, image_path: Path):
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            self._pixmap = pixmap
            self._update_preview()

            stat = image_path.stat()
            size_kb = stat.st_size / 1024
            downloaded = datetime.fromtimestamp(stat.st_mtime).strftime(
                MODIFIED_TIME_FORMAT)
            provider = _provider_name()

            # Name + rich details on hover, not as cluttering on-screen text.
            self._tooltip = (
                f"{t('gui.preview.tooltip.name', name=image_path.name)}\n"
                f"{t('gui.preview.tooltip.downloaded', time=downloaded)}\n"
                f"{t('gui.preview.tooltip.size', kb=size_kb)}\n"
                f"{t('gui.preview.tooltip.provider', name=provider)}"
            )
            self.preview_label.setToolTip(self._tooltip)
        else:
            self._pixmap = None
            self.preview_label.setText(t("gui.preview.failed"))
            self.preview_label.setToolTip("")

    def _update_preview(self):
        if self._pixmap is None:
            return
        size = self.preview_label.size()
        if size.width() < 4 or size.height() < 4:
            return
        scaled = self._pixmap.scaled(
            size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self._update_preview()

    def refresh_preview(self):
        self.load_current_wallpaper()

    def open_wallpaper_folder(self):
        import subprocess
        wallpaper_dir = Path.home() / "Pictures" / "Muralis"
        wallpaper_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["xdg-open", str(wallpaper_dir)])
