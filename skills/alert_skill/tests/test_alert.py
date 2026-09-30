import unittest
from skills.common.types import RecognitionResult, SecurityEvent
from skills.common.events import EventBus, EventType
from skills.alert_skill.implementation import AlertSkill


class TestAlertSkill(unittest.TestCase):
    def setUp(self):
        self.bus = EventBus()
        self.alerter = AlertSkill(event_bus=self.bus, cooldown_seconds=5.0)

    def test_alert_triggers_on_unauthorized(self):
        received_events = []
        self.bus.subscribe(EventType.UNAUTHORIZED_PERSON, lambda e: received_events.append(e))

        recs = [RecognitionResult(name="Unknown", person_id="", similarity=0.2, authorized=False, bbox=(10, 10, 50, 50))]
        event = self.alerter.evaluate_detections(recs, frame_timestamp=100.0)

        self.assertIsNotNone(event)
        self.assertIsInstance(event, SecurityEvent)
        self.assertEqual(len(received_events), 1)

    def test_cooldown_suppresses_rapid_fire(self):
        recs = [RecognitionResult(name="Unknown", person_id="", similarity=0.2, authorized=False, bbox=(10, 10, 50, 50))]
        # First alert at t=100
        e1 = self.alerter.evaluate_detections(recs, frame_timestamp=100.0)
        self.assertIsNotNone(e1)

        # Second alert at t=102 (within 5.0s cooldown) -> should be suppressed
        e2 = self.alerter.evaluate_detections(recs, frame_timestamp=102.0)
        self.assertIsNone(e2)

        # Third alert at t=106 (after 5.0s cooldown) -> should fire
        e3 = self.alerter.evaluate_detections(recs, frame_timestamp=106.0)
        self.assertIsNotNone(e3)


if __name__ == "__main__":
    unittest.main()
