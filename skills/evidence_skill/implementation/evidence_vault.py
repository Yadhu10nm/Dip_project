import os
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
import cv2
import numpy as np
import config
from skills.common.types import SecurityEvent


class EvidenceSkill:
    """
    Evidence Vault Skill.
    Captures, annotates, and persists high-resolution forensic photographic
    evidence of security breaches with timestamping and duplicate suppression.

    RULES:
    - Rule 8: Do not save hundreds of identical intruder snapshots every frame.
    Enforces a strict snapshot cooldown.
    """

    def __init__(
        self,
        storage_dir: str = config.INTRUDERS_DIR,
        cooldown_seconds: float = config.INTRUDER_SNAPSHOT_COOLDOWN,
    ):
        self.storage_dir = storage_dir
        self.cooldown_seconds = cooldown_seconds
        self.last_snapshot_time = 0.0
        os.makedirs(self.storage_dir, exist_ok=True)

    def capture_evidence(
        self,
        frame: np.ndarray,
        security_event: Optional[SecurityEvent] = None,
        force: bool = False,
    ) -> Optional[str]:
        """
        Saves snapshot of security breach to disk.
        Returns:
            Relative or absolute file path to saved JPEG evidence, or None if suppressed by cooldown.
        """
        if frame is None or frame.size == 0:
            return None

        now = time.time()
        if not force and (now - self.last_snapshot_time) < self.cooldown_seconds:
            return None  # Rule 8: Suppress duplicate snapshot

        self.last_snapshot_time = now
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"intruder_{timestamp_str}.jpg"
        filepath = os.path.join(self.storage_dir, filename)

        # Annotate snapshot with security watermark
        evidence_canvas = frame.copy()
        h, w = evidence_canvas.shape[:2]
        cv2.rectangle(evidence_canvas, (0, 0), (w, 32), (0, 0, 180), -1)
        cv2.putText(
            evidence_canvas,
            f"EVIDENCE RECORD // {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} // THREAT: HIGH",
            (10, 22),
            cv2.FONT_HERSHEY_DUPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )

        if security_event and security_event.bbox:
            x, y, bw, bh = security_event.bbox
            cv2.rectangle(evidence_canvas, (x, y), (x + bw, y + bh), (0, 0, 255), 2)

        cv2.imwrite(filepath, evidence_canvas)

        if security_event:
            security_event.evidence_file = filename

        return filepath

    def list_evidence(self) -> List[Dict[str, Any]]:
        """Returns metadata of all captured evidence snapshots."""
        records = []
        if not os.path.exists(self.storage_dir):
            return records

        for fname in sorted(os.listdir(self.storage_dir), reverse=True):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                fpath = os.path.join(self.storage_dir, fname)
                mtime = os.path.getmtime(fpath)
                records.append({
                    "filename": fname,
                    "filepath": fpath,
                    "timestamp": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "size_bytes": os.path.getsize(fpath),
                })
        return records
