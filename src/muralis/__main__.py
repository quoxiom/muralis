#!/usr/bin/env python3
"""Main entry point for Muralis - Smart Wallpaper Manager."""

import sys
import argparse
from pathlib import Path
from muralis.app import MuralisApp
from muralis import __version__

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Muralis - Smart Wallpaper Manager for Linux",
        epilog="Part of Qutility Suite by Quoxiom",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="muralis"
    )
    
    # Basic options
    parser.add_argument(
        "-c", "--config",
        default=str(Path.home() / ".config/muralis/config.ini"),
        help="Configuration file path (default: ~/.config/muralis/config.ini)"
    )
    
    parser.add_argument(
        "-p", "--provider",
        choices=["bing", "nasa", "unsplash", "wallhaven", "pexels", "wikimedia", "artinstitute"],
        help="Override wallpaper provider for this run"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one update cycle and exit"
    )
    
    parser.add_argument(
        "--set-daily",
        action="store_true",
        help="Setup systemd timer for daily automatic updates"
    )
    
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List all available wallpaper providers"
    )
    
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Display current configuration"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Muralis v{__version__}"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output for debugging"
    )
    
    # Configuration management commands
    parser.add_argument(
        "--export-config",
        metavar="FILE",
        help="Export current configuration to JSON file"
    )
    
    parser.add_argument(
        "--import-config",
        metavar="FILE",
        help="Import configuration from JSON file"
    )
    
    parser.add_argument(
        "--get",
        nargs=1,
        metavar="SECTION.KEY",
        help="Get configuration value (e.g., --get general.provider)"
    )
    
    parser.add_argument(
        "--set",
        nargs=2,
        metavar=("SECTION.KEY", "VALUE"),
        help="Set configuration value (e.g., --set general.provider nasa)"
    )
    
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Reset configuration to factory defaults"
    )
    
    # API key management commands
    parser.add_argument(
        "--check-keys",
        action="store_true",
        help="Check API key status for all providers"
    )
    
    parser.add_argument(
        "--set-key",
        nargs=2,
        metavar=("PROVIDER", "KEY"),
        help="Set API key for a provider (e.g., --set-key unsplash YOUR_KEY)"
    )
    
    parser.add_argument(
        "--remove-key",
        metavar="PROVIDER",
        help="Remove API key for a provider"
    )
    
    parser.add_argument(
        "--get-key-instructions",
        metavar="PROVIDER",
        help="Show instructions to get API key for a provider"
    )
    
    return parser.parse_args()


def handle_config_commands(args, app):
    """Handle configuration management commands."""
    
    # Export configuration to JSON
    if args.export_config:
        app.config.export_json(args.export_config)
        return True
    
    # Import configuration from JSON
    if args.import_config:
        app.config.import_json(args.import_config)
        return True
    
    # Get a configuration value
    if args.get:
        section_key = args.get[0]
        if '.' in section_key:
            section, key = section_key.split('.', 1)
            value = app.config.get(section, key)
            if value:
                print(value)
            else:
                print(f"Warning: '{section_key}' not found", file=sys.stderr)
        else:
            print(f"Error: Use format SECTION.KEY (e.g., general.provider)", file=sys.stderr)
        return True
    
    # Set a configuration value
    if args.set:
        section_key, value = args.set
        if '.' in section_key:
            section, key = section_key.split('.', 1)
            app.config.set(section, key, value)
            print(f"✓ Set {section}.{key} = {value}")
        else:
            print(f"Error: Use format SECTION.KEY (e.g., general.provider)", file=sys.stderr)
        return True
    
    # Reset configuration to defaults
    if args.reset_config:
        print("⚠️  Warning: This will reset all configuration to defaults.")
        confirm = input("Are you sure? (y/N): ")
        if confirm.lower() == 'y':
            app.config.create_default()
            print("✓ Configuration reset to defaults")
        else:
            print("Cancelled")
        return True
    
    return False


def handle_api_key_commands(args, app):
    """Handle API key management commands."""
    from muralis.utils.api_keys import APIKeyManager
    
    key_manager = APIKeyManager(app.config)
    
    # Show instructions for getting a key
    if args.get_key_instructions:
        provider = args.get_key_instructions.lower()
        instructions = key_manager.get_instructions(provider)
        if instructions:
            print(f"\n📝 Instructions for {provider.title()} API Key:")
            print(instructions)
        else:
            print(f"\n❌ No instructions available for '{provider}'")
            print(f"   Available providers: {', '.join(key_manager.PROVIDER_CONFIG.keys())}")
        return True
    
    # Set API key
    if args.set_key:
        provider, key = args.set_key
        provider = provider.lower()
        
        if provider not in key_manager.PROVIDER_CONFIG:
            print(f"\n❌ Unknown provider: {provider}")
            print(f"   Available: {', '.join(key_manager.PROVIDER_CONFIG.keys())}")
            return True
        
        # Validate key format
        if key_manager.validate_key(provider, key):
            key_manager.set_key(provider, key)
            print(f"\n✅ API key for {provider.title()} saved successfully!")
            print(f"   Run 'muralis --check-keys' to verify")
        else:
            print(f"\n❌ Invalid key format for {provider.title()}")
            print(f"   Key should match pattern: {key_manager.PROVIDER_CONFIG[provider].get('pattern', 'N/A')}")
            print(f"   Get a valid key from: {key_manager.PROVIDER_CONFIG[provider]['url']}")
        return True
    
    # Remove API key
    if args.remove_key:
        provider = args.remove_key.lower()
        
        if provider not in key_manager.PROVIDER_CONFIG:
            print(f"\n❌ Unknown provider: {provider}")
            return True
        
        key_manager.set_key(provider, '')
        print(f"\n✅ API key for {provider.title()} removed")
        return True
    
    # Check keys status
    if args.check_keys:
        key_manager.display_status()
        return True
    
    return False


def list_providers():
    """Display list of available providers."""
    print("\n📸 Available Wallpaper Providers")
    print("=" * 50)
    print("  ✅ bing         - Bing Daily Images (4K/8K, no key needed)")
    print("  ✅ nasa         - NASA APOD (no key needed)")
    print("  ✅ pexels       - Pexels Stock Photos (demo key included)")
    print("  ✅ wikimedia    - Wikimedia Commons (public domain)")
    print("  ✅ artinstitute - Art Institute of Chicago (museum art)")
    print("  ✅ wallhaven    - Wallhaven.cc (anime/gaming art)")
    print("  🔑 unsplash     - Unsplash (requires free API key)")
    print("\n💡 Legend:")
    print("  ✅ Works immediately")
    print("  🔑 Requires API key setup")
    print("\n📝 To set up API keys:")
    print("  muralis --check-keys              - Check key status")
    print("  muralis --set-key unsplash KEY    - Add Unsplash API key")
    print("  muralis --get-key-instructions unsplash - Get setup help")
    print()
    return 0


def show_help():
    """Display help information when no arguments provided."""
    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  Muralis v{__version__} - Smart Wallpaper Manager                        ║
║  Part of Qutility Suite by Quoxiom                                ║
╚══════════════════════════════════════════════════════════════════╝

📌 QUICK START
  muralis --once                    Get today's wallpaper
  muralis --once --provider nasa    Use specific provider
  muralis --set-daily               Setup automatic daily updates

🔧 CONFIGURATION
  muralis --show-config             View current settings
  muralis --set general.provider nasa   Change provider
  muralis --set image.resolution 3840x2160   Set 4K resolution
  muralis --reset-config            Reset to defaults
  muralis --export-config backup.json   Backup settings
  muralis --import-config backup.json    Restore settings

🔑 API KEYS (for Unsplash)
  muralis --check-keys              Check API key status
  muralis --set-key unsplash YOUR_KEY   Add Unsplash API key
  muralis --get-key-instructions unsplash   Get setup help

📋 PROVIDERS
  muralis --list-providers          Show all available providers

💡 TIPS
  • Config file location: ~/.config/muralis/config.ini
  • Edit config directly with any text editor
  • Wallpapers saved to: ~/Pictures/Muralis
  • Run with --verbose for debug output

📚 FULL DOCUMENTATION
  muralis --help                    Show this help
  https://github.com/quoxiom/qutility-muralis

""")


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Handle provider listing (no app needed)
    if args.list_providers:
        return list_providers()
    
    # Handle help when no actionable arguments
    if not (args.once or args.set_daily or args.show_config or 
            args.export_config or args.import_config or args.get or args.set or
            args.reset_config or args.check_keys or args.set_key or 
            args.remove_key or args.get_key_instructions):
        show_help()
        return 0
    
    # Create app for other commands
    app = MuralisApp(args.config, verbose=args.verbose)
    
    # Handle configuration commands
    if handle_config_commands(args, app):
        return 0
    
    # Handle API key commands
    if handle_api_key_commands(args, app):
        return 0
    
    # Handle show config
    if args.show_config:
        app.config.display()
        return 0
    
    # Handle set daily updates
    if args.set_daily:
        success = app.setup_scheduler()
        return 0 if success else 1
    
    # Handle run once
    if args.once:
        success = app.run_once(args.provider)
        return 0 if success else 1
    
    # Should never reach here
    show_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())