import cv2
import os
import numpy as np
import config
from core.dip_engine import DIPEngine

class FaceDetector:
    """
    Face detection using Haar feature-based cascade classifier
    coupled with DIP preprocessing (CLAHE) for high detection accuracy in diverse lighting.
    """

    def __init__(self, dip_engine: DIPEngine = None):
        self.dip_engine = dip_engine or DIPEngine()
        cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        if not os.path.exists(cascade_path):
            raise FileNotFoundError(f"Haar cascade XML not found at {cascade_path}")
        self.cascade = cv2.CascadeClassifier(cascade_path)

    def detect_faces(self, frame: np.ndarray):
        """
        Detects faces in frame. Returns a list of (x, y, w, h) bounding boxes.
        Applies CLAHE first to normalize lighting variations.
        """
        gray = self.dip_engine.to_grayscale(frame)
        enhanced_gray = self.dip_engine.apply_clahe(gray)

        faces = self.cascade.detectMultiScale(
            enhanced_gray,
            scaleFactor=config.HAAR_SCALE_FACTOR,
            minNeighbors=config.HAAR_MIN_NEIGHBORS,
            minSize=config.FACE_MIN_SIZE,
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        return list(faces)

    def extract_face_roi(self, frame: np.ndarray, bbox, margin_ratio=0.08):
        """
        Extracts face ROI with optional margin padding.
        Returns:
            face_roi: np.ndarray, cropped image
            safe_bbox: (x, y, w, h) adjusted bounding box inside frame boundary
        """
        h_frame, w_frame = frame.shape[:2]
        x, y, w, h = bbox

        # Margin expansion
        pad_x = int(w * margin_ratio)
        pad_y = int(h * margin_ratio)

        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(w_frame, x + w + pad_x)
        y2 = min(h_frame, y + h + pad_y)

        face_roi = frame[y1:y2, x1:x2]
        safe_bbox = (x1, y1, x2 - x1, y2 - y1)
        return face_roi, safe_bbox
