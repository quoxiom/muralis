"""GNOME desktop wallpaper setter for Muralis using gsettings command.

This module sets wallpapers on GNOME desktop environments using the native
gsettings command-line tool. It works without any Python dependencies beyond
the standard library.

Key features:
- Sets both light and dark mode wallpapers (GNOME 42+)
- Gracefully handles missing keys on older GNOME versions
- Proper error handling and logging
- No external Python dependencies required
"""

import subprocess
import logging
from typing import Optional
from .base import WallpaperSetter

# Set up logger
logger = logging.getLogger(__name__)


class GnomeSetter(WallpaperSetter):
    """Set wallpaper on GNOME desktop using gsettings command.

    This setter uses the native gsettings command to configure
    wallpapers on GNOME desktop environments. It automatically
    detects GNOME version capabilities and handles both light
    and dark mode wallpapers where supported.
    """

    # Schema and keys used by GNOME
    SCHEMA = "org.gnome.desktop.background"
    PICTURE_URI_KEY = "picture-uri"
    PICTURE_URI_DARK_KEY = "picture-uri-dark"
    PICTURE_OPTIONS_KEY = "picture-options"

    def __init__(self):
        """Initialize GNOME setter."""
        self._has_dark_mode: Optional[bool] = None

    def _check_dark_mode_support(self) -> bool:
        """Check if GNOME supports dark mode wallpaper (picture-uri-dark).

        This checks by attempting to read the key's range. If the key
        doesn't exist, gsettings returns a non-zero exit code.

        Returns:
            True if dark mode is supported, False otherwise
        """
        if self._has_dark_mode is not None:
            return self._has_dark_mode

        try:
            result = subprocess.run(
                ["gsettings", "get", self.SCHEMA, self.PICTURE_URI_DARK_KEY],
                capture_output=True,
                text=True,
                timeout=5,
            )
            self._has_dark_mode = result.returncode == 0
        except (subprocess.SubprocessError, OSError) as e:
            logger.debug(f"Dark mode check failed: {e}")
            self._has_dark_mode = False

        logger.debug(f"GNOME dark mode support: {self._has_dark_mode}")
        return bool(self._has_dark_mode)

    def _run_gsettings(self, key: str, value: Optional[str] = None, check: bool = True) -> bool:
        """Run gsettings command.

        Args:
            key: The gsettings key to set or get
            value: The value to set (None for get operation)
            check: If True, raise exception on failure

        Returns:
            True if successful, False otherwise
        """
        try:
            if value is not None:
                # Set operation
                cmd = ["gsettings", "set", self.SCHEMA, key, value]
                logger.debug(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            else:
                # Get operation (for checking)
                cmd = ["gsettings", "get", self.SCHEMA, key]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode != 0:
                if check:
                    logger.error(f"gsettings failed: {result.stderr}")
                return False

            return True

        except subprocess.TimeoutExpired:
            logger.error(f"gsettings timed out for key: {key}")
            return False
        except FileNotFoundError:
            logger.error("gsettings command not found. Is GNOME installed?")
            return False
        except Exception as e:
            logger.error(f"Unexpected error running gsettings: {e}")
            return False

    def set_wallpaper(self, image_path: str) -> bool:
        """Set wallpaper on GNOME desktop.

        Args:
            image_path: Absolute path to the wallpaper image file

        Returns:
            True if wallpaper was set successfully, False otherwise
        """
        if not image_path:
            logger.error("No image path provided")
            return False

        # Convert to file URI as expected by gsettings
        uri = f"file://{image_path}"
        logger.info(f"Setting GNOME wallpaper to: {uri[:80]}...")

        success = True

        # Set light mode wallpaper (always supported)
        if not self._run_gsettings(self.PICTURE_URI_KEY, uri, check=False):
            logger.error("Failed to set light mode wallpaper")
            success = False

        # Set dark mode wallpaper if supported (GNOME 42+)
        if self._check_dark_mode_support():
            if not self._run_gsettings(self.PICTURE_URI_DARK_KEY, uri, check=False):
                logger.warning("Failed to set dark mode wallpaper")
                # Don't mark overall as failed - dark mode is optional

        # Set picture options (zoom, centered, etc.)
        picture_options = self._get_picture_options()
        if picture_options:
            if not self._run_gsettings(self.PICTURE_OPTIONS_KEY, picture_options, check=False):
                logger.warning(f"Failed to set picture options to {picture_options}")

        if success:
            logger.info("GNOME wallpaper set successfully")
        else:
            logger.error("Failed to set GNOME wallpaper")

        return success

    def _get_picture_options(self) -> str:
        """Get the picture-options setting from config.

        Returns:
            String value for picture-options (default: 'zoom')
        """
        # This could be extended to read from config
        # For now, default to 'zoom' which scales to fill screen
        return "zoom"
