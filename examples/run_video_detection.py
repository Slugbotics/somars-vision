#!/usr/bin/env python3
"""
Example script for running YOLO detection on video file
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detector import YOLODetector


def main():
    """Run detection on video file"""
    
    print("=" * 60)
    print("YOLO Video Detection Example")
    print("=" * 60)
    
    # Get video path from command line or use default
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        print("Usage: python run_video_detection.py <video_path>")
        print("Example: python run_video_detection.py ../data/sample_videos/test.mp4")
        sys.exit(1)
    
    # Initialize detector
    detector = YOLODetector(
        model_path='yolov8n.pt',
        conf_threshold=0.25,
        iou_threshold=0.45
    )
    
    print(f"\nProcessing video: {video_path}")
    print("Press 'q' to quit\n")
    
    # Run detection on video
    detector.detect_from_video(
        video_path=video_path,
        display=True,
        save_output=True,
        output_path='output_video.mp4'
    )
    
    print("\nDetection completed!")


if __name__ == "__main__":
    main()
