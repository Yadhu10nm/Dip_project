import unittest
import numpy as np
from skills.dip_inspector_skill.implementation import DIPInspectorSkill


class TestDIPInspectorSkill(unittest.TestCase):
    def setUp(self):
        self.inspector = DIPInspectorSkill()
        self.frame = np.ones((480, 640, 3), dtype=np.uint8) * 120

    def test_quad_view_shape(self):
        quad = self.inspector.create_quad_view(self.frame)
        self.assertIsInstance(quad, np.ndarray)
        self.assertEqual(quad.shape, (480, 640, 3))


if __name__ == "__main__":
    unittest.main()
