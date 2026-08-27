# Muralis

> **"Of the wall"** — bring art to your desktop every day.

Muralis is a smart wallpaper manager for Linux desktops. It fetches fresh
wallpapers from a variety of sources (Bing, NASA, Unsplash, Pexels,
Wikimedia Commons, the Art Institute of Chicago and Wallhaven), applies
optional image effects, and sets them on your desktop — once, or automatically
every day via a systemd timer or cron job.

Muralis ships with both a **command-line interface** and a **graphical
interface** (PySide6), plus native support for GNOME, KDE Plasma, XFCE and
Cinnamon desktops.

## Highlights

- 🔀 **7 wallpaper sources** — Bing, NASA, Unsplash, Pexels, Wikimedia Commons,
  Art Institute of Chicago and Wallhaven
- 🖥️ **Native desktop support** — GNOME, KDE Plasma, XFCE, Cinnamon, with a
  generic fallback (feh, nitrogen, hsetroot, …)
- ⏰ **Automatic daily updates** — via a systemd user timer or cron fallback
- 🎨 **Image effects** — blur, darken, grayscale, vibrant and vignette
- 🖼️ **Graphical interface** — preview, history, settings and themes
- 🗂️ **Smart storage** — auto-cleanup by age or file count
- 🔐 **API key management** — check, set, remove and validate keys from the CLI
- 🌍 **Internationalization** — English and French, with user overridable keys
- 🎛️ **Themes** — `reasonix`, `docker-dark` and `light`, all user-editable

## Quick start

```bash
# Install
pip install muralis

# Download and set today's wallpaper
muralis --once

# Enable automatic daily updates
muralis --set-daily
```

## Contents

- [Installation](installation.md)
- [Usage](usage.md)

---

**Muralis** — a small wallpaper utility by Quoxiom.
