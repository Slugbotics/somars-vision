"""
YOLO Detector for SUAS Competition
Supports camera/video feed input for real-time object detection
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import argparse
import sys


class YOLODetector:
    """YOLO object detector with camera/video feed support"""
    
    def __init__(self, model_path='yolov8n.pt', conf_threshold=0.25, iou_threshold=0.45):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLO model weights
            conf_threshold: Confidence threshold for detections
            iou_threshold: IOU threshold for NMS
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        
    def detect_from_camera(self, camera_index=0, display=True, save_output=False, output_path='output.mp4'):
        """
        Run detection on camera feed
        
        Args:
            camera_index: Camera device index (0 for default camera)
            display: Whether to display the output
            save_output: Whether to save the output video
            output_path: Path to save output video
        """
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            return
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        
        # Setup video writer if saving output
        writer = None
        if save_output:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"Starting camera detection (Camera {camera_index})")
        print("Press 'q' to quit")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                
                # Run detection
                results = self.model(frame, conf=self.conf_threshold, iou=self.iou_threshold)
                
                # Draw results on frame
                annotated_frame = results[0].plot()
                
                # Display frame if requested
                if display:
                    cv2.imshow('YOLO Detection - Camera', annotated_frame)
                    
                # Save frame if requested
                if writer:
                    writer.write(annotated_frame)
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            cap.release()
            if writer:
                writer.release()
            if display:
                cv2.destroyAllWindows()
            print("Camera detection stopped")
    
    def detect_from_video(self, video_path, display=True, save_output=False, output_path='output.mp4'):
        """
        Run detection on video file
        
        Args:
            video_path: Path to video file
            display: Whether to display the output
            save_output: Whether to save the output video
            output_path: Path to save output video
        """
        if not Path(video_path).exists():
            print(f"Error: Video file not found: {video_path}")
            return
            
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Setup video writer if saving output
        writer = None
        if save_output:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"Processing video: {video_path}")
        print(f"Resolution: {width}x{height}, FPS: {fps}, Frames: {total_frames}")
        print("Press 'q' to quit")
        
        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Run detection
                results = self.model(frame, conf=self.conf_threshold, iou=self.iou_threshold)
                
                # Draw results on frame
                annotated_frame = results[0].plot()
                
                # Display frame if requested
                if display:
                    cv2.imshow('YOLO Detection - Video', annotated_frame)
                    
                # Save frame if requested
                if writer:
                    writer.write(annotated_frame)
                
                # Print progress
                if frame_count % 30 == 0:
                    progress = (frame_count / total_frames) * 100
                    print(f"Progress: {frame_count}/{total_frames} frames ({progress:.1f}%)")
                
                # Check for quit key
                if display and cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        finally:
            cap.release()
            if writer:
                writer.release()
            if display:
                cv2.destroyAllWindows()
            print(f"Video processing completed: {frame_count} frames processed")
    
    def detect_from_image(self, image_path, display=True, save_output=False, output_path='output.jpg'):
        """
        Run detection on single image
        
        Args:
            image_path: Path to image file
            display: Whether to display the output
            save_output: Whether to save the output image
            output_path: Path to save output image
        """
        if not Path(image_path).exists():
            print(f"Error: Image file not found: {image_path}")
            return
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image {image_path}")
            return
        
        print(f"Processing image: {image_path}")
        
        # Run detection
        results = self.model(image, conf=self.conf_threshold, iou=self.iou_threshold)
        
        # Draw results on image
        annotated_image = results[0].plot()
        
        # Display if requested
        if display:
            cv2.imshow('YOLO Detection - Image', annotated_image)
            print("Press any key to close")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # Save if requested
        if save_output:
            cv2.imwrite(output_path, annotated_image)
            print(f"Output saved to: {output_path}")
        
        print("Image processing completed")


def main():
    """Main entry point for the detector"""
    parser = argparse.ArgumentParser(description='YOLO Object Detection for SUAS Competition')
    parser.add_argument('--source', type=str, required=True,
                       help='Input source: camera index (0), video file path, or image file path')
    parser.add_argument('--model', type=str, default='yolov8n.pt',
                       help='Path to YOLO model weights (default: yolov8n.pt)')
    parser.add_argument('--conf', type=float, default=0.25,
                       help='Confidence threshold (default: 0.25)')
    parser.add_argument('--iou', type=float, default=0.45,
                       help='IOU threshold for NMS (default: 0.45)')
    parser.add_argument('--no-display', action='store_true',
                       help='Do not display output')
    parser.add_argument('--save', action='store_true',
                       help='Save output to file')
    parser.add_argument('--output', type=str, default='output',
                       help='Output file path (without extension)')
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = YOLODetector(
        model_path=args.model,
        conf_threshold=args.conf,
        iou_threshold=args.iou
    )
    
    # Determine input type and run detection
    source = args.source
    display = not args.no_display
    
    # Check if source is a camera index
    if source.isdigit():
        camera_index = int(source)
        output_path = f"{args.output}.mp4"
        detector.detect_from_camera(
            camera_index=camera_index,
            display=display,
            save_output=args.save,
            output_path=output_path
        )
    # Check if source is a video file
    elif Path(source).suffix.lower() in ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']:
        output_path = f"{args.output}.mp4"
        detector.detect_from_video(
            video_path=source,
            display=display,
            save_output=args.save,
            output_path=output_path
        )
    # Assume source is an image file
    else:
        output_path = f"{args.output}.jpg"
        detector.detect_from_image(
            image_path=source,
            display=display,
            save_output=args.save,
            output_path=output_path
        )


if __name__ == "__main__":
    main()
