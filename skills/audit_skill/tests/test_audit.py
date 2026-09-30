import unittest
import tempfile
import shutil
import os
from skills.audit_skill.implementation import AuditSkill


class TestAuditSkill(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test_audit.json")
        self.audit = AuditSkill(log_file=self.log_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_log_and_query_events(self):
        rec = self.audit.log_event("AUTHORIZED", person_name="Yadhu", similarity=0.93)
        self.assertEqual(rec["person"], "Yadhu")
        self.assertEqual(rec["event"], "AUTHORIZED")

        logs = self.audit.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["id"], rec["id"])

    def test_filter_and_clear(self):
        self.audit.log_event("AUTHORIZED", person_name="Alice")
        self.audit.log_event("UNAUTHORIZED", person_name="Unknown")

        auth_logs = self.audit.get_logs(event_type="AUTHORIZED")
        self.assertEqual(len(auth_logs), 1)
        self.assertEqual(auth_logs[0]["person"], "Alice")

        self.audit.clear_logs()
        self.assertEqual(len(self.audit.get_logs()), 0)


if __name__ == "__main__":
    unittest.main()
