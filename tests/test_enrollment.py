import unittest
from unittest.mock import MagicMock
import tempfile
import shutil
import numpy as np
from skills.common.types import FaceDetection, ProcessedFace
from skills.enrollment_skill.implementation import EnrollmentSkill


class TestEnrollment(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_det = MagicMock()
        self.mock_prep = MagicMock()
        self.mock_emb = MagicMock()
        self.mock_vdb = MagicMock()

        self.enroller = EnrollmentSkill(
            detector=self.mock_det,
            preprocessor=self.mock_prep,
            embedder=self.mock_emb,
            vector_db=self.mock_vdb,
            users_file=f"{self.temp_dir}/users.json",
            dataset_dir=f"{self.temp_dir}/dataset",
        )
        self.frame = np.ones((480, 640, 3), dtype=np.uint8) * 128

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_enrollment_zero_faces_rejected(self):
        self.mock_det.detect_faces.return_value = []
        ok, msg = self.enroller.enroll_single_image("u1", "Yadhu", self.frame)
        self.assertFalse(ok)
        self.assertIn("No face detected", msg)

    def test_enrollment_multiple_faces_rejected(self):
        # Strict Rule 4: Reject multiple faces in enrollment sample
        self.mock_det.detect_faces.return_value = [
            FaceDetection(10, 10, 50, 50),
            FaceDetection(100, 100, 50, 50),
        ]
        ok, msg = self.enroller.enroll_single_image("u1", "Yadhu", self.frame)
        self.assertFalse(ok)
        self.assertIn("Multiple faces", msg)

    def test_enrollment_single_face_accepted(self):
        self.mock_det.detect_faces.return_value = [FaceDetection(10, 10, 50, 50)]
        self.mock_prep.preprocess_face.return_value = ProcessedFace(
            image=np.zeros((112, 112, 3), dtype=np.uint8),
            bbox=(10, 10, 50, 50),
            original_shape=(480, 640),
        )
        self.mock_emb.generate_embedding.return_value = np.zeros(128, dtype=np.float32)

        ok, msg = self.enroller.enroll_single_image("u1", "Yadhu", self.frame)
        self.assertTrue(ok)
        self.assertIn("Successfully enrolled", msg)


if __name__ == "__main__":
    unittest.main()
