#!/usr/bin/env python3
"""Main entry point for Muralis."""

import sys
import argparse
from pathlib import Path
from muralis.app import MuralisApp
from muralis import __version__

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Muralis - Smart Wallpaper Manager for Linux",
        epilog="Part of Qutility Suite by Quoxiom",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "-c", "--config",
        default=str(Path.home() / ".config/muralis/config.ini"),
        help="Configuration file path"
    )
    
    parser.add_argument(
        "-p", "--provider",
        choices=["bing", "nasa", "unsplash", "wallhaven"],
        help="Override wallpaper provider"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one update cycle and exit"
    )
    
    parser.add_argument(
        "--set-daily",
        action="store_true",
        help="Setup systemd timer for daily updates"
    )
    
    parser.add_argument(
        "--list-providers",
        action="store_true",
        help="List available wallpaper providers"
    )
    
    parser.add_argument(
        "--show-config",
        action="store_true",
        help="Show current configuration"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"Muralis v{__version__}"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    if args.list_providers:
        print("Available providers:")
        print("  • bing       - Bing Daily Images")
        print("  • nasa       - NASA Astronomy Picture of the Day")
        print("  • unsplash   - Unsplash Community Photos")
        print("  • wallhaven  - Wallhaven.cc Artworks")
        return 0
    
    app = MuralisApp(args.config, verbose=args.verbose)
    
    if args.show_config:
        app.show_config()
        return 0
    
    if args.set_daily:
        app.setup_scheduler()
    elif args.once:
        success = app.run_once(args.provider)
        return 0 if success else 1
    else:
        # Interactive mode
        print(f"""
╔══════════════════════════════════════════════════╗
║  Muralis v{__version__} - Smart Wallpaper Manager      ║
║  Part of Qutility Suite by Quoxiom               ║
╚══════════════════════════════════════════════════╝

Quick commands:
  muralis --once              Get today's wallpaper
  muralis --set-daily         Setup automatic updates
  muralis --list-providers    See available sources
  muralis --help              Full documentation

Configuration file: {args.config}
        """)

if __name__ == "__main__":
    sys.exit(main())
