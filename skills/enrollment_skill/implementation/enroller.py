import os
import json
import time
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
import cv2
import numpy as np
import config
from skills.common.types import FaceDetection, ProcessedFace
from skills.face_detection_skill.implementation import FaceDetectionSkill
from skills.face_preprocessing_skill.implementation import FacePreprocessingSkill
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill
from skills.vector_database_skill.implementation import VectorDatabaseSkill


class EnrollmentSkill:
    """
    Personnel Enrollment Skill.
    Enrolls authorized personnel with strict single-face verification.

    RULES:
    - Rule 4: Never enroll an image containing multiple faces.
    - Exactly ONE face required per enrollment sample.
    - Zero faces rejected.
    """

    def __init__(
        self,
        detector: Optional[FaceDetectionSkill] = None,
        preprocessor: Optional[FacePreprocessingSkill] = None,
        embedder: Optional[FaceEmbeddingSkill] = None,
        vector_db: Optional[VectorDatabaseSkill] = None,
        users_file: str = config.USERS_FILE,
        dataset_dir: str = config.DATASET_DIR,
    ):
        self.detector = detector or FaceDetectionSkill()
        self.preprocessor = preprocessor or FacePreprocessingSkill()
        self.embedder = embedder or FaceEmbeddingSkill()
        self.vector_db = vector_db or VectorDatabaseSkill()
        self.users_file = users_file
        self.dataset_dir = dataset_dir

        os.makedirs(self.dataset_dir, exist_ok=True)
        if not os.path.exists(self.users_file):
            with open(self.users_file, "w") as f:
                json.dump([], f)

    def enroll_single_image(
        self,
        person_id: str,
        name: str,
        image: np.ndarray,
        sample_index: int = 0,
    ) -> Tuple[bool, str]:
        """
        Enrolls a single image into the person's profile.
        Strictly requires EXACTLY ONE face.
        Returns:
            (success: bool, message: str)
        """
        if image is None or image.size == 0:
            return False, "Invalid or empty image provided."

        # 1. Detect candidate faces
        detections = self.detector.detect_faces(image)

        # 2. Strict single face enforcement (Rule 4)
        if len(detections) == 0:
            return False, "Enrollment rejected: No face detected in image."
        if len(detections) > 1:
            return False, f"Enrollment rejected: Multiple faces ({len(detections)}) detected. Exactly one face required."

        det = detections[0]

        # 3. Preprocess the single localized face
        try:
            processed = self.preprocessor.preprocess_face(image, det)
        except Exception as e:
            return False, f"Face preprocessing failed: {e}"

        # 4. Generate 128-D embedding
        emb = self.embedder.generate_embedding(processed)

        # 5. Store in ChromaDB
        sample_id = f"sample_{sample_index:03d}"
        self.vector_db.add_person(person_id, name, [emb], [sample_id])

        # 6. Save image to dataset folder
        user_folder = os.path.join(self.dataset_dir, person_id)
        os.makedirs(user_folder, exist_ok=True)
        sample_path = os.path.join(user_folder, f"{sample_id}.jpg")
        cv2.imwrite(sample_path, processed.image)

        # 7. Update authorized_users.json registry
        self._record_user_registry(person_id, name, sample_path)

        return True, f"Successfully enrolled face sample {sample_id}."

    def enroll_batch_images(
        self,
        person_id: str,
        name: str,
        images: List[np.ndarray],
    ) -> Tuple[int, str]:
        """Enrolls a batch of image samples, skipping images with 0 or >1 faces."""
        successful = 0
        for idx, img in enumerate(images):
            ok, _ = self.enroll_single_image(person_id, name, img, sample_index=idx)
            if ok:
                successful += 1

        return successful, f"Enrolled {successful} of {len(images)} valid single-face samples."

    def delete_person(self, person_id: str) -> bool:
        """Removes person from ChromaDB and registry."""
        self.vector_db.delete_person(person_id)
        # Update JSON
        users = self.list_users()
        users = [u for u in users if u.get("id") != person_id]
        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)
        return True

    def list_users(self) -> List[Dict[str, Any]]:
        """Reads enrolled authorized users list from disk."""
        if not os.path.exists(self.users_file):
            return []
        try:
            with open(self.users_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _record_user_registry(self, person_id: str, name: str, sample_path: str):
        users = self.list_users()
        found = False
        rel_thumb = f"api/user_photo/{person_id}/sample_000.jpg"

        for u in users:
            if u.get("id") == person_id:
                u["sample_count"] = u.get("sample_count", 0) + 1
                found = True
                break

        if not found:
            users.append({
                "id": person_id,
                "name": name,
                "role": "Authorized Personnel",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sample_count": 1,
                "thumbnail": rel_thumb,
            })

        with open(self.users_file, "w") as f:
            json.dump(users, f, indent=2)
