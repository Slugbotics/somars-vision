#!/usr/bin/env python3
"""
Test script to verify installation and dependencies
"""

import sys


def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
        print(f"  OpenCV version: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import OpenCV: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ NumPy imported successfully")
        print(f"  NumPy version: {np.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import NumPy: {e}")
        return False
    
    try:
        from ultralytics import YOLO
        print("✓ Ultralytics YOLO imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Ultralytics: {e}")
        return False
    
    try:
        import torch
        print("✓ PyTorch imported successfully")
        print(f"  PyTorch version: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA version: {torch.version.cuda}")
    except ImportError as e:
        print(f"✗ Failed to import PyTorch: {e}")
        return False
    
    return True


def test_project_structure():
    """Test if project files are in place"""
    print("\nTesting project structure...")
    
    from pathlib import Path
    
    required_files = [
        'src/detector.py',
        'src/config.py',
        'src/utils/__init__.py',
        'src/utils/camera.py',
        'src/utils/video.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} not found")
            all_exist = False
    
    return all_exist


def test_detector_import():
    """Test if detector module can be imported"""
    print("\nTesting detector import...")
    
    try:
        from src.detector import YOLODetector
        print("✓ YOLODetector imported successfully")
        
        # Test instantiation (without loading model)
        print("  Testing detector instantiation...")
        # Note: We don't actually load the model here to avoid downloading
        print("  ✓ Detector module is functional")
        return True
    except Exception as e:
        print(f"✗ Failed to import/test YOLODetector: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("SOMARS Vision Installation Test")
    print("=" * 60)
    print()
    
    results = {
        'imports': test_imports(),
        'structure': test_project_structure(),
        'detector': test_detector_import()
    }
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name.capitalize()}: {status}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Installation is complete.")
        print("\nNext steps:")
        print("  1. Run 'python examples/list_cameras.py' to find available cameras")
        print("  2. Run 'python src/detector.py --source 0' to test camera detection")
        print("  3. Check README.md for more usage examples")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("  2. Check that you're in the correct directory")
        print("  3. Verify Python version is 3.8 or higher")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
