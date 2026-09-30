import unittest
import shutil
import tempfile
import numpy as np
from skills.common.types import ProcessedFace, RecognitionResult
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill
from skills.vector_database_skill.implementation import VectorDatabaseSkill
from skills.face_recognition_skill.implementation import FaceRecognitionSkill


class TestFaceRecognitionSkill(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vector_db = VectorDatabaseSkill(persist_dir=self.temp_dir, collection_name="test_recog")
        self.embedding = FaceEmbeddingSkill()
        self.recognizer = FaceRecognitionSkill(
            embedding_skill=self.embedding,
            vector_db_skill=self.vector_db,
            match_threshold=0.55
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unknown_when_empty_db(self):
        face_img = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        proc = ProcessedFace(image=face_img, bbox=(10, 10, 50, 50), original_shape=(480, 640))
        result = self.recognizer.recognize_face(proc)

        self.assertIsInstance(result, RecognitionResult)
        self.assertFalse(result.authorized)
        self.assertEqual(result.name, "Unknown")

    def test_known_person_authorized(self):
        face_img = np.random.randint(50, 200, (112, 112, 3), dtype=np.uint8)
        proc = ProcessedFace(image=face_img, bbox=(20, 20, 60, 60), original_shape=(480, 640))

        # Enroll face
        vec = self.embedding.generate_embedding(proc)
        self.vector_db.add_person("p_001", "Yadhu", [vec])

        # Test recognition with exact same face
        result = self.recognizer.recognize_face(proc)
        self.assertTrue(result.authorized)
        self.assertEqual(result.name, "Yadhu")
        self.assertEqual(result.person_id, "p_001")
        self.assertGreaterEqual(result.similarity, 0.55)


if __name__ == "__main__":
    unittest.main()
