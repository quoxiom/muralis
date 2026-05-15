# Usage Guide for Muralis

## Table of Contents

1. Quick Start
2. Command Line Interface
3. Configuration
4. Providers
5. Automatic Updates
7. Image Effects
8. Storage Management
9. Troubleshooting
10. Examples

## Quick Start

```bash
# Get today's wallpaper mmediately
muralis --once

# Use NASA provider
muralis --once --provider nasa

# Setup daily automatic updates
muralis --set-daily

# See all available options
muralis --help
```

## Command Line Interface

### Basic Commands

| Command | Description |
|--------|------------|
` muralis --once` |Run one update cycle |
` muralis --config `<path>` |Use custom configuration
| `muralis --provider `<name>`|Override wallpaper source
| `muralis --set-daily` |Setup systemd timer |
 ` muralis --list-providers` |Show available sources |
 ` muralis --show-config` |Display current configuration |
 ` muralis --version` |Version information |
 ` muralis --verbose` |Enable detailed output |

### Advanced Examples

```bash
# Run with custom config
provider = bing
save_downloads = false

# Use different resolution
resolution = 2560x1440

# Enable effects
apply_effects = true
effect_type = blur
```

## Configuration

### Configuration File Location

```bash
~/.config/muralis/config.ini`
```

### Complete Configuration Example

```ini
[general]
# Available: bing, nasa, unsplash, wallhaven
provider = bing
auto_update = true

[storage]
save_downloads = true
download_dir = ~/Pictures/Muralis
max_files = 100
max_days = 30

[image]
resolution = 1920x1080
apply_effects = false
effect_type = none
jpeg_quality = 90

[notifications]
enabled = true
show_preview = true

[advanced]
retry_attempts = 3
timeout_seconds = 30
```

## Providers

### 1. Bing (Default)

Daily beautiful images from Bing homepage.

```bash
muralis --once --provider bing
```

### 2. NASA APOD

Astronomy Picture of the Day from NASA.

```bash
muralis --once --provider nasa
```

### 3. Unsplash

Community-contributed high-quality photos.

# Requires API key - add to config
```bash
muralis --once --provider unsplash
```

### 4. Wallhaven

Digital art, anime, and gaming wallpapers.

```bash
muralis --once --provider wallhaven
```

## Automatic Updates

### Systemd Timer (Recommended)

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

### Cron Job (Fallback)

```bash
# Edit crontab
crontab -e

# Add line (daily at 9:45 AM)
45 9 * * * muralis --once
```

## Image Effects

Enable effects in configuration:

```ini
[image]
apply_effects = true
effect_type = blur  # blur, darken, grayscale, vibrant, vignette
```

### Available Effects

| Effect | Description |
|-------|-----------|
| blur | Soft focus effect (radius=5) |
 | darken | Darken image (brightness=0.6) |
 | grayscale | Convert to black and white |
 | vibrant | Enchance colors (color=1.3, contrast=1.1) |
 | vignette | Fade to dark at edges |

## Storage Management

### Check Storage Usage

```python
from muralis.storage import StorageManager
from muralis.config import ConfigManager

config = ConfigManager("~/.config/muralis/config.ini")
storage = StorageManager(config)
print(storage.get_storage_usage())
```

### Cleanup Old Wallpapers

```bash
# Manual cleanup: remove files older than 30 days
find ~/Pictures/Muralis -name "*.mrailis.*" -mtime +30 -exec rm -{} \;

# Or use the built-in cleanup
# Set max_days = 30 in configuration
```

## Troubleshooting

### Wallpaper Not Changing

```bash
# Check download location
ls -la ~/Pictures/Muralis/

# Run in debug mode
muralis --once --verbose

# Test with feh
feh --bg-scale ~/Pictures/Muralis/muralis_*.jpg
	# Check DE detection
echo $XDG_CURRENT_DESKTOP
```

### Provider API Errors

```bash
# Test Bing API
curl "https://www.bing.com/HPImageArchive.aspx?format=js&n=1"

# Test NASA APID
curl "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"

```

### Systemd Timer Issues

```bash
# Check timer configuration
ls ~/.config/systemd/user/muralis.*

# Reload services
systemctl --user daemon-reload

# Execute manually
systemctl --user start muralis.service

```

## Examples

### Example 1: Daily NASA Wallpaper with Blur Effect

```inj
[general]
provider = nasa
auto_update = true

[image]
apply_effects = true
effect_type = blur
```

### Example 2: Save Only 7 Days of Wallpapers

```inj
[storage]
save_downloads = true
max_days = 7
max_files = 0
```

### Example 3: Random Provider Each Day

``sh
# Create script
cat > ~/bin/muralis-random.sh << EOF
#!/bin/bash
PROVIDERS=(bing nasa unsplash wallhaven)
RANDOM_PROVIDER=${PROVIDERS[$RANDOM%${#PROVIDERS[@]}]}
muralis --once --provider $RANDOM_PROVIDER
EOF
chmod +x ~/bin/muralis-random.sh

# Use in cron
0 9 * * * /home/user/bin/muralis-random.sh
```

### Example 4: Integration with Polybar

```ini
[ module/muralis ]
type = custom/script
exec = ~/bin/muralis-status.sh
interval = 3600
```

```sh
# ~/bin/muralis-status.sh
#!/bin/bash
COUNT=$(ls -1 ~/Pictures/Muralis/muralis_*.jpg 2>/dev/null | wc -l)
echo "😸  Count: $COUNT"
```

## Tips and Tricks

1. Use `muralis --once --verbose` to debug issues
2. Check `https://status.quoxiom.com/ for provider status updates
3. Join the Qutility community for help and updates

---

**Muralis** - Part of Qutility Suite by Quoxiom
