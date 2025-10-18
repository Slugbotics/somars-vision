# Quick Start Guide

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Slugbotics/somars-vision.git
   cd somars-vision
   ```

2. **Set up Python virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Test installation**:
   ```bash
   python test_installation.py
   ```

## First Run

### Camera Detection (Real-time)

1. **List available cameras**:
   ```bash
   python examples/list_cameras.py
   ```

2. **Start camera detection** (using default camera):
   ```bash
   python src/detector.py --source 0
   ```
   
   Or use the example script:
   ```bash
   python examples/run_camera_detection.py
   ```

3. **Press 'q' to quit**

### Video File Detection

1. **Process a video file**:
   ```bash
   python src/detector.py --source path/to/your/video.mp4 --save
   ```

   Or use the example script:
   ```bash
   python examples/run_video_detection.py path/to/your/video.mp4
   ```

### Image Detection

```bash
python src/detector.py --source path/to/your/image.jpg --save
```

## Common Use Cases

### SUAS Competition - Drone Camera Feed

For real-time detection from a drone-mounted camera:

```bash
# Adjust camera index based on your setup (0, 1, 2, etc.)
python src/detector.py --source 0 --conf 0.3 --save --output suas_flight
```

### Record and Process Later

1. **Record raw video** (without detection for better performance):
   ```bash
   # Your drone's recording software saves to video.mp4
   ```

2. **Process recorded video**:
   ```bash
   python src/detector.py --source video.mp4 --save --output analyzed_flight
   ```

### High Accuracy Mode

For better detection accuracy (slower):

```bash
python src/detector.py --source 0 --model yolov8m.pt --conf 0.3
```

### Fast Performance Mode

For faster detection (less accurate):

```bash
python src/detector.py --source 0 --model yolov8n.pt --conf 0.25
```

## Troubleshooting

### "No module named 'cv2'"
Install OpenCV: `pip install opencv-python`

### "Camera not found" or black screen
- Check if camera is connected
- Try different camera indices: 0, 1, 2
- Run `python examples/list_cameras.py`
- Check camera permissions

### Slow performance
- Use smaller model: `--model yolov8n.pt`
- Reduce camera resolution in `src/config.py`
- Use GPU acceleration (requires CUDA setup)

### Model download issues
- Ensure internet connection
- Models auto-download on first run
- Check `weights/` directory

## Next Steps

1. Review `README.md` for detailed documentation
2. Customize detection settings in `src/config.py`
3. Modify SUAS-specific classes in `src/config.py`
4. Integrate with your drone control system
5. Test with real SUAS competition scenarios

## Support

For issues or questions:
- Open an issue on GitHub
- Contact Slugbotics team
- Check competition documentation
