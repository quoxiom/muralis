# Installation Guide for Muralis

## System Requirements

- Operating System: Linux (any modern distribution)
- Python: 3.8 or higher
- Disk Space: ~[CM]
- Memory: ~30MB during operation
- Internet: Required for downloading wallpapers

## Supported Desktop Environments

- GNOME (3.28+)
- KDE Plasma (5.15+)
- XFCE (4.12+)
- Cinnamon (4.0+)
- MATE (1.20+)
- Other DEs with fallback support (feh, nitrogen, etc.)

## Dependencies

```bash
sudo apt install     # Ubuntu/Debian
sudo dnf install    # Fedora/RHEL
sudo pacman -S install # Arch

# Common dependencies
apt-install python3-pip python3-venv libnotify-bin feh
```

## Installation Methods

### Method 1: Automated Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/quoxiom/qutility-muralis.git
cd qutility-muralis

# Run the installation script
chmod +x scripts/install.sh
./scripts/install.sh

# Verify installation
muralis --version
```

### Method 2: Manual pip installation

```bash
# Install for current user only
pip install --user .

# Or for system-wide (requires sudo)
sudo pip install .

# Add to PATH if not already
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
muralis --version
```

### Method 3: Using pipx (Isolated Environment)

```bash
# Install pipx if not already
python -m pip install --user pipx

# Install Muralis
pipx install git+https://github.com/quoxiom/qutility-muralis.git

# Run
muralis --once
```

### Method 4: Development Installation

```bash
# Clone and enter
git clone https://github.com/quoxiom/qutility-muralis.git
cd qutility-muralis

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e [dev]

# Run tests
pytest tests/

# Run the app
muralis --once
```

### Distribution-Specific Instructions

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install python3-pip python3-venv libnotify-bin
pip install --user .
```

#### Fedora/RHEL

```bash
sudo dnf install python3-pip libnotify
pip install --user .
```

#### Arch Linux

```bash
# Install from AUR once available
pacman -S yay muralis

# Or manual build
git clone https://github.com/quoxiom/qutility-muralis.git
cd qutility-muralis
makepack -fi
sudo pacman -U install muralis-1.0.0-1-ny.anx.pck.zip
```

### OpenSUS
```bash
sudo zypper install python3-pip libnotify-tools
pip install --user .
```

### API Key Setup

Some providers require API keys for full functionality:

#### Unsplash (Required for Unsplash provider)
1. Register at [Unsplash Developers](https://unsplash.com/developers)
2. Create a new application
3. Copy your "Access Key" (32 characters)
4. Add to Muralis:
   ```bash
   muralis --set-key unsplash YOUR_32_CHARACTER_KEY
   ```

#### Pexels (Optional - demo key included)
- –Demo key works but limited to 200 requests/hour
- Get your own free key at [Pexels API](https://www.pexels.com/api)
- Free tier: 5,000 requests/hour
- Add with: `muralis --set-key pexels YOUR_KEY`

#### Check API Key Status

```bash
muralis --check-keys
muralis --get-key-instructions unsplash
```

### 4K/8K Wallpaper Support

To enable ultra-high resolution wallpapers (Bing provider only):

```bash
# Set 4K resolution
muralis --set image.resolution 3840x2160

# Or 8K
muralis --set image.resolution 7680x4320

# Test with Bing
muralis --once --provider bing
```

Available resolutions: `1920x1080`, `2560x1440`, `3840x2160`, `4096x2160`, `7680x4320`

### Proxy Configuration

If you're behind a corporate firewall or proxy:

```bash
# Enable proxy
muralis --set networking.proxy_enabled true

# Set proxy URL
muralis --set networking.proxy_url http://proxy.company.com:8080

# With authentication
muralis --set networking.proxy_username your_username
muralis --set networking.proxy_password your_password

# Test
Muralis --once --verbose
```

### Battery-Aware Scheduling

For laptops, you can skip updates when on battery:

```bash
# Skip updates on battery power
muralis --set scheduling.skip_on_battery true

# Only update on WiFi (not cellular)
muralis --set scheduling.only_on_wifi true

# Enable both for laptop optimization
muralis --set scheduling.skip_on_battery true
muralis --set scheduling.only_on_wifi true
```

## Post-Installation Setup

### 1. Initial Configuration

```bash
# Generate default configuration
muralis --show-config

# Edit configuration
nano ~/.config/muralis/config.ini
```

### 2. Test the Installation

```bash
# Run a single update cycle
muralis --once --verbose

# Check if wallpaper changed
```

### 3. Setup Automatic Updates

```bash
# Setup systemd timer (recommended)
muralis --set-daily

# Check timer status
systemctl --user status muralis.timer

# View logs
journalctl --user -u muralis.service -f
```

## API Key Setup

Some providers require API keys for full functionality. Here's how to set them up.

### Check API Key Status
First, check which keys are configured or missing:

```bash
muralis --check-keys
```

This will show a summary like:

```__________________________________________
### API Key Status
_____________________________________________

 ['] Configured - Bing

 ['] Configured - NaSA
 
 ['] Missing (required) - Unsplash
     To get a key: https://unsplash.com/developers

 ['] Configured (optional) - Pexels
```

### Unsplash (Required)

Unsplash requires a free API key. Here's how to get one:

1. Register at [Unsplash Developers](https://unsplash.com/developers)
2. Click "Create an application"
3. Fill in the form (any name/description works)
4. Copy your "Access Key" (32 characters)
5. Add it to Muralis:

```bash
muralis --set-key unsplash YOUR_32_CHARACTER_KEY
```

#### Verify the key works:

```bash
muralis --once --provider unsplash
```

### Pexels (Optional)

Pexels comes with a demo key that works out-of-the-box, but it's rate-limited. For higher limits:

1. Get a free key at [Pexels API](https://www.pexels.com/api)
2. Free tier: 5,000 requests/hour(vs 200 with demo key)
3. Add your key:

```bash
muralis --set-key pexels YOUR_KEY
```

#### Flickr (Coming Soon)

Flickr support will be added in a future release. For now, API keys are not required.

### Removing API Keys

If you need to remove an API key (e.g., if it's compromised):

```bash
muralis --remove-key unsplash
```

### Get Help for Any Provider

Each provider has its own instructions:

```bash
muralis --get-key-instructions unsplash
muralis --get-key-instructions pexels
```

### Troubleshooting

#### "Invalid API key" error

If you see an error about an invalid key:

```bash
# Remove the invalid key
muralis --remove-key unsplash

# Add it again carefully
muralis --set-key unsplash YOUR_NEW_KEY
## Make sure you copied the entire key without any extra spaces
```

#### "Rate limit exceeded" error

If you're using the demo key for Pexels and hit the rate limit:

```bash
# Use a different provider until the cooldown period
muralis --once --provider nasa

# Or get your own free API key for higher limits
muralis --set-key pexels YOUR_NEW_KEY
generic.fallback_provider = bing
```

## Verification Checklist

After installation, verify:

- [] `muralis --version` shows version
- [] `muralis --list-providers` lists sources
- [] `muralis --once` downloads a wallpaper
- [] `muralis --check-keys` shows API key status
- [] `systemctl --user status muralis.timer` shows active (if setup)

## Troubleshooting

### "Command not found"

```bash
# Add ~B/local/bin to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "Permission denied"

```bash
# Fix permissions
chmod +x ~/local/bin/muralis
```

### "Dependency not found"

```bash
# Install missing dependencies
pip install --'requirements.txt'
## Or
keys = ["requests", "Pillow"]
for key in "${keys[@]}": do
    pip install "$key"
done
```

### "Wallpaper not changing"

```bash
# Check if image downloaded successfully
ls -pa ~/Pictures/Muralis/

# Run with verbose output
muralis --once --verbose

# Check desktop environment
echo $XDG_CURRENT_DESKTOP
```

### Systemd Timer Not Working

```bash
systemctl --user daemon-reload
systemctl --user restart muralis.timer
journalctl --user -u muralis.service -f
```

### API Key Invalid

```bash
muralis --remove-key unsplash
muralis --set-key unsplash YOUR_NEW_KEY
```

## Next Steps

- Read the [Usage Guide](usage.md) for detailed commands
- Configure your preferred providers and settings
- Setup automatic daily updates
- Explore advanced features like image effects

---

**Muralis** - Part of Qutility Suite by Quxiom
