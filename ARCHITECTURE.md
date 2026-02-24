# Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     OSC to UDP Haptics Converter                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐                    ┌──────────────────────┐
│   VR App        │                    │   Haptics GUI        │
│  (VRChat)       │                    │  (Main Thread)       │
│                 │                    │                      │
│  OSC Messages   │    UDP 9001        │  ┌────────────────┐  │
│  /avatar/...    │ ───────────────────>│  │ OSC Server     │  │
│                 │                    │  │ (Thread)       │  │
└─────────────────┘                    │  └────────┬───────┘  │
                                       │           │          │
                                       │           v          │
                                       │  ┌────────────────┐  │
                                       │  │ OSC Handler    │  │
                                       │  │ - Parse value  │  │
                                       │  │ - Map to ms    │  │
                                       │  └────────┬───────┘  │
                                       │           │          │
                                       │           v          │
                                       │  ┌────────────────┐  │
                                       │  │ HapticsOutput  │  │
                                       │  │ - Build packet │  │
                                       │  │ - Sequence #   │  │
                                       │  └────────┬───────┘  │
                                       │           │          │
                                       └───────────┼──────────┘
                                                   │
                                                   │ UDP
                                                   v
                                       ┌────────────────────┐
                                       │ Haptic Device      │
                                       │ (SlimeVR)          │
                                       │                    │
                                       │ IP: 192.168.1.100  │
                                       │ Port: 6969         │
                                       └────────────────────┘

UDP Packet Structure (14 bytes):
┌───────┬─────────┬──────────────┬──────────┐
│ 0-2   │ 3       │ 4-11         │ 12-13    │
│ ID    │ Type(2) │ Packet #     │ Duration │
│ 3B    │ 1B      │ 8B (BE)      │ 2B (BE)  │
└───────┴─────────┴──────────────┴──────────┘

OSC Value to Duration Mapping:
┌──────────────┬─────────────────────────┐
│ OSC Value    │ Duration (ms)           │
├──────────────┼─────────────────────────┤
│ True         │ 100                     │
│ False        │ 0 (off)                 │
│ 0.0 - 1.0    │ 0 - 500 (linear map)    │
│ > 1.0        │ Direct (capped 65535)   │
└──────────────┴─────────────────────────┘

Configuration Flow:
┌─────────────────┐
│ User configures │
│ in GUI:         │
│ - OSC Port      │
│ - Device IP     │
│ - Device Port   │
│ - OSC Path      │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Save Config     │──> haptics_config.json
└─────────────────┘

Testing Flow:
┌─────────────────┐
│ Click Test Btn  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Create packet   │
│ with duration   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Send UDP to     │
│ device          │
└─────────────────┘
```

## Component Responsibilities

### HapticsOutput
- Store device configuration (IP, port, OSC path)
- Generate SlimeVR packets
- Maintain packet sequence counter
- Send UDP packets

### HapticsGUI
- Main application window
- Manage multiple HapticsOutput instances
- Run OSC server in background thread
- Handle configuration persistence
- Provide test functionality

### OSC Server (Thread)
- Listen on configurable port
- Parse incoming OSC messages
- Route messages to correct output
- Convert OSC values to durations
- Non-blocking operation

## Data Flow

1. VR app sends OSC message: `/avatar/parameters/leftPawTouched = True`
2. OSC server receives and parses message
3. OSC handler maps value: `True → 100ms`
4. HapticsOutput builds packet:
   - Packet ID: [0, 0, 0]
   - Type: 2 (Vibrate)
   - Sequence: auto-increment
   - Duration: 100 (0x0064 BE)
5. UDP socket sends 14-byte packet to device
6. Device vibrates for 100ms
