"""
Camera handling utilities for video feed input
"""

import cv2
import numpy as np
from typing import Optional, Tuple


class CameraHandler:
    """Handler for camera/video capture devices"""
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize camera handler
        
        Args:
            camera_index: Camera device index (0 for default camera)
        """
        self.camera_index = camera_index
        self.cap = None
        self.is_opened = False
        
    def open(self) -> bool:
        """
        Open camera connection
        
        Returns:
            True if camera opened successfully, False otherwise
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        self.is_opened = self.cap.isOpened()
        
        if self.is_opened:
            print(f"Camera {self.camera_index} opened successfully")
        else:
            print(f"Failed to open camera {self.camera_index}")
            
        return self.is_opened
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera
        
        Returns:
            Tuple of (success, frame)
        """
        if not self.is_opened:
            return False, None
            
        ret, frame = self.cap.read()
        return ret, frame
    
    def get_properties(self) -> dict:
        """
        Get camera properties
        
        Returns:
            Dictionary of camera properties
        """
        if not self.is_opened:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'backend': self.cap.getBackendName()
        }
    
    def set_resolution(self, width: int, height: int) -> bool:
        """
        Set camera resolution
        
        Args:
            width: Frame width
            height: Frame height
            
        Returns:
            True if resolution set successfully
        """
        if not self.is_opened:
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Verify the resolution was set
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        if actual_width == width and actual_height == height:
            print(f"Resolution set to {width}x{height}")
            return True
        else:
            print(f"Requested {width}x{height}, got {actual_width}x{actual_height}")
            return False
    
    def set_fps(self, fps: int) -> bool:
        """
        Set camera FPS
        
        Args:
            fps: Frames per second
            
        Returns:
            True if FPS set successfully
        """
        if not self.is_opened:
            return False
        
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        return True
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            print(f"Camera {self.camera_index} released")
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
        
    @staticmethod
    def list_available_cameras(max_cameras: int = 10) -> list:
        """
        List available camera indices
        
        Args:
            max_cameras: Maximum number of cameras to check
            
        Returns:
            List of available camera indices
        """
        available = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()
        
        return available
