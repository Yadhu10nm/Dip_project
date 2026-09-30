import unittest
from unittest.mock import MagicMock
import tempfile
import shutil
import numpy as np
from skills.common.types import FaceDetection, ProcessedFace
from skills.enrollment_skill.implementation import EnrollmentSkill


class TestEnrollmentSkill(unittest.TestCase):
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
        self.dummy_img = np.ones((480, 640, 3), dtype=np.uint8) * 100

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_reject_zero_faces(self):
        self.mock_det.detect_faces.return_value = []
        ok, msg = self.enroller.enroll_single_image("p1", "Test", self.dummy_img)
        self.assertFalse(ok)
        self.assertIn("No face detected", msg)

    def test_reject_multiple_faces(self):
        # Rule 4: Multiple faces must be rejected
        self.mock_det.detect_faces.return_value = [
            FaceDetection(10, 10, 50, 50),
            FaceDetection(100, 100, 50, 50),
        ]
        ok, msg = self.enroller.enroll_single_image("p1", "Test", self.dummy_img)
        self.assertFalse(ok)
        self.assertIn("Multiple faces", msg)

    def test_accept_exactly_one_face(self):
        self.mock_det.detect_faces.return_value = [FaceDetection(10, 10, 50, 50)]
        self.mock_prep.preprocess_face.return_value = ProcessedFace(
            image=np.zeros((112, 112, 3), dtype=np.uint8),
            bbox=(10, 10, 50, 50),
            original_shape=(480, 640),
        )
        self.mock_emb.generate_embedding.return_value = np.zeros(128, dtype=np.float32)

        ok, msg = self.enroller.enroll_single_image("p1", "Alice", self.dummy_img)
        self.assertTrue(ok)
        self.assertIn("Successfully enrolled", msg)
        self.mock_vdb.add_person.assert_called_once()


if __name__ == "__main__":
    unittest.main()
