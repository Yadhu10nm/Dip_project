import os
import shutil
import unittest
import numpy as np
import cv2
import config
from core.dip_engine import DIPEngine
from core.detector import FaceDetector
from core.recognizer import LBPHFaceRecognizer, FaceRecognizer
from core.embedding_engine import EmbeddingEngine
from core.vector_store import ChromaFaceStore
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
            # Create an asymmetric frame: left half white (255), right half black (0)
            raw_frame = np.zeros((60, 80, 3), dtype=np.uint8)
            raw_frame[:, :40] = 255

            class FakeCapture:
                def isOpened(self):
                    return True

                def read(self):
                    return True, raw_frame.copy()

            system.cap = FakeCapture()
            flipped = system.read_raw_frame()

            # Verify that frame is horizontally inverted
            np.testing.assert_array_equal(flipped, cv2.flip(raw_frame, 1))
            self.assertEqual(flipped[0, 0, 0], 0)     # Left corner is now black
            self.assertEqual(flipped[0, 79, 0], 255)  # Right corner is now white
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
                "distance": 0.25,
                "score": 25.0
            }
        ]
        canvas = hud.draw_hud(self.synthetic_face, detections, fps=30.0)
        self.assertEqual(canvas.shape, self.synthetic_face.shape)

    def test_embedding_engine_generates_normalized_vectors(self):
        engine = EmbeddingEngine(self.dip)
        emb = engine.compute_embedding(self.synthetic_face)
        self.assertIsNotNone(emb)
        self.assertEqual(emb.shape, (128,))
        self.assertAlmostEqual(float(np.linalg.norm(emb)), 1.0, places=3)

    def test_chromadb_vector_store_cosine_search(self):
        test_store = ChromaFaceStore(collection_name="test_unit_collection")
        try:
            # Create two orthogonal normalized 128D embeddings
            v1 = np.zeros(128, dtype=np.float32)
            v1[0] = 1.0
            v2 = np.zeros(128, dtype=np.float32)
            v2[1] = 1.0

            test_store.add_face_embedding("USR_1", "Alice", v1, "s1")
            test_store.add_face_embedding("USR_2", "Bob", v2, "s2")

            # Query with v1
            matches = test_store.search_similar(v1, top_k=2)
            self.assertEqual(len(matches), 2)
            self.assertEqual(matches[0]["user_id"], "USR_1")
            self.assertAlmostEqual(matches[0]["similarity"], 1.0, places=2)
            self.assertAlmostEqual(matches[1]["similarity"], 0.0, places=2)

            # Test delete user
            test_store.delete_user("USR_1")
            remaining = test_store.search_similar(v1, top_k=2)
            self.assertEqual(len(remaining), 1)
            self.assertEqual(remaining[0]["user_id"], "USR_2")
        finally:
            try:
                test_store.client.delete_collection("test_unit_collection")
            except Exception:
                pass

    def test_multiple_images_enrollment(self):
        manager = AccessManager()
        test_uid = "AUTH_BATCH_TEST"
        test_dir = os.path.join(config.DATASET_DIR, test_uid)
        os.makedirs(test_dir, exist_ok=True)
        try:
            # Add user
            manager.add_user("Batch User", "Test Role")
            # Update user id to match
            users = manager.list_users()
            for u in users:
                if u["name"] == "Batch User":
                    u["id"] = test_uid
            manager._save_users(users)

            img1 = self.synthetic_face.copy()
            img2 = self.synthetic_face.copy()
            img3 = self.synthetic_face.copy()

            count, msg = manager.enroll_from_images(test_uid, [img1, img2, img3])
            self.assertGreater(count, 0)
            user_rec = manager.get_user(test_uid)
            self.assertIsNotNone(user_rec)
            self.assertGreater(user_rec["sample_count"], 0)
        finally:
            manager.revoke_user(test_uid)

    def test_recognizer_train_and_predict(self):
        test_user_id = "AUTH_TEST"
        test_user_dir = os.path.join(config.DATASET_DIR, test_user_id)
        os.makedirs(test_user_dir, exist_ok=True)

        try:
            for i in range(3):
                sample_img = self.synthetic_face.copy()
                cv2.imwrite(os.path.join(test_user_dir, f"sample_{i:02d}.jpg"), sample_img)

            test_store = ChromaFaceStore(collection_name="test_recognizer_train_collection")
            recognizer = FaceRecognizer(self.dip, vector_store=test_store)
            success, msg = recognizer.train_model(
                config.DATASET_DIR,
                [{"id": test_user_id, "name": "Test User"}]
            )
            self.assertTrue(success, f"Training failed: {msg}")
            self.assertTrue(recognizer.is_trained)

            # 1. Cosine similarity prediction (ChromaDB)
            is_auth, uid, cos_sim, score = recognizer.predict_cosine(self.synthetic_face)
            self.assertTrue(is_auth)
            self.assertEqual(uid, test_user_id)
            self.assertGreaterEqual(cos_sim, config.COSINE_SIMILARITY_THRESHOLD)

            # Predict completely different image (pure noise)
            noise_img = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
            is_auth_noise, _, cos_sim_noise, _ = recognizer.predict_cosine(noise_img)
            self.assertFalse(is_auth_noise)
            self.assertLess(cos_sim_noise, config.COSINE_SIMILARITY_THRESHOLD)

            # 2. LBPH prediction verification
            is_auth_lbph, uid_lbph, dist_lbph, _ = recognizer.predict_lbph(self.synthetic_face)
            self.assertTrue(is_auth_lbph)
            self.assertLess(dist_lbph, config.RECOGNITION_THRESHOLD)

        finally:
            if os.path.exists(test_user_dir):
                shutil.rmtree(test_user_dir, ignore_errors=True)
            try:
                test_store.client.delete_collection("test_recognizer_train_collection")
            except Exception:
                pass

if __name__ == "__main__":
    unittest.main()
