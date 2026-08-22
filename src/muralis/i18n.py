"""Internationalization (i18n) support for Muralis.

Translations are stored in JSON language files. A language file is looked up in
two places, in order of precedence:

1. User directory:  ~/.config/muralis/i18n/<lang>.json   (editable, overrides)
2. Package data:    src/muralis/i18n/<lang>.json          (shipped defaults)

The active language is selected from the current culture (LANGUAGE, LC_ALL,
LC_MESSAGES, LANG environment variables, then the system locale). If no file
exists for the detected language, English is used as the fallback, and missing
keys inside a partial translation fall back to the English value.
"""

import json
import locale
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_LANG = "en"

# User-editable translations directory
USER_I18N_DIR = Path.home() / ".config" / "muralis" / "i18n"

# Built-in translations shipped with the package
BUILTIN_I18N_DIR = Path(__file__).parent / "i18n"


def normalize_lang(code: str) -> str:
    """Normalize a locale code to a 2-letter language code.

    'en_US.UTF-8' -> 'en', 'en-US' -> 'en', 'pt_BR' -> 'pt'
    """
    code = code.replace("-", "_").split(".")[0].strip()
    return code.split("_")[0].lower()


def detect_language() -> str:
    """Detect the user's language from the current culture."""
    # LANGUAGE can hold a colon-separated list of fallbacks
    language_env = os.environ.get("LANGUAGE", "")
    if language_env:
        first = language_env.split(":")[0].strip()
        if first:
            return normalize_lang(first)

    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var, "")
        if value:
            return normalize_lang(value)

    try:
        current, _ = locale.getdefaultlocale()
        if current:
            return normalize_lang(current)
    except Exception:
        pass

    return DEFAULT_LANG


def _load_file(path: Path) -> Dict[str, Any]:
    """Load a JSON language/theme file, returning {} on any error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge override into base (override wins)."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Translator:
    """Loads and looks up translations for the active language."""

    def __init__(self, lang: Optional[str] = None):
        self.lang = (lang or detect_language()).lower()
        self._strings: Dict[str, Any] = {}
        self._load()

    def _read_lang(self, lang: str) -> Dict[str, Any]:
        """Read a language file, user dir first, then builtin."""
        merged: Dict[str, Any] = {}
        builtin = BUILTIN_I18N_DIR / f"{lang}.json"
        if builtin.exists():
            merged.update(_load_file(builtin))
        user = USER_I18N_DIR / f"{lang}.json"
        if user.exists():
            merged = _deep_merge(merged, _load_file(user))
        return merged

    def _load(self) -> None:
        """Load translations, falling back to English for missing pieces."""
        english = self._read_lang(DEFAULT_LANG)
        if self.lang == DEFAULT_LANG:
            self._strings = english
            return

        localized = self._read_lang(self.lang)
        # English is the base; localized overrides where provided.
        self._strings = _deep_merge(english, localized)

    def t(self, key_name: str, **kwargs: Any) -> str:
        """Translate a dotted key (e.g. 'gui.nav.preview'), formatting kwargs."""
        value = self._strings
        for part in key_name.split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return key_name
        if not isinstance(value, str):
            return key_name
        if kwargs:
            try:
                value = value.format(**kwargs)
            except (KeyError, IndexError, ValueError):
                pass
        return value


_translator: Optional[Translator] = None
_lock = threading.Lock()


def get_translator() -> Translator:
    """Get the process-wide translator (initialized once)."""
    global _translator
    with _lock:
        if _translator is None:
            _translator = Translator()
        return _translator


def set_language(lang: str) -> None:
    """Force a language (mainly for tests)."""
    global _translator
    with _lock:
        _translator = Translator(lang)


def t(key_name: str, **kwargs: Any) -> str:
    """Translate a key using the process-wide translator."""
    return get_translator().t(key_name, **kwargs)
