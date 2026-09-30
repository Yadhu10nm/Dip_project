import unittest
import shutil
import tempfile
import numpy as np
from skills.common.types import SecurityEvent
from skills.evidence_skill.implementation import EvidenceSkill


class TestEvidenceSkill(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.evidence = EvidenceSkill(storage_dir=self.temp_dir, cooldown_seconds=3.0)
        self.dummy_frame = np.ones((480, 640, 3), dtype=np.uint8) * 100

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_evidence_and_cooldown(self):
        evt = SecurityEvent(type="UNAUTHORIZED", timestamp="now", bbox=(10, 10, 50, 50), similarity=0.2)

        # First capture succeeds
        path1 = self.evidence.capture_evidence(self.dummy_frame, evt)
        self.assertIsNotNone(path1)

        # Immediate second capture suppressed by Rule 8
        path2 = self.evidence.capture_evidence(self.dummy_frame, evt)
        self.assertIsNone(path2)

        records = self.evidence.list_evidence()
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
