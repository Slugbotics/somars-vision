# SOMARS Vision - YOLO Object Detection for SUAS Competition

A computer vision system built with YOLOv8 for the Student Unmanned Aerial Systems (SUAS) competition. This system supports real-time object detection from camera feeds, video files, and images.

## Features

- **Camera Feed Support**: Real-time detection from USB cameras, webcams, or other video capture devices
- **Video File Processing**: Process pre-recorded video files with object detection
- **Image Detection**: Run detection on single images
- **Flexible Model Support**: Compatible with all YOLOv8 models (nano, small, medium, large, extra-large)
- **Configurable Detection**: Adjustable confidence and IOU thresholds
- **Output Options**: Display results in real-time and/or save to files
- **Utility Modules**: Camera handling and video processing utilities

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster inference

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Slugbotics/somars-vision.git
cd somars-vision
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

The first time you run detection, YOLOv8 will automatically download the model weights.

## Usage

### Command Line Interface

The main detector script supports various input sources:

#### Camera Feed Detection
```bash
# Use default camera (index 0)
python src/detector.py --source 0

# Use specific camera
python src/detector.py --source 1

# Save output video
python src/detector.py --source 0 --save --output camera_output
```

#### Video File Detection
```bash
# Process video file
python src/detector.py --source path/to/video.mp4

# Process and save output
python src/detector.py --source video.mp4 --save --output processed_video
```

#### Image Detection
```bash
# Process single image
python src/detector.py --source path/to/image.jpg --save
```

### Advanced Options

```bash
python src/detector.py \
    --source 0 \
    --model yolov8s.pt \
    --conf 0.3 \
    --iou 0.5 \
    --save \
    --output detection_results
```

**Parameters:**
- `--source`: Input source (camera index, video file, or image file)
- `--model`: YOLO model to use (default: yolov8n.pt)
  - Options: yolov8n.pt (fastest), yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt (most accurate)
- `--conf`: Confidence threshold (default: 0.25)
- `--iou`: IOU threshold for NMS (default: 0.45)
- `--no-display`: Don't display output window
- `--save`: Save output to file
- `--output`: Output file path (without extension)

### Example Scripts

#### List Available Cameras
```bash
python examples/list_cameras.py
```

#### Run Camera Detection
```bash
python examples/run_camera_detection.py
```

#### Run Video Detection
```bash
python examples/run_video_detection.py path/to/video.mp4
```

### Python API

You can also use the detector programmatically:

```python
from src.detector import YOLODetector

# Initialize detector
detector = YOLODetector(
    model_path='yolov8n.pt',
    conf_threshold=0.25,
    iou_threshold=0.45
)

# Camera detection
detector.detect_from_camera(camera_index=0, display=True, save_output=True)

# Video detection
detector.detect_from_video(
    video_path='video.mp4',
    display=True,
    save_output=True,
    output_path='output.mp4'
)

# Image detection
detector.detect_from_image(
    image_path='image.jpg',
    display=True,
    save_output=True,
    output_path='output.jpg'
)
```

## Project Structure

```
somars-vision/
├── src/
│   ├── detector.py          # Main detection script
│   ├── config.py            # Configuration settings
│   └── utils/
│       ├── __init__.py
│       ├── camera.py        # Camera handling utilities
│       └── video.py         # Video processing utilities
├── examples/
│   ├── run_camera_detection.py
│   ├── run_video_detection.py
│   └── list_cameras.py
├── data/                    # Data directory for samples
├── weights/                 # Model weights directory
├── requirements.txt         # Python dependencies
└── README.md
```

## Configuration

Edit `src/config.py` to customize default settings:

- Model paths and types
- Detection thresholds
- Camera resolution and FPS
- Output formats
- SUAS competition-specific class filters

## Troubleshooting

### Camera Not Found
- Verify camera is connected and not in use by another application
- Check camera permissions (may need sudo on Linux)
- Run `examples/list_cameras.py` to see available cameras
- Try different camera indices (0, 1, 2, etc.)

### Slow Performance
- Use a smaller model (yolov8n.pt is fastest)
- Reduce camera resolution in config
- Enable GPU acceleration (requires CUDA setup)
- Lower the confidence threshold

### Model Download Issues
- Ensure internet connection is available
- Models are downloaded automatically on first run
- Check `weights/` directory for downloaded models

## SUAS Competition Notes

This system is designed for the Student Unmanned Aerial Systems competition. Key features for SUAS:

- Real-time detection for autonomous systems
- Camera feed support for drone-mounted cameras
- Configurable detection classes in `src/config.py`
- Efficient processing for embedded systems

Customize the detection classes in `src/config.py` based on your specific competition requirements.

## License

[Add your license information here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub or contact the Slugbotics team.