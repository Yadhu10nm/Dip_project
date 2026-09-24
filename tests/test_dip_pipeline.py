import os
import shutil
import unittest
import numpy as np
import cv2
import config
from core.dip_engine import DIPEngine
from core.detector import FaceDetector
from core.recognizer import LBPHFaceRecognizer
from core.access_manager import AccessManager
from core.cctv_hud import CCTVHUD

class TestDIPPipeline(unittest.TestCase):

    def setUp(self):
        self.dip = DIPEngine()
        # Create a test synthetic face image (200x200 BGR)
        self.synthetic_face = np.full((200, 200, 3), 120, dtype=np.uint8)
        # Draw eyes and mouth for synthetic texture
        cv2.circle(self.synthetic_face, (60, 70), 18, (20, 20, 20), -1)
        cv2.circle(self.synthetic_face, (140, 70), 18, (20, 20, 20), -1)
        cv2.ellipse(self.synthetic_face, (100, 140), (45, 18), 0, 0, 180, (40, 40, 40), -1)

    def test_camera_flip_applies_to_raw_frames(self):
        old_flip = getattr(config, "CAMERA_FLIP", None)
        config.CAMERA_FLIP = True
        try:
            from core.surveillance_system import SurveillanceSystem

            system = SurveillanceSystem(camera_index=0)
            raw_frame = np.full((60, 80, 3), 42, dtype=np.uint8)

            class FakeCapture:
                def isOpened(self):
                    return True

                def read(self):
                    return True, raw_frame.copy()

            system.cap = FakeCapture()
            flipped = system.read_raw_frame()

            np.testing.assert_array_equal(flipped, cv2.flip(raw_frame, 1))
        finally:
            if old_flip is None:
                delattr(config, "CAMERA_FLIP")
            else:
                config.CAMERA_FLIP = old_flip

    def test_grayscale_conversion(self):
        gray = self.dip.to_grayscale(self.synthetic_face)
        self.assertEqual(len(gray.shape), 2)
        self.assertEqual(gray.shape, (200, 200))
        self.assertEqual(gray.dtype, np.uint8)

    def test_clahe_enhancement(self):
        gray = self.dip.to_grayscale(self.synthetic_face)
        equalized = self.dip.apply_clahe(gray)
        self.assertEqual(equalized.shape, gray.shape)
        self.assertEqual(equalized.dtype, np.uint8)

    def test_preprocess_face_roi(self):
        processed = self.dip.preprocess_face_roi(self.synthetic_face, (200, 200))
        self.assertEqual(processed.shape, (200, 200))
        self.assertEqual(processed.dtype, np.uint8)

    def test_lbp_texture_computation(self):
        gray = self.dip.to_grayscale(self.synthetic_face)
        lbp_map = self.dip.compute_lbp(gray)
        self.assertEqual(lbp_map.shape, gray.shape)
        self.assertEqual(lbp_map.dtype, np.uint8)
        # Verify texture variance exists
        self.assertGreater(np.max(lbp_map), 0)

    def test_dip_quad_view_generation(self):
        quad = self.dip.create_dip_quad_view(self.synthetic_face)
        self.assertEqual(len(quad.shape), 3)
        self.assertEqual(quad.shape[:2], self.synthetic_face.shape[:2])

    def test_cctv_hud_rendering(self):
        hud = CCTVHUD()
        detections = [
            {
                "bbox": (50, 50, 80, 80),
                "is_authorized": False,
                "user_id": "UNKNOWN",
                "name": "Intruder",
                "distance": 85.5,
                "score": 25.0
            }
        ]
        canvas = hud.draw_hud(self.synthetic_face, detections, fps=30.0)
        self.assertEqual(canvas.shape, self.synthetic_face.shape)

    def test_recognizer_train_and_predict(self):
        # Create a temporary test user and train
        test_user_id = "AUTH_TEST"
        test_user_dir = os.path.join(config.DATASET_DIR, test_user_id)
        os.makedirs(test_user_dir, exist_ok=True)

        try:
            # Save 3 synthetic samples
            for i in range(3):
                sample_img = self.synthetic_face.copy()
                cv2.imwrite(os.path.join(test_user_dir, f"sample_{i:02d}.jpg"), sample_img)

            recognizer = LBPHFaceRecognizer(self.dip)
            success, msg = recognizer.train_model(
                config.DATASET_DIR,
                [{"id": test_user_id, "name": "Test User"}]
            )
            self.assertTrue(success, f"Training failed: {msg}")
            self.assertTrue(recognizer.is_trained)

            # Predict identical face
            is_auth, uid, dist, score = recognizer.predict(self.synthetic_face)
            self.assertTrue(is_auth)
            self.assertEqual(uid, test_user_id)
            self.assertLess(dist, config.RECOGNITION_THRESHOLD)

            # Predict completely different image (pure white noise)
            noise_img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
            is_auth_noise, _, dist_noise, _ = recognizer.predict(noise_img)
            self.assertFalse(is_auth_noise)
            self.assertGreater(dist_noise, config.RECOGNITION_THRESHOLD)

        finally:
            if os.path.exists(test_user_dir):
                shutil.rmtree(test_user_dir, ignore_errors=True)

if __name__ == "__main__":
    unittest.main()
