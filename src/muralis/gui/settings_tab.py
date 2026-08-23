"""Settings tab for Muralis GUI.

Reasonix-style settings explorer: a left navigation list of categories (each
with a title and short description) and a content pane on the right, where
every row has its label on the left and the control on the right. Finite
options use segmented selection buttons, on/off options use toggle buttons.
"""

import configparser
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, QSignalBlocker, Signal
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QButtonGroup, QSpinBox,
    QScrollArea, QFrame, QLabel, QStackedWidget, QSizePolicy, QApplication
)

from muralis.i18n import t
from .theme import DEFAULT_THEME

PROVIDERS: List[Tuple[str, str]] = [
    ("bing", "gui.provider.bing"),
    ("nasa", "gui.provider.nasa"),
    ("pexels", "gui.provider.pexels"),
    ("wikimedia", "gui.provider.wikimedia"),
    ("artinstitute", "gui.provider.artinstitute"),
    ("wallhaven", "gui.provider.wallhaven"),
    ("unsplash", "gui.provider.unsplash"),
]

RESOLUTIONS = [
    ("FHD", "1920x1080"),
    ("2K", "2560x1440"),
    ("2.5K", "3840x2160"),
    ("4K", "4096x2160"),
    ("8K", "7680x4320"),
]
EFFECTS = ["none", "blur", "darken", "grayscale", "vibrant", "vignette"]

# Category order: key -> (title key, description key)
CATEGORIES = [
    ("general", "gui.settings.general", "gui.settings.desc.general"),
    ("image", "gui.settings.image", "gui.settings.desc.image"),
    ("storage", "gui.settings.storage", "gui.settings.desc.storage"),
    ("appearance", "gui.settings.appearance", "gui.settings.desc.appearance"),
]


class _NavItem(QWidget):
    """A settings-navigation row: title on top, muted description below."""

    clicked = Signal()

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsNavItem")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(1)

        title_label = QLabel(title)
        title_label.setObjectName("navTitle")
        layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("navDesc")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

    def set_selected(self, selected: bool):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and \
                self.rect().contains(event.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter,
                           Qt.Key.Key_Space):
            self.clicked.emit()
        super().keyPressEvent(event)


class SettingsTab(QWidget):
    """Settings tab for configuring Muralis."""

    def __init__(self, theme_manager=None,
                 on_theme_change: Optional[Callable[[str], None]] = None,
                 on_settings_changed: Optional[Callable[[], None]] = None,
                 parent=None):
        """Initialize the settings tab.

        Args:
            theme_manager: ThemeManager used to list available themes
            on_theme_change: Called with the new theme id when changed
            on_settings_changed: Called after settings are saved or reset
            parent: Parent widget
        """
        super().__init__(parent)

        self.config_path = Path.home() / ".config/muralis/config.ini"
        self.theme_manager = theme_manager
        self.on_theme_change = on_theme_change
        self.on_settings_changed = on_settings_changed

        self.nav_items: Dict[str, _NavItem] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._build_nav(body)
        self._build_panes(body)

        root.addLayout(body, 1)
        self._build_action_buttons()

        # Load current settings
        self.load_settings()
        self._show_category("general")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_nav(self, body: QHBoxLayout):
        """Left settings navigation list."""
        nav = QFrame()
        nav.setObjectName("settingsNav")
        nav.setFixedWidth(240)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(8, 12, 8, 12)
        nav_layout.setSpacing(2)

        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        nav_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        nav_content = QWidget()
        nav_content_layout = QVBoxLayout(nav_content)
        nav_content_layout.setContentsMargins(0, 0, 0, 0)
        nav_content_layout.setSpacing(2)

        for key, title_key, desc_key in CATEGORIES:
            item = _NavItem(t(title_key), t(desc_key), nav_content)
            item.clicked.connect(lambda k=key: self._show_category(k))
            self.nav_items[key] = item
            nav_content_layout.addWidget(item)

        nav_content_layout.addStretch()
        nav_scroll.setWidget(nav_content)
        nav_layout.addWidget(nav_scroll)

        body.addWidget(nav)

    def _build_panes(self, body: QHBoxLayout):
        """Right content panes (one per category), scrollable."""
        self.stack = QStackedWidget()
        self.stack.setObjectName("settingsStack")

        self.panes: Dict[str, QWidget] = {}
        for key, title_key, desc_key in CATEGORIES:
            pane = self._build_pane(key, t(title_key), t(desc_key))
            self.panes[key] = pane
            self.stack.addWidget(pane)

        body.addWidget(self.stack, 1)

    def _build_pane(self, key: str, title: str, description: str) -> QWidget:
        """A category pane: title, description, then setting rows.

        Wrapped in a scroll area so scrollbars appear when the content
        exceeds the available height.
        """
        content = QWidget()
        pane_layout = QVBoxLayout(content)
        pane_layout.setContentsMargins(20, 14, 20, 14)
        pane_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setObjectName("settingsPaneTitle")
        pane_layout.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("settingsPaneDesc")
        desc_label.setWordWrap(True)
        pane_layout.addWidget(desc_label)

        pane_layout.addSpacing(10)

        if key == "general":
            self._build_general_rows(pane_layout)
        elif key == "image":
            self._build_image_rows(pane_layout)
        elif key == "storage":
            self._build_storage_rows(pane_layout)
        else:
            self._build_appearance_rows(pane_layout)

        pane_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setWidget(content)
        return scroll

    # ------------------------------------------------------------------
    # Row helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _row(layout: QVBoxLayout, label: str, control: QWidget,
             description: str = ""):
        """A setting row: label (and description) left, control right.

        The label/description block and the control are top-aligned so the
        description sits directly under the setting name even when the control
        is taller (e.g. multi-line button grids).
        """
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 8, 0, 8)
        row_layout.setSpacing(16)
        # Align both columns to the top so the description hugs the label.
        row_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        left = QVBoxLayout()
        left.setSpacing(0)
        left.setContentsMargins(0, 0, 0, 0)
        left.setAlignment(Qt.AlignmentFlag.AlignTop)

        label_widget = QLabel(label)
        label_widget.setObjectName("rowLabel")
        left.addWidget(label_widget)

        if description:
            desc_widget = QLabel(description)
            desc_widget.setObjectName("rowDesc")
            desc_widget.setWordWrap(True)
            desc_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
            left.addWidget(desc_widget)

        row_layout.addLayout(left, 1)
        row_layout.addWidget(control, 0, Qt.AlignmentFlag.AlignTop)
        layout.addWidget(row)

    def _segmented(self, labels: List[str], cols: int,
                   values: Optional[List[str]] = None,
                   tooltips: Optional[List[str]] = None) -> Tuple[QWidget, List[QPushButton]]:
        """A grid of exclusive selection buttons.

        Each button carries its value in a 'value' property; labels may differ
        from values (e.g. localized provider names mapping to config keys).
        An optional ``tooltips`` list sets each button's hover tooltip.
        """
        if values is None:
            values = list(labels)
        widget = QWidget()
        widget.setObjectName("segGroup")
        grid = QGridLayout(widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(6)

        group = QButtonGroup(widget)
        group.setExclusive(True)

        buttons: List[QPushButton] = []
        for index, label in enumerate(labels):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setProperty("value", values[index])
            if tooltips:
                button.setToolTip(tooltips[index])
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setSizePolicy(
                QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
            group.addButton(button)
            buttons.append(button)
            grid.addWidget(button, index // cols, index % cols)
            # Center each button so the group reads as one aligned block.
            grid.setAlignment(button, Qt.AlignmentFlag.AlignHCenter)

        # Make every button in the group the same width, sized to the widest
        # label in its BOLD form (buttons render bold when selected), so the
        # checked text is never truncated.
        bold = QFont(QApplication.font())
        bold.setBold(True)
        fm = QFontMetrics(bold)
        max_w = max(fm.horizontalAdvance(b.text()) for b in buttons)
        max_w += 40  # comfortable padding; check/bold metrics can drift
        for b in buttons:
            b.setFixedWidth(max_w)
        return widget, buttons

    @staticmethod
    def _toggle_button(text: str, checked: bool = False) -> QPushButton:
        """A checkable push button styled as an on/off toggle.

        Sized for the BOLD (selected) label so the text is never truncated
        once the button is checked.
        """
        button = QPushButton(text)
        button.setObjectName("toggleButton")
        button.setCheckable(True)
        button.setChecked(checked)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        # Use the application font (which reflects the applied theme QSS font)
        # so the bold checked label fits once the stylesheet is active.
        bold = QFont(QApplication.font())
        bold.setBold(True)
        fm = QFontMetrics(bold)
        width = fm.horizontalAdvance(text) + 40
        button.setFixedWidth(width)
        return button

    def _spin(self, minimum: int, maximum: int, special_text: str):
        spin = QSpinBox()
        spin.setRange(minimum, maximum)
        spin.setSpecialValueText(special_text)
        spin.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        return spin

    # ------------------------------------------------------------------
    # Category rows
    # ------------------------------------------------------------------
    def _build_general_rows(self, layout: QVBoxLayout):
        provider_widget, self.provider_buttons = self._segmented(
            [t(key) for _, key in PROVIDERS], cols=4,
            values=[key for key, _ in PROVIDERS])
        # Disable providers that need an API key but aren't configured.
        enabled = {key: self._provider_configured(key) for key, _ in PROVIDERS}
        for button, (key, _) in zip(self.provider_buttons, PROVIDERS):
            if not enabled[key]:
                button.setEnabled(False)
        self._row(layout, t("gui.settings.provider"), provider_widget,
                  description=t("gui.settings.desc.provider"))
        layout.addSpacing(6)

        self.auto_update_toggle = self._toggle_button(t("gui.settings.auto_update"))
        self._row(layout, t("gui.settings.auto_update"),
                  self.auto_update_toggle,
                  description=t("gui.settings.desc.auto_update"))

        self.randomize_toggle = self._toggle_button(t("gui.settings.randomize"))
        self._row(layout, t("gui.settings.randomize"), self.randomize_toggle,
                  description=t("gui.settings.desc.randomize"))

    def _build_image_rows(self, layout: QVBoxLayout):
        resolution_labels = [label for label, _ in RESOLUTIONS]
        resolution_values = [res for _, res in RESOLUTIONS]
        resolution_widget, self.resolution_buttons = self._segmented(
            resolution_labels, cols=3,
            values=resolution_values,
            tooltips=resolution_values)
        self._row(layout, t("gui.settings.resolution"), resolution_widget,
                  description=t("gui.settings.desc.resolution"))
        layout.addSpacing(6)

        self.effects_toggle = self._toggle_button(t("gui.settings.effects"))
        self._row(layout, t("gui.settings.effects"), self.effects_toggle,
                  description=t("gui.settings.desc.effects"))

        effect_widget, self.effect_buttons = self._segmented(EFFECTS, cols=3)
        self.effect_widget = effect_widget
        self._row(layout, t("gui.settings.effect_type"), effect_widget,
                  description=t("gui.settings.desc.effect_type"))
        layout.addSpacing(6)

        self.effects_toggle.toggled.connect(self._update_effect_state)

    def _build_storage_rows(self, layout: QVBoxLayout):
        self.save_downloads_toggle = self._toggle_button(
            t("gui.settings.save_downloads"))
        self._row(layout, t("gui.settings.save_downloads"),
                  self.save_downloads_toggle,
                  description=t("gui.settings.desc.save_downloads"))

        self.max_files_spin = self._spin(0, 10000, t("gui.settings.unlimited"))
        self._row(layout, t("gui.settings.max_files"), self.max_files_spin,
                  description=t("gui.settings.desc.max_files"))

        self.max_days_spin = self._spin(0, 365, t("gui.settings.unlimited"))
        self._row(layout, t("gui.settings.max_days"), self.max_days_spin,
                  description=t("gui.settings.desc.max_days"))

    def _build_appearance_rows(self, layout: QVBoxLayout):
        theme_names = self._available_themes()
        theme_widget, self.theme_buttons = self._segmented(
            theme_names, cols=3, values=theme_names)
        for button, theme_id in zip(self.theme_buttons, theme_names):
            button.toggled.connect(
                lambda checked, tid=theme_id: self._on_theme_clicked(checked, tid))
        self._row(layout, t("gui.settings.theme"), theme_widget,
                  description=t("gui.settings.desc.theme"))
        layout.addSpacing(6)

    def _build_action_buttons(self):
        """Create Apply/Restore buttons (placed top-right in the page header)."""
        self.apply_btn = QPushButton(t("gui.settings.apply"))
        self.apply_btn.setObjectName("primaryButton")
        self.apply_btn.clicked.connect(self.save_settings)

        self.reset_btn = QPushButton(t("gui.settings.reset"))
        self.reset_btn.clicked.connect(self.reset_settings)

    def action_buttons(self) -> list:
        """Action buttons for the page header row (Apply, Restore, top-right)."""
        return [self.apply_btn, self.reset_btn]

    # ------------------------------------------------------------------
    # Navigation / helpers
    # ------------------------------------------------------------------
    def _show_category(self, key: str):
        """Select a settings category (nav highlight + content pane)."""
        for category_key, item in self.nav_items.items():
            item.set_selected(category_key == key)
        pane = self.panes.get(key)
        if pane is not None:
            self.stack.setCurrentWidget(pane)

    def _provider_configured(self, provider: str) -> bool:
        """True if the provider can be used (has whatever API key it needs)."""
        try:
            from muralis.config import ConfigManager
            from muralis.utils.api_keys import APIKeyManager
            config = ConfigManager(str(self.config_path))
            return APIKeyManager(config).is_configured(provider)
        except Exception:
            return False

    def _available_themes(self) -> List[str]:
        if self.theme_manager is None:
            return [DEFAULT_THEME]
        return [
            theme_id for theme_id in self.theme_manager.list_themes()
            if self.theme_manager.load_colors(theme_id)
        ]

    def _check_value(self, buttons: List[QPushButton], value: str,
                     fallback: Optional[str] = None) -> None:
        """Check the button whose value property equals value (no signals).

        If value is stale (not present in the buttons), the fallback is
        checked instead so a selection always exists.
        """
        for button in buttons:
            if button.property("value") == value:
                with QSignalBlocker(button):
                    button.setChecked(True)
                return
        if fallback is not None:
            for button in buttons:
                if button.property("value") == fallback:
                    with QSignalBlocker(button):
                        button.setChecked(True)
                    return

    @staticmethod
    def _set_toggle(button: QPushButton, value: bool) -> None:
        """Set a toggle without firing its toggled signal."""
        with QSignalBlocker(button):
            button.setChecked(value)

    def _checked_value(self, buttons: List[QPushButton], fallback: str) -> str:
        """Return the value property of the checked button."""
        for button in buttons:
            if button.isChecked():
                return button.property("value") or fallback
        return fallback

    def _update_effect_state(self, enabled: bool):
        """Enable/disable the effect type selector."""
        self.effect_widget.setEnabled(enabled)
        for button in self.effect_buttons:
            button.setEnabled(enabled)

    def _on_theme_clicked(self, checked: bool, theme_id: str):
        if checked and self.on_theme_change:
            self.on_theme_change(theme_id)

    # ------------------------------------------------------------------
    # Persistence    # ------------------------------------------------------------------
    def _load_raw(self) -> configparser.ConfigParser:
        config = configparser.ConfigParser()
        if self.config_path.exists():
            config.read(self.config_path)
        return config

    def load_settings(self):
        """Load settings from config file (defaults used when absent)."""
        config = self._load_raw()

        # Defaults first, so a missing/deleted config resets the UI
        self._check_value(self.provider_buttons, 'bing')
        self._check_value(self.resolution_buttons, '3840x2160')
        self._check_value(self.effect_buttons, 'none')
        self._check_value(self.theme_buttons, DEFAULT_THEME)
        self._set_toggle(self.auto_update_toggle, True)
        self._set_toggle(self.randomize_toggle, False)
        self._set_toggle(self.effects_toggle, False)
        self._set_toggle(self.save_downloads_toggle, True)
        self.max_files_spin.setValue(100)
        self.max_days_spin.setValue(30)

        # Overrides from the config file (with fallbacks for stale values)
        if config.has_section('general'):
            self._check_value(
                self.provider_buttons,
                config.get('general', 'provider', fallback='bing'),
                fallback='bing')
            self._set_toggle(self.auto_update_toggle,
                             config.getboolean('general', 'auto_update', fallback=True))
            self._set_toggle(self.randomize_toggle,
                             config.getboolean('general', 'randomize_provider', fallback=False))

        # Image
        if config.has_section('image'):
            self._check_value(
                self.resolution_buttons,
                config.get('image', 'resolution', fallback='3840x2160'),
                fallback='3840x2160')
            self._set_toggle(self.effects_toggle,
                             config.getboolean('image', 'apply_effects', fallback=False))
            self._check_value(
                self.effect_buttons,
                config.get('image', 'effect_type', fallback='none'),
                fallback='none')

        # Storage
        if config.has_section('storage'):
            self._set_toggle(self.save_downloads_toggle,
                             config.getboolean('storage', 'save_downloads', fallback=True))
            self.max_files_spin.setValue(
                config.getint('storage', 'max_files', fallback=100))
            self.max_days_spin.setValue(
                config.getint('storage', 'max_days', fallback=30))

        # Appearance
        if config.has_section('gui'):
            self._check_value(
                self.theme_buttons,
                config.get('gui', 'theme', fallback=DEFAULT_THEME),
                fallback=DEFAULT_THEME)

        self._update_effect_state(self.effects_toggle.isChecked())

    def save_settings(self):
        """Save settings to config file."""
        config = self._load_raw()

        # General section
        if 'general' not in config:
            config['general'] = {}
        config['general']['provider'] = self._checked_value(
            self.provider_buttons, 'bing')
        config['general']['auto_update'] = str(
            self.auto_update_toggle.isChecked()).lower()
        config['general']['randomize_provider'] = str(
            self.randomize_toggle.isChecked()).lower()

        # Image section
        if 'image' not in config:
            config['image'] = {}
        config['image']['resolution'] = self._checked_value(
            self.resolution_buttons, '3840x2160')
        config['image']['apply_effects'] = str(
            self.effects_toggle.isChecked()).lower()
        config['image']['effect_type'] = self._checked_value(
            self.effect_buttons, 'none')

        # Storage section
        if 'storage' not in config:
            config['storage'] = {}
        config['storage']['save_downloads'] = str(
            self.save_downloads_toggle.isChecked()).lower()
        config['storage']['max_files'] = str(self.max_files_spin.value())
        config['storage']['max_days'] = str(self.max_days_spin.value())

        # Appearance section
        if 'gui' not in config:
            config['gui'] = {}
        config['gui']['theme'] = self._checked_value(
            self.theme_buttons, DEFAULT_THEME)

        # Save config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            config.write(f)

        if self.on_settings_changed:
            self.on_settings_changed()

        from .dialogs import info, confirm
        info(self, t("gui.settings.success_title"), t("gui.settings.saved"))

    def reset_settings(self):
        """Reset settings to defaults."""
        from .dialogs import confirm, info
        if not confirm(self, t("gui.settings.reset_title"),
                       t("gui.settings.reset_confirm")):
            return
        if self.config_path.exists():
            self.config_path.unlink()
        self.load_settings()
        # Re-apply the appearance settings that were just reset
        if self.on_theme_change:
            self.on_theme_change(
                self._checked_value(self.theme_buttons, DEFAULT_THEME))
        if self.on_settings_changed:
            self.on_settings_changed()
        info(self, t("gui.settings.success_title"),
             t("gui.settings.reset_done"))
