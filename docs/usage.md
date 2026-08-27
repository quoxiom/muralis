# Usage Guide

## Table of contents

1. Quick start
2. Command-line interface
3. Configuration
4. Providers
5. Automatic updates
6. Image effects
7. Storage management
8. Themes & languages
9. Troubleshooting
10. Examples

---

## Quick start

```bash
# Download and set today's wallpaper (default provider from config)
muralis --once

# Use a specific provider
muralis --once --provider nasa

# Set up automatic daily updates
muralis --set-daily

# Show the current configuration
muralis --show-config

# List all providers
muralis --list-providers

# See all options
muralis --help
```

## Command-line interface

Run `muralis --help` to see the full list. Options can be combined.

```bash
# Run one update cycle using the Bing provider
muralis --once --provider bing
```

### Options

| Option | Description |
|--------|------------|
| `-gui`, `--gui` | Launch the graphical interface |
| `-c`, `--config PATH` | Use a custom configuration file |
| `-p`, `--provider NAME` | Override the wallpaper source |
| `--once` | Run one update cycle |
| `--set-daily` | Setup the systemd timer (daily updates) |
| `--list-providers` | Show available providers |
| `--show-config` | Display the current configuration |
| `--get SECTION.KEY` | Get a configuration value |
| `--set SECTION.KEY VALUE` | Set a configuration value |
| `--reset-config` | Reset to defaults |
| `--export-config FILE` | Export configuration to JSON |
| `--import-config FILE` | Import configuration from JSON |
| `--check-keys` | Show API key status |
| `--set-key PROVIDER KEY` | Set an API key |
| `--remove-key PROVIDER` | Remove an API key |
| `--get-key-instructions PROVIDER` | Show setup help for a provider |
| `--verbose` | Enable debug output |
| `-v`, `--version` | Show the version |

## Configuration

### Location

Settings are stored as **JSON** at `~/.config/muralis/config.json`. A legacy
`config.ini` is migrated automatically on first launch and then removed. The
application re-reads the file on each start, so external edits are picked up.

All settings can also be changed from the CLI:

```bash
muralis --get general.provider
muralis --set scheduling.update_time 14:30
muralis --export-config ~/muralis-backup.json
```

### Sections

| Section | Purpose |
|---------|---------|
| `general` | Provider, auto-update, randomize, fallback, offline mode |
| `image` | Resolution, effects, format, fit mode, upscaling, watermark |
| `storage` | Save/keep wallpapers, cleanup limits, organize-by |
| `scheduling` | Update time, battery/WiFi guards, minimum interval |
| `networking` | Proxy, user agent, SSL verification, timeouts |
| `wallpaper_effects` | Time-of-day themed effects (not yet wired in the pipeline) |
| `logging` | Log level, location, rotation |
| `advanced` | Caching, parallel downloads |
| `api_keys` | Provider API keys (masked in `--show-config`) |
| `gui` | Active theme (managed by the GUI) |

#### Examples

Change the provider:

```bash
muralis --set general.provider nasa
```

Enable 4K wallpapers (Bing):

```bash
muralis --set image.resolution 3840x2160
muralis --once --provider bing
```

Enable an image effect:

```bash
muralis --set image.apply_effects true
muralis --set image.effect_type blur
muralis --once
```

Proxy behind a corporate firewall:

```bash
muralis --set networking.proxy_enabled true
muralis --set networking.proxy_url http://proxy.company.com:8080
```

## Providers

| Provider        | API key    | Notes                                             |
|-----------------|------------|---------------------------------------------------|
| `bing`          | No         | Daily Bing homepage, up to 4K/8K                   |
| `nasa`          | Demo/own   | Astronomy Picture of the Day                       |
| `pexels`        | Optional    | Curated stock photos (demo key bundled)            |
| `wikimedia`     | No         | Public-domain Wikimedia Commons artwork            |
| `artinstitute`  | No         | Art Institute of Chicago                           |
| `wallhaven`     | No         | wallhaven.cc (SFW filter)                          |
| `unsplash`      | **Required**| Curated photos                                    |

### API key management

See [Provider setup](installation.md#provider-setup) for per-provider
instructions and which providers work out of the box.

```bash
# Check status of all API keys
muralis --check-keys

# Set an API key
muralis --set-key unsplash YOUR_32_CHAR_KEY

# Remove an API key
muralis --remove-key unsplash

# Get setup instructions
muralis --get-key-instructions unsplash
```

## Automatic updates

### Systemd timer (recommended)

```bash
# Setup
muralis --set-daily

# Check status
systemctl --user status muralis.timer

# View logs
journalctl --user -u muralis.service -f

# Disable
systemctl --user disable --now muralis.timer
```

### Cron fallback

If systemd user units aren't available, Muralis falls back to a cron job:

```bash
crontab -e
# Add a line: daily at 09:45
45 9 * * * muralis --once
```

### Battery & network guards

```bash
muralis --set scheduling.skip_on_battery true
muralis --set scheduling.only_on_wifi true
```

## Image effects

Enable them in the config, or from the GUI (**Settings → Image → Effects**):

```bash
muralis --set image.apply_effects true
muralis --set image.effect_type blur
```

| Effect | Description |
|--------|-------------|
| `blur` | Soft focus (Gaussian radius 5) |
| `darken` | Reduce brightness |
| `grayscale` | Black and white |
| `vibrant` | Boost color and contrast |
| `vignette` | Fade the edges to black |

## Storage management

Wallpapers are saved to `~/Pictures/Muralis` (configurable via
`storage.download_dir`). Retention is governed by:

- `storage.max_files` — keep at most N files (`0` = unlimited)
- `storage.max_days` — delete files older than N days (`0` = unlimited)

```bash
muralis --set storage.max_files 50
muralis --set storage.max_days 14
```

Cleanup happens automatically after every successful update. Manual check:

```bash
ls -la ~/Pictures/Muralis/
```

## Themes & languages

### Themes

Themes are JSON palettes in `~/.config/muralis/themes/`. Built-in themes
(`reasonix`, `docker-dark`, `light`) are copied there on first run and are
user-editable. Change the active theme in **Settings → Appearance → Theme**.

### Languages

The language is auto-detected from the locale (`LANGUAGE`, `LC_ALL`,
`LC_MESSAGES`, `LANG`), falling back to English. Shipped translations are in
the package; to override or add a language, drop a partial file at
`~/.config/muralis/i18n/<lang>.json` (missing keys fall back to English).

## Troubleshooting

### Wallpaper not changing

```bash
# Check the download location
ls -la ~/Pictures/Muralis/

# Run in debug mode
muralis --once --verbose

# Check desktop environment detection
echo $XDG_CURRENT_DESKTOP

# Manually set the wallpaper
feh --bg-scale ~/Pictures/Muralis/muralis_*.jpg
```

### Provider API errors

```bash
# Test the Bing endpoint
curl "https://www.bing.com/HPImageArchive.aspx?format=js&n=1"

# Test the NASA endpoint
curl "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
```

### Systemd timer issues

```bash
# Inspect the generated units
ls ~/.config/systemd/user/muralis.*

# Reload service definitions
systemctl --user daemon-reload

# Run the update job manually
systemctl --user start muralis.service
```

### Invalid API key

```bash
muralis --remove-key unsplash
muralis --set-key unsplash YOUR_NEW_KEY   # copy the full key, no leading spaces
```

## Examples

### Daily NASA wallpaper with a blur effect

```bash
muralis --set general.provider nasa
muralis --set image.apply_effects true
muralis --set image.effect_type blur
muralis --set-daily
```

### Keep only the last 7 days of wallpapers

```bash
muralis --set storage.save_downloads true
muralis --set storage.max_days 7
muralis --set storage.max_files 0
```

### Random provider each day

```bash
muralis --set general.randomize_provider true
muralis --set general.fallback_provider bing
```

### Random provider via a shell script

```bash
cat > ~/bin/muralis-random.sh <<'EOF'
#!/bin/bash
PROVIDERS=(bing nasa wallhaven pexels)
RANDOM_PROVIDER=${PROVIDERS[$RANDOM % ${#PROVIDERS[@]}]}
muralis --once --provider "$RANDOM_PROVIDER"
EOF
chmod +x ~/bin/muralis-random.sh

# Use in cron at 09:00
0 9 * * * /home/user/bin/muralis-random.sh
```

---

**Muralis** — a small wallpaper utility by Quoxiom.
