import os
import json
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional
import config


class AuditSkill:
    """
    Audit Trail Logging Skill.
    Thread-safely records, persists, queries, and filters surveillance events
    and recognition decisions in JSON format.
    """

    def __init__(self, log_file: str = config.AUDIT_LOG_FILE):
        self.log_file = log_file
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def log_event(
        self,
        event_type: str,
        person_name: str = "Unknown",
        similarity: float = 0.0,
        camera_id: str = config.CAMERA_NAME,
        threat_level: str = "LOW",
        evidence_path: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Appends an event record to the audit trail.
        """
        now = datetime.now()
        event_id = f"EV_{now.strftime('%Y%m%d_%H%M%S')}_{os.urandom(2).hex()}"
        record = {
            "id": event_id,
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
            "event": event_type,
            "person": person_name,
            "similarity": round(float(similarity), 4),
            "camera": camera_id,
            "threat_level": threat_level,
            "evidence_path": evidence_path,
        }
        if extra_data:
            record.update(extra_data)

        with self._lock:
            logs = self._read_logs_internal()
            logs.insert(0, record)  # Newest first
            if len(logs) > 1000:
                logs = logs[:1000]  # Cap maximum entries
            self._write_logs_internal(logs)

        return record

    def get_logs(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves historical audit records with optional event type filtering."""
        with self._lock:
            logs = self._read_logs_internal()

        if event_type:
            logs = [entry for entry in logs if entry.get("event") == event_type]

        return logs[:limit]

    def clear_logs(self):
        """Clears all audit logs."""
        with self._lock:
            self._write_logs_internal([])

    def _read_logs_internal(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _write_logs_internal(self, logs: List[Dict[str, Any]]):
        try:
            with open(self.log_file, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"[AuditSkill] Write error: {e}")
