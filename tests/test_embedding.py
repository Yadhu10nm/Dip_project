import unittest
import numpy as np
from skills.common.types import ProcessedFace
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill


class TestEmbedding(unittest.TestCase):
    def setUp(self):
        self.embedder = FaceEmbeddingSkill()

    def test_embedding_dimensions_and_unit_norm(self):
        face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        proc = ProcessedFace(image=face, bbox=(20, 20, 80, 80), original_shape=(480, 640))
        vec = self.embedder.generate_embedding(proc)

        self.assertIsInstance(vec, np.ndarray)
        self.assertEqual(vec.shape, (128,))
        self.assertAlmostEqual(np.linalg.norm(vec), 1.0, places=4)

    def test_rule2_reject_full_cctv_frame(self):
        # Full CCTV frame must be rejected with ValueError
        full_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with self.assertRaises(ValueError):
            self.embedder.generate_embedding(full_frame)


if __name__ == "__main__":
    unittest.main()
