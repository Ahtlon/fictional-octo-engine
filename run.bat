@echo off
REM Launcher script for OSC to UDP Haptics Converter (Windows)

echo Starting OSC to UDP Haptics Converter...

REM Check if requirements are installed
python -c "import pythonosc" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
python osc_haptics_gui.py

pause
