#!/bin/bash
# Uninstallation script for Muralis

set -e

echo "🗑️  Uninstalling Muralis"

# Remove pip package
pip uninstall muralis -y

# Remove configuration (optional)
read -p "Remove configuration files? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.config/muralis
    echo "✓ Configuration removed"
fi

# Remove systemd timer
systemctl --user stop muralis.timer 2>/dev/null || true
systemctl --user disable muralis.timer 2>/dev/null || true
rm -f ~/.config/systemd/user/muralis.{service,timer}
systemctl --user daemon-reload

# Remove cron job
crontab -l 2>/dev/null | grep -v "muralis" | crontab - 2>/dev/null || true

echo "✓ Muralis uninstalled"
