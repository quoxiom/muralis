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
    
    def supports_da(self) -> bool:
        """Check if running under KDE."""
        try:
            result = subprocess.run(
                ["kwriteconfig5", "--help"],
                capture_output=True
            )
            return result.returncode == 0 or os.environ.get('KDE_FULL_SESSION') == 'true'
        except FileNotFoundError:
            return False
