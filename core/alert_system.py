import os
import json
import time
import queue
import threading
from datetime import datetime
import cv2
import numpy as np
import config

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

class AlertSystem:
    """
    Manages audible security voice warnings, alarm sound beeps,
    and automated evidence snapshot logging for unauthorized intrusions.
    """

    def __init__(self):
        self.last_voice_alert_time = 0.0
        self.last_snapshot_time = 0.0
        self.voice_enabled = config.ENABLE_VOICE_ALERT
        self.chime_enabled = config.ENABLE_AUDIO_CHIME
        self.log_file = config.AUDIT_LOG_FILE

        # Worker thread queue for non-blocking voice speech
        self.speech_queue = queue.Queue()
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()

    def _speech_worker(self):
        """Dedicated background thread for speech synthesis to prevent video latency."""
        engine = None
        if HAS_PYTTSX3:
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 170)  # Urgent, crisp announcement speed
                engine.setProperty('volume', 1.0)
            except Exception as e:
                print(f"[Alert System] Failed to init pyttsx3: {e}")
                engine = None

        while True:
            text = self.speech_queue.get()
            if text is None:
                break
            if engine:
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"[Alert System] Speech error: {e}")
                    # Re-initialize engine if it was interrupted
                    try:
                        engine = pyttsx3.init()
                        engine.setProperty('rate', 170)
                    except Exception:
                        pass
            self.speech_queue.task_done()

    def trigger_intruder_alert(self, frame: np.ndarray, intruder_detections: list, camera_name: str = config.CAMERA_NAME):
        """
        Triggers acoustic alarm, voice announcement, and evidence snapshot capture.
        """
        current_time = time.time()

        # 1. Voice Announcement & Audio Beep
        if self.voice_enabled and (current_time - self.last_voice_alert_time >= config.ALERT_COOLDOWN_SECONDS):
            self.last_voice_alert_time = current_time

            # Short alarm beep
            if self.chime_enabled and HAS_WINSOUND:
                try:
                    winsound.Beep(2600, 150)
                except Exception:
                    pass

            # Queue spoken security warning
            msg = "Warning! Security alert! Unauthorized person detected on camera one!"
            self.speech_queue.put(msg)

        # 2. Automated Intruder Snapshot & Audit Logging
        if current_time - self.last_snapshot_time >= config.INTRUDER_SNAPSHOT_COOLDOWN:
            self.last_snapshot_time = current_time
            self._save_incident_snapshot(frame, intruder_detections, camera_name)

    def _save_incident_snapshot(self, frame: np.ndarray, intruder_detections: list, camera_name: str):
        """Saves timestamped image evidence and JSON audit log entry."""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        human_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"intruder_{timestamp_str}.jpg"
        filepath = os.path.join(config.INTRUDERS_DIR, filename)

        # Save snapshot
        cv2.imwrite(filepath, frame)

        # Append to audit log
        logs = self.get_audit_logs()
        avg_distance = (
            sum(d.get("distance", 0.0) for d in intruder_detections) / len(intruder_detections)
            if intruder_detections else 0.0
        )

        entry = {
            "id": f"EV_{timestamp_str}",
            "timestamp": human_time,
            "camera": camera_name,
            "type": "UNAUTHORIZED_INTRUSION",
            "threat_level": "HIGH",
            "intruder_count": len(intruder_detections),
            "avg_distance": round(avg_distance, 1),
            "snapshot_file": filename,
            "snapshot_url": f"/api/intruder_snapshot/{filename}"
        }

        logs.insert(0, entry)  # Prepend newest incident
        logs = logs[:100]  # Retain last 100 entries

        with open(self.log_file, "w") as f:
            json.dump(logs, f, indent=2)

    def get_audit_logs(self) -> list:
        """Retrieves history of intrusion events."""
        if not os.path.exists(self.log_file):
            return []
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def clear_audit_logs(self):
        """Clears audit logs."""
        with open(self.log_file, "w") as f:
            json.dump([], f, indent=2)
