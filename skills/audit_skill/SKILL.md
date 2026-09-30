# Audit Skill

## Purpose
Maintains a persistent, thread-safe audit log of all security events, access validations, person location events, and intruder breaches in structured JSON format.

## Responsibilities
- Record structured event entries with timestamp, person identity, recognition similarity, event type, camera ID, threat level, and evidence file references.
- Maintain thread-safe read and write locks over the log file.
- Enforce log rotation/capping to prevent unbounded growth.
- Provide query API with filtering and pagination.

## Inputs
- Event metadata: `event_type`, `person_name`, `similarity`, `camera_id`, `threat_level`, `evidence_path`.

## Outputs
- Structured log records (dict) and historical list of records.

## Tools / Libraries
- Python standard library (`json`, `threading`, `datetime`, `os`).

## Workflow
1. Receive `log_event()` request.
2. Format timestamp and unique event ID.
3. Lock file resource.
4. Prepend record to JSON array.
5. Write back to disk and release lock.

## Commands
- `log_event(...)`: Appends event record.
- `get_logs(limit, event_type)`: Queries audit history.
- `clear_logs()`: Resets audit history.

## Error Handling
- Recovers safely from malformed JSON by initializing a fresh log array.

## Performance Requirements
- Thread-safe disk append in <5ms.

## Dependencies
- Python JSON, `config.py`

## Example
```python
from skills.audit_skill.implementation import AuditSkill

audit = AuditSkill()
record = audit.log_event("AUTHORIZED", person_name="Yadhu", similarity=0.91)
print(f"Logged record: {record['id']}")
```

## Rules
- Thread safety must be guaranteed across concurrent video and web threads.
