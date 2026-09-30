# Evidence Skill

## Purpose
Maintains the forensic Evidence Vault by saving watermarked photographic snapshots of unauthorized intrusion events while suppressing duplicate frames via cooldown policies.

## Responsibilities
- Format timestamped filenames (`intruder_YYYYMMDD_HHMMSS.jpg`).
- Annotate evidence images with timestamps and threat bounding boxes.
- Enforce snapshot cooldown timers to avoid filling disk space.
- Persist images into `data/intruders/`.
- Provide query API to enumerate historical evidence snapshots.

## Inputs
- Video frame (`numpy.ndarray`).
- Optional `SecurityEvent` metadata.

## Outputs
- Absolute file path to saved JPEG file, or `None` if suppressed by cooldown.

## Tools / Libraries
- OpenCV (`cv2.imwrite`, `cv2.putText`, `cv2.rectangle`)
- Python `os`, `time`, `datetime`

## Workflow
1. Skill receives `capture_evidence(frame, security_event)`.
2. Check cooldown interval against `INTRUDER_SNAPSHOT_COOLDOWN`.
3. If cooldown has elapsed:
   - Overlay watermark header and threat bounding box.
   - Save high-resolution JPEG.
   - Attach filename to `security_event`.
   - Update last snapshot timestamp.

## Commands
- `capture_evidence(frame, security_event, force=False)`: Records an incident snapshot.
- `list_evidence()`: Enumerates recorded evidence snapshots.

## Error Handling
- Silently ignores empty frames.
- Catches I/O exceptions during write and logs warnings.

## Performance Requirements
- Non-blocking disk writing (typically <10ms for JPEG encoding).

## Dependencies
- `skills.common.types.SecurityEvent`

## Example
```python
from skills.evidence_skill.implementation import EvidenceSkill

vault = EvidenceSkill()
saved_path = vault.capture_evidence(frame, security_event)
if saved_path:
    print(f"Evidence locked at {saved_path}")
```

## Rules
- **Rule 8**: Do not save hundreds of identical intruder snapshots every frame. Enforce strict cooldown.
