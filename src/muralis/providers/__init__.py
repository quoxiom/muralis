"""Wallpaper providers for Muralis."""

from muralis.providers.base import WallpaperProvider
from muralis.providers.bing import BingProvider
from muralis.providers.nasa import NasaProvider
from muralis.providers.unsplash import UnsplashProvider
from muralis.providers.wallhaven import WallhavenProvider

def get_provider(name: str, config=None) -> WallpaperProvider:
    """Factory function to get provider by name."""
    providers = {
        'bing': BingProvider,
        'nasa': NasaProvider,
        'unsplash': UnsplashProvider,
        'wallhaven': WallhavenProvider
    }
    
    provider_class = providers.get(name.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {name}")
    
    return provider_class(config)

__all__ = [
    'WallpaperProvider',
    'BingProvider', 
    'NasaProvider',
    'UnsplashProvider',
    'WallhavenProvider',
    'get_provider'
]
