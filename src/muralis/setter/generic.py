"""Generic wallpaper setter for unknown desktop environments."""

import subprocess
from .base import WallpaperSetter


class GenericSetter(WallpaperSetter):
    """Fallback wallpaper setter using common tools."""

    def set_wallpaper(self, image_path: str) -> bool:
        """Try multiple methods to set wallpaper."""
        methods = [
            # GNOME/Unity/Cinnamon
            [
                "gsettings",
                "set",
                "org.gnome.desktop.background",
                "picture-uri",
                f"file://{image_path}",
            ],
            [
                "gsettings",
                "set",
                "org.cinnamon.desktop.background",
                "picture-uri",
                f"file://{image_path}",
            ],
            # feh (lightweight window managers)
            ["feh", "--bg-scale", image_path],
            ["feh", "--bg-fill", image_path],
            # nitrogen
            ["nitrogen", "--set-zoom-fill", image_path],
            ["nitrogen", "--set-scaled", image_path],
            # hsetroot
            ["hsetroot", "-fill", image_path],
            # ImageMagick
            ["display", "-window", "root", image_path],
            # xsetbg (X11)
            ["xsetbg", "-fullscreen", image_path],
            # wally
            ["wally", image_path],
        ]

        for method in methods:
            try:
                subprocess.run(method, check=True, capture_output=True, text=True)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        return False
