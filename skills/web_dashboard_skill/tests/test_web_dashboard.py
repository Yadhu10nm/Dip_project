import unittest
from unittest.mock import MagicMock
import numpy as np
from skills.system_orchestrator.implementation import SystemOrchestrator
from skills.web_dashboard_skill.implementation import WebDashboardSkill


class TestWebDashboardSkill(unittest.TestCase):
    def setUp(self):
        mock_camera = MagicMock()
        mock_camera.get_frame.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        self.orchestrator = SystemOrchestrator(camera=mock_camera)
        self.web_skill = WebDashboardSkill(orchestrator=self.orchestrator)
        self.client = self.web_skill.app.test_client()

    def tearDown(self):
        self.orchestrator.stop()

    def test_status_endpoint(self):
        resp = self.client.get("/api/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("fps", data)
        self.assertIn("total_faces", data)
        self.assertIn("is_dip_mode", data)

    def test_command_endpoint(self):
        resp = self.client.post("/api/command", json={"command": "locate Yadhu"})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("target"), "Yadhu")

    def test_toggle_dip_endpoint(self):
        resp = self.client.post("/api/toggle_dip")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))


if __name__ == "__main__":
    unittest.main()
