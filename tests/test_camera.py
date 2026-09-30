import unittest
import numpy as np
from skills.camera_skill.implementation import CameraSkill


class TestCamera(unittest.TestCase):
    def test_offline_frame_generation(self):
        cam = CameraSkill(camera_index=999, width=640, height=480)
        success, frame = cam.get_frame()
        self.assertFalse(success)
        self.assertIsInstance(frame, np.ndarray)
        self.assertEqual(frame.shape, (480, 640, 3))
        cam.stop()

    def test_mirror_toggle(self):
        cam = CameraSkill(camera_index=999)
        orig = cam.flip_horizontal
        flipped = cam.toggle_flip()
        self.assertEqual(flipped, not orig)
        cam.stop()


if __name__ == "__main__":
    unittest.main()
