import time
import cv2
import numpy as np
from typing import Optional, Tuple
import config


class CameraSkill:
    """
    Frame Acquisition Skill.
    Responsible exclusively for acquiring video frames from webcam or CCTV streams,
    managing device lifecycle, applying optional mirroring, and throttling frame rate.
    """

    def __init__(
        self,
        camera_index: int = config.CAMERA_INDEX,
        width: int = config.FRAME_WIDTH,
        height: int = config.FRAME_HEIGHT,
        target_fps: int = config.TARGET_FPS,
        flip_horizontal: bool = config.CAMERA_FLIP,
        flip_code: int = config.CAMERA_FLIP_CODE,
    ):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.target_fps = target_fps
        self.flip_horizontal = flip_horizontal
        self.flip_code = flip_code

        self._cap: Optional[cv2.VideoCapture] = None
        self._is_running = False
        self._last_frame_time = 0.0
        self._frame_interval = 1.0 / max(1, target_fps)

    def start(self) -> bool:
        """Opens camera capture device safely."""
        if self._is_running and self._cap is not None and self._cap.isOpened():
            return True

        # Try DirectShow first on Windows for faster webcam initialization
        self._cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self._cap.isOpened():
            # Fall back to default backend
            self._cap = cv2.VideoCapture(self.camera_index)

        if self._cap.isOpened():
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self._cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            self._is_running = True
            return True

        self._is_running = False
        return False

    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Captures a single frame, optionally mirrors it, and throttles to target FPS.
        Returns:
            (success: bool, frame: Optional[np.ndarray])
        """
        # Throttle frame rate
        now = time.time()
        elapsed = now - self._last_frame_time
        if elapsed < self._frame_interval:
            time.sleep(max(0.0, self._frame_interval - elapsed))

        if not self._is_running or self._cap is None or not self._cap.isOpened():
            # Fallback synthetic frame if camera unavailable (e.g. CI or unit testing)
            fallback = self._generate_fallback_frame()
            self._last_frame_time = time.time()
            return False, fallback

        ret, frame = self._cap.read()
        self._last_frame_time = time.time()

        if not ret or frame is None or frame.size == 0:
            return False, self._generate_fallback_frame()

        if self.flip_horizontal:
            frame = cv2.flip(frame, self.flip_code)

        return True, frame

    def toggle_flip(self) -> bool:
        """Toggles horizontal mirror flipping."""
        self.flip_horizontal = not self.flip_horizontal
        return self.flip_horizontal

    def is_opened(self) -> bool:
        """Check if camera device is active and opened."""
        return self._is_running and self._cap is not None and self._cap.isOpened()

    def stop(self):
        """Safely releases the camera resource."""
        self._is_running = False
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    def _generate_fallback_frame(self) -> np.ndarray:
        """Generates placeholder dark frame when camera is not connected."""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        cv2.putText(
            frame,
            "CAMERA SIGNAL OFFLINE / STANDBY",
            (self.width // 2 - 180, self.height // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 200),
            2,
            cv2.LINE_AA,
        )
        return frame
