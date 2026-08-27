"""KDE Plasma desktop wallpaper setter."""

import subprocess
from .base import WallpaperSetter

class KdeSetter(WallpaperSetter):
    """Set wallpaper on KDE Plasma desktop."""
    
    def set_wallpaper(self, image_path: str) -> bool:
        """Set wallpaper using plasma-apply-wallpaperimage."""
        try:
            # Try new method
            subprocess.run([
                "plasma-apply-wallpaperimage", image_path
            ], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Fallback to kwriteconfig5 (older KDE)
                subprocess.run([
                    "kwriteconfig5", "--file", "plasmarc",
                    "--group", "Wallpaper", "--key", "Image", image_path
                ], check=True, capture_output=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
