"""Wallpaper providers for Muralis."""

from typing import Dict, Callable

from muralis.providers.base import WallpaperProvider
from muralis.providers.bing import BingProvider
from muralis.providers.nasa import NasaProvider
from muralis.providers.unsplash import UnsplashProvider
from muralis.providers.wallhaven import WallhavenProvider
from muralis.providers.pexels import PexelsProvider
from muralis.providers.wikimedia import WikimediaProvider
from muralis.providers.artinstitute import ArtInstituteProvider

def get_provider(name: str, config=None) -> WallpaperProvider:
    """Factory function to get provider by name."""
    providers: Dict[str, Callable[..., WallpaperProvider]] = {
        'bing': BingProvider,
        'nasa': NasaProvider,
        'unsplash': UnsplashProvider,
        'wallhaven': WallhavenProvider,
        'pexels': PexelsProvider,
        'wikimedia': WikimediaProvider,
        'artinstitute': ArtInstituteProvider
    }
    
    provider_class = providers.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")
    
    return provider_class(config)

__all__ = [
    'WallpaperProvider',
    'BingProvider',
    'NasaProvider', 
    'UnsplashProvider',
    'WallhavenProvider',
    'PexelsProvider',
    'WikimediaProvider',
    'ArtInstituteProvider',
    'get_provider'
]