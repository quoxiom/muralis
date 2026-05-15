"""Desktop environment wallpaper setters."""

import os
from muralis.setter.base import WallpaperSetter
from muralis.setter.gnome import GnomeSetter
from muralis.setter.kde import KdeSetter
from muralis.setter.xfce import XfceSetter
from muralis.setter.cinnamon import CinnamonSetter
from muralis.setter.generic import GenericSetter

def get_wallpaper_setter() -> WallpaperSetter:
    """Auto-detect and return appropriate wallpaper setter."""
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    session = os.environ.get('DESKTOP_SESSION', '').lower()
    
    # Detect desktop environment
    if any(de in desktop or de in session for de in ['gnome', 'unity', 'budgie']):
        return GnomeSetter()
    elif any(de in desktop or de in session for de in ['kde', 'plasma']):
        return KdeSetter()
    elif 'xfce' in desktop or 'xfce' in session:
        return XfceSetter()
    elif 'cinnamon' in desktop or 'cinnamon' in session:
        return CinnamonSetter()
    else:
        return GenericSetter()

__all__ = [
    'WallpaperSetter',
    'GnomeSetter', 
    'KdeSetter',
    'XfceSetter',
    'CinnamonSetter',
    'GenericSetter',
    'get_wallpaper_setter'
]
