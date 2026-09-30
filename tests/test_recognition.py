import unittest
import tempfile
import shutil
import numpy as np
from skills.common.types import ProcessedFace
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill
from skills.vector_database_skill.implementation import VectorDatabaseSkill
from skills.face_recognition_skill.implementation import FaceRecognitionSkill


class TestRecognition(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vdb = VectorDatabaseSkill(persist_dir=self.temp_dir, collection_name="unit_recog")
        self.embedding = FaceEmbeddingSkill()
        self.recognizer = FaceRecognitionSkill(
            embedding_skill=self.embedding,
            vector_db_skill=self.vdb,
            match_threshold=0.55
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unknown_face_below_threshold(self):
        # Empty DB or random query -> classified as Unknown and unauthorized
        face = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
        proc = ProcessedFace(face, (10, 10, 50, 50), (480, 640))

        result = self.recognizer.recognize_face(proc)
        self.assertFalse(result.authorized)
        self.assertEqual(result.name, "Unknown")

    def test_known_face_authorized(self):
        face = np.random.randint(50, 200, (112, 112, 3), dtype=np.uint8)
        proc = ProcessedFace(face, (10, 10, 50, 50), (480, 640))

        vec = self.embedding.generate_embedding(proc)
        self.vdb.add_person("auth_01", "Yadhu", [vec])

        result = self.recognizer.recognize_face(proc)
        self.assertTrue(result.authorized)
        self.assertEqual(result.name, "Yadhu")
        self.assertGreaterEqual(result.similarity, 0.55)

    def test_multiple_known_people(self):
        face1 = np.ones((112, 112, 3), dtype=np.uint8) * 80
        proc1 = ProcessedFace(face1, (10, 10, 50, 50), (480, 640))
        vec1 = self.embedding.generate_embedding(proc1)
        self.vdb.add_person("p1", "Amith", [vec1])

        face2 = np.ones((112, 112, 3), dtype=np.uint8) * 180
        proc2 = ProcessedFace(face2, (20, 20, 50, 50), (480, 640))
        vec2 = self.embedding.generate_embedding(proc2)
        self.vdb.add_person("p2", "Yadhu", [vec2])

        res1 = self.recognizer.recognize_face(proc1)
        self.assertEqual(res1.name, "Amith")

        res2 = self.recognizer.recognize_face(proc2)
        self.assertEqual(res2.name, "Yadhu")

    def test_rag_consensus_decision(self):
        face = np.ones((112, 112, 3), dtype=np.uint8) * 120
        proc = ProcessedFace(face, (10, 10, 50, 50), (480, 640))
        vec = self.embedding.generate_embedding(proc)

        # Enroll multiple samples with minor variations
        samples = [vec + np.random.randn(128).astype(np.float32) * 0.01 for _ in range(4)]
        samples = [s / np.linalg.norm(s) for s in samples]
        self.vdb.add_person("p3", "Madhushree", samples)

        res = self.recognizer.recognize_face(proc)
        self.assertTrue(res.authorized)
        self.assertEqual(res.name, "Madhushree")
        self.assertEqual(res.backend, "chroma_rag")
        self.assertGreaterEqual(res.consensus, 0.40)
        self.assertGreater(len(res.evidence), 0)


if __name__ == "__main__":
    unittest.main()
