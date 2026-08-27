"""XFCE desktop wallpaper setter."""

import subprocess
from .base import WallpaperSetter


class XfceSetter(WallpaperSetter):
    """Set wallpaper on XFCE desktop."""

    def set_wallpaper(self, image_path: str) -> bool:
        """Set wallpaper using xfconf-query."""
        try:
            # Get the list of monitors
            result = subprocess.run(
                ["xfconf-query", "-c", "xfce4-desktop", "-l"], capture_output=True, text=True
            )

            # Find all backdrop properties
            props = [line for line in result.stdout.split("\n") if "last-image" in line]

            # Set for each monitor found
            for prop in props:
                subprocess.run(
                    ["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", image_path],
                    check=False,
                    capture_output=True,
                )

            return len(props) > 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
