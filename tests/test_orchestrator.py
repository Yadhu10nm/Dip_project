import unittest
from unittest.mock import MagicMock
import numpy as np
from skills.common.types import RecognitionResult
from skills.system_orchestrator.implementation import SystemOrchestrator


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.mock_camera = MagicMock()
        self.mock_camera.get_frame.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        self.mock_camera.is_opened.return_value = True

        self.orch = SystemOrchestrator(camera=self.mock_camera)
        # Mock surveillance to return recognizable outputs
        self.orch.surveillance.process_frame = MagicMock(return_value=[
            RecognitionResult(name="Yadhu", person_id="u01", similarity=0.91, authorized=True, bbox=(40, 40, 60, 60))
        ])

    def tearDown(self):
        self.orch.stop()

    def test_pipeline_cycle(self):
        frame, recs, loc = self.orch.process_cycle()
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].name, "Yadhu")

    def test_locate_flow(self):
        # User requests to locate Yadhu
        self.orch.execute_command("locate Yadhu")
        self.assertEqual(self.orch.state.locate_target, "Yadhu")

        # Cycle should find and return location
        _, _, loc = self.orch.process_cycle()
        self.assertIsNotNone(loc)
        self.assertTrue(loc.found)
        self.assertEqual(loc.name, "Yadhu")

        # Stop locating
        self.orch.execute_command("stop locating")
        self.assertIsNone(self.orch.state.locate_target)

    def test_toggle_dip_command(self):
        res = self.orch.execute_command("show DIP mode")
        self.assertTrue(res["success"])
        self.assertTrue(self.orch.state.dip_mode)


if __name__ == "__main__":
    unittest.main()
