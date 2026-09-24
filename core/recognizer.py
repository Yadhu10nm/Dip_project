import os
import json
import cv2
import numpy as np
import config
from core.dip_engine import DIPEngine

class LBPHFaceRecognizer:
    """
    Local Binary Patterns Histograms (LBPH) Face Recognizer.
    A premier Digital Image Processing approach for facial identification.
    Uses circular micro-texture histograms and Chi-Square distance metrics.
    """

    def __init__(self, dip_engine: DIPEngine = None):
        self.dip_engine = dip_engine or DIPEngine()
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=config.LBPH_RADIUS,
            neighbors=config.LBPH_NEIGHBORS,
            grid_x=config.LBPH_GRID_X,
            grid_y=config.LBPH_GRID_Y,
            threshold=300.0  # Max distance ceiling
        )
        self.label_map_file = os.path.join(config.MODELS_DIR, "label_map.json")
        self.int_to_user = {}  # int_label -> user_id (str)
        self.is_trained = False
        self.load_model()

    def train_model(self, dataset_dir: str, users: list):
        """
        Trains the LBPH model using registered face samples.
        Args:
            dataset_dir: Root dataset folder containing user_id subdirectories
            users: List of user dicts [{'id': 'USR_01', 'name': 'John'}, ...]
        """
        faces = []
        labels = []
        label_map = {}

        for idx, u in enumerate(users):
            user_id = u["id"]
            int_label = idx + 1
            label_map[str(int_label)] = user_id
            user_folder = os.path.join(dataset_dir, user_id)

            if not os.path.isdir(user_folder):
                continue

            for fname in os.listdir(user_folder):
                if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                fpath = os.path.join(user_folder, fname)
                img = cv2.imread(fpath)
                if img is None:
                    continue

                # Preprocess sample using DIP pipeline
                processed_roi = self.dip_engine.preprocess_face_roi(img, config.STANDARD_FACE_SIZE)
                faces.append(processed_roi)
                labels.append(int_label)

        if len(faces) == 0:
            self.is_trained = False
            if os.path.exists(config.MODEL_FILE):
                os.remove(config.MODEL_FILE)
            if os.path.exists(self.label_map_file):
                os.remove(self.label_map_file)
            return False, "No valid face samples found to train."

        # Train OpenCV LBPH Recognizer
        self.recognizer.train(faces, np.array(labels, dtype=np.int32))
        self.recognizer.write(config.MODEL_FILE)

        # Save label map
        self.int_to_user = {int(k): v for k, v in label_map.items()}
        with open(self.label_map_file, "w") as f:
            json.dump(label_map, f, indent=2)

        self.is_trained = True
        return True, f"LBPH model trained successfully with {len(faces)} samples across {len(label_map)} authorized users."

    def load_model(self):
        """Loads serialized model and label mappings from disk if available."""
        if os.path.exists(config.MODEL_FILE) and os.path.exists(self.label_map_file):
            try:
                self.recognizer.read(config.MODEL_FILE)
                with open(self.label_map_file, "r") as f:
                    raw_map = json.load(f)
                    self.int_to_user = {int(k): v for k, v in raw_map.items()}
                self.is_trained = True
                return True
            except Exception as e:
                print(f"[LBPH Recognizer] Failed to load existing model: {e}")
                self.is_trained = False
        else:
            self.is_trained = False
        return False

    def predict(self, face_roi: np.ndarray):
        """
        Classifies a detected face ROI:
        Returns:
            is_authorized: bool (True if recognized within threshold, False otherwise)
            user_id: str or None
            distance: float (Chi-Square histogram distance)
            match_score: float (0.0 to 100.0% confidence estimate)
        """
        if not self.is_trained or len(self.int_to_user) == 0:
            # If no authorized personnel are registered, every face is an intruder
            return False, None, 999.0, 0.0

        # Preprocess query face with identical DIP pipeline
        processed = self.dip_engine.preprocess_face_roi(face_roi, config.STANDARD_FACE_SIZE)

        label_int, distance = self.recognizer.predict(processed)

        # In LBPH, 0 is a perfect identical match, higher means greater histogram divergence.
        # Compute normalized match confidence:
        # 0 distance -> 100%, distance equal to threshold -> ~60%, distance 100+ -> ~0%
        if distance <= config.RECOGNITION_THRESHOLD:
            # Authorized individual recognized
            user_id = self.int_to_user.get(label_int)
            match_score = max(55.0, min(99.0, 100.0 - (distance / config.RECOGNITION_THRESHOLD) * 40.0))
            return True, user_id, distance, round(match_score, 1)
        else:
            # Unauthorized person / intruder
            match_score = max(0.0, min(50.0, 100.0 - (distance / config.RECOGNITION_THRESHOLD) * 50.0))
            return False, None, distance, round(match_score, 1)
