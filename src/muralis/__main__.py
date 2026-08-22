#!/usr/bin/env python3
"""Main entry point for Muralis - Smart Wallpaper Manager."""

import sys
import argparse
from pathlib import Path

from muralis.app import MuralisApp
from muralis import __version__
from muralis.i18n import t


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=t("cli.description"),
        epilog=t("cli.epilog"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="muralis"
    )
    
    # Basic options
    parser.add_argument(
        "-gui", "--gui",
        action="store_true",
        help=t("cli.help.gui")
    )
    
    parser.add_argument(
        "-c", "--config",
        default=str(Path.home() / ".config/muralis/config.ini"),
        help=t("cli.help.config")
    )
    
    parser.add_argument(
        "-p", "--provider",
        choices=["bing", "nasa", "unsplash", "wallhaven", "pexels", "wikimedia", "artinstitute"],
        help=t("cli.help.provider")
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help=t("cli.help.once")
    )
    
    parser.add_argument(
        "--set-daily",
        action="store_true",
        help=t("cli.help.set_daily")
    )
    
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help=t("cli.help.list_providers")
    )
    
    parser.add_argument(
        "--show-config",
        action="store_true",
        help=t("cli.help.show_config")
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Muralis v{__version__}"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help=t("cli.help.verbose")
    )
    
    # Configuration management commands
    parser.add_argument(
        "--export-config",
        metavar="FILE",
        help=t("cli.help.export_config")
    )
    
    parser.add_argument(
        "--import-config",
        metavar="FILE",
        help=t("cli.help.import_config")
    )
    
    parser.add_argument(
        "--get",
        nargs=1,
        metavar="SECTION.KEY",
        help=t("cli.help.get")
    )
    
    parser.add_argument(
        "--set",
        nargs=2,
        metavar=("SECTION.KEY", "VALUE"),
        help=t("cli.help.set")
    )
    
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help=t("cli.help.reset_config")
    )
    
    # API key management commands
    parser.add_argument(
        "--check-keys",
        action="store_true",
        help=t("cli.help.check_keys")
    )
    
    parser.add_argument(
        "--set-key",
        nargs=2,
        metavar=("PROVIDER", "KEY"),
        help=t("cli.help.set_key")
    )
    
    parser.add_argument(
        "--remove-key",
        metavar="PROVIDER",
        help=t("cli.help.remove_key")
    )
    
    parser.add_argument(
        "--get-key-instructions",
        metavar="PROVIDER",
        help=t("cli.help.get_key_instructions")
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
                print(t("cli.err.not_found", key=section_key), file=sys.stderr)
        else:
            print(t("cli.err.format"), file=sys.stderr)
        return True
    
    # Set a configuration value
    if args.set:
        section_key, value = args.set
        if '.' in section_key:
            section, key = section_key.split('.', 1)
            app.config.set(section, key, value)
            print(t("cli.ok.set", section=section, key=key, value=value))
        else:
            print(t("cli.err.format"), file=sys.stderr)
        return True
    
    # Reset configuration to defaults
    if args.reset_config:
        print(t("cli.warn.reset"))
        confirm = input(t("cli.prompt.confirm"))
        if confirm.lower() == 'y':
            app.config.create_default()
            print(t("cli.ok.reset"))
        else:
            print(t("cli.cancel"))
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
            print(t("cli.key.instructions_title", provider=provider.title()))
            print(instructions)
        else:
            print(t("cli.key.no_instructions", provider=provider))
            print(t("cli.key.available",
                    providers=", ".join(key_manager.PROVIDER_CONFIG.keys())))
        return True
    
    # Set API key
    if args.set_key:
        provider, key = args.set_key
        provider = provider.lower()
        
        if provider not in key_manager.PROVIDER_CONFIG:
            print(t("cli.key.unknown", provider=provider))
            print(t("cli.key.available_short",
                    providers=", ".join(key_manager.PROVIDER_CONFIG.keys())))
            return True
        
        # Validate key format
        if key_manager.validate_key(provider, key):
            key_manager.set_key(provider, key)
            print(t("cli.key.saved", provider=provider.title()))
            print(t("cli.key.verify"))
        else:
            print(t("cli.key.invalid", provider=provider.title()))
            print(t("cli.key.pattern",
                    pattern=key_manager.PROVIDER_CONFIG[provider].get('pattern', 'N/A')))
            print(t("cli.key.get_url",
                    url=key_manager.PROVIDER_CONFIG[provider]['url']))
        return True
    
    # Remove API key
    if args.remove_key:
        provider = args.remove_key.lower()
        
        if provider not in key_manager.PROVIDER_CONFIG:
            print(t("cli.key.unknown", provider=provider))
            return True
        
        key_manager.set_key(provider, '')
        print(t("cli.key.removed", provider=provider.title()))
        return True
    
    # Check keys status
    if args.check_keys:
        key_manager.display_status()
        return True
    
    return False


def list_providers():
    """Display list of available providers."""
    print(t("cli.providers.title"))
    print("=" * 50)
    for key in ["bing", "nasa", "pexels", "wikimedia", "artinstitute", "wallhaven"]:
        print(f"  ✅ {key:<13} - {t(f'cli.providers.{key}')}")
    print(f"  🔑 {'unsplash':<13} - {t('cli.providers.unsplash')}")
    print(t("cli.providers.legend"))
    print(t("cli.providers.works"))
    print(t("cli.providers.requires_key"))
    print(t("cli.providers.setup"))
    print(t("cli.providers.check_line"))
    print(t("cli.providers.set_line"))
    print(t("cli.providers.instructions_line"))
    print()
    return 0


def show_help():
    """Display help information when no arguments provided."""
    print(f"""
{t('cli.banner.title', version=__version__)}
{t('cli.banner.part_of')}
{'=' * 50}

{t('cli.banner.quick_start')}
{t('cli.banner.once_line')}
{t('cli.banner.once_provider_line')}
{t('cli.banner.set_daily_line')}
{t('cli.banner.gui_line')}
{t('cli.banner.gui_line_alt')}

{t('cli.banner.configuration')}
{t('cli.banner.show_config_line')}
{t('cli.banner.set_provider_line')}
{t('cli.banner.set_resolution_line')}
{t('cli.banner.reset_line')}
{t('cli.banner.export_line')}
{t('cli.banner.import_line')}

{t('cli.banner.api_keys')}
{t('cli.banner.check_keys_line')}
{t('cli.banner.set_key_line')}
{t('cli.banner.get_instructions_line')}

{t('cli.banner.providers')}
{t('cli.banner.list_providers_line')}

{t('cli.banner.tips')}
{t('cli.banner.tips_config')}
{t('cli.banner.tips_editor')}
{t('cli.banner.tips_folder')}
{t('cli.banner.tips_verbose')}

{t('cli.banner.docs')}
{t('cli.banner.docs_help_line')}
{t('cli.banner.docs_url')}

""")


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Launch GUI (imported lazily so the CLI stays fast when not needed)
    if args.gui:
        from muralis.gui import run_gui
        run_gui()
        return 0
    
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
