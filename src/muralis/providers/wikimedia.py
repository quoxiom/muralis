"""Wikimedia Commons provider - Public domain artwork."""

import requests
from typing import Dict, Optional, Any
import random
from .base import WallpaperProvider

class WikimediaProvider(WallpaperProvider):
    """Fetches public domain artwork from Wikimedia Commons."""
    
    API_URL = "https://commons.wikimedia.org/w/api.php"
    
    # Categories of interesting artwork
    CATEGORIES = [
        "Featured_pictures_on_Wikimedia_Commons",
        "Quality_images",
        "Valued_images",
        "Landscape_paintings",
        "Nature_photographs"
    ]
    
    @property
    def name(self) -> str:
        return "wikimedia"
    
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get random featured image from Wikimedia Commons."""
        try:
            # Get random featured image
            category = random.choice(self.CATEGORIES)
            
            params: Dict[str, Any] = {
                'action': 'query',
                'format': 'json',
                'list': 'random',
                'rnnamespace': 6,  # File namespace
                'rnlimit': 50,
                'generator': 'categorymembers',
                'gcmtitle': f'Category:{category}',
                'gcmlimit': 50,
                'prop': 'imageinfo',
                'iiprop': 'url|extmetadata'
            }
            
            response = requests.get(self.API_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get('query', {}).get('pages'):
                pages = list(data['query']['pages'].values())
                random_page = random.choice(pages)
                
                # Get the image URL
                if 'imageinfo' in random_page and len(random_page['imageinfo']) > 0:
                    url = random_page['imageinfo'][0].get('url')
                    if isinstance(url, str) and url:
                        # Try to get larger version if available
                        url = url.replace('px-', '').replace('-', '')
                        return url
            return None
            
        except Exception as e:
            print(f"Error fetching Wikimedia image: {e}")
            return None
    
    def get_metadata(self) -> Dict:
        """Get artwork metadata."""
        try:
            params: Dict[str, Any] = {
                'action': 'query',
                'format': 'json',
                'list': 'random',
                'rnnamespace': 6,
                'rnlimit': 1
            }
            
            response = requests.get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('query', {}).get('random'):
                item = data['query']['random'][0]
                return {
                    'title': item.get('title', 'Wikimedia Artwork'),
                    'copyright': 'Public Domain / Wikimedia Commons',
                    'provider': 'Wikimedia Commons'
                }
        except Exception:
            pass
        return {'title': 'Wikimedia Artwork', 'copyright': 'Public Domain'}