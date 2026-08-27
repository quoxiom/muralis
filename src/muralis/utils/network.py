"""Shared network session construction for Muralis.

Both the application downloads and the wallpaper providers build a
``requests.Session`` from the same config settings (proxy, user-agent, SSL
verification, redirects). Centralising that here keeps the two paths in sync.
"""

from typing import Optional, TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from muralis.config import ConfigManager


def build_session(config: Optional["ConfigManager"] = None) -> requests.Session:
    """Build a ``requests.Session`` configured from Muralis settings.

    When ``config`` is provided, the session honors the ``networking`` section
    (proxy, user-agent, SSL verification, max redirects). Without a config a
    plain session is returned.

    Args:
        config: Optional ``ConfigManager`` to read network settings from.

    Returns:
        A configured ``requests.Session``.
    """
    session = requests.Session()
    if config is None:
        return session

    proxy_settings = config.get_proxy_settings()
    if proxy_settings:
        session.proxies.update(proxy_settings)

    session.headers.update({
        'User-Agent': config.get_str(
            'networking', 'user_agent', 'Muralis/1.0'),
    })
    session.verify = config.get_bool('networking', 'verify_ssl', True)
    session.max_redirects = config.get_int(
        'networking', 'max_redirects', 5)
    return session
