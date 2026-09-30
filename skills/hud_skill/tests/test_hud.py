import unittest
import numpy as np
from skills.common.types import RecognitionResult, PersonLocation
from skills.hud_skill.implementation import HUDSkill


class TestHUDSkill(unittest.TestCase):
    def setUp(self):
        self.hud = HUDSkill()
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)

    def test_hud_rendering_authorized_and_unauthorized(self):
        recs = [
            RecognitionResult(name="Yadhu", person_id="u1", similarity=0.91, authorized=True, bbox=(50, 50, 80, 80)),
            RecognitionResult(name="Unknown", person_id="", similarity=0.25, authorized=False, bbox=(200, 100, 70, 70)),
        ]
        out = self.hud.render(self.frame, recs, fps=29.5)
        self.assertIsInstance(out, np.ndarray)
        self.assertEqual(out.shape, (480, 640, 3))

    def test_hud_rendering_locate_target(self):
        recs = [
            RecognitionResult(name="Yadhu", person_id="u1", similarity=0.95, authorized=True, bbox=(50, 50, 80, 80)),
        ]
        loc = PersonLocation(found=True, name="Yadhu", bbox=(50, 50, 80, 80), similarity=0.95)
        out = self.hud.render(self.frame, recs, person_location=loc, fps=30.0)
        self.assertEqual(out.shape, (480, 640, 3))


if __name__ == "__main__":
    unittest.main()
