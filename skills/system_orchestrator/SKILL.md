# System Orchestrator Skill

## Purpose
Acts as the central event-driven coordinator across all agentic skills, executing the primary vision loop, routing commands, managing application state, and ensuring strict adherence to system decision rules.

## Responsibilities
- Instantiate and configure all sub-skills via dependency injection.
- Maintain global `SystemState` (camera state, active locator target, DIP inspector toggle, sound state, FPS).
- Wire asynchronous event routing between alert, evidence, TTS, and audit skills via `EventBus`.
- Parse and dispatch user commands (`LOCATE_PERSON`, `STOP_LOCATING`, `TOGGLE_DIP`, `TOGGLE_SOUND`, etc.).
- Drive the real-time processing cycle (`process_cycle`).
- Safe initialization and teardown of camera and thread workers.

## Inputs
- Video stream frames, user commands, REST API calls, UI interactions.

## Outputs
- Annotated display frames, real-time telemetry, audit trails, and security alerts.

## Tools / Libraries
- Python, OpenCV, Threading, EventBus

## Workflow
1. Start camera device.
2. Initialize EventBus listeners for TTS and Evidence events.
3. In main loop:
   - Grab frame from `CameraSkill`.
   - Run multi-face detection, preprocessing, and recognition via `SurveillanceSkill`.
   - Check `PersonLocatorSkill` if a person search is requested.
   - Evaluate security breaches via `AlertSkill` (publishing events if unauthorized).
   - Render tactical HUD or DIP Inspector view.
   - Return composite frame and detection results.

## Commands
- `process_cycle()`: Runs one full surveillance frame iteration.
- `execute_command(command)`: Dispatches natural language or structured commands.
- `get_status()`: Consolidated health telemetry.
- `start_camera()` / `stop()`: Device and thread lifecycle.

## Error Handling
- Isolates errors between sub-skills to prevent single-face or single-event failures from crashing the surveillance stream.

## Performance Requirements
- Target: 25-30 FPS full-pipeline throughput.

## Dependencies
- Coordinates all 18 sub-skills.

## Example
```python
from skills.system_orchestrator.implementation import SystemOrchestrator

orchestrator = SystemOrchestrator()
orchestrator.start_camera()
frame, recognitions, locator = orchestrator.process_cycle()
```

## Rules
- The orchestrator should NOT contain implementation details of sub-skills; it solely coordinates them.
- All inter-skill triggers must route through the EventBus or clear skill interfaces.
