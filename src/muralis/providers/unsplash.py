"""Unsplash wallpaper provider."""

import requests
from typing import Dict, Optional
from .base import WallpaperProvider

class UnsplashProvider(WallpaperProvider):
    """Fetches random curated photos from Unsplash."""
    
    API_URL = "https://api.unsplash.com/photos/random"
    # Note: You need to register for an API key
    # https://unsplash.com/developers
    ACCESS_KEY = "YOUR_ACCESS_KEY"  # Replace with your key
    
    @property
    def name(self) -> str:
        return "unsplash"
    
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get random Unsplash photo URL."""
        if self.ACCESS_KEY == "YOUR_ACCESS_KEY":
            print("Warning: Unsplash API key not configured. Please set ACCESS_KEY")
            return None
        
        try:
            headers = {
                'Authorization': f'Client-ID {self.ACCESS_KEY}'
            }
            params = {
                'orientation': 'landscape',
                'content_filter': 'high',
                'w': 1920,
                'h': 1080
            }
            response = requests.get(self.API_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Get the raw image URL
            return data.get('urls', {}).get('raw') or data.get('urls', {}).get('full')
        except Exception as e:
            print(f"Error fetching Unsplash photo: {e}")
            return None
    
    def get_metadata(self) -> Dict:
        """Get Unsplash photo metadata."""
        if self.ACCESS_KEY == "YOUR_ACCESS_KEY":
            return {'title': 'Unsplash Photo', 'copyright': 'Unsplash'}
        
        try:
            headers = {'Authorization': f'Client-ID {self.ACCESS_KEY}'}
            response = requests.get(self.API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'title': data.get('alt_description', 'Unsplash Photo'),
                'copyright': f"© {data.get('user', {}).get('name', 'Photographer')} / Unsplash",
                'photographer': data.get('user', {}).get('name', ''),
                'location': data.get('location', {}).get('name', ''),
                'provider': 'Unsplash'
            }
        except Exception:
            pass
        return {'title': 'Unsplash Photo', 'copyright': 'Unsplash'}
