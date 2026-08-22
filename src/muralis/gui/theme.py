"""Theme management for the Muralis GUI.

Themes are editable JSON palette files living in the user's config directory
(``~/.config/muralis/themes/<name>.json``). Built-in themes shipped with the
package are copied there on first run, so users can freely modify them or add
new ones. Each theme file contains a ``colors`` object whose keys are
substituted into the QSS template below.
"""

import json
import string
from pathlib import Path
from typing import Dict, List, Optional, Any

DEFAULT_THEME = "reasonix"

# User-editable themes directory
THEMES_DIR = Path.home() / ".config" / "muralis" / "themes"

# Built-in themes shipped with the package
BUILTIN_THEMES_DIR = Path(__file__).parent / "themes"


def load_json(path: Path) -> Dict[str, Any]:
    """Load a JSON file, returning {} on any error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


class ThemeManager:
    """Loads, lists and applies user-editable themes."""

    def __init__(self, app=None):
        self.app = app
        self._seed_builtins()

    # ------------------------------------------------------------------
    # Theme files
    # ------------------------------------------------------------------
    def _seed_builtins(self) -> None:
        """Copy built-in themes to the user directory on first run.

        Failures (e.g. a read-only config directory) are ignored: the app
        falls back to reading the built-in themes directly.
        """
        try:
            THEMES_DIR.mkdir(parents=True, exist_ok=True)
        except OSError:
            return
        for builtin in BUILTIN_THEMES_DIR.glob("*.json"):
            dest = THEMES_DIR / builtin.name
            if not dest.exists():
                try:
                    dest.write_text(
                        builtin.read_text(encoding="utf-8"), encoding="utf-8")
                except OSError:
                    pass

    def list_themes(self) -> List[str]:
        """List available theme ids (built-in + user themes), sorted."""
        names = {p.stem for p in BUILTIN_THEMES_DIR.glob("*.json")}
        names.update(p.stem for p in THEMES_DIR.glob("*.json"))
        return sorted(names) or [DEFAULT_THEME]

    def load_colors(self, theme_id: str) -> Dict[str, Any]:
        """Load a theme's colors (builtin as the base, user file overrides).

        A partial or stale user theme (e.g. missing new token keys) falls back
        to the built-in values for those keys, so the QSS always substitutes
        and the UI never collapses to the platform default.
        """
        builtin = load_json(BUILTIN_THEMES_DIR / f"{theme_id}.json")
        merged = dict(builtin.get("colors", {}))

        user_path = THEMES_DIR / f"{theme_id}.json"
        if user_path.exists():
            user = load_json(user_path)
            user_colors = user.get("colors")
            if isinstance(user_colors, dict):
                merged.update(user_colors)
        return merged

    def apply(self, theme_id: str) -> bool:
        """Apply a theme to the application; returns True on success."""
        if self.app is None:
            return False
        colors = self.load_colors(theme_id)
        if not colors:
            return False
        try:
            qss = QSS_TEMPLATE.substitute(colors)
            self.app.setStyleSheet(qss)
            return True
        except (KeyError, ValueError):
            return False


# ----------------------------------------------------------------------
# QSS template
# ----------------------------------------------------------------------
# Design tokens consumed by theme.json:
#   Surfaces (dark→light): window < panel < raised < menu < tooltip
#   Text (strong→muted):   text_strong, text, text_muted, text_disabled
#   Buttons:               btn_bg / btn_hover / btn_active / border_strong
QSS_TEMPLATE = string.Template("""
/* ================= Base ================= */
QMainWindow, QDialog, #centralWidget {
    background-color: ${window};
    color: ${text};
}

QWidget {
    color: ${text};
    font-size: 13px;
    font-family: "Segoe UI", "Cantarell", "Ubuntu", "Noto Sans", "DejaVu Sans", sans-serif;
}

QLabel { background: transparent; }

/* ================= Typography scale ================= */
/* page header (view name) */
#pageHeader { color: ${text_strong}; font-size: 20px; font-weight: 700; }
#pageComment { color: ${text_muted}; font-size: 13px; }

/* settings pane title / description */
#settingsPaneTitle { color: ${text_strong}; font-size: 17px; font-weight: 600; }
#settingsPaneDesc { color: ${text_muted}; font-size: 13px; }

/* row label + value + description */
#rowLabel { color: ${text_strong}; font-size: 13px; font-weight: 500; }
#rowDesc { color: ${text_muted}; font-size: 12px; }

/* settings nav item */
#settingsNavItem #navTitle { color: ${text_strong}; font-size: 13px; font-weight: 600; background: transparent; }
#settingsNavItem #navDesc { color: ${text_muted}; font-size: 11px; background: transparent; }
#settingsNavItem[selected="true"] #navTitle { color: ${text_strong}; }
#settingsNavItem[selected="true"] #navDesc { color: ${text_muted}; }

/* about */
#aboutTitle { color: ${text_strong}; font-size: 26px; font-weight: 700; }
#aboutLink { color: ${accent}; text-decoration: underline; }
#pageSubtitle { color: ${text_muted}; font-size: 12px; padding-bottom: 8px; }

/* brand */
#brand { color: ${text_strong}; font-size: 20px; font-weight: 700; padding: 2px 8px; }
#brandSubtitle { color: ${text_muted}; font-size: 11px; padding: 0 8px 14px 8px; }

/* ================= Surfaces ================= */
/* the app background and the main content area */
#contentStack { background-color: ${window}; }
#settingsStack { background-color: ${window}; }

/* panels that sit inside the app background */
#sidebar { background-color: ${panel}; border-right: 1px solid ${border}; }
#settingsNav { background-color: ${panel}; border-right: 1px solid ${border}; }

/* raised cards / preview / info */
#thumbFrame, #infoFrame, #aboutCard, #previewImage {
    background-color: ${card};
    border: 1px solid ${border};
    border-radius: 10px;
}
#thumbFrame:hover { background-color: ${card_hover}; border-color: ${accent}; }
#previewImage { background-color: ${preview_bg}; }
#thumbInfo { color: ${text_muted}; font-size: 11px; padding: 2px; }

/* ================= Buttons ================= */
QPushButton {
    background-color: ${btn_bg};
    color: ${text};
    border: 1px solid ${border_strong};
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 13px;
}
QPushButton:hover { background-color: ${btn_hover}; border-color: ${accent}; }
QPushButton:pressed { background-color: ${btn_active}; }
QPushButton:disabled { color: ${text_disabled}; background-color: ${btn_bg}; border-color: ${border}; }

QPushButton#primaryButton { background-color: ${accent}; color: ${accent_text}; border: 1px solid ${accent}; font-weight: 600; }
QPushButton#primaryButton:hover { background-color: ${accent_hover}; border-color: ${accent_hover}; }

/* toggle: off = btn, on = accent fill */
QPushButton#toggleButton { text-align: left; }
QPushButton#toggleButton:checked { background-color: ${accent}; border-color: ${accent}; color: ${accent_text}; font-weight: 600; }

/* segmented member */
#segGroup QPushButton { text-align: center; }
#segGroup QPushButton:checked { background-color: ${accent}; border-color: ${accent}; color: ${accent_text}; font-weight: 600; }

/* icon-only buttons */
#iconButton { background: transparent; border: 1px solid transparent; border-radius: 8px; padding: 4px; }
#iconButton:hover { background-color: ${btn_hover}; }

/* ================= Navigation ================= */
#navButton { background: transparent; color: ${text}; border: none; border-left: 2px solid transparent; border-radius: 8px; text-align: left; padding: 9px 12px; font-size: 13px; }
#navButton:hover { background-color: ${btn_hover}; color: ${text_strong}; }
#navButton:checked { background-color: ${nav_active_bg}; color: ${text_strong}; border-left: 2px solid ${accent}; font-weight: 600; }
#navButton:focus { outline: none; }
#navButton[collapsed="true"] { text-align: center; padding-left: 0; padding-right: 0; }

#settingsNavItem { border-radius: 8px; padding: 0; }
#settingsNavItem:hover { background-color: ${btn_hover}; }
#settingsNavItem[selected="true"] { background-color: ${nav_active_bg}; }

/* ================= Inputs ================= */
QSpinBox, QDoubleSpinBox {
    background-color: ${input_bg}; color: ${text};
    border: 1px solid ${input_border}; border-radius: 8px; padding: 5px 8px;
    selection-background-color: ${selection}; selection-color: ${text};
}
QSpinBox:focus, QDoubleSpinBox:focus { border: 1px solid ${focus_border}; }
QSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { background-color: transparent; border: none; width: 18px; }
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-bottom: 5px solid ${text_muted}; }
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image: none; border-left: 4px solid transparent; border-right: 4px solid transparent; border-top: 5px solid ${text_muted}; }

/* ================= Scroll areas ================= */
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: ${window}; width: 12px; margin: 0; }
QScrollBar::handle:vertical { background: ${scroll_handle}; min-height: 30px; border-radius: 6px; margin: 2px; }
QScrollBar::handle:vertical:hover { background: ${scroll_handle_hover}; }
QScrollBar:horizontal { background: ${window}; height: 12px; margin: 0; }
QScrollBar::handle:horizontal { background: ${scroll_handle}; min-width: 30px; border-radius: 6px; margin: 2px; }
QScrollBar::handle:horizontal:hover { background: ${scroll_handle_hover}; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: none; }

/* ================= Status bar ================= */
QStatusBar { background-color: ${status_bg}; color: ${status_text}; font-size: 12px; }
QStatusBar::item { border: none; }
#statusInfo { color: ${status_text}; font-size: 12px; padding: 2px 8px; }

/* ================= Menus ================= */
QMenu { background-color: ${menu_bg}; color: ${text}; border: 1px solid ${border}; padding: 4px; border-radius: 6px; }
QMenu::item { padding: 6px 24px; border-radius: 6px; }
QMenu::item:selected { background-color: ${menu_hover}; color: ${text_strong}; }
QMenu::item:disabled { color: ${text_disabled}; }
QMenu::separator { height: 1px; background: ${border}; margin: 4px 8px; }

/* ================= Tooltips ================= */
QToolTip {
    background-color: ${tooltip_bg};
    color: ${tooltip_text};
    border: 1px solid ${border};
    border-radius: 6px;
    padding: 6px;
    font-size: 12px;
}

/* ================= Message boxes ================= */
QMessageBox { background-color: ${menu_bg}; }
QMessageBox QLabel { color: ${text}; }
""")


