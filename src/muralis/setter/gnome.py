"""GNOME desktop wallpaper setter."""

import subprocess
from .base import WallpaperSetter

class GnomeSetter(WallpaperSetter):
    """Set wallpaper on GNOME desktop."""
    
    def set_wallpaper(self, image_path: str) -> bool:
        """Set wallpaper using gsettings."""
        try:
            uri = f"file://{image_path}"
            
            # Set for light mode
            subprocess.run([
                "gsettings", "set", 
                "org.gnome.desktop.background", 
                "picture-uri", uri
            ], check=True, capture_output=True)
            
            # Set for dark mode (GNOME 42+)
            subprocess.run([
                "gsettings", "set", 
                "org.gnome.desktop.background", 
                "picture-uri-dark", uri
            ], check=True, capture_output=True)
            
            # Set picture options
            subprocess.run([
                "gsettings", "set",
                "org.gnome.desktop.background",
                "picture-options", "zoom"
            ], check=False, capture_output=True)
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def supports_da(self) -> bool:
        """Check if running under GNOME."""
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.background", "picture-uri"],
                capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
