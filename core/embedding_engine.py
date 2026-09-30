import os
import urllib.request
import cv2
import numpy as np
import config
from core.dip_engine import DIPEngine

class EmbeddingEngine:
    """
    Face Feature Embedding Engine.
    Converts facial images / ROIs into 128-dimensional unit-normalized embeddings
    suitable for vector databases (ChromaDB) and Cosine Similarity search.

    Architecture:
    1. Primary: OpenCV DNN SFace Face Recognition Network (128-D deep metric embedding).
    2. Resilient Fallback: DIP Multi-Region LBP Spatial Micro-Texture Descriptor (128-D unit vector).
    """

    SFACE_DOWNLOAD_URL = (
        "https://github.com/opencv/opencv_zoo/raw/main/models/"
        "face_recognition_sface/face_recognition_sface_2021dec.onnx"
    )

    def __init__(self, dip_engine: DIPEngine = None, model_path: str = None):
        self.dip_engine = dip_engine or DIPEngine()
        self.model_path = model_path or config.EMBEDDING_MODEL_PATH
        self.sface_recognizer = None
        self.embedding_dim = 128
        self._init_sface_model()

    def _init_sface_model(self):
        """Initializes OpenCV SFace ONNX recognizer with auto-download if needed."""
        try:
            if not os.path.exists(self.model_path):
                print(f"[EmbeddingEngine] SFace model not found at {self.model_path}. Attempting download...")
                os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
                req = urllib.request.Request(
                    self.SFACE_DOWNLOAD_URL,
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=15) as response, open(self.model_path, 'wb') as out_file:
                    out_file.write(response.read())
                print(f"[EmbeddingEngine] SFace model downloaded successfully.")

            if os.path.exists(self.model_path):
                self.sface_recognizer = cv2.FaceRecognizerSF.create(self.model_path, "")
                print(f"[EmbeddingEngine] SFace ONNX 128-D embedding model loaded successfully.")
        except Exception as e:
            print(f"[EmbeddingEngine] Note: SFace ONNX unavailable ({e}). Using DIP Spatial Texture Fallback.")
            self.sface_recognizer = None

    def compute_embedding(self, face_roi: np.ndarray) -> np.ndarray:
        """
        Extracts a 128-dimensional L2-normalized feature vector from face ROI.
        Returns:
            np.ndarray of shape (128,) with dtype np.float32, norm == 1.0
        """
        if face_roi is None or face_roi.size == 0:
            return np.zeros(self.embedding_dim, dtype=np.float32)

        # 1. Primary: SFace ONNX Deep Embedding
        if self.sface_recognizer is not None:
            try:
                # SFace expects 112x112 BGR image
                if len(face_roi.shape) == 2:
                    face_bgr = cv2.cvtColor(face_roi, cv2.COLOR_GRAY2BGR)
                else:
                    face_bgr = face_roi.copy()

                aligned = cv2.resize(face_bgr, (112, 112), interpolation=cv2.INTER_AREA)
                raw_feat = self.sface_recognizer.feature(aligned)
                feat = raw_feat.flatten().astype(np.float32)
                norm = np.linalg.norm(feat)
                if norm > 1e-6:
                    return feat / norm
            except Exception as e:
                # Fall back to DIP descriptor if SFace execution fails
                pass

        # 2. Resilient Fallback: DIP Spatial Multi-Region LBP Descriptor (128-D)
        return self._compute_dip_texture_embedding(face_roi)

    def _compute_dip_texture_embedding(self, face_roi: np.ndarray) -> np.ndarray:
        """
        DIP-based 128-dimensional feature embedding:
        1. Preprocess with CLAHE illumination balancing & Bilateral edge filtering.
        2. Compute Local Binary Pattern (LBP) texture map.
        3. Partition into 4x4 spatial grid (16 localized facial patches).
        4. Extract 8-bin micro-texture histogram per patch (16 x 8 = 128 dimensions).
        5. Square-root (Hellinger) compression and L2 normalization for Cosine Metric.
        """
        preprocessed = self.dip_engine.preprocess_face_roi(face_roi, (128, 128))
        lbp_map = self.dip_engine.compute_lbp(preprocessed)

        grid_rows, grid_cols = 4, 4
        patch_h, patch_w = 32, 32
        bins_per_patch = 8
        histograms = []

        for r in range(grid_rows):
            for c in range(grid_cols):
                patch = lbp_map[r * patch_h:(r + 1) * patch_h, c * patch_w:(c + 1) * patch_w]
                # 8 bins covering 0-256 (32 values per bin)
                hist, _ = np.histogram(patch, bins=bins_per_patch, range=(0, 256))
                hist = hist.astype(np.float32)
                p_norm = np.linalg.norm(hist)
                if p_norm > 1e-6:
                    hist = hist / p_norm
                histograms.append(hist)

        embedding = np.concatenate(histograms).astype(np.float32)  # Exactly 128 dimensions

        # Power normalization (Hellinger transform)
        embedding = np.sign(embedding) * np.sqrt(np.abs(embedding))

        # Global L2 unit normalization
        total_norm = np.linalg.norm(embedding)
        if total_norm > 1e-6:
            embedding = embedding / total_norm

        return embedding

    def compute_embeddings_batch(self, face_rois: list) -> list:
        """Computes embeddings for a batch of face images."""
        return [self.compute_embedding(roi) for roi in face_rois]
