"""Extended configuration management for Muralis with per-path singleton.

Settings are stored as JSON. Existing ``config.ini`` files are migrated to
``config.json`` on first load. The public get/set API is unchanged so callers
(CLI, GUI, scheduler) don't need to care about the underlying format.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from muralis.i18n import t
from muralis.providers.pexels import PexelsProvider
from muralis.providers import ALL_PROVIDERS


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigManager:
    """Configuration manager with per-file singleton pattern (JSON-backed)."""

    # Class-level cache: path -> instance
    _instances: Dict[str, 'ConfigManager'] = {}

    def __new__(cls, config_path: str):
        """Create or return cached instance for the given config path."""
        normalized_path = str(Path(config_path).expanduser().absolute())
        if normalized_path in cls._instances:
            return cls._instances[normalized_path]
        instance = super().__new__(cls)
        cls._instances[normalized_path] = instance
        return instance

    def __init__(self, config_path: str):
        """Initialize configuration manager.

        The instance is cached per-path, but the config is re-read from disk
        on every construction so external edits are picked up without restart.
        """
        if not hasattr(self, 'config_path'):
            self.config_path = Path(config_path).expanduser().absolute()
            self.config: Dict[str, Dict[str, str]] = {}
            self.load()
            return
        # Cached instance: refresh from disk so external edits take effect.
        self.load()

    # ------------------------------------------------------------------
    # Instance cache helpers
    # ------------------------------------------------------------------
    @classmethod
    def clear_cache(cls):
        cls._instances.clear()

    @classmethod
    def get_instance_count(cls) -> int:
        return len(cls._instances)

    @classmethod
    def get_instance_paths(cls) -> List[str]:
        return list(cls._instances.keys())

    # ------------------------------------------------------------------
    # Disk I/O
    # ------------------------------------------------------------------
    def load(self):
        """Load configuration from disk (migrating INI to JSON if needed)."""
        if self.config_path.exists():
            data = self._read_json(self.config_path)
            if data is not None:
                self.config = data
            else:
                self._migrate_from_ini(self.config_path)
            self._migrate_config()
            self.validate()
            return
        # Try a legacy INI at a sibling path (old default config.ini).
        legacy = self.config_path
        if self.config_path.suffix.lower() == '.json':
            legacy = self.config_path.with_suffix('.ini')
        if legacy.exists() and legacy != self.config_path:
            self._migrate_from_ini(legacy)
            self._migrate_config()
            self.validate()
            return
        self.create_default()

    def _read_json(self, path: Path) -> Optional[Dict[str, Dict[str, str]]]:
        """Read a JSON config dict, or None if the file isn't JSON."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, dict):
                return {str(s): {str(k): str(v) for k, v in opts.items()}
                        if isinstance(opts, dict) else {}
                        for s, opts in data.items()}
        except (OSError, json.JSONDecodeError, ValueError):
            return None
        return None

    def _write_json(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def _migrate_from_ini(self, ini_path: Path):
        """Migrate a legacy INI file into the JSON config dict."""
        import configparser
        parser = configparser.ConfigParser()
        parser.read(ini_path)
        self.config = {}
        for section in parser.sections():
            self.config[section] = dict(parser.items(section))
        # Only migrate config used by Muralis (skip foreign sections).
        allowed = set(self.DEFAULT_CONFIG.keys())
        self.config = {s: o for s, o in self.config.items()
                       if s in allowed or s == 'api_keys' or s == 'general'}
        # Keep api_keys from legacy even though it's not a DEFAULT section key.
        for section, opts in self.DEFAULT_CONFIG.items():
            self.config.setdefault(section, {})
            for key, value in opts.items():
                self.config[section].setdefault(key, value)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_json()
        # Remove the legacy INI now that it's migrated.
        try:
            ini_path.unlink()
        except OSError:
            pass

    def _migrate_config(self):
        """Add any missing default sections/keys to the current config."""
        modified = False
        for section, options in self.DEFAULT_CONFIG.items():
            if section not in self.config:
                self.config[section] = dict(options)
                modified = True
            else:
                for key, value in options.items():
                    if key not in self.config[section]:
                        self.config[section][key] = value
                        modified = True
        if modified:
            self._write_json()

    def create_default(self):
        for section, options in self.DEFAULT_CONFIG.items():
            self.config[section] = dict(options)
        self._write_json()
        print(t("cli.config.created", path=self.config_path))

    def save(self):
        """Persist the current config to disk."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_json()

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate(self):
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
                    choices = ", ".join(rules["choices"])
                    errors.append(f"{key}: '{value}' is not valid. Choose from: {choices}")
            elif rules["type"] == "resolution":
                if not self._validate_resolution(value):
                    errors.append(f"{key}: '{value}' is not a valid resolution (format: WxH)")
            elif rules["type"] == "time":
                if not self._validate_time(value):
                    errors.append(f"{key}: '{value}' is not a valid time (format: HH:MM)")
        if errors:
            print(t("cli.warn.validation"))
            for error in errors:
                print(f"  • {error}")
            print(t("cli.warn.validation_continue"))

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------
    def get_str(self, section: str, key: str, fallback: str = "") -> str:
        try:
            value = self.config.get(section, {}).get(key)
            return str(value) if value is not None else fallback
        except Exception:
            return fallback

    def get_bool(self, section: str, key: str, fallback: bool = False) -> bool:
        val = self.get_str(section, key, str(fallback).lower())
        return val.lower() in ['true', 'yes', '1', 'on']

    def get_int(self, section: str, key: str, fallback: int = 0) -> int:
        val = self.get_str(section, key, str(fallback))
        try:
            return int(val)
        except (ValueError, TypeError):
            return fallback

    def get_optional(self, section: str, key: str) -> Optional[str]:
        value = self.get_str(section, key)
        return value if value else None

    # ------------------------------------------------------------------
    # ConfigParser-compatible surface
    #
    # These are thin aliases so the GUI and legacy call sites can keep using
    # ConfigParser-style calls (``get``/``getboolean``/``getint``/``set`` and
    # section subscripting) without a separate facade. ConfigManager is the
    # single config source.
    # ------------------------------------------------------------------
    def get(self, section: str, key: str, fallback: str = "") -> str:
        """ConfigParser-style ``get`` (alias for ``get_str``)."""
        return self.get_str(section, key, fallback)

    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """ConfigParser-style ``getboolean`` (alias for ``get_bool``)."""
        return self.get_bool(section, key, fallback)

    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """ConfigParser-style ``getint`` (alias for ``get_int``)."""
        return self.get_int(section, key, fallback)

    def has_section(self, section: str) -> bool:
        """ConfigParser-style ``has_section``."""
        return section in self.config

    def setdefault_section(self, section: str) -> Dict[str, str]:
        """Return (creating if needed) the mutable option mapping for a section."""
        return self.config.setdefault(section, {})

    def __contains__(self, section: object) -> bool:
        return str(section) in self.config

    def __getitem__(self, section: str) -> Dict[str, str]:
        return self.config.setdefault(section, {})

    def __setitem__(self, section: str, options: Dict[str, Any]):
        current = self.config.setdefault(section, {})
        for key, value in options.items():
            current[str(key)] = str(value)

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------
    def set(self, section: str, key: str, value: str):
        self.config.setdefault(section, {})[key] = str(value)
        self.save()

    def get_all(self) -> Dict[str, Any]:
        return {section: dict(options) for section, options in self.config.items()}

    def get_download_dir(self) -> Path:
        return Path(self.get_str('storage', 'download_dir', '~/Pictures/Muralis')).expanduser()

    def get_log_file(self) -> Path:
        return Path(self.get_str('logging', 'log_file', '~/.local/share/muralis/muralis.log')).expanduser()

    def get_proxy_settings(self) -> Optional[Dict]:
        if not self.get_bool('networking', 'proxy_enabled', False):
            return None
        proxy_url = self.get_str('networking', 'proxy_url', '')
        if not proxy_url:
            return None
        username = self.get_str('networking', 'proxy_username', '')
        password = self.get_str('networking', 'proxy_password', '')
        if username and password:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            proxy_url = f"{parsed.scheme}://{username}:{password}@{parsed.netloc}{parsed.path}"
        return {'http': proxy_url, 'https': proxy_url}

    def get_update_time(self) -> str:
        return self.get_str('scheduling', 'update_time', '09:00')

    def get_api_key(self, provider: str) -> Optional[str]:
        key = self.get_optional('api_keys', f"{provider}_key")
        return key if key else None

    def set_api_key(self, provider: str, key: str):
        self.set('api_keys', f"{provider}_key", key)

    # ------------------------------------------------------------------
    # Display / import / export
    # ------------------------------------------------------------------
    def display(self):
        print("\n" + "=" * 60)
        print(t("cli.config.title"))
        print("=" * 60)
        print(t("cli.config.file", path=self.config_path))
        print("=" * 60)
        for section, options in self.config.items():
            print(f"\n[{section}]")
            for key, value in options.items():
                value = str(value)
                if 'key' in key or 'password' in key or 'secret' in key:
                    if len(value) > 8:
                        value = value[:4] + "..." + value[-4:]
                    elif value:
                        value = "***"
                if value.lower() in ['true', 'false']:
                    value = "✓" if value.lower() == 'true' else "✗"
                print(f"  {key:25} = {value}")
        print("\n" + "=" * 60)

    def export_json(self, filepath: str):
        data = self.get_all()
        export_path = Path(filepath).expanduser()
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(t("cli.ok.exported", path=export_path))

    def import_json(self, filepath: str):
        import_path = Path(filepath).expanduser()
        with open(import_path, 'r') as f:
            data = json.load(f)
        for section, options in data.items():
            opts = self.config.setdefault(str(section), {})
            for key, value in options.items():
                opts[str(key)] = str(value)
        self.save()
        print(t("cli.ok.imported", path=import_path))

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------
    def _validate_resolution(self, resolution: str) -> bool:
        import re
        return bool(re.match(r'^\d{3,4}x\d{3,4}$', resolution))

    def _validate_time(self, time_str: str) -> bool:
        import re
        return bool(re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', time_str))

    # ------------------------------------------------------------------
    # Defaults & validation rules
    # ------------------------------------------------------------------
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
            "user_agent": "Muralis/1.0",
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
        "notifications": {
            "enabled": "true"
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
            # Public demo key (rate-limited). Users should register their own at
            # https://www.pexels.com/api and override with `muralis --set-key pexels ...`.
            "pexels_key": PexelsProvider.API_KEY,
            "flickr_key": "",
            "flickr_secret": ""
        }
    }

    VALIDATION_RULES = {
        "general.provider": {"type": "choice", "choices": ALL_PROVIDERS},
        "general.update_interval": {"type": "int", "min": 300, "max": 604800},
        "image.resolution": {"type": "resolution"},
        "image.jpeg_quality": {"type": "int", "min": 1, "max": 100},
        "image.effect_type": {"type": "choice", "choices": ["none", "blur", "darken", "grayscale", "vibrant", "vignette"]},
        "image.fit_mode": {"type": "choice", "choices": ["zoom", "fill", "fit", "stretch", "center"]},
        "image.image_format": {"type": "choice", "choices": ["jpg", "png", "webp"]},
        "storage.max_files": {"type": "int", "min": 0, "max": 10000},
        "storage.max_days": {"type": "int", "min": 0, "max": 365},
        "storage.compression_level": {"type": "int", "min": 0, "max": 9},
        "scheduling.update_time": {"type": "time"},
        "scheduling.random_delay_minutes": {"type": "int", "min": 0, "max": 120},
        "scheduling.minimum_interval_hours": {"type": "int", "min": 1, "max": 24},
        "logging.log_level": {"type": "choice", "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
        "advanced.cache_size_mb": {"type": "int", "min": 100, "max": 5000},
        "advanced.parallel_downloads": {"type": "int", "min": 1, "max": 5}
    }
