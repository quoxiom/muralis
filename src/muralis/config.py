"""Configuration management for Muralis."""

import os
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "general": {
        "provider": "bing",
        "auto_update": "true",
        "update_interval": "86400",
        "randomize": "false"
    },
    "storage": {
        "save_downloads": "true",
        "download_dir": "~/Pictures/Muralis",
        "max_files": "100",
        "max_days": "30",
        "keep_favorites": "false"
    },
    "image": {
        "resolution": "1920x1080",
        "apply_effects": "false",
        "effect_type": "none",
        "jpeg_quality": "90",
        "fit_mode": "zoom"
    },
    "notifications": {
        "enabled": "true",
        "show_preview": "true",
        "sound": "false"
    },
    "advanced": {
        "retry_attempts": "3",
        "timeout_seconds": "30",
        "user_agent": "Muralis/1.0 (Qutility Suite)"
    }
}

class ConfigManager:
    """Manages Muralis configuration."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path).expanduser()
        self.config = configparser.ConfigParser()
        self.load()
    
    def load(self):
        """Load configuration from file or create default."""
        if self.config_path.exists():
            self.config.read(self.config_path)
            self._migrate_config()
        else:
            self.create_default()
    
    def _migrate_config(self):
        """Migrate old config to new format if needed."""
        modified = False
        for section, options in DEFAULT_CONFIG.items():
            if section not in self.config:
                self.config[section] = options
                modified = True
            else:
                for key, value in options.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value
                        modified = True
        
        if modified:
            self.save()
    
    def create_default(self):
        """Create default configuration file."""
        for section, options in DEFAULT_CONFIG.items():
            self.config[section] = options
        self.save()
        print(f"✓ Created default configuration at {self.config_path}")
    
    def save(self):
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            self.config.write(f)
    
    def get(self, section: str, key: str, fallback=None) -> str:
        """Get string configuration value."""
        try:
            return self.config.get(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    def get_bool(self, section: str, key: str, fallback=False) -> bool:
        """Get boolean configuration value."""
        val = self.get(section, key, str(fallback)).lower()
        return val in ['true', 'yes', '1', 'on']
    
    def get_int(self, section: str, key: str, fallback=0) -> int:
        """Get integer configuration value."""
        try:
            return int(self.get(section, key, fallback))
        except (ValueError, TypeError):
            return fallback
    
    def set(self, section: str, key: str, value: str):
        """Set configuration value."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
        self.save()
    
    def get_download_dir(self) -> Path:
        """Get download directory path."""
        dir_path = self.get('storage', 'download_dir', '~/Pictures/Muralis')
        return Path(dir_path).expanduser()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        result = {}
        for section in self.config.sections():
            result[section] = dict(self.config.items(section))
        return result
    
    def display(self):
        """Display current configuration."""
        print("\nCurrent Muralis Configuration:")
        print("=" * 40)
        for section in self.config.sections():
            print(f"\n[{section}]")
            for key, value in self.config.items(section):
                print(f"  {key} = {value}")
