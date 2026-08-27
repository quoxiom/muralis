"""Cinnamon desktop wallpaper setter."""

import subprocess
from .base import WallpaperSetter


class CinnamonSetter(WallpaperSetter):
    """Set wallpaper on Cinnamon desktop."""

    def set_wallpaper(self, image_path: str) -> bool:
        """Set wallpaper using gsettings (Cinnamon uses GNOME backend)."""
        try:
            uri = f"file://{image_path}"
            subprocess.run(
                ["gsettings", "set", "org.cinnamon.desktop.background", "picture-uri", uri],
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
