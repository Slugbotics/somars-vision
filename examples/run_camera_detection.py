#!/usr/bin/env python3
"""
Example script for running YOLO detection on camera feed
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detector import YOLODetector


def main():
    """Run detection on default camera (index 0)"""
    
    print("=" * 60)
    print("YOLO Camera Detection Example")
    print("=" * 60)
    
    # Initialize detector with nano model for faster inference
    detector = YOLODetector(
        model_path='yolov8n.pt',  # Nano model will be downloaded automatically
        conf_threshold=0.25,
        iou_threshold=0.45
    )
    
    print("\nStarting camera detection...")
    print("Press 'q' to quit\n")
    
    # Run detection on default camera (0)
    detector.detect_from_camera(
        camera_index=0,
        display=True,
        save_output=False
    )


if __name__ == "__main__":
    main()
