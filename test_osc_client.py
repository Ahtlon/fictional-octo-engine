#!/usr/bin/env python3
"""
OSC Test Client - Send test OSC messages to the haptics converter
"""

from pythonosc import udp_client
import time
import argparse


def send_test_messages(ip="127.0.0.1", port=9001):
    """Send test OSC messages"""
    client = udp_client.SimpleUDPClient(ip, port)
    
    print(f"Sending test OSC messages to {ip}:{port}")
    print("-" * 50)
    
    # Test cases
    test_cases = [
        ("/avatar/parameters/leftPawTouched", True, "Boolean True (should vibrate 100ms)"),
        ("/avatar/parameters/rightPawTouched", 0.5, "Float 0.5 (should vibrate 250ms)"),
        ("/avatar/parameters/headTouch", 1000, "Integer 1000 (should vibrate 1000ms)"),
        ("/avatar/parameters/leftPawTouched", False, "Boolean False (should stop)"),
    ]
    
    for path, value, description in test_cases:
        print(f"\n{description}")
        print(f"  Path: {path}")
        print(f"  Value: {value}")
        client.send_message(path, value)
        print(f"  ✓ Sent")
        time.sleep(2)
    
    print("\n" + "-" * 50)
    print("All test messages sent!")


def main():
    parser = argparse.ArgumentParser(description="Send test OSC messages")
    parser.add_argument("--ip", default="127.0.0.1", help="OSC server IP")
    parser.add_argument("--port", type=int, default=9001, help="OSC server port")
    
    args = parser.parse_args()
    
    try:
        send_test_messages(args.ip, args.port)
    except KeyboardInterrupt:
        print("\nAborted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
