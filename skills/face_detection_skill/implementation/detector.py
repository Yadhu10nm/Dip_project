import os
import urllib.request
import cv2
import numpy as np
from typing import List, Optional
import config
from skills.common.types import FaceDetection


class FaceDetectionSkill:
    """
    Advanced Multi-Face Detection Skill.
    Ensemble Architecture:
    1. Primary: OpenCV YuNet Deep Neural Network Face Detector (cv2.FaceDetectorYN).
       High precision across varied head yaw, pitch, tilt, low-light, and multi-face scenes.
    2. Resilient Fallback: Optimized Haar Feature-based Cascade Classifier with CLAHE.

    STRICT RULE:
    Only identifies candidate HUMAN FACE regions.
    Does not detect arbitrary non-face objects.
    """

    YUNET_DOWNLOAD_URL = (
        "https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_detection_yunet/face_detection_yunet_2023mar.onnx"
    )

    def __init__(
        self,
        yunet_path: Optional[str] = None,
        cascade_path: Optional[str] = None,
        confidence_threshold: float = config.YUNET_CONFIDENCE_THRESHOLD,
        scale_factor: float = config.HAAR_SCALE_FACTOR,
        min_neighbors: int = config.HAAR_MIN_NEIGHBORS,
        min_size: tuple = config.FACE_MIN_SIZE,
    ):
        self.yunet_path = yunet_path or config.YUNET_MODEL_PATH
        self.confidence_threshold = confidence_threshold
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size

        self.yunet_detector = None
        self._init_yunet()

        # Initialize Haar Cascade Fallback
        if cascade_path is None:
            cascade_path = os.path.join(
                cv2.data.haarcascades, "haarcascade_frontalface_default.xml"
            )
        self.cascade = cv2.CascadeClassifier(cascade_path)
        self.classifier = self.cascade  # Backward compatibility alias & test mocking point

        self.clahe = cv2.createCLAHE(
            clipLimit=config.CLAHE_CLIP_LIMIT,
            tileGridSize=config.CLAHE_TILE_GRID_SIZE,
        )

    def _init_yunet(self):
        """Initializes OpenCV YuNet face detector model with auto-download if needed."""
        try:
            if not os.path.exists(self.yunet_path):
                os.makedirs(os.path.dirname(self.yunet_path), exist_ok=True)
                req = urllib.request.Request(
                    self.YUNET_DOWNLOAD_URL,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as response, open(self.yunet_path, 'wb') as out_file:
                    out_file.write(response.read())

            if os.path.exists(self.yunet_path):
                # Default size (320, 320), dynamically updated on incoming frame shape
                self.yunet_detector = cv2.FaceDetectorYN.create(
                    self.yunet_path,
                    "",
                    (320, 320),
                    score_threshold=self.confidence_threshold,
                    nms_threshold=0.3,
                    top_k=5000,
                )
        except Exception as e:
            print(f"[FaceDetectionSkill] YuNet initialization notice: {e}. Using Haar fallback.")
            self.yunet_detector = None

    def detect_faces(self, frame: np.ndarray) -> List[FaceDetection]:
        """
        Detects multiple human faces in the video frame.
        Input: BGR or Grayscale frame (np.ndarray)
        Output: List[FaceDetection]
        """
        if frame is None or frame.size == 0:
            return []

        h, w = frame.shape[:2]

        # 1. Primary: YuNet Deep Neural Network Face Detector
        if self.yunet_detector is not None:
            try:
                # Ensure BGR input for YuNet
                if len(frame.shape) == 2:
                    bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                else:
                    bgr = frame

                self.yunet_detector.setInputSize((w, h))
                _, faces = self.yunet_detector.detect(bgr)

                if faces is not None and len(faces) > 0:
                    detections = []
                    for face in faces:
                        fx = max(0, int(face[0]))
                        fy = max(0, int(face[1]))
                        fw = min(w - fx, int(face[2]))
                        fh = min(h - fy, int(face[3]))
                        score = float(face[14]) if len(face) > 14 else 1.0

                        if fw >= self.min_size[0] and fh >= self.min_size[1]:
                            lmarks = [float(v) for v in face[4:14]] if len(face) >= 14 else None
                            detections.append(
                                FaceDetection(
                                    x=fx,
                                    y=fy,
                                    width=fw,
                                    height=fh,
                                    confidence=round(score, 3),
                                    landmarks=lmarks,
                                    raw_face=face.copy() if hasattr(face, "copy") else face,
                                )
                            )
                    if detections:
                        return detections
            except Exception as e:
                # Fall back to Haar Cascade if YuNet evaluation encounters an error
                pass

        # 2. Resilient Fallback: Haar Cascade Multi-Scale
        return self._detect_haar_fallback(frame)

    def _detect_haar_fallback(self, frame: np.ndarray) -> List[FaceDetection]:
        """Haar Cascade fallback face detection."""
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame.copy()

        # Run on standard grayscale for clean edge gradients
        faces = self.classifier.detectMultiScale(
            gray,
            scaleFactor=self.scale_factor,
            minNeighbors=self.min_neighbors,
            minSize=self.min_size,
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        detections = []
        for (x, y, w, h) in faces:
            detections.append(
                FaceDetection(
                    x=int(x),
                    y=int(y),
                    width=int(w),
                    height=int(h),
                    confidence=1.0,
                )
            )

        return detections
