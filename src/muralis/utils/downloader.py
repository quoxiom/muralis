"""Download utilities for Muralis.

The streaming + retry logic lives here (not on the application object) so it
can be reused and tested in isolation. Optional ``session`` / ``headers`` let
callers pass a configured ``requests.Session`` (proxy, SSL, user-agent) or
extra headers without changing the module's behaviour.
"""

import requests
import time
from pathlib import Path
from typing import Optional

from muralis.i18n import t

DEFAULT_USER_AGENT = "Muralis/0.4.0 (+https://quoxiom.com)"


def download_image(
    url: str,
    save_path: str,
    timeout: int = 30,
    retries: int = 3,
    session: Optional[requests.Session] = None,
    headers: Optional[dict] = None,
) -> bool:
    """Download image from URL to local path with retries.

    Args:
        url: Image URL to download
        save_path: Local path to save image
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        session: Optional ``requests.Session`` to use (enables proxy/SSL/UA
            configuration from the caller). A fresh session is created when
            omitted.
        headers: Optional extra request headers (merged with the default
            user-agent).

    Returns:
        bool: True if successful, False otherwise
    """
    request_headers = {"User-Agent": DEFAULT_USER_AGENT}
    if headers:
        request_headers.update(headers)

    session = session or requests.Session()
    save_path_obj = Path(save_path)

    for attempt in range(retries):
        try:
            response = session.get(
                url,
                headers=request_headers,
                timeout=timeout,
                stream=True,
            )
            response.raise_for_status()

            # Check content type
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                print(t("cli.download.not_image", content_type=content_type))

            # Save image
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path_obj, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Verify file was created and has content
            if save_path_obj.exists() and save_path_obj.stat().st_size > 0:
                return True
            else:
                print(t("cli.download.empty", path=save_path_obj))

        except requests.RequestException as e:
            if attempt < retries - 1:
                wait_time = 2**attempt  # Exponential backoff
                print(t("cli.download.retrying", attempt=attempt + 1, error=e, wait=wait_time))
                time.sleep(wait_time)
                continue
            else:
                print(t("cli.download.failed", retries=retries, error=e))

        except Exception as e:
            print(t("cli.download.unexpected", error=e))
            return False

    return False
