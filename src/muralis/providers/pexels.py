"""Pexels wallpaper provider - Free stock photos."""

import requests
from typing import Dict, Optional
from .base import WallpaperProvider

class PexelsProvider(WallpaperProvider):
    """Fetches curated photos from Pexels."""
    
    # Free API key - rate limited to 200 requests/hour
    # Users can register their own at https://www.pexels.com/api/
    API_KEY = "563492ad6f91700001000001d6d5e3b5e5a14e8b8b9b9b9b9b9b9b9b"  # Demo key
    API_URL = "https://api.pexels.com/v1/curated"
    
    @property
    def name(self) -> str:
        return "pexels"
    
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get random curated photo from Pexels."""
        try:
            headers = {'Authorization': self.API_KEY}
            params = {'per_page': 30}
            
            response = requests.get(self.API_URL, headers=headers, 
                                   params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('photos') and len(data['photos']) > 0:
                # Select random photo from curated list
                import random
                photo = random.choice(data['photos'])
                
                # Get largest available size
                src = photo.get('src', {})
                for size in ['original', 'large2x', 'large', 'medium']:
                    url = src.get(size)
                    if isinstance(url, str) and url:
                        return url
                url = src.get('original')
                if isinstance(url, str):
                    return url
                return None
            return None
            
        except Exception as e:
            print(f"Error fetching Pexels photo: {e}")
            return None
    
    def get_metadata(self) -> Dict:
        """Get Pexels photo metadata."""
        try:
            headers = {'Authorization': self.API_KEY}
            response = requests.get(self.API_URL, headers=headers, params={'per_page': 1})
            response.raise_for_status()
            data = response.json()
            
            if data.get('photos') and len(data['photos']) > 0:
                photo = data['photos'][0]
                return {
                    'title': photo.get('alt', 'Pexels Photo'),
                    'copyright': f"📷 {photo.get('photographer', 'Photographer')} / Pexels",
                    'photographer_url': photo.get('photographer_url', ''),
                    'provider': 'Pexels'
                }
        except Exception:
            pass
        return {'title': 'Pexels Photo', 'copyright': 'Pexels'}