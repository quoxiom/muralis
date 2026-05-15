#!/bin/bash
# Installation script for Muralis

set -e

echo "🎨 Installing Muralis - Qutility Suite"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "Error: Python 3.8+ required (found $python_version)"
    exit 1
fi

# Install using pip
pip install --user .

# Create symlink if needed
if [[ ! -f ~/.local/bin/muralis ]]; then
    echo "Creating symlink..."
    ln -s ~/.local/bin/muralis /usr/local/bin/muralis 2>/dev/null || true
fi

echo "✓ Installation complete!"
echo ""
echo "Quick start:"
echo "  muralis --once"
echo "  muralis --set-daily"
