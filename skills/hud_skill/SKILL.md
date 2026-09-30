# HUD Skill

## Purpose
Renders tactical cyber-security surveillance Heads-Up Display (HUD) overlays, targeting brackets, threat callouts, laser pointers, and person locator tracking reticles directly onto video frames.

## Responsibilities
- Render tactical telemetry headers and footers (`REC` indicator, timestamp, camera ID, FPS).
- Draw green tactical corner brackets and verified badges for authorized personnel.
- Draw red reticles, pointing callout lines, and warning cards for unauthorized intruders.
- Render amber/gold targeting reticles when a specific person is actively located via `person_locator_skill`.
- Render flashing perimeter threat boundaries during security breaches.

## Inputs
- Video frame (`numpy.ndarray`).
- List of `RecognitionResult` objects.
- Optional `PersonLocation` tracking state.
- Telemetry parameters (`fps`, `is_dip_mode`).

## Outputs
- Annotated BGR video frame (`numpy.ndarray`).

## Tools / Libraries
- OpenCV (`cv2.putText`, `cv2.rectangle`, `cv2.line`, `cv2.circle`, `cv2.drawMarker`)
- NumPy

## Workflow
1. Receive video frame and recognition outputs.
2. Draw top and bottom telemetry chrome.
3. For each recognition result:
   - If matches active locate target $\implies$ render amber locate reticle.
   - Else if authorized $\implies$ render emerald green brackets.
   - Else $\implies$ render red targeting reticle with pointing callout.
4. If intruder detected $\implies$ pulse screen border in red.
5. Return rendered frame.

## Commands
- `render(frame, recognition_results, person_location, fps, is_dip_mode)`: Renders HUD.

## Error Handling
- Returns original frame untouched if frame is None or empty.

## Performance Requirements
- Sub-3ms rendering time per frame.

## Dependencies
- `skills.common.types.RecognitionResult`
- `skills.common.types.PersonLocation`

## Example
```python
from skills.hud_skill.implementation import HUDSkill

hud = HUDSkill()
rendered_frame = hud.render(frame, recognitions, person_loc, fps=30.0)
```

## Rules
- Strictly visual; do not modify recognition data or state.
