#!/bin/bash
# Launcher script for OSC to UDP Haptics Converter

echo "Starting OSC to UDP Haptics Converter..."

# Check if requirements are installed
if ! python3 -c "import pythonosc" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the application
python3 osc_haptics_gui.py
