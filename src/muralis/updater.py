"""Wallpaper update pipeline for Muralis.

Separated from ``MuralisApp`` so the download -> effects -> set -> cleanup ->
notify sequence is a self-contained, testable unit rather than a monolithic
method on the application object.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Callable, Dict

from muralis.config import ConfigManager
from muralis.storage import StorageManager
from muralis.setter.base import WallpaperSetter
from muralis.utils.notify import send_notification


class WallpaperUpdater:
    """Runs a single wallpaper update cycle.

    The updater owns the pipeline steps; the caller (``MuralisApp``) is
    responsible for scheduling rules, provider selection and wiring in the
    concrete ``download`` callback.
    """

    def __init__(
        self,
        config: ConfigManager,
        setter: WallpaperSetter,
        storage: StorageManager,
        download: Callable[[str, Path], bool],
        logger: logging.Logger,
    ):
        self.config = config
        self.setter = setter
        self.storage = storage
        self.download = download
        self.logger = logger

    def update(self, provider: Any) -> bool:
        """Fetch, download, and set a new wallpaper from ``provider``.

        Args:
            provider: A wallpaper-provider instance (``get_daily_url``,
                ``get_metadata``, ``name``).

        Returns:
            True if the update completed, False otherwise.
        """
        try:
            self.logger.info(f"📡 Using provider: {provider.name}")

            # Get wallpaper URL
            resolution = self.config.get_str('image', 'resolution', '3840x2160')
            self.logger.debug(f"Requested resolution: {resolution}")

            url = provider.get_daily_url(resolution)
            if not url:
                self.logger.error("❌ Failed to get wallpaper URL from provider")
                return False

            self.logger.debug(f"Download URL: {url[:100]}...")

            # Generate a filename from provider metadata
            image_path = self._build_image_path(provider)
            metadata = self._provider_metadata(provider)

            # Download image
            if not self.download(url, image_path):
                return False

            # Apply effects if configured
            final_path = self._apply_effects(image_path)

            # Set wallpaper
            self.logger.info("🖥️  Setting wallpaper...")
            if not self.setter.set_wallpaper(str(final_path)):
                self.logger.error("❌ Failed to set wallpaper")
                return False

            self.logger.info("✅ Wallpaper set successfully")

            # Storage cleanup / temp deletion
            self._cleanup(image_path, final_path)

            # Send notification
            self._notify(provider, metadata)

            self.logger.info("🎉 Wallpaper update cycle completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False

    # ------------------------------------------------------------------
    # Pipeline steps
    # ------------------------------------------------------------------
    def _build_image_path(self, provider: Any) -> Path:
        """Build the on-disk destination path for a provider's wallpaper."""
        download_dir = self.config.get_download_dir()
        date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        metadata = self._provider_metadata(provider)
        title = metadata.get('title', provider.name)
        safe_title = "".join(
            c for c in title[:30] if c.isalnum() or c in (' ', '-', '_')
        ).strip()
        filename = f"muralis_{date_str}_{provider.name}_{safe_title}.jpg"
        return download_dir / filename

    def _provider_metadata(self, provider: Any) -> Dict[str, Any]:
        """Return provider metadata (never raising)."""
        try:
            metadata = provider.get_metadata()
            return metadata if isinstance(metadata, dict) else {}
        except Exception as e:
            self.logger.warning(f"Could not read provider metadata: {e}")
            return {}

    def _apply_effects(self, image_path: Path) -> Path:
        """Apply the configured image effect, returning the final path."""
        if not self.config.get_bool('image', 'apply_effects', False):
            return image_path
        from muralis.utils.effects import apply_effect
        effect_type = self.config.get_str('image', 'effect_type', 'none')
        if effect_type == 'none':
            return image_path
        self.logger.info(f"🎨 Applying effect: {effect_type}")
        return Path(apply_effect(str(image_path), effect_type))

    def _cleanup(self, image_path: Path, final_path: Path):
        """Delete temporary files or clean up old wallpapers per policy."""
        if not self.config.get_bool('storage', 'save_downloads', True):
            image_path.unlink(missing_ok=True)
            if final_path != image_path:
                final_path.unlink(missing_ok=True)
            self.logger.info("🗑️  Deleted temporary wallpaper (save_downloads=false)")
            return
        deleted = self.storage.cleanup_old()
        if deleted > 0:
            self.logger.info(f"💾 Cleaned up {deleted} old wallpaper(s)")

    def _notify(self, provider: Any, metadata: Dict[str, Any]):
        """Send a desktop notification when notifications are enabled."""
        if not self.config.get_bool('notifications', 'enabled', True):
            return
        title = f"Muralis: {provider.name.title()}"
        message = metadata.get('copyright', metadata.get('title', 'Wallpaper updated'))
        if len(message) > 100:
            message = message[:97] + "..."
        send_notification(title, message)
