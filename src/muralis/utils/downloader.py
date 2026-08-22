"""Download utilities for Muralis."""

import requests
import time
from pathlib import Path
from typing import Optional

from muralis.i18n import t

def download_image(url: str, save_path: str, timeout: int = 30, retries: int = 3) -> bool:
    """Download image from URL to local path with retries.
    
    Args:
        url: Image URL to download
        save_path: Local path to save image
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        
    Returns:
        bool: True if successful, False otherwise
    """
    headers = {
        'User-Agent': 'Muralis/0.4.0 (Qutility Suite; +https://quoxiom.com)'
    }
    
    save_path_obj = Path(save_path)
    
    for attempt in range(retries):
        try:
            response = requests.get(
                url, 
                headers=headers, 
                timeout=timeout, 
                stream=True
            )
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type:
                print(t("cli.download.not_image", content_type=content_type))
            
            # Save image
            with open(save_path_obj, 'wb') as f:
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
                wait_time = 2 ** attempt  # Exponential backoff
                print(t("cli.download.retrying",
                         attempt=attempt + 1, error=e, wait=wait_time))
                time.sleep(wait_time)
                continue
            else:
                print(t("cli.download.failed", retries=retries, error=e))
                
        except Exception as e:
            print(t("cli.download.unexpected", error=e))
            return False
    
    return False
