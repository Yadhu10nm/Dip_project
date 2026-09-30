import time
import queue
import threading
from typing import Optional
import config


class TTSSkill:
    """
    Asynchronous Text-to-Speech (TTS) Skill.
    Runs speech synthesis completely off-thread in a dedicated daemon worker
    with message deduplication and cooldown enforcement.

    RULES:
    - Never block the video acquisition or processing threads.
    - Suppress identical message spam within cooldown duration.
    """

    def __init__(
        self,
        enabled: bool = config.ENABLE_VOICE_ALERT,
        cooldown_seconds: float = config.TTS_COOLDOWN_SECONDS,
    ):
        self.enabled = enabled
        self.cooldown_seconds = cooldown_seconds
        self._queue: queue.Queue = queue.Queue(maxsize=10)
        self._last_spoken_time: dict = {}
        self._is_running = True
        self._lock = threading.Lock()

        # Start background consumer thread
        self._worker_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self._worker_thread.start()

    def speak(self, text: str, force: bool = False):
        """
        Enqueues a text message to be spoken asynchronously.
        Applies cooldown debounce to avoid repeated speech.
        """
        if not self.enabled or not text or not text.strip():
            return

        clean_text = text.strip()
        now = time.time()

        with self._lock:
            last_time = self._last_spoken_time.get(clean_text, 0.0)
            if not force and (now - last_time) < self.cooldown_seconds:
                return  # Cooldown active, suppress duplicate utterance

            self._last_spoken_time[clean_text] = now

        try:
            self._queue.put_nowait(clean_text)
        except queue.Full:
            pass  # Drop if queue is saturated

    def set_enabled(self, enabled: bool):
        """Enables or disables voice synthesis."""
        self.enabled = enabled

    def is_enabled(self) -> bool:
        return self.enabled

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        return self.enabled

    def _speech_worker(self):
        """Dedicated background thread managing pyttsx3 speech synthesis."""
        engine = None
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", 160)
            engine.setProperty("volume", 0.9)
        except Exception as e:
            # Fallback for headless environments without SAPI5
            print(f"[TTSSkill] Speech engine initialization notice: {e}")
            engine = None

        while self._is_running:
            try:
                text = self._queue.get(timeout=0.5)
                if not text:
                    continue

                if engine is not None and self.enabled:
                    try:
                        engine.say(text)
                        engine.runAndWait()
                    except Exception as e:
                        print(f"[TTSSkill] Playback warning: {e}")
                else:
                    # Log utterance to console in mock/fallback mode
                    print(f"[TTS Audio Broadcast]: {text}")

                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TTSSkill] Worker exception: {e}")

    def stop(self):
        """Stops the worker thread."""
        self._is_running = False
