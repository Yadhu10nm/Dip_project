import unittest
import tempfile
import shutil
import numpy as np
from skills.common.types import SecurityEvent
from skills.evidence_skill.implementation import EvidenceSkill


class TestEvidence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vault = EvidenceSkill(storage_dir=self.temp_dir, cooldown_seconds=4.0)
        self.frame = np.ones((480, 640, 3), dtype=np.uint8) * 120

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_duplicate_snapshot_prevention_rule8(self):
        evt = SecurityEvent(type="UNAUTHORIZED", timestamp="now", bbox=(50, 50, 80, 80), similarity=0.25)

        # First capture executes
        path1 = self.vault.capture_evidence(self.frame, evt)
        self.assertIsNotNone(path1)

        # Immediate second capture suppressed by cooldown (Rule 8)
        path2 = self.vault.capture_evidence(self.frame, evt)
        self.assertIsNone(path2)

        # List records
        files = self.vault.list_evidence()
        self.assertEqual(len(files), 1)


if __name__ == "__main__":
    unittest.main()
