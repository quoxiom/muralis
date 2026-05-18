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
# Get today's wallpaper
muralis --once

# Use NASA provider
muralis --once --provider nasa

# Setup daily automatic updates
muralis --set-daily

# View current configuration
muralis --show-config

# List all providers
muralis --list-providers

# Check API key status
```

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

### Running Muralis
` muralis --[option]` 

Please check the command line options below. Some options can be combined. e.g The following command will run one update cycle using the 'Bing' provider.

` muralis --run-once --provider bing` 


### Command Line Options

| Option | Description |
|--------|------------|
| `-c`, `--config` | Custom configuration file |
| c-p`, `--provider` | Override wallpaper source |
| `--once` | Run one update cycle |
| `--set-daily` | Setup systemd timer |
| `--list-providers` | Show all available sources |
| `--show-config` | Display current configuration |
| `--get` | Get a configuration value |
| `--set` | Set a configuration value |
| `--reset-config` | Reset to factory defaults |
| `--export-config` | Export configuration to JSON |
| `--import-config` | Import configuration from JSON |
| `--check-keys` | Check API key status |
| `--set-key` | Set API key for a provider |
| `--remove-key` | Remove API key |
| `--get-key-instructions` | Show API key setup help |
| `--verbose` | Enable debug output |

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
# Muralis Configuration File
# Part of Qutility Suite by Quoxiom
# Location: ~/.config/muralis/config.ini

[general]
# Available providers: bing, nasa, unsplash, pexels, wikimedia, artinstitute, wallhaven
provider = bing

# Automatically update wallpaper on schedule
auto_update = true

# Update interval in seconds (86400 = 1 day)
update_interval = 86400

# Randomize provider selection each day
randomize_provider = false

# Fallback provider if primary fails
fallback_provider = bing

# Timezone for scheduling
timezone = UTC

# Offline mode (don't download new wallpapers)
offline_mode = false

# Network timeout in seconds
network_timeout = 30

# Number of retry attempts for failed downloads
retry_attempts = 3

[image]
# Desired resolution (1920x1080, 2560x1440, 3840x2160, 4096x2160, 7680x4320)
resolution = 3840x2160

# Apply image effects
apply_effects = false

# Effect type: none, blur, darken, grayscale, vibrant, vignette
effect_type = none

# JPEG quality (1-100)
jpeg_quality = 90

# Image fitting: zoom, fill, fit, stretch, center
fit_mode = zoom

# Upscale lower resolution images
upscale_image = false

# Upscale factor (2, 4)
upscale_factor = 2

# Maintain aspect ratio when scaling
maintain_aspect_ratio = true

# Image format: jpg, png, webp
image_format = jpg

# Color profile: auto, srgb, adobe_rgb
color_profile = auto

# Add watermark to wallpaper
watermark = false

# Watermark position: top-left, top-right, bottom-left, bottom-right, center
watermark_position = bottom-right

# Watermark text
watermark_text = Muralis

[storage]
# Save downloaded wallpapers
save_downloads = true

# Directory to store wallpapers
download_dir = ~/Pictures/Muralis

# Maximum number of files to keep (0 = unlimited)
max_files = 100

# Maximum age in days (0 = unlimited)
max_days = 30

# Keep favorited wallpapers forever
keep_favorites = false

# Organize by: date, provider, resolution, none
organize_by = date

# Create subdirectories by year/month
create_subdirs = true

# Auto-tag wallpapers with source/category
auto_tag = true

# Sync to cloud storage
sync_to_cloud = false

# Cloud sync folder path (for rsync, rclone, etc.)
sync_path = 

# Compression level for PNG images (0-9)
compression_level = 6

[scheduling]
# Update time (24-hour format)
update_time = 09:00

# Random delay in minutes to spread out updates
random_delay_minutes = 30

# Update when system boots
update_on_boot = false

# Update when waking from sleep
update_on_wake = true

# Minimum interval between updates (hours)
minimum_interval_hours = 6

# Skip update when on battery power
skip_on_battery = false

# Only update when on WiFi (not cellular)
only_on_wifi = true

[networking]
# Enable proxy support
proxy_enabled = false

# Proxy URL (http://proxy.example.com:8080)
proxy_url = 

# Proxy username (if authentication required)
proxy_username = 

# Proxy password
proxy_password = 

# Custom user agent string
user_agent = Muralis/1.0 (Qutility Suite)

# Verify SSL certificates
verify_ssl = true

# Download timeout in seconds
download_timeout = 30

# Maximum number of redirects to follow
max_redirects = 5

[wallpaper_effects]
# Change effects based on time of day
daily_theme = false

# Effect for morning (6am-12pm): bright, vibrant, none
morning_effect = bright

# Effect for afternoon (12pm-5pm): vibrant, none
afternoon_effect = vibrant

# Effect for evening (5pm-9pm): warm, darken, none
evening_effect = warm

# Effect for night (9pm-6am): dark, none
night_effect = dark

# Auto-adjust brightness based on ambient light (requires sensor)
auto_adjust_brightness = false

# Auto-adjust contrast based on content
auto_adjust_contrast = false

# Extract dominant color for system theme
dominant_color = false

[logging]
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
log_level = INFO

# Log file location
log_file = ~/.local/share/muralis/muralis.log

# Keep logs for this many days
log_rotation_days = 30

# Enable debug mode (very verbose)
debug_mode = false

# Log HTTP traffic (may contain sensitive data)
log_http_traffic = false

[advanced]
# Config file version (auto-managed)
config_version = 2

# Enable experimental features
experimental_features = false

# Enable caching
cache_enabled = true

# Cache size in MB
cache_size_mb = 500

# Number of parallel downloads
parallel_downloads = 1

# Maximum simultaneous connections
max_connections = 5

[api_keys]
# Unsplash - REQUIRED for Unsplash provider
# Get your free key at: https://unsplash.com/developers
# Free tier: 50 requests/hour (plenty for daily use)
unsplash_key = 

# Pexels - OPTIONAL (demo key works, but limited to 200/hour)
# Get your own key at: https://www.pexels.com/api/
# Free tier: 5,000 requests/hour
pexels_key = 563492ad6f91700001000001d6d5e3b5e5a14e8b8b9b9b9b9b9b9b

# Flickr - OPTIONAL (coming soon)
flickr_key = 
flickr_secret = 
```

### Configuration Examples

#### Change Provider

```ini
[general]
provider = nasa
```

Or via CLI:

```bash
muralis --set general.provider nasa
```

#### Enable 4K/8K Wallpapers

```bash
muralis --set image.resolution 3840x2160
muralis --once --provider bing
```

#### Enable Image Effects

```bash
muralis --set image.apply_effects true
muralis --set image.effect_type blur
muralis --once
```

#### Setup Proxy

```bash
muralis --set networking.proxy_enabled true
muralis --set networking.proxy_url http://proxy:1234@example.com:8080
muralis --once
```

#### Schedule Updates at Custom Time

```bash
muralis --set scheduling.update_time 14:30
muralis --set scheduling.random_delay_minutes 45
```

#### Battery-Aware Updates (For Laptops)

```bash
# Skip updates when on battery power
muralis --set scheduling.skip_on_battery true

# Only update on WiFi
muralis --set scheduling.only_on_wifi true
```

#### Export and Import Configuration

```bash
# Backup config
Muralis --export-config ~/muralis_backup.json

# Restore config
muralis --import-config ~/muralis_backup.json
```

### Advanced Usage Examples

#### Daily NaSA Wallpaper with Blur

```ini
[general]
provider = nasa

$image]
apply_effects = true
effect_type = blur
```

#### Random Provider Each Day

```inj
[general]
randomize_provider = true
fallback_provider = bing
```

#### Save Only 7 Days of Wallpapers

```ini
[storage]
save_downloads = true
max_days = 7
max_files = 0
```

#### WiFi-Only Mode for Notebooks

```inj
[scheduling]
skip_on_battery = true
only_on_wifi = true
```

#### 4K Downloads with Caching

```ini
[advanced]
cache_enabled = true
cache_size_mb = 1000
```

## Providers

### Providers

| Provider | Description | API Key | 4K Support |
|---------|-----------|--------|---------|
| bing    | Bing Daily Images | No needed | 🚠 Yes |
| nasa    | NASA AP OD | Demo key | 😠 Yes |
| pexels   | Pexels Stock Photos | Demo key | 🚀 ' |
| wikimedia | Wikimedia Commons | No needed | 🚀 Yes |
| artinstitute | Art Institute of Chicago | No needed | 🚀 Yes |
| wallhaven | Wallhaven cc | No needed | 🚠 Yes |
| unsplash | Unsplash Photos | Required | 🚀 Yes |

### API Key Management

```bash
# Check status of all API keys
muralis --check-keys

# Set API key for Unsplash
muralis --set-key unsplash YOUR_32_CHAR_KEY

# Remove API key
muralis --remove-key unsplash

# Get setup instructions
muralis --get-key-instructions unsplash
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
