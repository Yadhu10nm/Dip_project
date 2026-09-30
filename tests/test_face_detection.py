import unittest
from unittest.mock import MagicMock
import numpy as np
from skills.face_detection_skill.implementation import FaceDetectionSkill


class TestFaceDetection(unittest.TestCase):
    def setUp(self):
        self.detector = FaceDetectionSkill()

    def test_no_face_detected(self):
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        faces = self.detector.detect_faces(blank)
        self.assertEqual(len(faces), 0)

    def test_one_face_mocked(self):
        self.detector.classifier = MagicMock()
        self.detector.classifier.detectMultiScale.return_value = np.array([[100, 100, 80, 80]])

        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        faces = self.detector.detect_faces(frame)
        self.assertEqual(len(faces), 1)
        self.assertEqual(faces[0].bbox, (100, 100, 80, 80))

    def test_multiple_faces_mocked(self):
        self.detector.classifier = MagicMock()
        self.detector.classifier.detectMultiScale.return_value = np.array([
            [50, 50, 60, 60],
            [200, 150, 70, 70],
            [350, 200, 80, 80],
        ])

        frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
        faces = self.detector.detect_faces(frame)
        self.assertEqual(len(faces), 3)


if __name__ == "__main__":
    unittest.main()
