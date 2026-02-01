"""
Motion Detector module.
Provides a reusable MotionDetector class for detecting and recording movement.
"""

import os
from datetime import datetime
from typing import Optional, Tuple

import cv2
import numpy as np


class MotionDetector:
    """
    Detects motion from a video source and records when movement is detected.
    
    Usage:
        with MotionDetector(camera_id=0) as detector:
            detector.run()
    """
    
    def __init__(
        self,
        camera_id: int = 0,
        threshold: int = 200000,
        record_buffer_frames: int = 15,
        output_dir: str = "output_files",
        show_preview: bool = True,
    ):
        """
        Initialize the motion detector.
        
        Args:
            camera_id: Camera device ID (default: 0)
            threshold: Motion sensitivity threshold (higher = less sensitive)
            record_buffer_frames: Frames to keep recording after motion stops
            output_dir: Directory to save recordings
            show_preview: Whether to show live preview windows
        """
        self.camera_id = camera_id
        self.threshold = threshold
        self.record_buffer_frames = record_buffer_frames
        self.output_dir = output_dir
        self.show_preview = show_preview
        
        self._video: Optional[cv2.VideoCapture] = None
        self._writer: Optional[cv2.VideoWriter] = None
        self._frame_size: Tuple[int, int] = (0, 0)
        self._last_frame: Optional[np.ndarray] = None
        self._record_buffer: int = 0
        self._is_recording: bool = False
    
    def __enter__(self) -> "MotionDetector":
        """Context manager entry."""
        self._setup()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - cleanup resources."""
        self._cleanup()
    
    def _setup(self) -> None:
        """Initialize video capture and create output directory."""
        self._ensure_output_dir()
        
        self._video = cv2.VideoCapture(self.camera_id)
        if not self._video.isOpened():
            raise RuntimeError(f"Could not open camera {self.camera_id}")
        
        self._frame_size = (
            int(self._video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(self._video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        
        # Read initial frame
        ret, frame = self._video.read()
        if not ret:
            raise RuntimeError("Could not read from camera")
        self._last_frame = frame
    
    def _cleanup(self) -> None:
        """Release all resources."""
        if self._video is not None:
            self._video.release()
            self._video = None
        
        if self._writer is not None:
            self._writer.release()
            self._writer = None
        
        cv2.destroyAllWindows()
    
    def _ensure_output_dir(self) -> None:
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _get_next_filename(self) -> str:
        """Get the next available filename for recording."""
        existing = [f for f in os.listdir(self.output_dir) if f.endswith('.avi')]
        return os.path.join(self.output_dir, f"recording_{len(existing):04d}.avi")
    
    def _start_recording(self) -> None:
        """Start a new recording session."""
        if self._writer is not None:
            self._writer.release()
        
        filename = self._get_next_filename()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self._writer = cv2.VideoWriter(filename, fourcc, 30, self._frame_size)
        self._is_recording = True
        print(f"Recording started: {filename}")
    
    def _stop_recording(self) -> None:
        """Stop the current recording session."""
        if self._writer is not None:
            self._writer.release()
            self._writer = None
        self._is_recording = False
        print("Recording stopped")
    
    def _calculate_motion(self, frame: np.ndarray) -> Tuple[int, np.ndarray]:
        """
        Calculate motion between current and last frame.
        
        Returns:
            Tuple of (motion_value, difference_image)
        """
        gray_curr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_last = cv2.cvtColor(self._last_frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.subtract(gray_curr, gray_last)
        motion = int(np.sum(diff))
        return motion, diff
    
    def _add_overlay(self, frame: np.ndarray, is_moving: bool) -> np.ndarray:
        """Add timestamp and status overlay to frame."""
        frame = frame.copy()
        
        # Timestamp
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        cv2.putText(
            frame, timestamp,
            (self._frame_size[0] - 250, self._frame_size[1] - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )
        
        # Status
        if is_moving:
            status, color = "REC - Moving", (0, 0, 255)
        else:
            status, color = "Standby", (0, 255, 0)
        
        cv2.putText(frame, status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        return frame
    
    def process_frame(self, frame: np.ndarray) -> bool:
        """
        Process a single frame for motion detection.
        
        Args:
            frame: The frame to process
            
        Returns:
            True if motion was detected, False otherwise
        """
        motion, diff = self._calculate_motion(frame)
        motion_detected = motion > self.threshold
        
        # Update recording buffer
        if motion_detected:
            if not self._is_recording:
                self._start_recording()
            self._record_buffer = self.record_buffer_frames
        else:
            self._record_buffer -= 1
            if self._record_buffer <= 0 and self._is_recording:
                self._stop_recording()
        
        # Write frame if recording
        is_moving = self._record_buffer > 0
        if is_moving and self._writer is not None:
            self._writer.write(frame)
        
        # Show preview
        if self.show_preview:
            display_frame = self._add_overlay(frame, is_moving)
            cv2.imshow("Live", display_frame)
            cv2.imshow("Motion", diff)
        
        self._last_frame = frame
        return motion_detected
    
    def run(self) -> None:
        """
        Run the motion detection loop.
        Press 'q' to quit.
        """
        print(f"Motion detection started (threshold={self.threshold})")
        print("Press 'q' to quit")
        
        while True:
            ret, frame = self._video.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            self.process_frame(frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        print("Motion detection stopped")
