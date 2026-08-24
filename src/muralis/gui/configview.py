"""Shared ConfigParser-compatible view over the JSON-backed ConfigManager.

The GUI historically read settings through raw ``configparser`` calls on
``config.ini`` (``.get`` / ``.getboolean`` / ``.getint`` / ``has_section`` /
``config[section][key] = ...`` / ``config.write``). After the INI -> JSON
migration this module exposes those same calls over the JSON value store so
the GUI call sites keep working unchanged.
"""

from pathlib import Path
from typing import Any, Dict, Optional


class ConfigView:
    """Minimal ConfigParser-like facade over a ConfigManager instance."""

    def __init__(self, config_path: str):
        from muralis.config import ConfigManager
        self._cm = ConfigManager(config_path)

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------
    def get(self, section: str, key: str, fallback: str = "") -> str:
        return self._cm.get_str(section, key, fallback)

    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        return self._cm.get_bool(section, key, fallback)

    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        return self._cm.get_int(section, key, fallback)

    def has_section(self, section: str) -> bool:
        return section in self._cm.config

    def __contains__(self, section: object) -> bool:
        return str(section) in self._cm.config

    # ------------------------------------------------------------------
    # Writes (mirror the ConfigParser section/option subscript API)
    # ------------------------------------------------------------------
    def set(self, section: str, key: str, value: str) -> None:
        self._cm.set(section, key, value)

    def __setitem__(self, section: str, options: Dict[str, Any]):
        current = self._cm.config.setdefault(section, {})
        for key, value in options.items():
            current[str(key)] = str(value)

    def __getitem__(self, section: str) -> Dict[str, str]:
        return self._cm.config.setdefault(section, {})

    def setdefault_section(self, section: str) -> Dict[str, str]:
        return self._cm.config.setdefault(section, {})

    def save(self) -> None:
        self._cm.save()


def config_view(config_path: Optional[str] = None) -> ConfigView:
    """Create a ConfigView for the app config (default ~/.config/muralis/config.json)."""
    if config_path is None:
        config_path = str(Path.home() / ".config" / "muralis" / "config.json")
    return ConfigView(config_path)
