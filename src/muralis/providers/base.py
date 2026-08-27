"""Abstract base class for wallpaper providers."""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from muralis.config import ConfigManager


class WallpaperProvider(ABC):
    """Base class for all wallpaper providers."""

    # Default request timeout (seconds) used when the provider isn't given a
    # config to read a timeout from.
    DEFAULT_TIMEOUT = 15

    def __init__(self, config: Optional["ConfigManager"] = None):
        """Initialize provider with optional configuration."""
        self.config = config
        self._http_session: Optional[requests.Session] = None

    def _session(self) -> requests.Session:
        """Return a lazily-built ``requests.Session`` from config settings.

        When a config is available the session honors proxy, SSL verification
        and user-agent settings so providers respect the same network options
        as downloads. Providers without a config get a plain session.
        """
        if self._http_session is not None:
            return self._http_session

        from muralis.utils.network import build_session

        session = build_session(self.config)
        self._http_session = session
        return session

    def _get(self, url: str, timeout: Optional[int] = None, **kwargs: Any) -> requests.Response:
        """Perform a GET request through the configured session."""
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        return self._session().get(url, timeout=timeout, **kwargs)

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""
        pass

    @abstractmethod
    def get_daily_url(self, resolution: str = "1920x1080") -> Optional[str]:
        """Get URL for today's wallpaper.

        Args:
            resolution: Desired image resolution (e.g., '1920x1080')

        Returns:
            URL string or None if unavailable
        """
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the current wallpaper.

        Returns:
            Dictionary with keys: title, copyright, date, etc.
        """
        pass

    def supports_resolution(self, resolution: str) -> bool:
        """Check if provider supports specific resolution."""
        # Override in subclasses if needed
        return True

    def get_available_resolutions(self) -> list:
        """Get list of available resolutions."""
        return ["1920x1080", "2560x1440", "3840x2160"]
