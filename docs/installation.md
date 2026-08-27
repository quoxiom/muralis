# Installation Guide

## System requirements

- **OS:** Linux (any modern distribution)
- **Python:** 3.9 or higher
- **Disk space:** a few MB for the package (more for downloaded wallpapers)
- **Memory:** ~30 MB during operation
- **Internet:** required for downloading wallpapers
- **Desktop notifications:** `libnotify-bin` (`notify-send`)

## Supported desktop environments

- GNOME (3.28+) — uses `gsettings`
- KDE Plasma (5.15+) — uses `plasma-apply-wallpaperimage` / `kwriteconfig5`
- XFCE (4.12+) — uses `xfconf-query`
- Cinnamon (4.0+) — uses `gsettings`
- Others — generic fallback (feh, nitrogen, hsetroot, …)

## Dependencies

Core Python dependencies (`requests`, `pillow`) are installed automatically by
pip. Optional GUI support requires `PySide6`.

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install python3-pip python3-venv libnotify-bin

# Fedora / RHEL
sudo dnf install python3-pip libnotify

# Arch Linux
sudo pacman -S python-pip python-virtualenv libnotify
```

## Installation methods

### Method 1 — pip (recommended)

The package is published on PyPI. For the command-line interface:

```bash
pip install muralis
```

To add the graphical interface:

```bash
pip install "muralis[gui]"
```

### Method 2 — from source (editable, for development)

```bash
git clone https://github.com/quoxiom/muralis.git
cd muralis
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run the test suite
pytest tests/
```

### Method 3 — using pipx (isolated)

```bash
pipx install git+https://github.com/quoxiom/muralis.git
muralis --once
```

### Method 4 — automated install script

```bash
git clone https://github.com/quoxiom/muralis.git
cd muralis
chmod +x scripts/install.sh
./scripts/install.sh

# Verify
muralis --version
```

## Verify the installation

```bash
muralis --version          # shows the version
muralis --list-providers   # lists available providers
muralis --check-keys       # shows API key status
```

## Provider setup

Muralis supports these wallpaper sources. Most work out of the box; only
**Unsplash** requires an API key before it can be used.

| Provider | Works out of the box? | Setup required |
|---|---|---|
| `bing` | ✅ Yes | none |
| `nasa` | ✅ Yes | none (demo key bundled, rate-limited) |
| `wikimedia` | ✅ Yes | none |
| `artinstitute` | ✅ Yes | none |
| `wallhaven` | ✅ Yes | none |
| `pexels` | ✅ Yes | none (demo key bundled, ~200 req/hour) |
| `unsplash` | ❌ No | **API key required** |

Choose the active provider from the config, the GUI (**Settings → General →
Provider**), or the CLI:

```bash
muralis --set general.provider unsplash
muralis --once --provider bing
```

Your own API keys are stored locally in `~/.config/muralis/config.json`
(`api_keys` section). They are masked when you run `muralis --show-config`.

### bing — Bing Daily Image

- Needs **no API key**.
- Provider: `bing` (default). Supports resolutions up to 4K/8K.

```bash
muralis --set general.provider bing
muralis --set image.resolution 3840x2160
muralis --once
```

### nasa — Astronomy Picture of the Day

- Works out of the box with a public **demo key** (`DEMO_KEY`), which is
  rate-limited.
- Optional: register a free key at <https://api.nasa.gov/> for a higher limit.

```bash
# Optional: use your own key
muralis --set general.provider nasa
```

### unsplash — curated photos

- **Requires an API key** (this is the only provider that must be configured).
- Register a free application at <https://unsplash.com/developers>, copy your
  32-character **Access Key**, then set it:

```bash
muralis --set-key unsplash YOUR_32_CHARACTER_KEY
muralis --set general.provider unsplash
```

The key is validated on `--set-key`; invalid formats are rejected.

### pexels — stock photos

- Works out of the box with the bundled **public demo key** (~200
  requests/hour).
- Optional: register a free key at <https://www.pexels.com/api/> for 5,000
  requests/hour.

```bash
muralis --set-key pexels YOUR_KEY
muralis --set general.provider pexels
```

### wikimedia — public-domain art

- Needs **no API key**.
- Source: `<https://commons.wikimedia.org>` featured/quality images and
  landscape/nature photographs.

### artinstitute — Art Institute of Chicago

- Needs **no API key**.

### wallhaven — wallhaven.cc

- Needs **no API key**. Uses the SFW filter by default.

### Check key status

```bash
muralis --check-keys                # show which providers are ready
muralis --get-key-instructions unsplash   # per-provider setup help
muralis --remove-key unsplash       # remove a configured key
```

> **Security note:** your API keys are stored in
> `~/.config/muralis/config.json`. Keep that file private and don't commit it
> to version control. Muralis never uploads your keys anywhere — the only
> credentials that ship with the package are clearly-labeled **public demo
> keys** for providers that offer them.

## Post-installation setup

### 1. Generate a default configuration

```bash
muralis --show-config       # creates ~/.config/muralis/config.json on first run
```

The configuration file is JSON at `~/.config/muralis/config.json`. A legacy
`config.ini` (if present) is migrated automatically.

### 2. Test a single update cycle

```bash
muralis --once --verbose
```

### 3. Enable automatic daily updates

```bash
muralis --set-daily                 # installs a systemd user timer
systemctl --user status muralis.timer
journalctl --user -u muralis.service -f
```

## Uninstalling

```bash
make uninstall        # from a source checkout
pip uninstall muralis # when installed via pip
```

---

**Muralis** — a small wallpaper utility by Quoxiom.
