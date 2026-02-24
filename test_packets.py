#!/usr/bin/env python3
"""
Test script for OSC to UDP Haptics Converter
Validates packet structure and basic functionality
"""

import struct
import sys
import os


class HapticsOutput:
    """Represents a single haptics output configuration (test version)"""
    
    def __init__(self, output_id):
        self.output_id = output_id
        self.packet_id = [0, 0, 0]  # 3-byte packet ID
        self.packet_number = 0
        
    def create_vibrate_packet(self, duration_ms):
        """
        Create a SlimeVR Vibrate packet
        
        Packet structure (14 bytes):
        - Bytes 0-2: Packet ID (uint8[3])
        - Byte 3: Packet Type (2 = Vibrate)
        - Bytes 4-11: Packet Number (uint64 BigEndian)
        - Bytes 12-13: Duration in milliseconds (uint16 BigEndian)
        """
        # Ensure duration is within valid range
        duration_ms = max(0, min(65535, int(duration_ms)))
        
        # Build packet
        packet = bytearray()
        
        # Packet ID (3 bytes)
        packet.extend(self.packet_id)
        
        # Packet Type (1 byte) - 2 for Vibrate
        packet.append(2)
        
        # Packet Number (8 bytes, BigEndian uint64)
        packet.extend(struct.pack('>Q', self.packet_number))
        self.packet_number += 1
        
        # Duration (2 bytes, BigEndian uint16)
        packet.extend(struct.pack('>H', duration_ms))
        
        return bytes(packet)


def test_packet_structure():
    """Test that packets are created with correct structure"""
    print("Testing packet structure...")
    
    output = HapticsOutput(0)
    
    # Test with various durations
    test_cases = [
        (0, "Zero duration (stop vibration)"),
        (100, "100ms vibration"),
        (500, "500ms vibration"),
        (1000, "1 second vibration"),
        (65535, "Maximum duration (65535ms)"),
    ]
    
    for duration, description in test_cases:
        print(f"\n{description}:")
        packet = output.create_vibrate_packet(duration)
        
        # Verify packet size
        assert len(packet) == 14, f"Packet size should be 14 bytes, got {len(packet)}"
        print(f"  ✓ Packet size: {len(packet)} bytes")
        
        # Verify packet structure
        # Bytes 0-2: Packet ID
        packet_id = packet[0:3]
        print(f"  ✓ Packet ID: {list(packet_id)}")
        
        # Byte 3: Packet Type (should be 2)
        packet_type = packet[3]
        assert packet_type == 2, f"Packet type should be 2, got {packet_type}"
        print(f"  ✓ Packet Type: {packet_type} (Vibrate)")
        
        # Bytes 4-11: Packet Number (BigEndian uint64)
        packet_number = struct.unpack('>Q', packet[4:12])[0]
        print(f"  ✓ Packet Number: {packet_number}")
        
        # Bytes 12-13: Duration (BigEndian uint16)
        packet_duration = struct.unpack('>H', packet[12:14])[0]
        assert packet_duration == duration, f"Duration should be {duration}, got {packet_duration}"
        print(f"  ✓ Duration: {packet_duration} ms")
        
        # Print hex dump
        hex_dump = ' '.join(f'{b:02x}' for b in packet)
        print(f"  Hex: {hex_dump}")
    
    print("\n✓ All packet structure tests passed!")


def test_packet_sequence():
    """Test that packet numbers increment"""
    print("\n\nTesting packet sequence...")
    
    output = HapticsOutput(0)
    
    prev_number = -1
    for i in range(5):
        packet = output.create_vibrate_packet(100)
        packet_number = struct.unpack('>Q', packet[4:12])[0]
        
        if prev_number >= 0:
            assert packet_number == prev_number + 1, \
                f"Packet number should increment: {prev_number} -> {packet_number}"
        
        print(f"  Packet {i}: Number = {packet_number}")
        prev_number = packet_number
    
    print("\n✓ Packet sequence test passed!")


def test_duration_clamping():
    """Test that duration is clamped to valid range"""
    print("\n\nTesting duration clamping...")
    
    output = HapticsOutput(0)
    
    # Test negative duration (should clamp to 0)
    packet = output.create_vibrate_packet(-100)
    duration = struct.unpack('>H', packet[12:14])[0]
    assert duration == 0, f"Negative duration should clamp to 0, got {duration}"
    print(f"  ✓ Negative duration (-100) clamped to: {duration}")
    
    # Test duration > 65535 (should clamp to 65535)
    packet = output.create_vibrate_packet(100000)
    duration = struct.unpack('>H', packet[12:14])[0]
    assert duration == 65535, f"Duration > 65535 should clamp to 65535, got {duration}"
    print(f"  ✓ Large duration (100000) clamped to: {duration}")
    
    print("\n✓ Duration clamping test passed!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("OSC to UDP Haptics Converter - Packet Tests")
    print("=" * 60)
    
    try:
        test_packet_structure()
        test_packet_sequence()
        test_duration_clamping()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
