"""Bing wallpaper provider."""

import requests
from typing import Dict, Optional
from .base import WallpaperProvider

class BingProvider(WallpaperProvider):
    """Fetches daily Bing wallpaper."""
    
    BASE_URL = "https://www.bing.com"
    # TODO: Add support for different markets (mkt parameter) and multiple images (n parameter)
    API_URL = f"{BASE_URL}/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    
    @property
    def name(self) -> str:
        return "bing"
    
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get Bing daily wallpaper URL."""
        try:
            response = requests.get(self.API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('images') and len(data['images']) > 0:
                image_url = data['images'][0]['url']
                full_url = f"{self.BASE_URL}{image_url}"
                return full_url
        except Exception as e:
            print(f"Error fetching Bing wallpaper: {e}")
            return None
    
    def get_metadata(self) -> Dict:
        """Get Bing wallpaper metadata."""
        try:
            response = requests.get(self.API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('images') and len(data['images']) > 0:
                img = data['images'][0]
                return {
                    'title': img.get('title', ''),
                    'copyright': img.get('copyright', ''),
                    'date': img.get('startdate', '')
                }
        except Exception:
            pass
        return {}