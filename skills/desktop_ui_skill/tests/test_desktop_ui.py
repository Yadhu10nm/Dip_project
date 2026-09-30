import unittest
from unittest.mock import MagicMock
import numpy as np
from skills.system_orchestrator.implementation import SystemOrchestrator
from skills.desktop_ui_skill.implementation import DesktopUISkill


class TestDesktopUISkill(unittest.TestCase):
    def setUp(self):
        mock_camera = MagicMock()
        mock_camera.get_frame.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        self.orchestrator = SystemOrchestrator(camera=mock_camera)
        self.desktop_skill = DesktopUISkill(orchestrator=self.orchestrator)

    def tearDown(self):
        self.orchestrator.stop()

    def test_init_properties(self):
        self.assertEqual(self.desktop_skill.window_name, "AI SECURITY CCTV // TACTICAL SURVEILLANCE")
        self.assertIsNotNone(self.desktop_skill.orchestrator)


if __name__ == "__main__":
    unittest.main()
