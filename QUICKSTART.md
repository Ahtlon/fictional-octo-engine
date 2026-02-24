# Quick Start Guide

## Installation (5 minutes)

### Prerequisites
- Python 3.6 or higher
- pip package manager

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ahtlon/fictional-octo-engine.git
   cd fictional-octo-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   
   **Linux/Mac:**
   ```bash
   ./run.sh
   ```
   
   **Windows:**
   ```
   run.bat
   ```
   
   **Or directly:**
   ```bash
   python osc_haptics_gui.py
   ```

## First Time Setup (2 minutes)

### Configure Your First Output

1. **Device Settings** (already filled with defaults):
   - Device IP: `127.0.0.1` (change to your device's IP)
   - Port: `6969` (SlimeVR default)

2. **OSC Path**:
   - Default: `/avatar/parameters/output0`
   - Change to match your VRChat parameter (e.g., `/avatar/parameters/leftPawTouched`)

3. **Test the Connection**:
   - Click "Test (100ms)" button
   - Your haptic device should vibrate for 100ms
   - If it doesn't work, check IP address and port

### Start the OSC Server

1. **Set OSC Port**: Default is `9001` (VRChat default)
2. Click **"Start OSC Server"**
3. Status should change to "Running" (green)

## VRChat Integration (3 minutes)

### Setup Avatar Parameters

1. In your VRChat avatar, add parameters:
   - `leftPawTouched` (bool)
   - `rightPawTouched` (bool)
   - etc.

2. Configure outputs in the app:
   - Output 0: `/avatar/parameters/leftPawTouched`
   - Output 1: `/avatar/parameters/rightPawTouched`

3. Set device IPs:
   - Left device: IP of left haptic device
   - Right device: IP of right haptic device

4. Save configuration:
   - Click **"Save Config"**
   - Creates `haptics_config.json`

### Test in VRChat

1. Start VRChat
2. Enable OSC in VRChat settings
3. Touch triggers on your avatar
4. Haptic devices should vibrate!

## Common Use Cases

### Single Device, Multiple Zones

```json
{
  "osc_port": 9001,
  "outputs": [
    {
      "device_ip": "192.168.1.100",
      "device_port": 6969,
      "osc_path": "/avatar/parameters/headTouch"
    },
    {
      "device_ip": "192.168.1.100",
      "device_port": 6969,
      "osc_path": "/avatar/parameters/leftHandTouch"
    },
    {
      "device_ip": "192.168.1.100",
      "device_port": 6969,
      "osc_path": "/avatar/parameters/rightHandTouch"
    }
  ]
}
```

### Multiple Devices

```json
{
  "osc_port": 9001,
  "outputs": [
    {
      "device_ip": "192.168.1.100",
      "device_port": 6969,
      "osc_path": "/avatar/parameters/leftPawTouched"
    },
    {
      "device_ip": "192.168.1.101",
      "device_port": 6969,
      "osc_path": "/avatar/parameters/rightPawTouched"
    }
  ]
}
```

## Troubleshooting

### OSC Server Won't Start

**Problem**: Error when starting OSC server

**Solutions**:
1. Check if port 9001 is already in use
2. Try a different port (e.g., 9002)
3. Check firewall settings
4. Restart the application

### No Vibration on Test

**Problem**: Test button doesn't trigger vibration

**Solutions**:
1. Verify device IP is correct
2. Check device port (default: 6969)
3. Ensure device is powered on
4. Check network connectivity
5. Verify device supports SlimeVR protocol

### VRChat OSC Not Working

**Problem**: OSC messages not received from VRChat

**Solutions**:
1. Enable OSC in VRChat settings
2. Verify OSC port matches (default: 9001)
3. Restart VRChat after changes
4. Check avatar parameters are configured
5. Ensure OSC server is running (green status)

### Wrong Device Vibrates

**Problem**: Different device vibrates than expected

**Solutions**:
1. Check device IP addresses
2. Verify OSC paths match avatar parameters
3. Review configuration file
4. Test each device individually

## Tips

- **Save Early**: Save your configuration after initial setup
- **Test First**: Use test buttons before VRChat testing
- **One at a Time**: Configure and test outputs one at a time
- **Use Example**: Copy `haptics_config.example.json` as starting point
- **Check Logs**: Console window shows OSC messages received

## Next Steps

- See `README.md` for detailed documentation
- See `DEVELOPER.md` for advanced customization
- See `ARCHITECTURE.md` for technical details
- Run `python test_osc_client.py` to test OSC reception

## Support

For issues, please check:
1. This quick start guide
2. README.md troubleshooting section
3. GitHub issues
4. DEVELOPER.md for technical details
