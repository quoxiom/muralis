"""Main application orchestrator for Muralis."""

import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from muralis.config import ConfigManager
from muralis.providers import get_provider
from muralis.setter import get_wallpaper_setter
from muralis.storage import StorageManager
from muralis.scheduler import SchedulerManager
from muralis.utils.downloader import download_image
from muralis.utils.notify import send_notification

class MuralisApp:
    """Main application class for Muralis wallpaper manager."""
    
    def __init__(self, config_path: str, verbose: bool = False):
        self.config = ConfigManager(config_path)
        self.storage = StorageManager(self.config)
        self.setter = get_wallpaper_setter()
        self.scheduler = SchedulerManager(self.config)
        
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - Muralis - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger("muralis")
    
    def run_once(self, provider_override: Optional[str] = None) -> bool:
        """Run one wallpaper update cycle.
        
        Args:
            provider_override: Optional provider name to override config
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.info("🖼️  Starting Muralis wallpaper update...")
        
        # Get provider
        provider_name = provider_override or self.config.get('general', 'provider')
        provider = get_provider(provider_name, self.config)
        self.logger.info(f"📡 Using provider: {provider.name}")
        
        try:
            # Get wallpaper URL
            resolution = self.config.get('image', 'resolution', '1920x1080')
            url = provider.get_daily_url(resolution)
            
            if not url:
                self.logger.error("❌ Failed to get wallpaper URL")
                return False
            
            self.logger.debug(f"Download URL: {url}")
            
            # Download image
            download_dir = self.config.get_download_dir()
            download_dir.mkdir(parents=True, exist_ok=True)
            
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"muralis_{date_str}_{provider_name}.jpg"
            image_path = download_dir / filename
            
            timeout = self.config.get_int('advanced', 'timeout_seconds', 30)
            retries = self.config.get_int('advanced', 'retry_attempts', 3)
            
            self.logger.info(f"📥 Downloading wallpaper...")
            if not download_image(url, str(image_path), timeout, retries):
                self.logger.error("❌ Failed to download wallpaper")
                return False
            
            self.logger.info(f"✓ Downloaded to: {image_path}")
            
            # Apply effects if configured
            if self.config.get_bool('image', 'apply_effects', False):
                from muralis.utils.effects import apply_effect
                effect = self.config.get('image', 'effect_type', 'none')
                image_path = apply_effect(str(image_path), effect)
                self.logger.info(f"🎨 Applied effect: {effect}")
            
            # Set wallpaper
            self.logger.info(f"🖥️  Setting wallpaper...")
            if not self.setter.set_wallpaper(str(image_path)):
                self.logger.error("❌ Failed to set wallpaper")
                return False
            
            self.logger.info("✅ Wallpaper set successfully")
            
            # Handle storage
            if not self.config.get_bool('storage', 'save_downloads', True):
                image_path.unlink()
                self.logger.info("🗑️  Deleted temporary wallpaper")
            else:
                self.storage.cleanup_old()
                self.logger.info("💾 Wallpaper saved to storage")
            
            # Send notification
            if self.config.get_bool('notifications', 'enabled', True):
                metadata = provider.get_metadata()
                title = metadata.get('title', f"Muralis: {provider_name.title()}")
                message = metadata.get('copyright', 'Your wallpaper has been updated')
                send_notification(title, message)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False
    
    def setup_scheduler(self) -> bool:
        """Setup automatic wallpaper updates."""
        self.logger.info("🔧 Setting up automatic updates...")
        if self.scheduler.setup():
            self.logger.info("✅ Daily updates scheduled successfully")
            if self.config.get_bool('notifications', 'enabled', True):
                send_notification("Muralis", "Daily wallpaper updates have been scheduled")
            return True
        else:
            self.logger.error("❌ Failed to setup scheduler")
            return False
    
    def show_config(self):
        """Display current configuration."""
        self.config.display()
    
    def run_daemon(self):
        """Run as daemon with scheduler."""
        self.logger.info("🚀 Starting Muralis in daemon mode")
        self.scheduler.start()
