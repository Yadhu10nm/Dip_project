import unittest
import numpy as np
from skills.common.types import FaceDetection, ProcessedFace
from skills.face_preprocessing_skill.implementation import FacePreprocessingSkill


class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        self.preprocessor = FacePreprocessingSkill(target_size=(112, 112))
        self.frame = np.ones((480, 640, 3), dtype=np.uint8) * 150

    def test_preprocess_face_roi(self):
        det = FaceDetection(x=120, y=80, width=100, height=100)
        proc = self.preprocessor.preprocess_face(self.frame, det)

        self.assertIsInstance(proc, ProcessedFace)
        self.assertEqual(proc.image.shape, (112, 112, 3))
        self.assertEqual(proc.bbox, (120, 80, 100, 100))

    def test_reject_zero_dimension_box(self):
        with self.assertRaises(ValueError):
            self.preprocessor.preprocess_face(self.frame, (50, 50, 0, 100))


if __name__ == "__main__":
    unittest.main()
