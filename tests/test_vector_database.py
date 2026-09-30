import unittest
import tempfile
import shutil
import numpy as np
from skills.vector_database_skill.implementation import VectorDatabaseSkill


class TestVectorDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vdb = VectorDatabaseSkill(persist_dir=self.temp_dir, collection_name="unit_test_vdb")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cosine_similarity_retrieval(self):
        vec1 = np.random.randn(128).astype(np.float32)
        vec1 /= np.linalg.norm(vec1)

        self.vdb.add_person("user_01", "Amith", [vec1])

        # Query exact vector
        res = self.vdb.search_face(vec1, top_k=1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["name"], "Amith")
        self.assertAlmostEqual(res[0]["similarity"], 1.0, places=3)

    def test_delete_person(self):
        vec = np.random.randn(128).astype(np.float32)
        vec /= np.linalg.norm(vec)

        self.vdb.add_person("user_02", "Yadhu", [vec])
        self.assertEqual(self.vdb.count(), 1)

        self.vdb.delete_person("user_02")
        self.assertEqual(self.vdb.count(), 0)

    def test_rag_search_with_consensus(self):
        base_a = np.random.randn(128).astype(np.float32)
        base_a /= np.linalg.norm(base_a)

        # Create slight variations for User A
        samples_a = [base_a]
        for i in range(4):
            noise = np.random.randn(128).astype(np.float32) * 0.05
            v = base_a + noise
            v /= np.linalg.norm(v)
            samples_a.append(v)

        # Create vectors for User B (orthogonal)
        base_b = np.random.randn(128).astype(np.float32)
        base_b /= np.linalg.norm(base_b)
        samples_b = [base_b]

        self.vdb.add_person("user_a", "Alice", samples_a)
        self.vdb.add_person("user_b", "Bob", samples_b)

        # Query with base_a
        rag_res = self.vdb.search_face_rag(base_a, top_k=5, min_consensus=0.40)
        self.assertIsNotNone(rag_res)
        self.assertEqual(rag_res["person_id"], "user_a")
        self.assertEqual(rag_res["name"], "Alice")
        self.assertTrue(rag_res["has_consensus"])
        self.assertGreaterEqual(rag_res["consensus_ratio"], 0.40)
        self.assertGreaterEqual(rag_res["similarity"], 0.85)
        self.assertGreater(len(rag_res["evidence"]), 0)

    def test_rag_search_empty(self):
        vec = np.random.randn(128).astype(np.float32)
        vec /= np.linalg.norm(vec)
        self.assertIsNone(self.vdb.search_face_rag(vec))


if __name__ == "__main__":
    unittest.main()
