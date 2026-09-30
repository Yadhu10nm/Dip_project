import unittest
from skills.tts_skill.implementation import TTSSkill


class TestTTS(unittest.TestCase):
    def setUp(self):
        self.tts = TTSSkill(enabled=True, cooldown_seconds=3.0)

    def tearDown(self):
        self.tts.stop()

    def test_tts_cooldown_debounce(self):
        msg = "Warning! Unauthorized person detected."
        self.tts.speak(msg)
        with self.tts._lock:
            t1 = self.tts._last_spoken_time.get(msg)
        self.assertIsNotNone(t1)

        # Immediate repeat should be blocked by cooldown
        self.tts.speak(msg)
        with self.tts._lock:
            t2 = self.tts._last_spoken_time.get(msg)
        self.assertEqual(t1, t2)

    def test_tts_mute_toggle(self):
        self.tts.set_enabled(False)
        self.assertFalse(self.tts.is_enabled())
        self.tts.speak("Should not speak")
        self.assertEqual(self.tts._queue.qsize(), 0)


if __name__ == "__main__":
    unittest.main()
