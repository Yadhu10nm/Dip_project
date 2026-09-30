import unittest
import numpy as np
from unittest.mock import MagicMock
from skills.common.types import RecognitionResult
from skills.system_orchestrator.implementation import SystemOrchestrator


class TestSystemOrchestrator(unittest.TestCase):
    def setUp(self):
        self.mock_camera = MagicMock()
        self.mock_camera.get_frame.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        self.mock_camera.is_opened.return_value = True

        self.orchestrator = SystemOrchestrator(camera=self.mock_camera)
        # Mock surveillance to return controlled outputs
        self.orchestrator.surveillance.process_frame = MagicMock(return_value=[
            RecognitionResult(name="Yadhu", person_id="u1", similarity=0.92, authorized=True, bbox=(50, 50, 60, 60))
        ])

    def tearDown(self):
        self.orchestrator.stop()

    def test_process_cycle_flow(self):
        frame, recs, loc = self.orchestrator.process_cycle()
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0].name, "Yadhu")
        self.assertIsNone(loc)

    def test_execute_locate_command(self):
        res = self.orchestrator.execute_command("locate Yadhu")
        self.assertTrue(res["success"])
        self.assertEqual(self.orchestrator.state.locate_target, "Yadhu")

        # Now cycle should locate Yadhu
        _, _, loc = self.orchestrator.process_cycle()
        self.assertIsNotNone(loc)
        self.assertTrue(loc.found)
        self.assertEqual(loc.name, "Yadhu")

        # Stop locating
        res_stop = self.orchestrator.execute_command("stop locating")
        self.assertTrue(res_stop["success"])
        self.assertIsNone(self.orchestrator.state.locate_target)


if __name__ == "__main__":
    unittest.main()
