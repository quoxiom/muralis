"""Base class for desktop environment setters."""

from abc import ABC, abstractmethod

class WallpaperSetter(ABC):
    """Abstract base class for setting wallpapers."""
    
    @abstractmethod
    def set_wallpaper(self, image_path: str) -> bool:
        """Set wallpaper for desktop environment.
        
        Args:
            image_path: Path to image file
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
