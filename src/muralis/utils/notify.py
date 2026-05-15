"""Notification utilities for Muralis."""

import subprocess
from typing import Optional

def send_notification(title: str, message: str, urgency: str = "normal") -> bool:
    """Send desktop notification.
    
    Args:
        title: Notification title
        message: Notification message body
        urgency: Notification urgency (low, normal, critical)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        subprocess.run([
            'notify-send',
            '--expire-time=5000',
            f'--urgency={urgency}',
            '--icon=wallpaper',
            title,
            message
        ], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        # notify-send not installed
        return False
    except subprocess.CalledProcessError:
        return False

def send_error_notification(title: str, message: str) -> bool:
    """Send error notification with critical urgency."""
    return send_notification(f"⚠️ {title}", message, urgency="critical")

def send_success_notification(title: str, message: str) -> bool:
    """Send success notification."""
    return send_notification(f"✓ {title}", message, urgency="low")
