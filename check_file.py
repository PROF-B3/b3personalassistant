#!/usr/bin/env python3
"""Check for null bytes in video_processing.py"""

with open('modules/video_processing.py', 'rb') as f:
    data = f.read()
    print(f"File size: {len(data)} bytes")
    print(f"Null bytes found: {data.count(b'\x00')}")
    
    # Find positions of null bytes
    null_positions = [i for i, byte in enumerate(data) if byte == 0]
    if null_positions:
        print(f"Null bytes at positions: {null_positions[:10]}")  # Show first 10
    else:
        print("No null bytes found") 