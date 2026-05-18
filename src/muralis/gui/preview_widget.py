"""Wallpaper preview widget for Muralis GUI."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
from typing import Optional, Callable


class PreviewWidget(QWidget):
    """Widget for displaying current wallpaper preview."""
    
    def __init__(self, refresh_callback: Optional[Callable] = None, parent=None):
        """Initialize the preview widget.
        
        Args:
            refresh_callback: Callback function to call when refresh is requested
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.refresh_callback = refresh_callback
        
        layout = QVBoxLayout(self)
        
        # Preview image
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(400)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.preview_label)
        
        # Info frame
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        info_layout = QHBoxLayout(info_frame)
        
        self.info_label = QLabel("No wallpaper loaded")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(self.info_label)
        
        layout.addWidget(info_frame)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh Now")
        self.refresh_btn.clicked.connect(self.request_refresh)
        button_layout.addWidget(self.refresh_btn)
        
        self.open_folder_btn = QPushButton("📁 Open Folder")
        self.open_folder_btn.clicked.connect(self.open_wallpaper_folder)
        button_layout.addWidget(self.open_folder_btn)
        
        layout.addLayout(button_layout)
    
    def request_refresh(self):
        """Request a wallpaper refresh."""
        if self.refresh_callback:
            self.refresh_callback()
        else:
            print("No refresh callback set")
    
    def load_current_wallpaper(self):
        """Load and display the current wallpaper."""
        wallpaper_dir = Path.home() / "Pictures" / "Muralis"
        
        if wallpaper_dir.exists():
            wallpapers = list(wallpaper_dir.glob("muralis_*.jpg"))
            if wallpapers:
                latest = max(wallpapers, key=lambda p: p.stat().st_mtime)
                self.display_wallpaper(latest)
                return
        
        # No wallpaper found
        self.preview_label.setText("No wallpaper found\nRun 'muralis --once' first")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setText("No wallpaper downloaded yet")
    
    def display_wallpaper(self, image_path: Path):
        """Display a wallpaper from path."""
        pixmap = QPixmap(str(image_path))
        if not pixmap.isNull():
            # Scale to fit while maintaining aspect ratio
            scaled = pixmap.scaled(
                800, 450,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
            
            # Update info
            size_mb = image_path.stat().st_size / (1024 * 1024)
            self.info_label.setText(
                f"📷 {image_path.name}\n"
                f"📏 Size: {size_mb:.2f} MB\n"
                f"🕒 Modified: {image_path.stat().st_mtime}"
            )
        else:
            self.preview_label.setText("Failed to load image")
            self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def refresh_preview(self):
        """Refresh the preview display."""
        self.load_current_wallpaper()
    
    def open_wallpaper_folder(self):
        """Open the wallpaper folder in file manager."""
        import subprocess
        wallpaper_dir = Path.home() / "Pictures" / "Muralis"
        wallpaper_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["xdg-open", str(wallpaper_dir)])