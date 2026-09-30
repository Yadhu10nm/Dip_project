# Alert Skill

## Purpose
Monitors recognition streams, detects unauthorized breaches, enforces alerting cooldown policies, and dispatches security events across the system event bus.

## Responsibilities
- Filter incoming recognition decisions for unauthorized identities.
- Apply cooldown debounce timers to prevent alert flooding.
- Construct standardized `SecurityEvent` payloads.
- Dispatch `UNAUTHORIZED_PERSON`, `TTS_REQUESTED`, and `EVIDENCE_REQUESTED` events.

## Inputs
- List of `RecognitionResult` objects.

## Outputs
- Optional `SecurityEvent` instance when a cooldown-compliant breach occurs.

## Tools / Libraries
- Python standard library (`time`, `datetime`).

## Workflow
1. Receive recognition results.
2. Check if any subject is `authorized=False`.
3. Check elapsed time against `ALERT_COOLDOWN_SECONDS`.
4. If cooldown expired, format `SecurityEvent`.
5. Emit events over `EventBus` to notify TTS and Evidence skills.

## Commands
- `evaluate_detections(recognition_results, timestamp)`: Evaluates threat state.
- `reset_cooldown()`: Clears debounce state.

## Error Handling
- Safely returns `None` when no intruders are present or during cooldown without throwing exceptions.

## Performance Requirements
- Sub-millisecond evaluation time.

## Dependencies
- `skills.common.types.SecurityEvent`
- `skills.common.types.RecognitionResult`
- `skills.common.events.EventBus`

## Example
```python
from skills.alert_skill.implementation import AlertSkill

alerter = AlertSkill(event_bus=event_bus)
event = alerter.evaluate_detections(current_recognitions)
if event:
    print(f"Alert triggered: {event.type} at {event.timestamp}")
```

## Rules
- **Rule 7**: Do not repeatedly trigger alarms for the same event without cooldown.
- Decoupled: Never directly manipulate audio devices or filesystems; dispatch events.
