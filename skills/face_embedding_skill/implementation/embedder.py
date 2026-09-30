import os
import urllib.request
from typing import Union
import cv2
import numpy as np
import config
from skills.common.types import ProcessedFace


class FaceEmbeddingSkill:
    """
    Face Feature Embedding Skill.
    Extracts 128-dimensional unit-normalized facial embeddings using OpenCV SFace ONNX
    with a resilient DIP spatial multi-region LBP texture fallback.

    STRICT RULE:
    The embedding engine must never receive the complete CCTV frame.
    It accepts only a detected/preprocessed face ROI.
    """

    SFACE_DOWNLOAD_URL = (
        "https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_recognition_sface/face_recognition_sface_2021dec.onnx"
    )

    def __init__(self, model_path: str = None, yunet_path: str = None):
        self.model_path = model_path or config.EMBEDDING_MODEL_PATH
        self.yunet_path = yunet_path or config.YUNET_MODEL_PATH
        self.embedding_dim = 128
        self.sface_recognizer = None
        self.yunet_detector = None
        self._init_sface_model()
        self._init_yunet_model()

    def _init_yunet_model(self):
        """Initializes auxiliary YuNet detector for landmark alignment on face crops."""
        try:
            if os.path.exists(self.yunet_path):
                self.yunet_detector = cv2.FaceDetectorYN.create(
                    self.yunet_path, "", (200, 200), score_threshold=0.45, nms_threshold=0.3
                )
        except Exception:
            self.yunet_detector = None

    def _init_sface_model(self):
        """Attempts to load OpenCV FaceRecognizerSF ONNX model or download if missing."""
        try:
            if not os.path.exists(self.model_path):
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                req = urllib.request.Request(
                    self.SFACE_DOWNLOAD_URL,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as response, open(self.model_path, 'wb') as out_file:
                    out_file.write(response.read())

            if os.path.exists(self.model_path):
                self.sface_recognizer = cv2.FaceRecognizerSF.create(self.model_path, "")
        except Exception:
            # Fall back gracefully to DIP spatial descriptor if download or ONNX unavailable
            self.sface_recognizer = None

    def generate_embedding(self, face: Union[ProcessedFace, np.ndarray]) -> np.ndarray:
        """
        Extracts a 128-dimensional L2-normalized feature vector from a face ROI.
        Input:
            face: ProcessedFace or cropped face image numpy array (strictly face ROI).
        Output:
            numpy.ndarray of shape (128,) and dtype np.float32 with unit norm (1.0).
        """
        if isinstance(face, ProcessedFace):
            face_img = face.image
        elif isinstance(face, np.ndarray):
            face_img = face
        else:
            raise TypeError("Expected ProcessedFace or numpy.ndarray face crop.")

        if face_img is None or face_img.size == 0:
            return np.zeros(self.embedding_dim, dtype=np.float32)

        # Enforce rule: Reject huge full-frame images accidentally passed directly
        if face_img.shape[0] > 400 and face_img.shape[1] > 400:
            raise ValueError(
                "Violation: Image dimensions too large for face ROI. "
                "Only cropped human face regions may enter the embedding pipeline."
            )

        # 1. Primary: SFace Deep Metric Embedding with 5-Landmark Affine Alignment
        if self.sface_recognizer is not None:
            try:
                if len(face_img.shape) == 2:
                    bgr_face = cv2.cvtColor(face_img, cv2.COLOR_GRAY2BGR)
                else:
                    bgr_face = face_img.copy()

                raw_face = getattr(face, "raw_face", None) if isinstance(face, ProcessedFace) else None

                # If no landmarks provided, detect landmarks within the cropped face ROI
                if raw_face is None and self.yunet_detector is not None:
                    try:
                        self.yunet_detector.setInputSize((bgr_face.shape[1], bgr_face.shape[0]))
                        _, faces_in_crop = self.yunet_detector.detect(bgr_face)
                        if faces_in_crop is not None and len(faces_in_crop) > 0:
                            raw_face = faces_in_crop[0]
                    except Exception:
                        pass

                # Canonical pose alignment
                if raw_face is not None:
                    try:
                        aligned = self.sface_recognizer.alignCrop(bgr_face, raw_face)
                    except Exception:
                        aligned = cv2.resize(bgr_face, (112, 112), interpolation=cv2.INTER_AREA)
                else:
                    aligned = cv2.resize(bgr_face, (112, 112), interpolation=cv2.INTER_AREA)

                raw_feat = self.sface_recognizer.feature(aligned)
                feat = raw_feat.flatten().astype(np.float32)
                norm = np.linalg.norm(feat)
                if norm > 1e-6:
                    return feat / norm
            except Exception:
                pass

        # 2. Resilient Fallback: DIP Spatial Multi-Region LBP Descriptor (128-D)
        return self._compute_dip_texture_embedding(face_img)

    def _compute_dip_texture_embedding(self, face_img: np.ndarray) -> np.ndarray:
        """
        128-D spatial LBP descriptor:
        Partitions face into 4x4 spatial patches (16 regions), computes 8-bin LBP histogram
        per region (16 * 8 = 128 dimensions), applies Hellinger transform and L2 unit normalization.
        """
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img.copy()

        resized = cv2.resize(gray, (128, 128))
        # Compute vectorized LBP
        h, w = resized.shape
        center = resized[1:h-1, 1:w-1].astype(np.int16)
        n0 = (resized[0:h-2, 0:w-2].astype(np.int16) >= center) * 1
        n1 = (resized[0:h-2, 1:w-1].astype(np.int16) >= center) * 2
        n2 = (resized[0:h-2, 2:w  ].astype(np.int16) >= center) * 4
        n3 = (resized[1:h-1, 2:w  ].astype(np.int16) >= center) * 8
        n4 = (resized[2:h  , 2:w  ].astype(np.int16) >= center) * 16
        n5 = (resized[2:h  , 1:w-1].astype(np.int16) >= center) * 32
        n6 = (resized[2:h  , 0:w-2].astype(np.int16) >= center) * 64
        n7 = (resized[1:h-1, 0:w-2].astype(np.int16) >= center) * 128
        lbp = (n0 + n1 + n2 + n3 + n4 + n5 + n6 + n7).astype(np.uint8)

        # 4x4 grid (16 patches x 8 bins = 128 D)
        patch_h, patch_w = 31, 31
        histograms = []
        for r in range(4):
            for c in range(4):
                patch = lbp[r*patch_h:(r+1)*patch_h, c*patch_w:(c+1)*patch_w]
                hist, _ = np.histogram(patch, bins=8, range=(0, 256))
                hist = hist.astype(np.float32)
                hist_norm = np.linalg.norm(hist)
                if hist_norm > 1e-6:
                    hist = hist / hist_norm
                histograms.append(hist)

        embedding = np.concatenate(histograms).astype(np.float32)
        # Hellinger kernel mapping
        embedding = np.sqrt(np.maximum(embedding, 0.0))
        norm = np.linalg.norm(embedding)
        if norm > 1e-6:
            embedding = embedding / norm
        return embedding
