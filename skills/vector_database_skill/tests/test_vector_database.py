import unittest
import shutil
import tempfile
import numpy as np
from skills.vector_database_skill.implementation import VectorDatabaseSkill


class TestVectorDatabaseSkill(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = VectorDatabaseSkill(persist_dir=self.temp_dir, collection_name="test_collection")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_add_and_search_face(self):
        # Create normalized 128-D vector
        vec = np.random.randn(128).astype(np.float32)
        vec /= np.linalg.norm(vec)

        self.db.add_person("p_001", "Alice", [vec], ["sample_01"])
        self.assertEqual(self.db.count(), 1)

        # Search with the exact same vector -> similarity should be ~1.0
        results = self.db.search_face(vec, top_k=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["person_id"], "p_001")
        self.assertEqual(results[0]["name"], "Alice")
        self.assertGreater(results[0]["similarity"], 0.99)

    def test_delete_person(self):
        vec = np.random.randn(128).astype(np.float32)
        vec /= np.linalg.norm(vec)
        self.db.add_person("p_002", "Bob", [vec])
        self.assertEqual(self.db.count(), 1)

        self.db.delete_person("p_002")
        self.assertEqual(self.db.count(), 0)


if __name__ == "__main__":
    unittest.main()
