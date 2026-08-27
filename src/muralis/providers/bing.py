"""Bing wallpaper provider with 4K/UHD support."""

from typing import Dict, Optional, List
from .base import WallpaperProvider

class BingProvider(WallpaperProvider):
    """Fetches daily Bing homepage wallpaper with resolution options."""
    
    BASE_URL = "https://www.bing.com"
    API_URL = f"{BASE_URL}/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"
    
    # Resolution mapping for Bing
    RESOLUTION_MAP = {
        "1366x768": "1366x768",
        "1920x1080": "1920x1080",
        "1920x1200": "1920x1200", 
        "2560x1440": "2560x1440",
        "3840x2160": "UHD",  # Bing's UHD parameter
        # "4096x2160": "4K", # For future use if Bing supports DCI 4K explicitly
        # "7680x4320": "8K", # For future use if Bing supports 8K explicitly
        "mobile": "768x1280",
        "tablet": "1280x768"
    }
    
    @property
    def name(self) -> str:
        return "bing"
    
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get Bing daily wallpaper URL with specific resolution."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }

            response = self._get(self.API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('images') and len(data['images']) > 0:
                image_url = data['images'][0]['url']
                
                # Get resolution-specific URL
                bing_res = self.RESOLUTION_MAP.get(resolution, "1920x1080")
                
                # Replace resolution in URL
                full_url = f"{self.BASE_URL}{image_url}"
                
                if bing_res == "UHD":
                    # Bing UHD uses different URL pattern
                    full_url = full_url.replace("1920x1080", "UHD")
                    #full_url = full_url.replace(".jpg", "_UHD.jpg")
                # For future use if Bing supports explicit DCI 4K/8K parameters
                # elif resolution == "4096x2160":
                #     full_url = full_url.replace("1920x1080", "4K")
                # elif resolution == "7680x4320":
                #     full_url = full_url.replace("1920x1080", "8K")
                elif resolution != "1920x1080":
                    full_url = full_url.replace("1920x1080", bing_res)
                
                return full_url
            return None
            
        except Exception as e:
            print(f"Error fetching Bing wallpaper: {e}")
            return None
    
    def get_metadata(self) -> Dict:
        """Get Bing wallpaper metadata."""
        try:
            response = self._get(self.API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('images') and len(data['images']) > 0:
                img = data['images'][0]
                return {
                    'title': img.get('title', 'Bing Daily Image'),
                    'copyright': img.get('copyright', '© Microsoft Bing'),
                    'date': img.get('startdate', ''),
                    'urlbase': img.get('urlbase', ''),
                    'provider': 'Bing',
                    'resolution_available': self.get_available_resolutions()
                }
        except Exception:
            pass
        return {'title': 'Bing Daily Wallpaper', 'copyright': '© Microsoft Bing'}
    
    def get_available_resolutions(self) -> List[str]:
        """Get list of available resolutions."""
        return list(self.RESOLUTION_MAP.keys())
    
    def supports_resolution(self, resolution: str) -> bool:
        """Check if resolution is supported."""
        return resolution in self.RESOLUTION_MAP