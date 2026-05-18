"""History tab for Muralis GUI."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from pathlib import Path
from typing import Optional, Callable


class HistoryTab(QWidget):
    """History tab showing past wallpapers."""
    
    def __init__(self, refresh_callback: Optional[Callable] = None, parent=None):
        """Initialize the history tab.
        
        Args:
            refresh_callback: Callback function to call when refresh is requested
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.refresh_callback = refresh_callback
        
        layout = QVBoxLayout(self)
        
        # Scroll area for thumbnails
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.thumbnails_widget = QWidget()
        self.thumbnails_layout = QGridLayout(self.thumbnails_widget)
        scroll.setWidget(self.thumbnails_widget)
        
        layout.addWidget(scroll)
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh History")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)
        layout.addWidget(self.refresh_btn)
        
        # Load history
        self.refresh_history()
    
    def _clear_thumbnails(self):
        """Clear all thumbnails from the layout."""
        if not self.thumbnails_layout:
            return
        
        # Remove all items from the layout
        while self.thumbnails_layout.count():
            item = self.thumbnails_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
    
    def _on_refresh_clicked(self):
        """Handle refresh button click."""
        if self.refresh_callback:
            self.refresh_callback()
        else:
            self.refresh_history()
    
    def refresh_history(self):
        """Refresh the history display."""
        # Clear existing thumbnails
        self._clear_thumbnails()
        
        # Load wallpapers
        wallpaper_dir = Path.home() / "Pictures" / "Muralis"
        
        if not wallpaper_dir.exists():
            no_wallpapers = QLabel("No wallpapers found. Run 'muralis --once' first.")
            no_wallpapers.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.thumbnails_layout.addWidget(no_wallpapers, 0, 0)
            return
        
        wallpapers = sorted(
            wallpaper_dir.glob("muralis_*.jpg"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if not wallpapers:
            no_wallpapers = QLabel("No wallpapers found yet")
            no_wallpapers.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.thumbnails_layout.addWidget(no_wallpapers, 0, 0)
            return
        
        # Display thumbnails in a grid (4 columns)
        cols = 4
        for i, wallpaper in enumerate(wallpapers[:50]):  # Limit to 50
            row = i // cols
            col = i % cols
            
            # Create frame for each thumbnail
            frame = self._create_thumbnail_frame(wallpaper, i)
            self.thumbnails_layout.addWidget(frame, row, col)
    
    def _create_thumbnail_frame(self, wallpaper_path: Path, index: int) -> QFrame:
        """Create a thumbnail frame for a wallpaper.
        
        Args:
            wallpaper_path: Path to the wallpaper image
            index: Index for unique identification
            
        Returns:
            QFrame containing the thumbnail
        """
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #3d3d3d;
            }
        """)
        
        frame_layout = QVBoxLayout(frame)
        
        # Thumbnail image
        pixmap = QPixmap(str(wallpaper_path))
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                200, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label = QLabel()
            image_label.setPixmap(scaled)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(image_label)
        
        # File info
        name = wallpaper_path.name
        if len(name) > 35:
            name = name[:32] + "..."
        info_label = QLabel(name)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("font-size: 10px; padding: 2px;")
        frame_layout.addWidget(info_label)
        
        # Set as wallpaper button
        set_btn = QPushButton("Set as Wallpaper")
        set_btn.clicked.connect(lambda checked, path=wallpaper_path: self._set_as_wallpaper(path))
        frame_layout.addWidget(set_btn)
        
        return frame
    
    def _set_as_wallpaper(self, wallpaper_path: Path):
        """Set a selected wallpaper from history."""
        from muralis.setter import get_wallpaper_setter
        
        setter = get_wallpaper_setter()
        if setter.set_wallpaper(str(wallpaper_path)):
            if self.refresh_callback:
                self.refresh_callback()