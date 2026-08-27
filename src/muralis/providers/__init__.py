"""Wallpaper providers for Muralis.

``PROVIDER_CLASSES`` is the single, authoritative registry of available
providers. Everything that needs to know "what providers exist" (the CLI
argparse choices, config validation, the 'list providers' command, provider
randomisation, and the GUI settings tab) should read from this registry rather
than re-declaring the provider list.
"""

from typing import Dict, Callable, List

from muralis.providers.base import WallpaperProvider
from muralis.providers.bing import BingProvider
from muralis.providers.nasa import NasaProvider
from muralis.providers.unsplash import UnsplashProvider
from muralis.providers.wallhaven import WallhavenProvider
from muralis.providers.pexels import PexelsProvider
from muralis.providers.wikimedia import WikimediaProvider
from muralis.providers.artinstitute import ArtInstituteProvider

# Single source of truth for the available providers: name -> class.
PROVIDER_CLASSES: Dict[str, Callable[..., WallpaperProvider]] = {
    "bing": BingProvider,
    "nasa": NasaProvider,
    "pexels": PexelsProvider,
    "wikimedia": WikimediaProvider,
    "artinstitute": ArtInstituteProvider,
    "wallhaven": WallhavenProvider,
    "unsplash": UnsplashProvider,
}

# Ordered list of provider keys (order matters: it defines CLI/GUI ordering).
ALL_PROVIDERS: List[str] = list(PROVIDER_CLASSES.keys())


def get_provider(name: str, config=None) -> WallpaperProvider:
    """Factory function to get provider by name."""
    provider_class = PROVIDER_CLASSES.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}. Available: {ALL_PROVIDERS}")
    return provider_class(config)


__all__ = [
    "WallpaperProvider",
    "BingProvider",
    "NasaProvider",
    "UnsplashProvider",
    "WallhavenProvider",
    "PexelsProvider",
    "WikimediaProvider",
    "ArtInstituteProvider",
    "PROVIDER_CLASSES",
    "ALL_PROVIDERS",
    "get_provider",
]
