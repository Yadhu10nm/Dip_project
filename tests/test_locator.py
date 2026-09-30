import unittest
from skills.common.types import RecognitionResult
from skills.person_locator_skill.implementation import PersonLocatorSkill


class TestLocator(unittest.TestCase):
    def setUp(self):
        self.locator = PersonLocatorSkill(target_person="Yadhu")

    def test_locate_yadhu_found(self):
        recs = [
            RecognitionResult(name="Amith", person_id="1", similarity=0.9, authorized=True, bbox=(10, 10, 50, 50)),
            RecognitionResult(name="Yadhu", person_id="2", similarity=0.94, authorized=True, bbox=(150, 100, 80, 80)),
        ]
        loc = self.locator.locate_in_detections(recs)
        self.assertTrue(loc.found)
        self.assertEqual(loc.name, "Yadhu")
        self.assertEqual(loc.bbox, (150, 100, 80, 80))

    def test_locate_yadhu_not_visible(self):
        recs = [
            RecognitionResult(name="Amith", person_id="1", similarity=0.9, authorized=True, bbox=(10, 10, 50, 50)),
            RecognitionResult(name="Unknown", person_id="", similarity=0.2, authorized=False, bbox=(100, 100, 60, 60)),
        ]
        loc = self.locator.locate_in_detections(recs)
        self.assertFalse(loc.found)
        self.assertEqual(loc.name, "Yadhu")
        self.assertIsNone(loc.bbox)


if __name__ == "__main__":
    unittest.main()
