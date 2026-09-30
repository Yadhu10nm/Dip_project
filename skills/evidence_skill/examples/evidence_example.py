import numpy as np
from skills.evidence_skill.implementation import EvidenceSkill
from skills.common.types import SecurityEvent


def main():
    vault = EvidenceSkill()
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    evt = SecurityEvent(type="UNAUTHORIZED", timestamp="2026-09-30 18:45:00", bbox=(50, 50, 100, 100), similarity=0.3)
    path = vault.capture_evidence(frame, evt, force=True)
    print(f"[EvidenceSkill] Captured test snapshot: {path}")


if __name__ == "__main__":
    main()
