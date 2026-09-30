import unittest
import numpy as np
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill
from skills.common.types import ProcessedFace


class TestFaceEmbeddingSkill(unittest.TestCase):
    def setUp(self):
        self.embedder = FaceEmbeddingSkill()

    def test_embedding_output_shape_and_norm(self):
        face_img = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        processed = ProcessedFace(image=face_img, bbox=(10, 10, 50, 50), original_shape=(480, 640))
        vec = self.embedder.generate_embedding(processed)

        self.assertIsInstance(vec, np.ndarray)
        self.assertEqual(vec.shape, (128,))
        norm = np.linalg.norm(vec)
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_full_frame_rejection_rule(self):
        large_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            self.embedder.generate_embedding(large_frame)


if __name__ == "__main__":
    unittest.main()
