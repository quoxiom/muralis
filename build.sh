#!/bin/bash
# Debug build script for Muralis

set -e

echo "🔨 Building Muralis..."
echo "======================"
echo "Current directory: $(pwd)"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ ERROR: setup.py not found!"
    echo "Make sure you're running this from the project root directory"
    exit 1
fi

# Check Python version
echo "Python version:"
python --version
echo ""

# Clean previous builds
echo "🧹 Cleaning old builds..."
rm -rf build/ dist/ *.egg-info
echo "✓ Clean complete"
echo ""

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install --upgrade pip
pip install build wheel twine
echo "✓ Dependencies installed"
echo ""

# Check if src directory exists
if [ ! -d "src/muralis" ]; then
    echo "❌ ERROR: src/muralis directory not found!"
    echo "Expected structure: src/muralis/__init__.py"
    exit 1
fi

# Check for __init__.py
if [ ! -f "src/muralis/__init__.py" ]; then
    echo "❌ ERROR: src/muralis/__init__.py not found!"
    exit 1
fi

# Build the package
echo "🏗️ Building package..."
python -m build

# Show results
echo ""
echo "✅ Build complete!"
echo "======================"
echo "📁 Build artifacts:"
ls -lh dist/ 2>/dev/null || echo "No artifacts found"

# Check package validity
if [ -f "dist/*.whl" ]; then
    echo ""
    echo "🔍 Checking package..."
    twine check dist/* 2>/dev/null || echo "Package check skipped"
fi

echo ""
echo "📦 To install the built package:"
echo "  pip install dist/*.whl"