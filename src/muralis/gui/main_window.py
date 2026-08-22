"""Main window for Muralis GUI.

Modern Reasonix-style layout: a collapsible drawer (sidebar) with greyscale
icons, a themed status bar with live info, and no menu bar — all settings live
in the Settings page.
"""

import configparser
from pathlib import Path
from datetime import datetime, timedelta

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QStatusBar,
    QFrame, QButtonGroup
)
from PySide6.QtCore import Qt, QTimer, QSize

from muralis import __version__
from muralis.i18n import t

from .settings_tab import SettingsTab
from .history_tab import HistoryTab
from .preview_widget import PreviewWidget
from .tray_icon import TrayIcon
from .theme import ThemeManager, DEFAULT_THEME
from .icons import app_icon, make_icon, render_pixmap, ICON_IDLE

CONFIG_PATH = Path.home() / ".config" / "muralis" / "config.ini"
WALLPAPER_DIR = Path.home() / "Pictures" / "Muralis"


def _safe_mtime(path: Path) -> float:
    """Modified time, tolerating files that vanish between glob and stat."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0

# Navigation entries: (key, icon name, translation key, page comment key)
NAV_ITEMS = [
    ("preview", "preview", "gui.nav.preview", "gui.page.preview_subtitle"),
    ("history", "history", "gui.nav.history", "gui.page.history_subtitle"),
    ("settings", "settings", "gui.nav.settings", "gui.page.settings_subtitle"),
    ("about", "about", "gui.nav.about", ""),
]

SIDEBAR_WIDTH_EXPANDED = 220
SIDEBAR_WIDTH_COLLAPSED = 56


class MainWindow(QMainWindow):
    """Main application window for Muralis."""

    def __init__(self, parent=None):
        """Initialize the main window."""
        super().__init__(parent)

        self.setWindowTitle("Muralis")
        self.setWindowIcon(app_icon())
        self.setMinimumSize(1000, 700)
        self.resize(1150, 780)

        # Theme manager (applies the stored theme, seeded with defaults)
        self.theme_manager = ThemeManager(self)

        # Central widget
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Left navigation drawer (collapsible)
        self._sidebar_collapsed = False
        self._build_sidebar(root_layout)

        # Content stack (pages switched by the drawer)
        self.stack = QStackedWidget()
        self.stack.setObjectName("contentStack")
        root_layout.addWidget(self.stack, 1)

        # Build pages
        self.preview_widget = PreviewWidget(
            refresh_callback=self._refresh_wallpaper,
            parent=self
        )
        self.history_tab = HistoryTab(
            refresh_callback=self._refresh_wallpaper,
            wallpaper_applied_callback=self._load_current_wallpaper,
            parent=self
        )
        self.settings_tab = SettingsTab(
            theme_manager=self.theme_manager,
            on_theme_change=self._set_theme,
            on_tray_toggle=self.toggle_tray_icon,
            on_quit=self._request_quit,
            on_settings_changed=self._update_status_bar,
            parent=self
        )
        self.about_page = self._build_about_page()

        self.pages = [
            ("preview", self._make_page(
                t("gui.nav.preview"), t("gui.page.preview_subtitle"),
                self.preview_widget)),
            ("history", self._make_page(
                t("gui.nav.history"), t("gui.page.history_subtitle"),
                self.history_tab)),
            ("settings", self._make_page(
                t("gui.nav.settings"), t("gui.page.settings_subtitle"),
                self.settings_tab)),
            ("about", self._make_page(
                t("gui.nav.about"), "", self.about_page)),
        ]
        for _, page in self.pages:
            self.stack.addWidget(page)

        # Create status bar with live info
        self._build_status_bar()

        # Create system tray icon
        self.tray_icon = TrayIcon(refresh_callback=self._refresh_wallpaper)

        # Apply the stored theme (after widgets exist)
        self._apply_stored_theme()

        # Tray visibility from config
        self.tray_icon.setVisible(
            self._read_config().getboolean("gui", "show_tray", fallback=True))

        # Setup auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh_preview)
        self.refresh_timer.start(60000)  # Refresh every minute

        # Start on the preview page
        self._show_page("preview")

        # Load initial data
        self._load_current_wallpaper()
        self._update_status_bar()

    # ------------------------------------------------------------------
    # Layout construction
    # ------------------------------------------------------------------
    def _build_sidebar(self, root_layout: QHBoxLayout):
        """Build the collapsible left-hand navigation drawer."""
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(SIDEBAR_WIDTH_EXPANDED)

        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(12, 14, 12, 12)
        side_layout.setSpacing(4)

        # Top row: drawer toggle + app name
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self.drawer_btn = QPushButton()
        self.drawer_btn.setObjectName("iconButton")
        self.drawer_btn.setIcon(make_icon("drawer", ICON_IDLE, 20))
        self.drawer_btn.setIconSize(QSize(20, 20))
        self.drawer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.drawer_btn.setToolTip(t("gui.nav.collapse"))
        self.drawer_btn.clicked.connect(self._toggle_sidebar)
        top_row.addWidget(self.drawer_btn)

        self.brand_label = QLabel(t("gui.nav.brand"))
        self.brand_label.setObjectName("brand")
        top_row.addWidget(self.brand_label)

        top_row.addStretch()
        side_layout.addLayout(top_row)

        self.brand_subtitle = QLabel(t("gui.nav.brand_subtitle"))
        self.brand_subtitle.setObjectName("brandSubtitle")
        self.brand_subtitle.setWordWrap(True)
        side_layout.addWidget(self.brand_subtitle)

        side_layout.addSpacing(12)

        # Navigation buttons (mutually exclusive)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.nav_buttons = {}
        self.nav_meta = {}  # key -> (icon name, label)
        for key, icon_name, label_key, _comment in NAV_ITEMS:
            label = t(label_key)
            button = QPushButton(label)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setIcon(make_icon(icon_name, ICON_IDLE, 18))
            button.setIconSize(QSize(18, 18))
            button.toggled.connect(
                lambda checked, b=button, n=icon_name: b.setIcon(
                    make_icon(n, self._theme_accent() if checked else ICON_IDLE,
                              18))
            )
            button.clicked.connect(
                lambda checked=False, k=key: self._show_page(k)
            )
            self.nav_group.addButton(button)
            self.nav_buttons[key] = button
            self.nav_meta[key] = (icon_name, label)
            side_layout.addWidget(button)

        side_layout.addStretch()

        root_layout.addWidget(self.sidebar)

    def _toggle_sidebar(self):
        """Collapse or expand the drawer."""
        self._set_sidebar_collapsed(not self._sidebar_collapsed)

    def _set_sidebar_collapsed(self, collapsed: bool):
        """Set the drawer collapsed state (icons only or icon + label)."""
        self._sidebar_collapsed = collapsed
        width = SIDEBAR_WIDTH_COLLAPSED if collapsed else SIDEBAR_WIDTH_EXPANDED
        self.sidebar.setFixedWidth(width)

        for button in self.nav_buttons.values():
            button.setProperty("collapsed", collapsed)
            button.style().unpolish(button)
            button.style().polish(button)
        for key, button in self.nav_buttons.items():
            icon_name, label = self.nav_meta[key]
            button.setText(label if not collapsed else "")
            button.setToolTip("" if not collapsed else label)

        self.brand_label.setVisible(not collapsed)
        self.brand_subtitle.setVisible(not collapsed)

        if collapsed:
            self.drawer_btn.setToolTip(t("gui.nav.expand"))
        else:
            self.drawer_btn.setToolTip(t("gui.nav.collapse"))

    def _build_about_page(self) -> QWidget:
        """Build the About page."""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("aboutCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(8)

        # Application icon
        icon_label = QLabel()
        icon_label.setPixmap(render_pixmap("muralis", 64, "#ffffff"))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)

        title = QLabel(t("gui.nav.brand"))
        title.setObjectName("aboutTitle")
        card_layout.addWidget(title)

        desc = QLabel(t("gui.about.desc"))
        desc.setWordWrap(True)
        card_layout.addWidget(desc)

        version = QLabel(t("gui.about.version", version=__version__))
        version.setObjectName("pageSubtitle")
        card_layout.addWidget(version)

        card_layout.addSpacing(8)

        github = QLabel(f'<a href="https://github.com/quoxiom/qutility-muralis">'
                        f"{t('gui.about.github')}</a>")
        github.setObjectName("aboutLink")
        github.setOpenExternalLinks(True)
        card_layout.addWidget(github)

        docs = QLabel(f'<a href="https://github.com/quoxiom/qutility-muralis/wiki">'
                      f"{t('gui.about.docs')}</a>")
        docs.setObjectName("aboutLink")
        docs.setOpenExternalLinks(True)
        card_layout.addWidget(docs)

        card_layout.addStretch()
        layout.addWidget(card)

        return page

    def _make_page(self, title: str, comment: str, widget: QWidget) -> QWidget:
        """Wrap a page widget with a header.

        The comment (description) is placed in front of the view name, on the
        same line, instead of below it.
        """
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        header = QLabel(title)
        header.setObjectName("pageHeader")
        header_row.addWidget(header)

        if comment:
            comment_label = QLabel(comment)
            comment_label.setObjectName("pageComment")
            header_row.addWidget(comment_label)

        header_row.addStretch()
        layout.addLayout(header_row)

        layout.addWidget(widget, 1)
        return page

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _build_status_bar(self):
        """Build the status bar with live information."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_info = QLabel("")
        self.status_info.setObjectName("statusInfo")
        self.status_bar.addPermanentWidget(self.status_info)

        self.status_bar.showMessage(t("gui.status.ready"))

    def _read_config(self) -> configparser.ConfigParser:
        """Read the config file (empty parser if missing)."""
        config = configparser.ConfigParser()
        if CONFIG_PATH.exists():
            config.read(CONFIG_PATH)
        return config

    def _provider_name(self, key: str) -> str:
        """Localized display name for a provider key."""
        localized = t(f"gui.provider.{key}")
        return key if localized == f"gui.provider.{key}" else localized

    def _update_status_bar(self):
        """Refresh the status bar info (image, provider, daily update)."""
        # Current image
        image_name = "—"
        if WALLPAPER_DIR.exists():
            wallpapers = sorted(
                WALLPAPER_DIR.glob("muralis_*.jpg"),
                key=_safe_mtime,
                reverse=True
            )
            if wallpapers:
                image_name = wallpapers[0].name

        # Provider
        config = self._read_config()
        provider = config.get("general", "provider", fallback="bing")

        # Daily update status
        timer_path = Path.home() / ".config/systemd/user/muralis.timer"
        sep = t("gui.statusbar.sep")
        if timer_path.exists():
            fetch_time = self._next_fetch_time(timer_path)
            provider_display = self._provider_name(provider)
            schedule = t("gui.statusbar.update_on",
                         provider=provider_display, time=fetch_time)
            next_fetch = t("gui.statusbar.update_next", time=fetch_time)
            update_text = f"{schedule}{sep}{next_fetch}"
        else:
            update_text = t("gui.statusbar.update_off")

        parts = [
            t("gui.statusbar.image", name=image_name),
            t("gui.statusbar.provider", name=self._provider_name(provider)),
            update_text,
        ]
        self.status_info.setText(sep.join(parts))

    @staticmethod
    def _next_fetch_time(timer_path: Path) -> str:
        """Parse the systemd timer's OnCalendar and format the next run."""
        hour = 9
        minute = 0  # defaults match the shipped timer template (09:00)
        try:
            for line in timer_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("OnCalendar="):
                    spec = line.split("=", 1)[1].strip()
                    # e.g. "*-*-* 09:00:00"
                    time_part = spec.split()[-1]
                    parts = time_part.split(":")
                    hour = int(parts[0])
                    minute = int(parts[1]) if len(parts) > 1 else 0
                    break
        except (OSError, ValueError):
            pass

        now = datetime.now()
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate = candidate + timedelta(days=1)
        return candidate.strftime("%d %b %Y %H:%M")

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def _show_page(self, key: str):
        """Switch to the page identified by key."""
        for index, (page_key, page) in enumerate(self.pages):
            if page_key == key:
                self.stack.setCurrentIndex(index)
                self.nav_buttons[key].setChecked(True)
                break

    # ------------------------------------------------------------------
    # Theming
    # ------------------------------------------------------------------
    def _theme_accent(self) -> str:
        """The accent color of the currently applied theme."""
        theme_id = self._read_config().get(
            "gui", "theme", fallback=DEFAULT_THEME)
        colors = self.theme_manager.load_colors(theme_id)
        accent = colors.get("accent")
        return accent if isinstance(accent, str) else ICON_IDLE

    def _refresh_nav_icons(self):
        """Re-tint the drawer icons (selected item uses the theme accent)."""
        accent = self._theme_accent()
        for key, button in self.nav_buttons.items():
            icon_name = self.nav_meta[key][0]
            button.setIcon(make_icon(
                icon_name, accent if button.isChecked() else ICON_IDLE, 18))

    def _apply_stored_theme(self):
        """Apply the theme saved in the config (default: reasonix)."""
        config = self._read_config()
        theme_id = config.get("gui", "theme", fallback=DEFAULT_THEME)
        if not self.theme_manager.apply(theme_id):
            self.theme_manager.apply(DEFAULT_THEME)

    def _set_theme(self, theme_id: str):
        """Apply a theme and persist the choice in the config."""
        if self.theme_manager.apply(theme_id):
            self._refresh_nav_icons()
            try:
                config = self._read_config()
                if "gui" not in config:
                    config["gui"] = {}
                config["gui"]["theme"] = theme_id
                CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    config.write(f)
            except OSError:
                # Read-only config dir: theme applies for this session only
                pass

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _load_current_wallpaper(self):
        """Load and display the current wallpaper."""
        self.preview_widget.load_current_wallpaper()

    def _refresh_wallpaper(self):
        """Manually refresh the wallpaper."""
        from muralis.app import MuralisApp

        self.status_bar.showMessage(t("gui.status.updating"))

        try:
            app = MuralisApp(str(CONFIG_PATH))
            if app.run_once():
                self.status_bar.showMessage(t("gui.status.success"), 3000)
                self._load_current_wallpaper()
                self.history_tab.refresh_history()
                self._update_status_bar()
            else:
                self.status_bar.showMessage(t("gui.status.failed"), 3000)
                from .dialogs import warning
                warning(self, t("gui.dialog.error_title"),
                        t("gui.dialog.failed_update"))
        except Exception as e:
            self.status_bar.showMessage(t("gui.status.error", error=str(e)), 5000)
            from .dialogs import critical
            critical(self, t("gui.dialog.error_title"),
                     t("gui.dialog.failed_update_detail", error=str(e)))

    def _auto_refresh_preview(self):
        """Auto-refresh the preview (not the wallpaper itself)."""
        self.preview_widget.refresh_preview()

    def toggle_tray_icon(self, show: bool):
        """Show/hide the tray icon and persist the choice."""
        self.tray_icon.setVisible(show)
        try:
            config = self._read_config()
            if "gui" not in config:
                config["gui"] = {}
            config["gui"]["show_tray"] = str(show).lower()
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                config.write(f)
        except OSError:
            pass

    def _request_quit(self):
        """Quit the application (from the Settings page)."""
        self.tray_icon.hide()
        self.close()

    def closeEvent(self, event):
        """Handle window close event."""
        # Hide to tray instead of quitting
        if self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.show_message(
                t("gui.nav.brand"),
                t("gui.tray.minimized")
            )
            event.ignore()
        else:
            event.accept()
