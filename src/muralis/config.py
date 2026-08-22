"""Extended configuration management for Muralis with per-path singleton."""

import os
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import time

from muralis.i18n import t

class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigManager:
    """Configuration manager with per-file singleton pattern."""
    
    # Class-level cache: path -> instance
    _instances: Dict[str, 'ConfigManager'] = {}
    
    def __new__(cls, config_path: str):
        """Create or return cached instance for the given config path."""
        # Normalize the path to absolute path
        normalized_path = str(Path(config_path).expanduser().absolute())
        
        # Return existing instance if it exists
        if normalized_path in cls._instances:
            return cls._instances[normalized_path]
        
        # Create new instance and cache it
        instance = super().__new__(cls)
        cls._instances[normalized_path] = instance
        return instance
    
    def __init__(self, config_path: str):
        """Initialize configuration manager.

        The instance is cached per-path, but the config is re-read from disk
        on every construction so changes made by other code (e.g. the GUI
        Settings page) are picked up without restarting the application.
        """
        if not hasattr(self, 'config_path'):
            self.config_path = Path(config_path).expanduser().absolute()
            self.config = configparser.ConfigParser()
            self.load()
            return
        # Cached instance: refresh from disk so external edits take effect.
        self.load()
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached instances (useful for testing)."""
        cls._instances.clear()
    
    @classmethod
    def get_instance_count(cls) -> int:
        """Get number of cached instances (useful for debugging)."""
        return len(cls._instances)
    
    @classmethod
    def get_instance_paths(cls) -> List[str]:
        """Get all cached config paths (useful for debugging)."""
        return list(cls._instances.keys())
    
    def load(self):
        """Load configuration from file or create default."""
        if self.config_path.exists():
            self.config.read(self.config_path)
            self._migrate_config()
            self.validate()
        else:
            self.create_default()
    
    def _migrate_config(self):
        """Migrate old config to new format."""
        modified = False
        
        # Add missing sections
        for section, options in self.DEFAULT_CONFIG.items():
            if section not in self.config:
                self.config[section] = options
                modified = True
            else:
                # Add missing keys in existing sections
                for key, value in options.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value
                        modified = True
        
        if modified:
            self.save()
    
    def create_default(self):
        """Create default configuration file."""
        for section, options in self.DEFAULT_CONFIG.items():
            self.config[section] = options
        self.save()
        print(t("cli.config.created", path=self.config_path))
    
    def save(self):
        """Save configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            self.config.write(f)
    
    def validate(self):
        """Validate current configuration."""
        errors = []
        
        for key, rules in self.VALIDATION_RULES.items():
            section, option = key.split('.')
            value = self.get_str(section, option, "")
            
            if rules["type"] == "int":
                try:
                    int_val = int(value)
                    if "min" in rules and int_val < rules["min"]:
                        errors.append(f"{key}: {value} is below minimum {rules['min']}")
                    if "max" in rules and int_val > rules["max"]:
                        errors.append(f"{key}: {value} exceeds maximum {rules['max']}")
                except ValueError:
                    errors.append(f"{key}: '{value}' is not a valid integer")
            
            elif rules["type"] == "choice":
                if value not in rules["choices"]:
                    errors.append(f"{key}: '{value}' is not valid. Choose from: {', '.join(rules['choices'])}")
            
            elif rules["type"] == "resolution":
                if not self._validate_resolution(value):
                    errors.append(f"{key}: '{value}' is not a valid resolution (format: WxH, e.g., 1920x1080)")
            
            elif rules["type"] == "time":
                if not self._validate_time(value):
                    errors.append(f"{key}: '{value}' is not a valid time (format: HH:MM, 24-hour)")
        
        if errors:
            print(t("cli.warn.validation"))
            for error in errors:
                print(f"  • {error}")
            print(t("cli.warn.validation_continue"))
    
    def get_str(self, section: str, key: str, fallback: str = "") -> str:
        """Get string configuration value."""
        try:
            value = self.config.get(section, key, fallback=fallback)
            return value if value is not None else fallback
        except Exception:
            return fallback
    
    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        """Get boolean configuration value."""
        val = self.get_str(section, key, str(fallback).lower())
        return val.lower() in ['true', 'yes', '1', 'on']
    
    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        """Get integer configuration value."""
        val = self.get_str(section, key, str(fallback))
        try:
            return int(val)
        except (ValueError, TypeError):
            return fallback
    
    def get_float(self, section: str, key: str, fallback: float = 0.0) -> float:
        """Get float configuration value."""
        val = self.get_str(section, key, str(fallback))
        try:
            return float(val)
        except (ValueError, TypeError):
            return fallback
    
    def get_optional(self, section: str, key: str) -> Optional[str]:
        """Get optional string value (may return None)."""
        try:
            value = self.config.get(section, key, fallback=None)
            return value if value else None
        except Exception:
            return None
    
    def get_time(self, section: str, key: str) -> Optional[time]:
        """Get time configuration value."""
        time_str = self.get_optional(section, key)
        if time_str and self._validate_time(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return time(hour=hours, minute=minutes)
        return None
    
    def get_resolution(self, section: str, key: str) -> tuple:
        """Get resolution as (width, height) tuple."""
        res_str = self.get_str(section, key, "1920x1080")
        if 'x' in res_str:
            parts = res_str.split('x')
            if len(parts) == 2:
                try:
                    return (int(parts[0]), int(parts[1]))
                except ValueError:
                    pass
        return (1920, 1080)
    
    def set(self, section: str, key: str, value: str):
        """Set configuration value and save immediately."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = str(value)
        self.save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration as dictionary."""
        result = {}
        for section in self.config.sections():
            result[section] = dict(self.config.items(section))
        return result
    
    def get_download_dir(self) -> Path:
        """Get download directory path."""
        dir_path = self.get_str('storage', 'download_dir', '~/Pictures/Muralis')
        return Path(dir_path).expanduser()
    
    def get_log_file(self) -> Path:
        """Get log file path."""
        log_path = self.get_str('logging', 'log_file', '~/.local/share/muralis/muralis.log')
        return Path(log_path).expanduser()
    
    def get_proxy_settings(self) -> Optional[Dict]:
        """Get proxy settings for requests."""
        if not self.get_bool('networking', 'proxy_enabled', False):
            return None
        
        proxy_url = self.get_str('networking', 'proxy_url', '')
        if not proxy_url:
            return None
        
        username = self.get_str('networking', 'proxy_username', '')
        password = self.get_str('networking', 'proxy_password', '')
        
        if username and password:
            # Add authentication to proxy URL
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            proxy_url = f"{parsed.scheme}://{username}:{password}@{parsed.netloc}{parsed.path}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_update_time(self) -> str:
        """Get update time as string for scheduler."""
        return self.get_str('scheduling', 'update_time', '09:00')
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        key = self.get_optional('api_keys', f"{provider}_key")
        return key if key else None
    
    def set_api_key(self, provider: str, key: str):
        """Set API key for a provider."""
        self.set('api_keys', f"{provider}_key", key)
    
    def display(self):
        """Display current configuration in a readable format."""
        print("\n" + "=" * 60)
        print(t("cli.config.title"))
        print("=" * 60)
        print(t("cli.config.file", path=self.config_path))
        print("=" * 60)
        
        for section in self.config.sections():
            print(f"\n[{section}]")
            for key, value in self.config.items(section):
                # Mask sensitive values
                if 'key' in key or 'password' in key or 'secret' in key:
                    if value and len(value) > 8:
                        value = value[:4] + "..." + value[-4:]
                    elif value:
                        value = "***"
                
                # Format boolean values nicely
                if value.lower() in ['true', 'false']:
                    value = "✓" if value.lower() == 'true' else "✗"
                
                print(f"  {key:25} = {value}")
        
        print("\n" + "=" * 60)
    
    def export_json(self, filepath: str):
        """Export configuration to JSON file."""
        data = self.get_all()
        export_path = Path(filepath).expanduser()
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(t("cli.ok.exported", path=export_path))
    
    def import_json(self, filepath: str):
        """Import configuration from JSON file."""
        import_path = Path(filepath).expanduser()
        with open(import_path, 'r') as f:
            data = json.load(f)
        
        for section, options in data.items():
            if section not in self.config:
                self.config[section] = {}
            for key, value in options.items():
                self.config[section][key] = str(value)
        
        self.save()
        print(t("cli.ok.imported", path=import_path))
    
    def _validate_resolution(self, resolution: str) -> bool:
        """Validate resolution format (e.g., 1920x1080)."""
        import re
        pattern = r'^\d{3,4}x\d{3,4}$'
        return bool(re.match(pattern, resolution))
    
    def _validate_time(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        import re
        pattern = r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$'
        return bool(re.match(pattern, time_str))
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "general": {
            "provider": "bing",
            "auto_update": "true",
            "update_interval": "86400",
            "randomize_provider": "false",
            "fallback_provider": "bing",
            "timezone": "UTC",
            "offline_mode": "false",
            "network_timeout": "30",
            "retry_attempts": "3"
        },
        "image": {
            "resolution": "3840x2160",
            "apply_effects": "false",
            "effect_type": "none",
            "jpeg_quality": "90",
            "fit_mode": "zoom",
            "upscale_image": "false",
            "upscale_factor": "2",
            "maintain_aspect_ratio": "true",
            "image_format": "jpg",
            "color_profile": "auto",
            "watermark": "false",
            "watermark_position": "bottom-right",
            "watermark_text": "Muralis"
        },
        "storage": {
            "save_downloads": "true",
            "download_dir": "~/Pictures/Muralis",
            "max_files": "100",
            "max_days": "30",
            "keep_favorites": "false",
            "organize_by": "date",
            "create_subdirs": "true",
            "auto_tag": "true",
            "sync_to_cloud": "false",
            "sync_path": "",
            "compression_level": "6"
        },
        "scheduling": {
            "update_time": "09:00",
            "random_delay_minutes": "30",
            "update_on_boot": "false",
            "update_on_wake": "true",
            "minimum_interval_hours": "6",
            "skip_on_battery": "false",
            "only_on_wifi": "true"
        },
        "networking": {
            "proxy_enabled": "false",
            "proxy_url": "",
            "proxy_username": "",
            "proxy_password": "",
            "user_agent": "Muralis/1.0 (Qutility Suite)",
            "verify_ssl": "true",
            "download_timeout": "30",
            "max_redirects": "5"
        },
        "wallpaper_effects": {
            "daily_theme": "false",
            "morning_effect": "bright",
            "afternoon_effect": "vibrant",
            "evening_effect": "warm",
            "night_effect": "dark",
            "auto_adjust_brightness": "false",
            "auto_adjust_contrast": "false",
            "dominant_color": "false"
        },
        "logging": {
            "log_level": "INFO",
            "log_file": "~/.local/share/muralis/muralis.log",
            "log_rotation_days": "30",
            "debug_mode": "false",
            "log_http_traffic": "false"
        },
        "advanced": {
            "config_version": "2",
            "experimental_features": "false",
            "cache_enabled": "true",
            "cache_size_mb": "500",
            "parallel_downloads": "1",
            "max_connections": "5"
        },
        "api_keys": {
            "unsplash_key": "",
            "pexels_key": "563492ad6f91700001000001d6d5e3b5e5a14e8b8b9b9b9b9b9b9b",
            "flickr_key": "",
            "flickr_secret": ""
        }
    }
    
    # Validation rules
    VALIDATION_RULES = {
        "general.provider": {
            "type": "choice",
            "choices": ["bing", "nasa", "unsplash", "pexels", "wikimedia", "artinstitute", "wallhaven"],
            "message": "Provider must be one of: bing, nasa, unsplash, pexels, wikimedia, artinstitute, wallhaven"
        },
        "general.update_interval": {"type": "int", "min": 300, "max": 604800},
        "image.resolution": {"type": "resolution"},
        "image.jpeg_quality": {"type": "int", "min": 1, "max": 100},
        "image.effect_type": {
            "type": "choice",
            "choices": ["none", "blur", "darken", "grayscale", "vibrant", "vignette"]
        },
        "image.fit_mode": {
            "type": "choice",
            "choices": ["zoom", "fill", "fit", "stretch", "center"]
        },
        "image.image_format": {
            "type": "choice",
            "choices": ["jpg", "png", "webp"]
        },
        "storage.max_files": {"type": "int", "min": 0, "max": 10000},
        "storage.max_days": {"type": "int", "min": 0, "max": 365},
        "storage.compression_level": {"type": "int", "min": 0, "max": 9},
        "scheduling.update_time": {"type": "time"},
        "scheduling.random_delay_minutes": {"type": "int", "min": 0, "max": 120},
        "scheduling.minimum_interval_hours": {"type": "int", "min": 1, "max": 24},
        "logging.log_level": {
            "type": "choice",
            "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        },
        "advanced.cache_size_mb": {"type": "int", "min": 100, "max": 5000},
        "advanced.parallel_downloads": {"type": "int", "min": 1, "max": 5}
    }