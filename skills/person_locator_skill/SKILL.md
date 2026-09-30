# Person Locator Skill

## Purpose
Searches and tracks a specific named individual across live camera detections, reporting exact bounding coordinates and similarity when found or confirming absence.

## Responsibilities
- Parse and maintain target person search requests.
- Inspect real-time recognition results for each frame.
- Compare identities deterministically against the query name.
- Generate `PersonLocation` output with localization bounding box.
- Report `found=False` when the requested person is not in view.

## Inputs
- `LocatePersonCommand` or target name string.
- List of `RecognitionResult` objects for the active frame.

## Outputs
- `PersonLocation` containing `(found: bool, name: str, bbox: Optional[tuple], similarity: float)`.

## Tools / Libraries
- Python standard library, Dataclasses.

## Workflow
1. Set target identity (e.g., "Yadhu").
2. For each incoming frame, receive recognized candidate faces.
3. Compare candidate identities against the target name.
4. If a candidate matches with authorized status, return `PersonLocation(found=True, ...)`.
5. If no candidate matches, return `PersonLocation(found=False, ...)`.

## Commands
- `set_target(name_or_command)`: Activates target search.
- `clear_target()`: Clears active search.
- `locate_in_detections(recognition_results)`: Evaluates current detections.

## Error Handling
- Safely handles None or empty target requests without raising exceptions.

## Performance Requirements
- Sub-millisecond matching over candidate recognition results.

## Dependencies
- `skills.common.types.LocatePersonCommand`
- `skills.common.types.PersonLocation`
- `skills.common.types.RecognitionResult`

## Example
```python
from skills.person_locator_skill.implementation import PersonLocatorSkill
from skills.common.types import LocatePersonCommand

locator = PersonLocatorSkill()
locator.set_target(LocatePersonCommand(person_name="Yadhu"))
location = locator.locate_in_detections(current_recognitions)
if location.found:
    print(f"Target located at {location.bbox} with similarity {location.similarity:.2f}")
else:
    print("Target person is not currently visible.")
```

## Rules
- **Rule 9**: Only highlight a face whose recognition result matches the requested person.
- **Rule 10**: If no matching face exists, explicitly report that the target is not currently visible.
