from typing import Tuple, Union
import cv2
import numpy as np
import config
from skills.common.types import FaceDetection, ProcessedFace


class FacePreprocessingSkill:
    """
    Face Preprocessing Skill.
    Extracts strictly detected face regions, normalizes illumination with CLAHE,
    applies edge-preserving bilateral filtering, and canonicalizes dimensions.

    STRICT RULE:
    Never accept arbitrary whole frames or unlocalized regions as valid faces.
    """

    def __init__(
        self,
        target_size: Tuple[int, int] = config.STANDARD_FACE_SIZE,
        margin_ratio: float = 0.08,
        use_bilateral: bool = True,
    ):
        self.target_size = target_size
        self.margin_ratio = margin_ratio
        self.use_bilateral = use_bilateral
        self.clahe = cv2.createCLAHE(
            clipLimit=config.CLAHE_CLIP_LIMIT,
            tileGridSize=config.CLAHE_TILE_GRID_SIZE,
        )

    def preprocess_face(
        self,
        frame: np.ndarray,
        detection_or_bbox: Union[FaceDetection, Tuple[int, int, int, int]],
    ) -> ProcessedFace:
        """
        Crops and normalizes a detected face region.
        Input:
            frame: Raw camera frame (BGR or Gray)
            detection_or_bbox: FaceDetection object or (x, y, w, h) tuple
        Output:
            ProcessedFace containing the prepared face ROI
        """
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame passed to FacePreprocessingSkill.")

        if isinstance(detection_or_bbox, FaceDetection):
            x, y, w, h = detection_or_bbox.bbox
        elif isinstance(detection_or_bbox, (tuple, list)) and len(detection_or_bbox) == 4:
            x, y, w, h = [int(v) for v in detection_or_bbox]
        else:
            raise TypeError("Expected FaceDetection or 4-tuple (x, y, w, h) bounding box.")

        if w <= 0 or h <= 0:
            raise ValueError(f"Invalid bounding box dimensions: w={w}, h={h}")

        frame_h, frame_w = frame.shape[:2]

        # Apply safe margin padding
        pad_x = int(w * self.margin_ratio)
        pad_y = int(h * self.margin_ratio)

        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(frame_w, x + w + pad_x)
        y2 = min(frame_h, y + h + pad_y)

        cropped = frame[y1:y2, x1:x2]
        if cropped.size == 0:
            raise ValueError("Cropped face region is empty.")

        # Canonical resize
        interp = cv2.INTER_AREA if (cropped.shape[0] > self.target_size[1]) else cv2.INTER_CUBIC
        resized = cv2.resize(cropped, self.target_size, interpolation=interp)

        # Enhance contrast and smooth noise while preserving edges
        if len(resized.shape) == 3:
            # Equalize luminance in YCrCb or LAB space to maintain color fidelity
            lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            l_eq = self.clahe.apply(l)
            if self.use_bilateral:
                l_eq = cv2.bilateralFilter(l_eq, d=5, sigmaColor=35, sigmaSpace=35)
            lab_eq = cv2.merge([l_eq, a, b])
            normalized = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)
        else:
            eq = self.clahe.apply(resized)
            if self.use_bilateral:
                eq = cv2.bilateralFilter(eq, d=5, sigmaColor=35, sigmaSpace=35)
            normalized = eq

        # Transform raw face landmarks relative to the cropped ROI coordinate system
        roi_face = None
        if isinstance(detection_or_bbox, FaceDetection) and detection_or_bbox.raw_face is not None:
            try:
                rf = np.array(detection_or_bbox.raw_face, dtype=np.float32).copy()
                scale_x = float(self.target_size[0]) / max(1, cropped.shape[1])
                scale_y = float(self.target_size[1]) / max(1, cropped.shape[0])
                rf[0] = (rf[0] - x1) * scale_x
                rf[1] = (rf[1] - y1) * scale_y
                rf[2] *= scale_x
                rf[3] *= scale_y
                if len(rf) >= 14:
                    rf[4::2] = (rf[4::2] - x1) * scale_x
                    rf[5::2] = (rf[5::2] - y1) * scale_y
                roi_face = rf
            except Exception:
                roi_face = None

        return ProcessedFace(
            image=normalized,
            bbox=(x, y, w, h),
            original_shape=(frame_h, frame_w),
            is_aligned=True,
            raw_face=roi_face,
        )
