"""API key management for Muralis providers."""

import re
from typing import Dict, List, Optional, Any

from muralis.i18n import t

from muralis.config import ConfigManager


class APIKeyManager:
    """Manage and validate API keys for various providers."""

    # Provider configuration
    PROVIDER_CONFIG: Dict[str, Dict[str, Any]] = {
        "unsplash": {
            "key_name": "unsplash_key",
            "pattern": r"^[a-zA-Z0-9_-]{32}$",
            "required": True,
            "url": "https://unsplash.com/developers",
            "message": "Get your free Unsplash API key (50 requests/hour)",
            "instructions": """
To get an Unsplash API key:
1. Go to https://unsplash.com/developers
2. Sign in or create an account
3. Click "Create an application"
4. Fill in the form (any name/description)
5. Copy your "Access Key" (starts with random characters)
6. Add it to your config file
            """,
        },
        "pexels": {
            "key_name": "pexels_key",
            "pattern": r"^[a-zA-Z0-9]{32,}$",
            "required": False,
            "url": "https://www.pexels.com/api/",
            "message": "Optional: Get higher rate limits (5,000/hour)",
            "instructions": """
To upgrade from demo key:
1. Visit https://www.pexels.com/api/
2. Sign up for a free account
3. Get your API key
4. Add to config for higher rate limits
            """,
        },
        "flickr": {
            "key_name": "flickr_key",
            "pattern": r"^[a-f0-9]{32}$",
            "required": False,
            "url": "https://www.flickr.com/services/api/",
            "message": "Optional: Enable Flickr integration",
            "instructions": """
To add Flickr support:
1. Go to https://www.flickr.com/services/api/
2. Create an app to get API key
3. Add both key and secret to config
            """,
        },
    }

    def __init__(self, config: ConfigManager):
        """Initialize with config manager."""
        self.config = config

    def get_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        if provider not in self.PROVIDER_CONFIG:
            return None

        # ConfigManager.get_api_key() expects the provider name and appends
        # '_key' itself (e.g. 'unsplash' -> 'unsplash_key'), so pass `provider`
        # rather than the already-suffixed key_name.
        key = self.config.get_api_key(provider)

        # Return None if empty string
        return key if key and key.strip() else None

    def set_key(self, provider: str, key: str) -> bool:
        """Set API key for a provider."""
        if provider not in self.PROVIDER_CONFIG:
            return False

        key_name = self.PROVIDER_CONFIG[provider]["key_name"]
        self.config.set("api_keys", key_name, key)
        return True

    def validate_key(self, provider: str, key: str) -> bool:
        """Validate API key format for a provider."""
        if provider not in self.PROVIDER_CONFIG:
            return False

        pattern = self.PROVIDER_CONFIG[provider].get("pattern")
        if pattern:
            return bool(re.match(pattern, key))
        return True

    def is_valid(self, provider: str) -> bool:
        """Check if provider has a valid API key configured."""
        key = self.get_key(provider)
        if not key:
            return False

        return self.validate_key(provider, key)

    def is_configured(self, provider: str) -> bool:
        """Check if provider is properly configured to work."""
        config = self.PROVIDER_CONFIG.get(provider, {})

        # Required providers must have valid key
        if config.get("required", False):
            return self.is_valid(provider)

        # Optional providers are always "configured" (will use demo or skip)
        return True

    def get_missing_required_keys(self) -> List[Dict]:
        """Get list of missing required API keys."""
        missing = []
        for provider, config in self.PROVIDER_CONFIG.items():
            if config.get("required", False):
                if not self.is_valid(provider):
                    missing.append(
                        {
                            "provider": provider,
                            "key_name": config["key_name"],
                            "url": config["url"],
                            "message": config["message"],
                        }
                    )
        return missing

    def get_status_summary(self) -> Dict:
        """Get status summary for all providers."""
        status = {}
        for provider in self.PROVIDER_CONFIG:
            status[provider] = {
                "has_key": self.get_key(provider) is not None,
                "is_valid": self.is_valid(provider),
                "is_configured": self.is_configured(provider),
                "required": self.PROVIDER_CONFIG[provider].get("required", False),
            }
        return status

    def display_status(self):
        """Display API key status in a nice format."""
        print("\n" + "=" * 60)
        print(t("cli.key.status_title"))
        print("=" * 60)

        for provider, config in self.PROVIDER_CONFIG.items():
            provider_title = provider.title()
            has_key = self.get_key(provider) is not None
            is_valid = self.is_valid(provider)
            is_required = config.get("required", False)

            # Determine status icon
            if is_required and not is_valid:
                icon = "❌"
                status_text = t("cli.key.status_missing")
            elif is_required and is_valid:
                icon = "✅"
                status_text = t("cli.key.status_ok")
            elif has_key and is_valid:
                icon = "🔑"
                status_text = t("cli.key.status_ok_optional")
            else:
                icon = "⚪"
                status_text = t("cli.key.status_missing_optional")

            print(f"\n{icon} {provider_title}: {status_text}")

            if is_required and not is_valid:
                print(f"   → {config['message']}")
                print(f"   → {config['url']}")
            elif has_key and is_valid:
                provider_key = self.get_key(provider)
                key_display = provider_key[:8] + "..." if provider_key else "None"
                print(t("cli.key.key_label", key=key_display))

        print("\n" + "=" * 60)
        print("💡 Tip: Run 'muralis --set-key PROVIDER YOUR_KEY' to add API keys")
        print("=" * 60)

    def get_instructions(self, provider: str) -> Optional[str]:
        """Get setup instructions for a provider."""
        if provider in self.PROVIDER_CONFIG:
            instructions = self.PROVIDER_CONFIG[provider].get("instructions")
            return instructions if isinstance(instructions, str) else None
        return None
