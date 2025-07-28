#!/bin/bash

# Plex Trailer Checker - Setup Script
# This script sets up the environment and runs the trailer checker

set -e  # Exit on any error

echo "🎬 Plex Trailer Checker Setup"
echo "============================="

# Check if we're in the right directory
if [ ! -f "plex_trailer_checker.py" ]; then
    echo "❌ Error: plex_trailer_checker.py not found"
    echo "Please run this script from the plex_trailer_checker directory"
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
if [ -z "$python_version" ]; then
    echo "❌ Error: Python 3 is required but not found"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if yt-dlp is working
echo "🎥 Checking yt-dlp installation..."
if command -v yt-dlp &> /dev/null; then
    echo "✓ yt-dlp is available"
else
    echo "❌ yt-dlp not found in PATH"
    echo "Installing yt-dlp..."
    pip install yt-dlp
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Run the trailer checker:"
echo "     ./run.sh"
echo ""
echo "  2. Or run manually:"
echo "     source venv/bin/activate"
echo "     python3 plex_trailer_checker.py"
echo ""
echo "💡 The script will create a config.json file on first run"
echo "   and guide you through the setup process." 