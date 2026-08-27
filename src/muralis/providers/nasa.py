"""NASA Astronomy Picture of the Day provider."""

from typing import Dict, Optional, Any
from datetime import datetime
from .base import WallpaperProvider

class NasaProvider(WallpaperProvider):
    """Fetches NASA's Astronomy Picture of the Day."""
    
    API_URL = "https://api.nasa.gov/planetary/apod"
    API_KEY = "DEMO_KEY"  # Replace with your API key for production
    
    @property
    def name(self) -> str:
        return "nasa"
    
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get NASA APOD image URL."""
        try:
            params: Dict[str, Any] = {
                'api_key': self.API_KEY,
                'hd': True
            }
            response = self._get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check if it's an image (not video)
            if data.get('media_type') == 'image':
                hdurl = data.get('hdurl')
                if isinstance(hdurl, str) and hdurl:
                    return hdurl
                url = data.get('url')
                if isinstance(url, str) and url:
                    return url
            return None
        except Exception as e:
            print(f"Error fetching NASA APOD: {e}")
            return None
    
    def get_metadata(self) -> Dict:
        """Get NASA APOD metadata."""
        try:
            params = {'api_key': self.API_KEY}
            response = self._get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return {
                'title': data.get('title', 'Astronomy Picture of the Day'),
                'copyright': data.get('copyright', 'NASA'),
                'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
                'explanation': data.get('explanation', ''),
                'provider': 'NASA'
            }
        except Exception:
            pass
        return {'title': 'NASA APOD', 'copyright': 'NASA'}
    
    def supports_resolution(self, resolution: str) -> bool:
        """NASA images are usually very high resolution."""
        return True
