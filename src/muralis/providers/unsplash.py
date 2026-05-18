"""Unsplash wallpaper provider with API key support."""

import requests
from typing import Dict, Optional
from .base import WallpaperProvider

class UnsplashProvider(WallpaperProvider):
    """Fetches random curated photos from Unsplash."""
    
    API_URL = "https://api.unsplash.com/photos/random"
    
    @property
    def name(self) -> str:
        return "unsplash"
    
    def _get_api_key(self) -> Optional[str]:
        """Get Unsplash API key from config."""
        if self.config:
            key = self.config.get('api_keys', 'unsplash_key', fallback=None)
            if key and key.strip() and key != '':
                return key.strip()
        return None
    
    def _check_api_key(self) -> bool:
        """Check if API key is configured."""
        key = self._get_api_key()
        if not key:
            print("\n⚠️  Unsplash requires an API key")
            print("   Get your free key at: https://unsplash.com/developers")
            print("   Then add to config: muralis --set-key unsplash YOUR_KEY\n")
            return False
        
        # Basic format validation
        if len(key) != 32 or not all(c.isalnum() or c in '-_' for c in key):
            print("\n⚠️  Invalid Unsplash API key format")
            print("   Key should be 32 characters (letters, numbers, - and _)")
            print("   Run: muralis --set-key unsplash YOUR_CORRECT_KEY\n")
            return False
        
        return True
    
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get random Unsplash photo URL."""
        if not self._check_api_key():
            return None
        
        try:
            api_key = self._get_api_key()
            headers = {'Authorization': f'Client-ID {api_key}'}
            
            # Parse resolution for width/height
            if 'x' in resolution:
                width, height = resolution.split('x')
            else:
                width, height = "1920", "1080"
            
            params = {
                'orientation': 'landscape',
                'content_filter': 'high',
                'w': width,
                'h': height,
                'fit': 'crop'
            }
            
            response = requests.get(
                self.API_URL, 
                headers=headers, 
                params=params, 
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            # Get the raw image URL (highest quality)
            image_url = data.get('urls', {}).get('raw')
            if not image_url:
                image_url = data.get('urls', {}).get('full')
            if not image_url:
                image_url = data.get('urls', {}).get('regular')
            
            # Add resolution parameters to raw URL
            if image_url and 'raw' in image_url:
                image_url = f"{image_url}&w={width}&h={height}&fit=crop"
            
            return image_url
            
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                print("\n❌ Invalid Unsplash API key")
                print("   Please check your key and try again")
                print("   Update with: muralis --set-key unsplash YOUR_KEY\n")
            else:
                print(f"Error fetching Unsplash photo: {e}")
            return None
        except Exception as e:
            print(f"Error fetching Unsplash photo: {e}")
            return None
    
    def get_metadata(self) -> Dict:
        """Get Unsplash photo metadata."""
        if not self._check_api_key():
            return {'title': 'Unsplash Photo', 'copyright': 'Unsplash (API key required)'}
        
        try:
            api_key = self._get_api_key()
            headers = {'Authorization': f'Client-ID {api_key}'}
            
            response = requests.get(self.API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            photographer = data.get('user', {}).get('name', 'Unknown Photographer')
            photographer_username = data.get('user', {}).get('username', '')
            
            return {
                'title': data.get('alt_description', 'Unsplash Photo'),
                'copyright': f"📷 {photographer} / Unsplash",
                'photographer': photographer,
                'username': photographer_username,
                'likes': data.get('likes', 0),
                'downloads': data.get('downloads', 0),
                'provider': 'Unsplash',
                'profile_url': f"https://unsplash.com/@{photographer_username}" if photographer_username else ''
            }
        except Exception as e:
            print(f"Error fetching metadata: {e}")
            return {'title': 'Unsplash Photo', 'copyright': 'Unsplash'}
    
    def get_available_resolutions(self) -> list:
        """Unsplash supports various resolutions."""
        return ['1920x1080', '2560x1440', '3840x2160', '4096x2160', '5120x2880']
    
    def supports_resolution(self, resolution: str) -> bool:
        """Unsplash supports high resolutions."""
        return True