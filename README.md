# ♥ Muralis

### Smart Wallpaper Manager for Linux

**Part of the Qutility Suite by Quxiom**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

[![Platform: Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org)

> *Muralis* (Latin-inspired): *"Of the wall"* - Bringing art to your desktop daily.

## Quick Start

```bash
git clone https://github.com/quoxiom/qutility-muralis.git
cd qutility-muralis
./scripts/install.sh
muralis --once
muralis --set-daily
```

## Features

- 🌀 Multiple providers (Bing, NaSA, Unsplash, Wallhaven)
- 🖤 All Linux desktop environments supported
- 🔂 Automatic daily updates via systemd
- 😨 Image effects (blur, darken, grayscale)
- 📓 Desktop notifications
- 💾 Configurable storage management

## Installation

```bash
git clone https://github.com/quoxiom/qutility-muralis.git
cd qutility-muralis
pip install --user .
muralis --version
```

## Usage

```bash
Muralis --once
muralis --once --provider nasa
muralis --set-daily
muralis --show-config
muralis --list-providers
```

## Configuration

Edit `~/.config/muralis/config.ini`:

```ini[general]
provider = bing
auto_update = true

[storage]
save_downloads = true
download_dir = ~/Pictures/Muralis

[image]
resolution = 1920x1080
apply_effects = false
```

## License

MIT License - Copyright (c) 2024 Quoxiom (Qmber Haidry)

---

**Muralis** - Part of Qutility Suite by Quoxiom