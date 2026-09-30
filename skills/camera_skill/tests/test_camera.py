import unittest
import numpy as np
from skills.camera_skill.implementation import CameraSkill


class TestCameraSkill(unittest.TestCase):
    def setUp(self):
        # Use an invalid index to test graceful fallback handling without hardware
        self.camera = CameraSkill(camera_index=999, width=320, height=240, target_fps=30)

    def tearDown(self):
        self.camera.stop()

    def test_camera_fallback_when_offline(self):
        success, frame = self.camera.get_frame()
        self.assertFalse(success)
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(frame.shape, (240, 320, 3))

    def test_toggle_flip(self):
        initial = self.camera.flip_horizontal
        flipped = self.camera.toggle_flip()
        self.assertEqual(flipped, not initial)


if __name__ == "__main__":
    unittest.main()
