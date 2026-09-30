import os
import json
import shutil
import cv2
from datetime import datetime
import numpy as np
import config
from core.recognizer import LBPHFaceRecognizer
from core.detector import FaceDetector

class AccessManager:
    """
    Manages authorized personnel access whitelist, face datasets,
    and automatic LBPH model retraining upon database modifications.
    """

    def __init__(self, recognizer: LBPHFaceRecognizer = None, detector: FaceDetector = None):
        self.recognizer = recognizer or LBPHFaceRecognizer()
        self.detector = detector or FaceDetector()
        self.users_file = config.USERS_FILE
        self._ensure_users_file()

    def _ensure_users_file(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w") as f:
                json.dump([], f, indent=2)

    def list_users(self) -> list:
        """Returns list of authorized users."""
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def get_user(self, user_id: str):
        """Finds user by ID."""
        for u in self.list_users():
            if u["id"] == user_id:
                return u
        return None

    def _save_users(self, users: list):
        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)

    def add_user(self, name: str, role: str = "Authorized Personnel") -> dict:
        """
        Creates new user profile and allocates storage directory.
        """
        users = self.list_users()
        user_num = len(users) + 1
        user_id = f"AUTH_{user_num:03d}"

        # Ensure unique ID
        existing_ids = {u["id"] for u in users}
        while user_id in existing_ids:
            user_num += 1
            user_id = f"AUTH_{user_num:03d}"

        user_dir = os.path.join(config.DATASET_DIR, user_id)
        os.makedirs(user_dir, exist_ok=True)

        user_record = {
            "id": user_id,
            "name": name.strip(),
            "role": role.strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sample_count": 0,
            "thumbnail": None
        }

        users.append(user_record)
        self._save_users(users)
        return user_record

    def save_face_sample(self, user_id: str, face_img: np.ndarray) -> bool:
        """
        Saves a single face sample into the user's dataset directory and indexes into ChromaDB.
        """
        user_dir = os.path.join(config.DATASET_DIR, user_id)
        if not os.path.isdir(user_dir):
            os.makedirs(user_dir, exist_ok=True)

        existing = [f for f in os.listdir(user_dir) if f.endswith(".jpg")]
        sample_idx = len(existing)
        sample_id = f"sample_{sample_idx:03d}"
        sample_path = os.path.join(user_dir, f"{sample_id}.jpg")

        cv2.imwrite(sample_path, face_img)

        # Update sample count and thumbnail
        user_name = "Authorized Personnel"
        users = self.list_users()
        for u in users:
            if u["id"] == user_id:
                u["sample_count"] = sample_idx + 1
                if u.get("thumbnail") is None:
                    u["thumbnail"] = f"api/user_photo/{user_id}/sample_000.jpg"
                user_name = u.get("name", user_name)
                break
        self._save_users(users)

        # Add 128-D embedding directly to ChromaDB
        if hasattr(self.recognizer, "enroll_face_sample"):
            self.recognizer.enroll_face_sample(user_id, user_name, face_img, sample_id)

        return True

    def enroll_from_frame(self, user_id: str, frame: np.ndarray) -> bool:
        """
        Detects face in frame, crops ROI, and saves as sample.
        """
        faces = self.detector.detect_faces(frame)
        if len(faces) == 0:
            return False

        # Pick largest face
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        face_roi, _ = self.detector.extract_face_roi(frame, largest_face)
        if face_roi.size == 0:
            return False

        return self.save_sample_with_augmentations(user_id, face_roi)

    def enroll_from_images(self, user_id: str, images: list) -> tuple:
        """
        Processes and enrolls multiple images for an authorized user.
        For each image:
        - Locates faces using detector (or uses portrait if pre-cropped)
        - Crops face ROI
        - Augments (original + horizontal mirror flip)
        - Saves to dataset directory
        - Converts to 128-D embeddings and indexes in ChromaDB
        """
        user = self.get_user(user_id)
        if not user:
            return 0, f"User {user_id} not found."

        collected_rois = []
        for img in images:
            if img is None or img.size == 0:
                continue

            faces = self.detector.detect_faces(img)
            if len(faces) > 0:
                for rect in faces:
                    roi, _ = self.detector.extract_face_roi(img, rect)
                    if roi.size > 0:
                        collected_rois.append(roi)
            else:
                # If Haar Cascade did not detect a face, check if it's already a cropped portrait
                h, w = img.shape[:2]
                if h >= 50 and w >= 50:
                    roi = cv2.resize(img, config.STANDARD_FACE_SIZE)
                    collected_rois.append(roi)

        if not collected_rois:
            return 0, "No clear faces could be detected in the provided images."

        saved_count = 0
        for roi in collected_rois:
            self.save_sample_with_augmentations(user_id, roi)
            saved_count += 2  # base + flipped

        # Synchronize and retrain models
        self.retrain()
        return saved_count, f"Processed {len(images)} images -> generated {saved_count} face samples with ChromaDB embeddings."

    def save_sample_with_augmentations(self, user_id: str, face_roi: np.ndarray) -> bool:
        """
        Saves the face ROI along with horizontal flip augmentation
        to ensure robust recognition under varied angles.
        """
        # Base image
        self.save_face_sample(user_id, face_roi)

        # Horizontal flip (mirror)
        flipped = cv2.flip(face_roi, 1)
        self.save_face_sample(user_id, flipped)
        return True

    def revoke_user(self, user_id: str) -> bool:
        """
        Revokes access: deletes dataset folder, removes from JSON,
        removes vectors from ChromaDB, and auto-retrains model.
        """
        users = self.list_users()
        users = [u for u in users if u["id"] != user_id]
        self._save_users(users)

        user_dir = os.path.join(config.DATASET_DIR, user_id)
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir, ignore_errors=True)

        # Remove from ChromaDB vector store
        if hasattr(self.recognizer, "remove_user"):
            self.recognizer.remove_user(user_id)

        # Retrain model
        self.retrain()
        return True

    def retrain(self) -> tuple:
        """
        Retrains models (indexes embeddings into ChromaDB and fits LBPH).
        """
        users = self.list_users()
        success, message = self.recognizer.train_model(config.DATASET_DIR, users)
        return success, message
