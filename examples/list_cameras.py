#!/usr/bin/env python3
"""
Example script to list available cameras
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.camera import CameraHandler


def main():
    """List all available camera devices"""
    
    print("=" * 60)
    print("Available Camera Devices")
    print("=" * 60)
    print("\nScanning for cameras (this may take a moment)...\n")
    
    available_cameras = CameraHandler.list_available_cameras(max_cameras=5)
    
    if available_cameras:
        print(f"Found {len(available_cameras)} camera(s):")
        for idx in available_cameras:
            print(f"\nCamera {idx}:")
            with CameraHandler(idx) as cam:
                properties = cam.get_properties()
                print(f"  Resolution: {properties.get('width', 'N/A')}x{properties.get('height', 'N/A')}")
                print(f"  FPS: {properties.get('fps', 'N/A')}")
                print(f"  Backend: {properties.get('backend', 'N/A')}")
    else:
        print("No cameras found!")
        print("\nTroubleshooting tips:")
        print("  - Check if a camera is connected")
        print("  - Verify camera permissions")
        print("  - Try running with sudo (Linux)")
        print("  - Check if camera is being used by another application")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
