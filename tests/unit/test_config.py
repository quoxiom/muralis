#!/usk/bin/env python3
"""Tests for configuration manager."""

import tempfile
from pathlib import Path
import json
from muralis.config import ConfigManager

class TestConfigManager:
    " ""Test ConfigManager class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "config.ini"
        self.config = ConfigManager(str(self.config_path))

    def test_create_default_config(self):
        """Test default config creation."""
        assert self.config_path.exists()
        
        # Test default values
        provider = self.config.get_str('general', 'provider', '')
        assert provider == 'bing'
        
        resolution = self.config.get_str('image', 'resolution', '')
        assert resolution == '3840x2160'

    def test_get_str(self):
        """Test getting string values."""
        value = self.config.get_str('general', 'non_existent', 'default')
        assert value == 'default'

    def test_get_bool(self):
        """Test getting boolean values."""
        self.config.set('general', 'test_true', 'true')
        self.config.set('general', 'test_false', 'false')
        
        assert self.config.get_bool('general', 'test_true') == True
        assert self.config.get_bool('general', 'test_false') == False


    def test_set_and_get(self):
        """Test setting and getting values."""
        self.config.set('test', 'key', 'value')
        value = self.config.get_str('test', 'key', '')
        assert value == 'value'

    def test_export_import_json(self):
        """Test exporting and importing JSON."""
        export_path = Path(self.temp_dir.name) / 'export.json'
        self.config.export_json(str(export_path))
        assert export_path.exists()
        
        # Create new config and import
        new_config = ConfigManager(str(Path(self.temp_dir.name) / 'new_config.ini'))
        new_config.import_json(str(export_path))

    def test_validation(self):
        """Test configuration validation."""
        # Test invalid resolution
        self.config.set('image', 'resolution', 'invalid')
        self.config.validate() # Should not raise exception

    def test_get_download_dir(self):
        """Test getting download directory."""
        download_dir = self.config.get_download_dir()
        assert isinstance(download_dir, Path)
        # Default is ~/Pictures/Muralis
        assert 'Muralis' in str(download_dir)

    def test_get_proxy_settings(self):
        """Test proxy settings."""
        self.config.set('networking', 'proxy_enabled', 'true')
        self.config.set('networking', 'proxy_url', 'http://proxy:1234@example.com:8080')
        
        proxy = self.config.get_proxy_settings()
        assert proxy is not None
        assert 'http' in proxy

    def test_migration(self):
        """Test config migration from old version (INI -> JSON)."""
        # Create an old-style INI config file.
        old_ini = Path(self.temp_dir.name) / 'legacy.ini'
        old_ini.write_text(
            "[general]\nprovider = nasa\n[image]\nresolution = 1920x1080\n",
            encoding='utf-8')
        # Load it through ConfigManager: it migrates to JSON and keeps values.
        migrated = ConfigManager(str(old_ini))
        assert migrated.get_str('general', 'provider') == 'nasa'
        assert migrated.get_str('image', 'resolution') == '1920x1080'
        # Defaults are filled in for the migrated config.
        assert migrated.get_str('image', 'effect_type') == 'none'

    def teardown_method(self):
        """Clean test fixtures."""
        self.temp_dir.cleanup()