##! Muralis - Smart Wallpaper Manager for Linux

![[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![[Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
![[Platform: Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org)

>**Muralis** (Latin-inspired): **"Of the wall"** - Bringing art to your desktop daily.

### Part of Qutility Suite by Quoxiom

### Quick Start

```bash
git clone https://github.com/quoxiom/qutility-muralis.git
cd qutility-muralis
python -m pip install -e .
muralis --once
muralis --set-daily
```

### Features

- ✃ Multiple providers (Bing, NASA, Unsplash, Pexels, Wikimedia, Art Institute, Wallhaven)
- ◠ All Linux desktop environments supported (GNOME, KDE, XFCE, Cinnamon, Mate)
- 🔂 Automatic daily updates via systemd timer
- 😨 Image effects (blur, darken, grayscale, vibrant, vignette)
- 📓 Desktop notifications
- 💾 Smart storage management with auto-cleanup
- ✔ Multi-monitor support
- 🚀 4K/8K wallpaper support (Bing)
- 🔜 Proxy support
- ✿ Battery-aware updates

### Installation

```bash
# From source
git clone https://github.com/quoxiom/qutility-muralis.git
cd qutility-muralis
pip install --user .

# Or using pipx
pipx install git+https://github.com/quoxiom/qutility-muralis.git
```

### ConfigurationSettings

Edit `~/.config/muralis/config.ini`:J
```bash
nano ~/.config/muralis/config.ini
```

[general]
provider = bing # Bing, NASA, Unsplash, Pexels, Wikimedia, ArtInstitute, Wallhaven
randomize_provider = false
fallback_provider = bing


[image]
resolution = 3840x2160 # 1920x1080, 2560x1440, 3840x2160, 4096x2160
apply_effects = false
effect_type = none # blur, darken, grayscale, vibrant, vignette


for virtual environment

source venv/bin/activate
	# Run the app
muralis --once
```

After installation, you can:

```bash
# Launch the graphical interface (either works)
muralis -gui
muralis-gui

# Run once
muralis --once

# Use specific provider
muralis --once --provider nasa

# Setup daily automatic updates
muralis --set-daily

# Show configuration
muralis --show-config

# List available providers
muralis --list-providers

# Check API key status
muralis --check-keys

# Set API key for Unsplash
muralis --set-key unsplash YOUR_KEY

# Get a specific setting
muralis --get general.provider

# Set a specific setting
muralis --set general.provider nasa

# Reset to defaults
muralis --reset-config
```

#### Themes

Themes are editable JSON files stored in `~/.config/muralis/themes/`. Built-in
themes (`docker-dark`, `light`) are copied there on first run — modify them or
add new ones (each `<name>.json` with a `colors` object appears in
**View → Theme**). The chosen theme is remembered in the config.

#### Languages

All user-facing text is extracted into JSON language files. The active language
is picked from your locale (`LANGUAGE`, `LC_ALL`, `LANG`), with English as the
default when no file exists for the detected language. Shipped translations
live in the package; put an override at
`~/.config/muralis/i18n/<lang>.json` (only the keys you translate are needed —
missing keys fall back to English).

### API Key Setup
Should have: 🗻 Read them through.

    [advanced]
    parallel_downloads = 1
    max_connections = 5

    [api_keys]
    # Unsplash - Register at https://unsplash.com/developers
    unsplash_key =

    # Pexels - Optional (demo key included)
    pexels_key = 563492ad6f9170000100001d6d5e3b5e5a14e8b8b9b9b9b9b9b9b

    # Flickr - Coming soon
    sample configuration

### Desktop Environment Support

- GNOME - Uses gsettings
- KDE Plasma - Uses plasma-applywallpaperimage
- XFCE - Uses xfconf-query
- Cinnamon - Uses gsettings
- Generic - Fallback to feh, nitrogen, etc.

### Automatic Updates

```bash
# Check timer status
systemctl --user status muralis.timer

# View logs
journalctl --user -u muralis.service -f

# Disable automatic updates
systemctl --user disable --now muralis.timer
```

### Troubleshooting

```bash
# Run with verbose output
muralis --once --verbose

# Check configuration
cat ~/.config/muralis/config.ini

# Manually set wallpaper
feh --bg-scale ~/Pictures/Muralis/muralis_*.jpg
```

### License

MIT License - Copyright (c) 2026 Quoxiom (Qamber Haidry)

---

**Muralis** - Part of Qutility Suite by Quxiom
