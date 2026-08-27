"""Config-view helper for the GUI.

Historically the GUI read settings through a ConfigParser-style facade over the
JSON-backed configuration. ``ConfigManager`` now exposes that same surface
directly (``get``/``getboolean``/``getint``/``set``/``has_section``/``save``
and section subscripting), so this module is just a thin factory returning a
``ConfigManager`` for the app config path.
"""

from pathlib import Path
from typing import Optional


def config_view(config_path: Optional[str] = None):
    """Return a ``ConfigManager`` for the app config.

    Args:
        config_path: Path to the config file (default
            ~/.config/muralis/config.json).
    """
    from muralis.config import ConfigManager

    if config_path is None:
        config_path = str(Path.home() / ".config" / "muralis" / "config.json")
    return ConfigManager(config_path)
