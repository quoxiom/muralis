"""Main application orchestrator for Muralis."""

import logging
import requests
from pathlib import Path
from typing import Optional
from muralis.config import ConfigManager
from muralis.providers import get_provider, ALL_PROVIDERS
from muralis.setter import get_wallpaper_setter
from muralis.storage import StorageManager
from muralis.scheduler import SchedulerManager
from muralis.utils.notify import send_notification


class MuralisApp:
    """Main application class for Muralis wallpaper manager."""

    def __init__(self, config_path: str, verbose: bool = False):
        """Initialize Muralis application.

        Args:
            config_path: Path to configuration file
            verbose: Enable verbose logging
        """
        self.config = ConfigManager(config_path)
        self.storage = StorageManager(self.config)
        self.setter = get_wallpaper_setter()
        self.scheduler = SchedulerManager(self.config)

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        log_file = self.config.get_log_file()

        # Configure logging. Tolerate an unwritable log directory (e.g.
        # headless/read-only installs): fall back to console-only logging
        # rather than crashing at startup.
        handlers: list = [logging.StreamHandler()]
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_file))
        except (OSError, PermissionError, ValueError):
            pass

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - Muralis - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=handlers,
        )
        self.logger = logging.getLogger("muralis")
        self.log_file = log_file

        self.logger.info(f"Muralis v{self._get_version()} initialized")
        self.logger.debug(f"Config file: {self.config.config_path}")
        self.logger.debug(f"Log file: {log_file}")

    def _get_version(self) -> str:
        """Get Muralis version."""
        try:
            from muralis import __version__

            return __version__
        except ImportError:
            return "1.0.0"

    def get_network_session(self) -> requests.Session:
        """Create requests session with proxy settings.

        Returns:
            Configured requests Session object
        """
        from muralis.utils.network import build_session

        session = build_session(self.config)
        proxy_settings = self.config.get_proxy_settings()
        if proxy_settings:
            self.logger.debug(f"Proxy configured: {list(proxy_settings.keys())}")
        return session

    def get_timeout(self) -> int:
        """Get request timeout from config.

        Returns:
            Timeout in seconds
        """
        return self.config.get_int("networking", "download_timeout", 30)

    def download_image(self, url: str, save_path: Path) -> bool:
        """Download image with proper timeout handling.

        The streaming + retry logic lives in ``muralis.utils.downloader``; this
        thin wrapper supplies the configured network session (proxy, SSL,
        user-agent, redirects) and the configured timeout.

        Args:
            url: Image URL to download
            save_path: Path to save the image

        Returns:
            True if successful, False otherwise
        """
        from muralis.utils.downloader import download_image as _download

        self.logger.info(f"Downloading from: {url[:80]}...")
        ok = _download(
            url, str(save_path), timeout=self.get_timeout(), session=self.get_network_session()
        )
        if ok and save_path.exists():
            self.logger.info(f"✓ Downloaded {save_path.stat().st_size:,} bytes to {save_path.name}")
        elif not ok:
            self.logger.error("Failed to download image")
        return ok

    def get_provider(self, provider_name: Optional[str] = None):
        """Get provider instance with fallback support.

        Args:
            provider_name: Name of provider (uses config if None)

        Returns:
            Provider instance
        """
        if not provider_name:
            provider_name = self.config.get_str("general", "provider", "bing")

        # Randomize provider if enabled
        if self.config.get_bool("general", "randomize_provider", False):
            import random

            provider_name = random.choice(ALL_PROVIDERS)
            self.logger.info(f"🎲 Randomized provider: {provider_name}")

        # Get provider
        try:
            provider = get_provider(provider_name, self.config)
            self.logger.debug(f"Provider loaded: {provider_name}")
            return provider
        except Exception as e:
            self.logger.error(f"Failed to load provider {provider_name}: {e}")

            # Try fallback provider
            fallback = self.config.get_str("general", "fallback_provider", "bing")
            if fallback != provider_name:
                self.logger.info(f"Falling back to {fallback} provider")
                try:
                    return get_provider(fallback, self.config)
                except Exception as e2:
                    self.logger.error(f"Fallback also failed: {e2}")

            raise

    def should_update(self) -> bool:
        """Check if wallpaper should be updated based on rules.

        Returns:
            True if update should proceed, False otherwise
        """
        # Check if on battery
        if self.config.get_bool("scheduling", "skip_on_battery", False):
            if self._is_on_battery():
                self.logger.info("Skipping update: on battery power")
                return False

        # Check if on WiFi (if only_on_wifi is enabled)
        if self.config.get_bool("scheduling", "only_on_wifi", True):
            if not self._is_on_wifi():
                self.logger.info("Skipping update: not on WiFi")
                return False

        # Check offline mode
        if self.config.get_bool("general", "offline_mode", False):
            self.logger.info("Skipping update: offline mode enabled")
            return False

        return True

    def _is_on_battery(self) -> bool:
        """Check if system is running on battery."""
        try:
            # Check common power supply paths
            power_paths = [
                "/sys/class/power_supply/AC/online",
                "/sys/class/power_supply/BAT0/status",
                "/sys/class/power_supply/BAT1/status",
            ]

            for path in power_paths:
                p = Path(path)
                if p.exists():
                    if "AC" in str(path):
                        with open(path, "r") as f:
                            return f.read().strip() == "0"
                    else:
                        with open(path, "r") as f:
                            return "Discharging" in f.read().strip()
        except Exception:
            pass
        return False

    def _is_on_wifi(self) -> bool:
        """Check if connected to WiFi (not cellular)."""
        try:
            # Check network interface
            import subprocess

            result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            # Assume WiFi if we can't determine
            return True

    def run_once(self, provider_override: Optional[str] = None) -> bool:
        """Run one wallpaper update cycle.

        Args:
            provider_override: Optional provider name to override config

        Returns:
            True if successful, False otherwise
        """
        self.logger.info("🖼️  Starting Muralis wallpaper update...")

        # Check scheduling rules
        if not self.should_update():
            return False

        # Get provider
        try:
            provider = self.get_provider(provider_override)
        except Exception as e:
            self.logger.error(f"Failed to get provider: {e}")
            return False

        from muralis.updater import WallpaperUpdater

        updater = WallpaperUpdater(
            config=self.config,
            setter=self.setter,
            storage=self.storage,
            download=self.download_image,
            logger=self.logger,
        )
        return updater.update(provider)

    def setup_scheduler(self) -> bool:
        """Setup automatic wallpaper updates.

        Returns:
            True if successful, False otherwise
        """
        self.logger.info("🔧 Setting up automatic updates...")
        if self.scheduler.setup():
            self.logger.info("✅ Daily updates scheduled successfully")

            update_time = self.config.get_update_time()
            self.logger.info(f"📅 Wallpaper will update daily at {update_time}")

            if self.config.get_bool("notifications", "enabled", True):
                send_notification("Muralis", f"Daily wallpaper updates scheduled at {update_time}")
            return True
        else:
            self.logger.error("❌ Failed to setup scheduler")
            return False

    def show_config(self):
        """Display current configuration."""
        self.config.display()

    def run_daemon(self):
        """Run as a foreground scheduler daemon (auto-update loop)."""
        self.logger.info("🚀 Starting Muralis in daemon mode")
        self.scheduler.start(run_callback=self.run_once)
