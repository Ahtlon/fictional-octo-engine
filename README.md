# OSC to UDP Haptics Converter

A Python GUI application that converts OSC (Open Sound Control) commands to UDP packets for VR full body tracking haptics. This application is designed to work with SlimeVR-compatible devices and enables haptic feedback triggered by VR avatar parameters.

## Features

- **OSC Server**: Receives OSC messages from VR applications (e.g., VRChat)
- **UDP Packet Generation**: Converts OSC commands to SlimeVR Vibrate packets
- **Multiple Outputs**: Configure multiple haptic devices with different OSC paths
- **Test Functionality**: Test buttons for each output with different durations
- **Configuration Management**: Save and load configurations to/from JSON files
- **User-Friendly GUI**: Built with tkinter for easy configuration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ahtlon/fictional-octo-engine.git
cd fictional-octo-engine
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python osc_haptics_gui.py
```

### Configuration

1. **OSC Server Settings**:
   - Set the OSC Listen Port (default: 9001)
   - Click "Start OSC Server" to begin listening for OSC messages

2. **Haptics Outputs**:
   - **Device IP**: The IP address of your haptic device
   - **Port**: The UDP port of your haptic device (default: 6969)
   - **OSC Path**: The OSC path to listen for (e.g., `/avatar/parameters/leftPawTouched`)

3. **Test Buttons**:
   - Click test buttons to send vibrate packets with different durations (100ms, 500ms, 1000ms)

4. **Add/Remove Outputs**:
   - Click "Add Output" to create a new haptics output
   - Click "Remove" on any output to delete it (minimum 1 output required)

5. **Save/Load Configuration**:
   - Click "Save Config" to save your current configuration to `haptics_config.json`
   - Click "Load Config" to load a previously saved configuration
   - An example configuration file is provided as `haptics_config.example.json`

## Example Configuration

See `haptics_config.example.json` for an example configuration file with multiple outputs configured for VRChat avatar parameters.

## Testing

### Packet Structure Tests

Run the packet structure validation tests:
```bash
python test_packets.py
```

This validates that the UDP packets are correctly formatted according to the SlimeVR specification.

### OSC Client Test

To test the OSC server functionality, first start the GUI application and start the OSC server, then run:
```bash
python test_osc_client.py
```

This will send test OSC messages to the haptics converter. You can specify a different IP/port:
```bash
python test_osc_client.py --ip 127.0.0.1 --port 9001
```

## UDP Packet Structure

The application generates SlimeVR Vibrate packets with the following structure:

| Offset | Size | Type | Description |
|--------|------|------|-------------|
| 0-2 | 3 bytes | uint8[3] | Packet ID |
| 3 | 1 byte | uint8 | Packet Type (2 = Vibrate) |
| 4-11 | 8 bytes | uint64 (BE) | Packet Number |
| 12-13 | 2 bytes | uint16 (BE) | Duration in milliseconds |

**Total packet size:** 14 bytes

### Field Descriptions

- **Packet ID (bytes 0-2):** Standard SlimeVR packet identifier (3 bytes)
- **Packet Type (byte 3):** Must be `2` to indicate a Vibrate packet
- **Packet Number (bytes 4-11):** BigEndian uint64, standard packet sequencing
- **Duration (bytes 12-13):** BigEndian uint16 (0-65535 milliseconds)
  - `0`: Turn off vibration immediately
  - `1-65535`: Vibrate for specified milliseconds

## OSC Value Mapping

The application automatically maps OSC values to vibration durations:

- **Boolean values**: `True` → 100ms, `False` → 0ms
- **Float values (0-1)**: Mapped to 0-500ms range
- **Numeric values (>1)**: Used directly as milliseconds (capped at 65535)
- **No value**: Default 100ms

## Example VRChat Setup

1. In VRChat, create avatar parameters (e.g., `leftPawTouched`, `rightPawTouched`)
2. Configure outputs in the application to match your OSC paths:
   - Output 0: `/avatar/parameters/leftPawTouched`
   - Output 1: `/avatar/parameters/rightPawTouched`
3. Set device IPs to your haptic device addresses
4. Start the OSC server
5. When avatar parameters change in VRChat, haptic feedback will be triggered

## License

This project is licensed under the MIT License - see the LICENSE file for details.