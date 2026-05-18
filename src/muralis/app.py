"""Main application orchestrator for Muralis."""

import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from muralis.config import ConfigManager
from muralis.providers import get_provider
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
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - Muralis - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("muralis")
        
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
        session = requests.Session()
        
        # Configure proxy
        proxy_settings = self.config.get_proxy_settings()
        if proxy_settings:
            session.proxies.update(proxy_settings)
            self.logger.debug(f"Proxy configured: {list(proxy_settings.keys())}")
        
        # Configure user agent
        user_agent = self.config.get_str('networking', 'user_agent', 'Muralis/1.0')
        session.headers.update({'User-Agent': user_agent})
        
        # Verify SSL
        verify_ssl = self.config.get_bool('networking', 'verify_ssl', True)
        session.verify = verify_ssl
        
        # Set max redirects
        max_redirects = self.config.get_int('networking', 'max_redirects', 5)
        session.max_redirects = max_redirects
        
        return session
    
    def get_timeout(self) -> int:
        """Get request timeout from config.
        
        Returns:
            Timeout in seconds
        """
        return self.config.get_int('networking', 'download_timeout', 30)
    
    def download_image(self, url: str, save_path: Path) -> bool:
        """Download image with proper timeout handling.
        
        Args:
            url: Image URL to download
            save_path: Path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_network_session()
        timeout = self.get_timeout()
        
        try:
            self.logger.info(f"Downloading from: {url[:80]}...")
            self.logger.debug(f"Timeout: {timeout}s, Save path: {save_path}")
            
            response = session.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                self.logger.warning(f"URL may not be an image (Content-Type: {content_type})")
            
            # Save image
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was created
            if save_path.exists() and save_path.stat().st_size > 0:
                file_size = save_path.stat().st_size
                self.logger.info(f"✓ Downloaded {file_size:,} bytes to {save_path.name}")
                return True
            else:
                self.logger.error("Downloaded file is empty")
                return False
                
        except requests.Timeout:
            self.logger.error(f"Download timed out after {timeout} seconds")
            return False
        except requests.RequestException as e:
            self.logger.error(f"Download failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during download: {e}")
            return False
    
    def get_provider(self, provider_name: Optional[str] = None):
        """Get provider instance with fallback support.
        
        Args:
            provider_name: Name of provider (uses config if None)
            
        Returns:
            Provider instance
        """
        if not provider_name:
            provider_name = self.config.get_str('general', 'provider', 'bing')
        
        # Randomize provider if enabled
        if self.config.get_bool('general', 'randomize_provider', False):
            import random
            providers = ['bing', 'nasa', 'pexels', 'wikimedia', 'artinstitute']
            provider_name = random.choice(providers)
            self.logger.info(f"🎲 Randomized provider: {provider_name}")
        
        # Get provider
        try:
            provider = get_provider(provider_name, self.config)
            self.logger.debug(f"Provider loaded: {provider_name}")
            return provider
        except Exception as e:
            self.logger.error(f"Failed to load provider {provider_name}: {e}")
            
            # Try fallback provider
            fallback = self.config.get_str('general', 'fallback_provider', 'bing')
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
        if self.config.get_bool('scheduling', 'skip_on_battery', False):
            if self._is_on_battery():
                self.logger.info("Skipping update: on battery power")
                return False
        
        # Check if on WiFi (if only_on_wifi is enabled)
        if self.config.get_bool('scheduling', 'only_on_wifi', True):
            if not self._is_on_wifi():
                self.logger.info("Skipping update: not on WiFi")
                return False
        
        # Check offline mode
        if self.config.get_bool('general', 'offline_mode', False):
            self.logger.info("Skipping update: offline mode enabled")
            return False
        
        return True
    
    def _is_on_battery(self) -> bool:
        """Check if system is running on battery."""
        try:
            # Check common power supply paths
            power_paths = [
                '/sys/class/power_supply/AC/online',
                '/sys/class/power_supply/BAT0/status',
                '/sys/class/power_supply/BAT1/status'
            ]
            
            for path in power_paths:
                p = Path(path)
                if p.exists():
                    if 'AC' in str(path):
                        with open(path, 'r') as f:
                            return f.read().strip() == '0'
                    else:
                        with open(path, 'r') as f:
                            return 'Discharging' in f.read().strip()
        except Exception:
            pass
        return False
    
    def _is_on_wifi(self) -> bool:
        """Check if connected to WiFi (not cellular)."""
        try:
            # Check network interface
            import subprocess
            result = subprocess.run(
                ['iwgetid', '-r'],
                capture_output=True,
                text=True
            )
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
            self.logger.info(f"📡 Using provider: {provider.name}")
        except Exception as e:
            self.logger.error(f"Failed to get provider: {e}")
            return False
        
        try:
            # Get wallpaper URL
            resolution = self.config.get_str('image', 'resolution', '3840x2160')
            self.logger.debug(f"Requested resolution: {resolution}")
            
            url = provider.get_daily_url(resolution)
            if not url:
                self.logger.error("❌ Failed to get wallpaper URL from provider")
                return False
            
            self.logger.debug(f"Download URL: {url[:100]}...")
            
            # Generate filename
            download_dir = self.config.get_download_dir()
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Get metadata for better filename
            metadata = provider.get_metadata()
            title = metadata.get('title', provider.name)
            safe_title = "".join(c for c in title[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"muralis_{date_str}_{provider.name}_{safe_title}.jpg"
            image_path = download_dir / filename
            
            # Download image
            if not self.download_image(url, image_path):
                return False
            
            # Apply effects if configured
            final_path = image_path
            if self.config.get_bool('image', 'apply_effects', False):
                from muralis.utils.effects import apply_effect
                effect_type = self.config.get_str('image', 'effect_type', 'none')
                if effect_type != 'none':
                    self.logger.info(f"🎨 Applying effect: {effect_type}")
                    final_path = apply_effect(str(image_path), effect_type)
            
            # Set wallpaper
            self.logger.info("🖥️  Setting wallpaper...")
            if not self.setter.set_wallpaper(str(final_path)):
                self.logger.error("❌ Failed to set wallpaper")
                return False
            
            self.logger.info("✅ Wallpaper set successfully")
            
            # Handle storage cleanup
            if not self.config.get_bool('storage', 'save_downloads', True):
                image_path.unlink()
                if final_path != image_path:
                    final_path.unlink()
                self.logger.info("🗑️  Deleted temporary wallpaper (save_downloads=false)")
            else:
                # Clean up old wallpapers
                deleted = self.storage.cleanup_old()
                if deleted > 0:
                    self.logger.info(f"💾 Cleaned up {deleted} old wallpaper(s)")
            
            # Send notification
            if self.config.get_bool('notifications', 'enabled', True):
                title = f"Muralis: {provider.name.title()}"
                message = metadata.get('copyright', metadata.get('title', 'Wallpaper updated'))
                if len(message) > 100:
                    message = message[:97] + "..."
                send_notification(title, message)
            
            self.logger.info("🎉 Wallpaper update cycle completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False
    
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
            
            if self.config.get_bool('notifications', 'enabled', True):
                send_notification(
                    "Muralis", 
                    f"Daily wallpaper updates scheduled at {update_time}"
                )
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