import unittest
from skills.common.types import RecognitionResult, LocatePersonCommand, PersonLocation
from skills.person_locator_skill.implementation import PersonLocatorSkill


class TestPersonLocatorSkill(unittest.TestCase):
    def setUp(self):
        self.locator = PersonLocatorSkill()

    def test_locate_person_found(self):
        self.locator.set_target(LocatePersonCommand(person_name="Yadhu"))
        recognitions = [
            RecognitionResult(name="Amith", person_id="001", similarity=0.88, authorized=True, bbox=(10, 10, 50, 50)),
            RecognitionResult(name="Yadhu", person_id="002", similarity=0.92, authorized=True, bbox=(100, 100, 60, 60)),
        ]

        loc = self.locator.locate_in_detections(recognitions)
        self.assertTrue(loc.found)
        self.assertEqual(loc.name, "Yadhu")
        self.assertEqual(loc.bbox, (100, 100, 60, 60))
        self.assertEqual(loc.similarity, 0.92)

    def test_locate_person_not_visible(self):
        self.locator.set_target("Yadhu")
        recognitions = [
            RecognitionResult(name="Amith", person_id="001", similarity=0.88, authorized=True, bbox=(10, 10, 50, 50)),
            RecognitionResult(name="Unknown", person_id="", similarity=0.20, authorized=False, bbox=(70, 70, 50, 50)),
        ]

        loc = self.locator.locate_in_detections(recognitions)
        self.assertFalse(loc.found)
        self.assertEqual(loc.name, "Yadhu")
        self.assertIsNone(loc.bbox)


if __name__ == "__main__":
    unittest.main()
