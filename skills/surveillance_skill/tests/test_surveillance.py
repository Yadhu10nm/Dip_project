import unittest
import numpy as np
from unittest.mock import MagicMock
from skills.common.types import FaceDetection, ProcessedFace, RecognitionResult
from skills.surveillance_skill.implementation import SurveillanceSkill


class TestSurveillanceSkill(unittest.TestCase):
    def setUp(self):
        self.mock_detector = MagicMock()
        self.mock_preprocessor = MagicMock()
        self.mock_recognizer = MagicMock()
        self.surveillance = SurveillanceSkill(
            detector=self.mock_detector,
            preprocessor=self.mock_preprocessor,
            recognizer=self.mock_recognizer,
        )

    def test_multi_face_pipeline(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # 2 detected faces
        self.mock_detector.detect_faces.return_value = [
            FaceDetection(x=10, y=10, width=50, height=50),
            FaceDetection(x=200, y=100, width=60, height=60),
        ]
        self.mock_preprocessor.preprocess_face.side_effect = [
            ProcessedFace(image=np.zeros((112, 112, 3), dtype=np.uint8), bbox=(10, 10, 50, 50), original_shape=(480, 640)),
            ProcessedFace(image=np.zeros((112, 112, 3), dtype=np.uint8), bbox=(200, 100, 60, 60), original_shape=(480, 640)),
        ]
        self.mock_recognizer.recognize_face.side_effect = [
            RecognitionResult(name="Alice", person_id="p1", similarity=0.9, authorized=True, bbox=(10, 10, 50, 50)),
            RecognitionResult(name="Unknown", person_id="", similarity=0.3, authorized=False, bbox=(200, 100, 60, 60)),
        ]

        results = self.surveillance.process_frame(frame)
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].authorized)
        self.assertEqual(results[0].name, "Alice")
        self.assertFalse(results[1].authorized)
        self.assertEqual(results[1].name, "Unknown")


if __name__ == "__main__":
    unittest.main()
