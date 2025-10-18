"""
Configuration settings for YOLO detector
"""

# Model settings
DEFAULT_MODEL = 'yolov8n.pt'  # Nano model for faster inference
# Other options: yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt

# Detection parameters
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45

# Camera settings
DEFAULT_CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Video processing
VIDEO_BATCH_SIZE = 1  # Process frames in batches for efficiency

# Display settings
DISPLAY_WINDOW_NAME = 'YOLO Detection'
DISPLAY_WAIT_TIME = 1  # milliseconds

# Output settings
DEFAULT_OUTPUT_DIR = 'outputs'
VIDEO_CODEC = 'mp4v'
IMAGE_FORMAT = 'jpg'

# SUAS Competition specific classes (customize based on competition requirements)
SUAS_CLASSES = {
    'standard': [
        'person',
        'bicycle',
        'car',
        'motorcycle',
        'airplane',
        'bus',
        'train',
        'truck',
        'boat',
        'traffic light',
        'fire hydrant',
        'stop sign',
        'parking meter',
        'bench',
        'bird',
        'cat',
        'dog',
        'horse',
        'sheep',
        'cow',
        'elephant',
        'bear',
        'zebra',
        'giraffe',
    ]
}
