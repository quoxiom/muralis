# Muralis — Smart Wallpaper Manager for Linux

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Platform: Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org)
[![CI](https://github.com/quoxiom/muralis/actions/workflows/ci.yaml/badge.svg)](https://github.com/quoxiom/muralis/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/quoxiom/muralis/branch/main/graph/badge.svg)](https://codecov.io/gh/quoxiom/muralis)

> **Muralis** (Latin-inspired): *"Of the wall"* — bringing art to your desktop daily.

**A small wallpaper utility by Quoxiom.**

Muralis fetches fresh wallpapers from multiple providers, applies optional
image effects, and sets them on your Linux desktop — either once or
automatically every day. It works from the command line or from a full
graphical interface (Qt/PySide6).

## Features

- 🔀 **7 wallpaper sources** — Bing, NASA, Unsplash, Pexels, Wikimedia Commons,
  Art Institute of Chicago, Wallhaven
- 🖥️ **Native desktop support** — GNOME, KDE Plasma, XFCE, Cinnamon, plus a
  generic fallback (feh, nitrogen, hsetroot, display, xsetbg, wally)
- ⏰ **Automatic daily updates** — via a systemd user timer (cron fallback)
- 🎨 **Image effects** — blur, darken, grayscale, vibrant, vignette
- 🖼️ **Graphical interface** — preview, history, settings and themes
- 📓 **Desktop notifications** (via `notify-send`)
- 💾 **Smart storage management** with auto-cleanup by age or file count
- 🔐 **API key management** — check, set, remove and validate keys from the CLI
- 🌍 **Internationalization** — English and French, user-overridable
- 🎛️ **Editable themes** (`reasonix`, `docker-dark`, `light`)
- 🚀 **Up to 4K/8K wallpaper support** (Bing provider)
- ⚡ **Proxy support** and **battery-aware scheduling**

## Quick start

```bash
git clone https://github.com/quoxiom/muralis.git
cd muralis
python -m pip install -e .
muralis --once          # fetch and set today's wallpaper
muralis --set-daily     # enable automatic daily updates
```

For the graphical interface:

```bash
pip install -e ".[gui]"
muralis-gui            # or: muralis -gui
```

## Installation

### From source

```bash
git clone https://github.com/quoxiom/muralis.git
cd muralis
pip install --user .
```

### Using pipx (isolated)

```bash
pipx install git+https://github.com/quoxiom/muralis.git
```

### Development setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
pytest tests/
```

See [docs/installation.md](docs/installation.md) for distribution-specific
instructions.

## Usage

The configuration is stored (JSON) at `~/.config/muralis/config.json`. A
legacy `config.ini` is migrated automatically on first launch. Uninstall-style
checks and live edits in `~/.config/muralis/` are picked up on next run.

### Command line

```bash
# Launch the graphical interface (either works)
muralis -gui
muralis-gui

# Run once (default provider from config)
muralis --once

# Use a specific provider
muralis --once --provider nasa

# Setup daily automatic updates (systemd timer, cron fallback)
muralis --set-daily

# Show current configuration
muralis --show-config

# List available providers
muralis --list-providers

# Get / set a specific setting
muralis --get general.provider
muralis --set general.provider nasa

# Export / import configuration
muralis --export-config ~/muralis-backup.json
muralis --import-config ~/muralis-backup.json

# Reset configuration to defaults
muralis --reset-config

# API key management
muralis --check-keys
muralis --set-key unsplash YOUR_KEY
muralis --remove-key unsplash
muralis --get-key-instructions pexels

# Enable debug logging
muralis --once --verbose
```

Run `muralis --help` for the full list of options.

### Providers

| Provider        | API key  | Notes                          |
|-----------------|----------|--------------------------------|
| `bing`          | no       | Daily Bing homepage            |
| `nasa`          | demo/by  | Astronomy Picture of the Day   |
| `unsplash`      | **required** | Curated photos            |
| `pexels`        | optional | Demo key ships built-in        |
| `wikimedia`     | no       | Public-domain Commons artwork  |
| `artinstitute`  | no       | Art Institute of Chicago       |
| `wallhaven`     | no       | wallhaven.cc (SFW)             |

### Image effects

Set `apply_effects = true` and choose an `effect_type` (`blur`, `darken`,
`grayscale`, `vibrant`, `vignette`) via the GUI or CLI:

```bash
muralis --set image.apply_effects true
muralis --set image.effect_type blur
muralis --once
```

### Themes

Themes are editable JSON palettes stored in `~/.config/muralis/themes/`.
Built-in themes (`reasonix`, `docker-dark`, `light`) are copied there on first
run. The active theme is saved in the `gui` section of the config and can be
changed from **Settings → Appearance**.

### Languages

User-facing text is extracted into JSON language files. The active language is
detected from `LANGUAGE`, `LC_ALL`, `LC_MESSAGES` and `LANG` (English is the
fallback). Shipped languages live in the package; put overrides in
`~/.config/muralis/i18n/<lang>.json` (missing keys fall back to English).

## Automatic updates

```bash
# Setup (recommended: systemd user timer)
muralis --set-daily

# Check timer status
systemctl --user status muralis.timer

# View logs
journalctl --user -u muralis.service -f

# Disable automatic updates
systemctl --user disable --now muralis.timer
```

Set the update time (and battery/WiFi preferences) in the **Scheduling**
section of the config, or from the CLI:

```bash
muralis --set scheduling.update_time 14:30
muralis --set scheduling.skip_on_battery true
muralis --set scheduling.only_on_wifi true
```

## Desktop environment support

| Desktop     | Mechanism                                  |
|-------------|--------------------------------------------|
| GNOME       | `gsettings` (sets light + dark wallpapers) |
| KDE Plasma  | `plasma-apply-wallpaperimage` / `kwriteconfig5` |
| XFCE        | `xfconf-query`                             |
| Cinnamon    | `gsettings` (org.cinnamon.desktop.background) |
| Other       | Generic fallback (feh, nitrogen, etc.)     |

## Troubleshooting

```bash
# Run with verbose output
muralis --once --verbose

# Check the generated configuration
cat ~/.config/muralis/config.json

# Manually set a downloaded wallpaper
feh --bg-scale ~/Pictures/Muralis/muralis_*.jpg
```

See [docs/usage.md](docs/usage.md) for more troubleshooting steps.

## Development

```bash
make dev       # install in editable mode with dev deps
make test      # run the test suite
make coverage  # coverage report (htmlcov/)
make lint      # flake8
make format    # black
make docs      # build the mkdocs site
```

## Contributing

Contributions are welcome! This is a small hobby utility, so keep changes
focused and friendly.

- **Report bugs / request features** — open an [issue](https://github.com/quoxiom/muralis/issues).
- **Submit code** — fork the repo, open a [pull request](https://github.com/quoxiom/muralis/pulls), and follow the [contributing guide](CONTRIBUTING.md).
- **Code style** — 100-column lines, `black` formatting, `flake8` clean, and
  type hints. Run `make test`, `make lint`, and `make format` before pushing.
- **New providers** — implement `WallpaperProvider` and register it in
  `src/muralis/providers/__init__.py` (the single source of truth — the CLI,
  GUI and config all pick it up automatically).

## License

MIT License — Copyright (c) 2026 Quoxiom (Qamber Haidry).

---

**Muralis** — a small wallpaper utility by Quoxiom.
