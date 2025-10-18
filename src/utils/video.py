"""
Video processing utilities
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


class VideoProcessor:
    """Handler for video file processing"""
    
    def __init__(self, video_path: str):
        """
        Initialize video processor
        
        Args:
            video_path: Path to video file
        """
        self.video_path = Path(video_path)
        self.cap = None
        self.is_opened = False
        self.properties = {}
        
    def open(self) -> bool:
        """
        Open video file
        
        Returns:
            True if video opened successfully, False otherwise
        """
        if not self.video_path.exists():
            print(f"Video file not found: {self.video_path}")
            return False
        
        self.cap = cv2.VideoCapture(str(self.video_path))
        self.is_opened = self.cap.isOpened()
        
        if self.is_opened:
            self._read_properties()
            print(f"Video opened: {self.video_path}")
            print(f"Properties: {self.properties}")
        else:
            print(f"Failed to open video: {self.video_path}")
            
        return self.is_opened
    
    def _read_properties(self):
        """Read video properties"""
        if not self.is_opened:
            return
        
        self.properties = {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'frame_count': int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'codec': int(self.cap.get(cv2.CAP_PROP_FOURCC))
        }
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read next frame from video
        
        Returns:
            Tuple of (success, frame)
        """
        if not self.is_opened:
            return False, None
            
        ret, frame = self.cap.read()
        return ret, frame
    
    def get_properties(self) -> dict:
        """
        Get video properties
        
        Returns:
            Dictionary of video properties
        """
        return self.properties
    
    def get_current_frame_number(self) -> int:
        """
        Get current frame number
        
        Returns:
            Current frame number
        """
        if not self.is_opened:
            return -1
        
        return int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
    
    def seek_to_frame(self, frame_number: int) -> bool:
        """
        Seek to specific frame
        
        Args:
            frame_number: Frame number to seek to
            
        Returns:
            True if seek successful
        """
        if not self.is_opened:
            return False
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        return True
    
    def release(self):
        """Release video resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            print(f"Video released: {self.video_path}")
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()


class VideoWriter:
    """Handler for writing video output"""
    
    def __init__(self, output_path: str, fps: int, width: int, height: int, codec: str = 'mp4v'):
        """
        Initialize video writer
        
        Args:
            output_path: Output video path
            fps: Frames per second
            width: Frame width
            height: Frame height
            codec: Video codec (default: mp4v)
        """
        self.output_path = Path(output_path)
        self.fps = fps
        self.width = width
        self.height = height
        self.codec = codec
        self.writer = None
        self.is_opened = False
        
    def open(self) -> bool:
        """
        Open video writer
        
        Returns:
            True if writer opened successfully
        """
        # Create output directory if it doesn't exist
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        self.writer = cv2.VideoWriter(
            str(self.output_path),
            fourcc,
            self.fps,
            (self.width, self.height)
        )
        
        self.is_opened = self.writer.isOpened()
        
        if self.is_opened:
            print(f"Video writer opened: {self.output_path}")
        else:
            print(f"Failed to open video writer: {self.output_path}")
            
        return self.is_opened
    
    def write_frame(self, frame: np.ndarray) -> bool:
        """
        Write frame to video
        
        Args:
            frame: Frame to write
            
        Returns:
            True if frame written successfully
        """
        if not self.is_opened:
            return False
        
        self.writer.write(frame)
        return True
    
    def release(self):
        """Release writer resources"""
        if self.writer is not None:
            self.writer.release()
            self.is_opened = False
            print(f"Video writer released: {self.output_path}")
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()
