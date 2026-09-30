import unittest
import numpy as np
from skills.face_preprocessing_skill.implementation import FacePreprocessingSkill
from skills.common.types import FaceDetection, ProcessedFace


class TestFacePreprocessingSkill(unittest.TestCase):
    def setUp(self):
        self.preprocessor = FacePreprocessingSkill(target_size=(112, 112))
        # Create synthetic test frame
        self.frame = np.ones((480, 640, 3), dtype=np.uint8) * 128

    def test_preprocess_valid_detection(self):
        det = FaceDetection(x=100, y=100, width=80, height=80)
        processed = self.preprocessor.preprocess_face(self.frame, det)

        self.assertIsInstance(processed, ProcessedFace)
        self.assertEqual(processed.image.shape, (112, 112, 3))
        self.assertEqual(processed.bbox, (100, 100, 80, 80))

    def test_invalid_input_handling(self):
        with self.assertRaises(ValueError):
            self.preprocessor.preprocess_face(None, (10, 10, 20, 20))

        with self.assertRaises(ValueError):
            self.preprocessor.preprocess_face(self.frame, (10, 10, 0, 0))


if __name__ == "__main__":
    unittest.main()
