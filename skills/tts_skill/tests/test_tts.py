import unittest
import time
from skills.tts_skill.implementation import TTSSkill


class TestTTSSkill(unittest.TestCase):
    def setUp(self):
        self.tts = TTSSkill(enabled=True, cooldown_seconds=2.0)

    def tearDown(self):
        self.tts.stop()

    def test_speak_cooldown(self):
        msg = "Test message"
        # First speak
        self.tts.speak(msg)
        with self.tts._lock:
            last_t1 = self.tts._last_spoken_time.get(msg)
        self.assertIsNotNone(last_t1)

        # Immediate second speak -> timestamp should remain same due to cooldown
        self.tts.speak(msg)
        with self.tts._lock:
            last_t2 = self.tts._last_spoken_time.get(msg)
        self.assertEqual(last_t1, last_t2)

    def test_toggle_audio(self):
        initial = self.tts.is_enabled()
        toggled = self.tts.toggle()
        self.assertEqual(toggled, not initial)


if __name__ == "__main__":
    unittest.main()
