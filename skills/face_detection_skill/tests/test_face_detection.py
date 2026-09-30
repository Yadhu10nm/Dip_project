import unittest
import numpy as np
import cv2
from skills.face_detection_skill.implementation import FaceDetectionSkill


class TestFaceDetectionSkill(unittest.TestCase):
    def setUp(self):
        self.detector = FaceDetectionSkill()

    def test_empty_frame_handling(self):
        self.assertEqual(self.detector.detect_faces(None), [])
        empty = np.zeros((0, 0, 3), dtype=np.uint8)
        self.assertEqual(self.detector.detect_faces(empty), [])

    def test_blank_frame_no_faces(self):
        # A solid black frame should contain zero detected faces
        black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = self.detector.detect_faces(black_frame)
        self.assertEqual(len(detections), 0)


if __name__ == "__main__":
    unittest.main()
