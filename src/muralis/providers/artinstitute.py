"""Art Institute of Chicago provider - Museum artwork."""

from typing import Dict, Optional, Any
import random
from .base import WallpaperProvider


class ArtInstituteProvider(WallpaperProvider):
    """Fetches artwork from Art Institute of Chicago API."""

    API_URL = "https://api.artic.edu/api/v1/artworks"

    @property
    def name(self) -> str:
        return "artinstitute"

    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get random artwork from Art Institute."""
        try:
            # Get random artwork with image
            params: Dict[str, Any] = {
                "limit": 100,
                "fields": "id,title,image_id,artist_display,date_display",
                "has_image": True,
            }

            response = self._get(self.API_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("data") and len(data["data"]) > 0:
                artwork = random.choice(data["data"])

                if artwork.get("image_id"):
                    # Construct image URL
                    image_id = artwork["image_id"]
                    # Get full resolution (original)
                    image_url = f"https://www.artic.edu/iiif/2/{image_id}/full/2000,/0/default.jpg"
                    return image_url
            return None

        except Exception as e:
            print(f"Error fetching Art Institute artwork: {e}")
            return None

    def get_metadata(self) -> Dict:
        """Get artwork metadata."""
        try:
            params: Dict[str, Any] = {
                "limit": 1,
                "fields": "title,artist_display,date_display,place_of_origin",
            }
            response = self._get(self.API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("data") and len(data["data"]) > 0:
                art = data["data"][0]
                return {
                    "title": art.get("title", "Artwork"),
                    "copyright": art.get("artist_display", "Art Institute of Chicago"),
                    "date": art.get("date_display", ""),
                    "origin": art.get("place_of_origin", ""),
                    "provider": "Art Institute of Chicago",
                }
        except Exception:
            pass
        return {"title": "Museum Artwork", "copyright": "Art Institute of Chicago"}
