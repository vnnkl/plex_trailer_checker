#!/bin/bash

# Plex Trailer Checker - Run Script
# This script activates the virtual environment and runs the trailer checker

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "plex_trailer_checker.py" ]; then
    echo "❌ Error: plex_trailer_checker.py not found"
    echo "Please run this script from the plex_trailer_checker directory"
    exit 1
fi

echo "🎬 Starting Plex Trailer Checker..."
echo ""

# Activate virtual environment and run
source venv/bin/activate
python3 plex_trailer_checker.py

echo ""
echo "🏁 Trailer check complete!" 