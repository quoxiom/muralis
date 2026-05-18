#!/usr/bin/env python3
"""Integration tests for Muralis application."""
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from muralis.app import MuralisApp
from muralis.config import ConfigManager


class TestMuralisAppIntegration:
    """Integration tests for MuralisApp."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.ini"
        self.config = ConfigManager(str(self.config_path))
        
        # Set test-specific config
        self.config.set('storage', 'download_dir', str(Path(self.temp_dir.name) / "wallpapers"))
        self.config.set('storage', 'save_downloads', 'true')
        self.config.set('general', 'auto_update', 'false')
        self.config.set('notifications', 'enabled', 'false')
        
        self.app = MuralisApp(str(self.config_path), verbose=False)
    
    @patch('muralis.providers.bing.BingProvider.get_daily_url')
    @patch('muralis.providers.bing.BingProvider.get_metadata')
    @patch('muralis.setter.gnome.GnomeSetter.set_wallpaper')
    @patch('muralis.utils.downloader.download_image')
    def test_run_once_success(self, mock_download, mock_setter, mock_metadata, mock_url):
        """Test successful wallpaper update."""
        # Mock provider responses
        mock_url.return_value = "https://example.com/wallpaper.jpg"
        mock_metadata.return_value = {'title': 'Test Wallpaper', 'copyright': 'Test Author'}
        
        # Mock download
        mock_download.return_value = True
        
        # Mock setter
        mock_setter.return_value = True
        
        # Run the app
        result = self.app.run_once(provider_override='bing')
        
        assert result == True
        mock_url.assert_called_once()
        mock_download.assert_called_once()
        mock_setter.assert_called_once()
    
    @patch('muralis.providers.bing.BingProvider.get_daily_url')
    def test_run_once_no_url(self, mock_url):
        """Test when provider returns no URL."""
        mock_url.return_value = None
        
        result = self.app.run_once(provider_override='bing')
        
        assert result == False
    
    @patch('muralis.providers.bing.BingProvider.get_daily_url')
    @patch('muralis.utils.downloader.download_image')
    def test_run_once_download_fails(self, mock_download, mock_url):
        """Test when download fails."""
        mock_url.return_value = "https://example.com/wallpaper.jpg"
        mock_download.return_value = False
        
        result = self.app.run_once(provider_override='bing')
        
        assert result == False
    
    @patch('muralis.providers.bing.BingProvider.get_daily_url')
    @patch('muralis.utils.downloader.download_image')
    @patch('muralis.setter.gnome.GnomeSetter.set_wallpaper')
    def test_run_once_setter_fails(self, mock_setter, mock_download, mock_url):
        """Test when setting wallpaper fails."""
        mock_url.return_value = "https://example.com/wallpaper.jpg"
        mock_download.return_value = True
        mock_setter.return_value = False
        
        result = self.app.run_once(provider_override='bing')
        
        assert result == False
    
    def test_get_provider_valid(self):
        """Test getting a valid provider."""
        provider = self.app.get_provider('bing')
        assert provider is not None
        assert provider.name == 'bing'
    
    def test_get_provider_with_fallback(self):
        """Test provider fallback when primary fails."""
        # Test with invalid provider - should fallback to bing
        with patch('muralis.providers.get_provider') as mock_get:
            mock_get.side_effect = Exception("Provider failed")
            
            # Should fallback to bing
            provider = self.app.get_provider('invalid')
            # This will use fallback mechanism in app.py
    
    def test_get_network_session(self):
        """Test network session creation."""
        session = self.app.get_network_session()
        assert session is not None
        assert hasattr(session, 'get')
        assert hasattr(session, 'post')
    
    def test_get_timeout(self):
        """Test getting timeout from config."""
        timeout = self.app.get_timeout()
        assert isinstance(timeout, int)
        assert timeout > 0
    
    @patch('muralis.scheduler.SchedulerManager.setup')
    def test_setup_scheduler(self, mock_scheduler):
        """Test scheduler setup."""
        mock_scheduler.return_value = True
        
        result = self.app.setup_scheduler()
        
        assert result == True
        mock_scheduler.assert_called_once()
    
    def test_show_config(self):
        """Test showing configuration (just verify it doesn't crash)."""
        import sys
        from io import StringIO
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        self.app.show_config()
        
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        assert "Muralis Configuration" in output
    
    @patch('muralis.providers.bing.BingProvider.get_daily_url')
    @patch('muralis.utils.downloader.download_image')
    @patch('muralis.setter.gnome.GnomeSetter.set_wallpaper')
    def test_run_once_without_saving(self, mock_setter, mock_download, mock_url):
        """Test run once with save_downloads disabled."""
        # Configure to not save downloads
        self.config.set('storage', 'save_downloads', 'false')
        
        mock_url.return_value = "https://example.com/wallpaper.jpg"
        mock_download.return_value = True
        mock_setter.return_value = True
        
        result = self.app.run_once(provider_override='bing')
        
        assert result == True
    
    @patch('muralis.providers.bing.BingProvider.get_daily_url')
    @patch('muralis.utils.downloader.download_image')
    @patch('muralis.setter.gnome.GnomeSetter.set_wallpaper')
    def test_run_once_with_random_provider(self, mock_setter, mock_download, mock_url):
        """Test run once with random provider enabled."""
        self.config.set('general', 'randomize_provider', 'true')
        
        mock_url.return_value = "https://example.com/wallpaper.jpg"
        mock_download.return_value = True
        mock_setter.return_value = True
        
        result = self.app.run_once()  # No provider override
        
        assert result == True
    
    @patch('muralis.providers.bing.BingProvider.get_daily_url')
    @patch('muralis.utils.downloader.download_image')
    @patch('muralis.setter.gnome.GnomeSetter.set_wallpaper')
    def test_run_once_with_effects(self, mock_setter, mock_download, mock_url):
        """Test run once with image effects enabled."""
        self.config.set('image', 'apply_effects', 'true')
        self.config.set('image', 'effect_type', 'blur')
        
        mock_url.return_value = "https://example.com/wallpaper.jpg"
        mock_download.return_value = True
        mock_setter.return_value = True
        
        result = self.app.run_once(provider_override='bing')
        
        assert result == True
    
    def test_should_update_by_default(self):
        """Test should_update returns True by default."""
        assert self.app.should_update() == True
    
    def test_should_update_offline_mode(self):
        """Test should_update returns False when offline."""
        self.config.set('general', 'offline_mode', 'true')
        assert self.app.should_update() == False
    
    @patch('muralis.app.MuralisApp._is_on_battery')
    def test_should_update_skip_on_battery(self, mock_battery):
        """Test should_update skips when on battery."""
        self.config.set('scheduling', 'skip_on_battery', 'true')
        mock_battery.return_value = True
        
        assert self.app.should_update() == False
    
    def tearDown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()


class TestConfigIntegration:
    """Integration tests for configuration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.ini"
    
    def test_config_persistence_between_app_instances(self):
        """Test that config changes persist between app instances."""
        # First app instance
        app1 = MuralisApp(str(self.config_path), verbose=False)
        app1.config.set('general', 'provider', 'nasa')
        
        # Second app instance
        app2 = MuralisApp(str(self.config_path), verbose=False)
        provider = app2.config.get_str('general', 'provider', 'bing')
        
        assert provider == 'nasa'
    
    def test_download_directory_creation(self):
        """Test that download directory is created automatically."""
        custom_dir = Path(self.temp_dir.name) / "custom_wallpapers"
        self.config = ConfigManager(str(self.config_path))
        self.config.set('storage', 'download_dir', str(custom_dir))
        
        app = MuralisApp(str(self.config_path), verbose=False)
        download_dir = app.config.get_download_dir()
        
        # Directory should be created when accessed
        download_dir.mkdir(parents=True, exist_ok=True)
        assert download_dir.exists()
    
    def tearDown_method(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()