"""Abstract base class for wallpaper providers."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

class WallpaperProvider(ABC):
    """Base class for all wallpaper providers."""
    
    def __init__(self, config=None):
        """Initialize provider with optional configuration."""
        self.config = config
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass
    
    @property
    def display_name(self) -> str:
        """Human-readable provider name."""
        return self.name.title()
    
    @abstractmethod
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get URL for today's wallpaper.
        
        Args:
            resolution: Desired image resolution (e.g., '1920x1080')
            
        Returns:
            URL string or None if unavailable
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current wallpaper.
        
        Returns:
            Dictionary with keys: title, copyright, date, etc.
        """
        pass
    
    def supports_resolution(self, resolution: str) -> bool:
        """Check if provider supports specific resolution."""
        # Override in subclasses if needed
        return True
    
    def get_available_resolutions(self) -> list:
        """Get list of available resolutions."""
        return ['1920x1080', '2560x1440', '3840x2160']
