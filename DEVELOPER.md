# Developer Documentation

## Project Structure

```
fictional-octo-engine/
├── osc_haptics_gui.py          # Main GUI application
├── test_packets.py             # Packet structure validation tests
├── test_osc_client.py          # OSC test client
├── requirements.txt            # Python dependencies
├── haptics_config.example.json # Example configuration
├── run.sh                      # Linux/Mac launcher
├── run.bat                     # Windows launcher
├── README.md                   # User documentation
└── DEVELOPER.md                # This file
```

## Architecture

### Core Components

1. **HapticsOutput Class**
   - Manages individual haptic device output configuration
   - Builds SlimeVR UDP packets
   - Handles packet sequencing
   - Sends UDP packets to devices

2. **HapticsGUI Class**
   - Main GUI application using tkinter
   - Manages multiple HapticsOutput instances
   - Runs OSC server in background thread
   - Handles configuration save/load

### UDP Packet Format

The application generates SlimeVR Vibrate packets:

```
Offset  Size    Type        Description
0-2     3B      uint8[3]    Packet ID
3       1B      uint8       Packet Type (2 = Vibrate)
4-11    8B      uint64 BE   Packet Number
12-13   2B      uint16 BE   Duration (milliseconds)
```

**Total:** 14 bytes

### OSC Message Handling

The OSC server listens for messages on configured paths and converts values to vibration durations:

- **Boolean**: `True` → 100ms, `False` → 0ms
- **Float (0-1)**: Linearly mapped to 0-500ms
- **Numeric (>1)**: Direct milliseconds (capped at 65535)
- **No value**: Default 100ms

### Threading Model

- **Main Thread**: GUI event loop (tkinter)
- **OSC Server Thread**: Background daemon thread for OSC message handling
  - Created when "Start OSC Server" is clicked
  - Automatically terminated when application closes

## Development

### Running Tests

```bash
# Packet structure tests
python test_packets.py

# OSC client test (requires running GUI)
python test_osc_client.py
```

### Code Style

- Python 3.6+ compatible
- PEP 8 style guide
- Docstrings for all classes and public methods
- Type hints encouraged but not required

### Adding Features

#### Adding New Packet Types

To add support for different SlimeVR packet types:

1. Extend `HapticsOutput` class with new packet builder method
2. Update packet type constants
3. Add UI controls for new packet parameters
4. Update documentation

#### Adding New OSC Value Mappings

To customize OSC value to duration mapping:

1. Modify `HapticsGUI.osc_handler()` method
2. Add new value type detection logic
3. Update README documentation

## Dependencies

- **python-osc** (>=1.8.0): OSC protocol implementation
  - Used for OSC server and client
  - Handles OSC message parsing

- **tkinter**: GUI framework (built-in to Python)
  - Standard Python GUI library
  - No installation needed on most systems

## Configuration File Format

```json
{
  "osc_port": 9001,
  "outputs": [
    {
      "device_ip": "127.0.0.1",
      "device_port": 6969,
      "osc_path": "/avatar/parameters/example",
      "packet_id": [0, 0, 0]
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **"Module not found: tkinter"**
   - Install python3-tk package
   - Ubuntu/Debian: `sudo apt install python3-tk`
   - macOS: Usually included with Python
   - Windows: Reinstall Python with tkinter option

2. **OSC Server won't start**
   - Check if port is already in use
   - Try a different port number
   - Check firewall settings

3. **Packets not received by device**
   - Verify device IP address is correct
   - Check network connectivity
   - Ensure device port is correct (default: 6969)
   - Check if device supports SlimeVR protocol

## Future Enhancements

Potential improvements:

- [ ] Support for other SlimeVR packet types
- [ ] Advanced OSC filtering (regex patterns)
- [ ] Packet logging/debugging view
- [ ] Multiple OSC servers on different ports
- [ ] Preset configurations
- [ ] Dark theme support
- [ ] System tray integration
- [ ] Auto-start with OS
- [ ] Configuration profiles

## Contributing

When contributing:

1. Maintain backward compatibility
2. Add tests for new features
3. Update documentation
4. Follow existing code style
5. Keep changes minimal and focused

## License

MIT License - See LICENSE file for details
