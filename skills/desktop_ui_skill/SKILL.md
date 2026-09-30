# Desktop UI Skill

## Purpose
Renders a standalone native OpenCV window providing full-framerate CCTV HUD surveillance and interactive keyboard controls.

## Responsibilities
- Create and manage the OpenCV display window (`cv2.namedWindow`, `cv2.imshow`).
- Poll operator keyboard events (`cv2.waitKey`).
- Handle hotkeys (`R` for registration, `D` for DIP view, `S` for sound, `L` for logs, `Q` for exit).
- Cleanly release window resources on exit.

## Inputs
- Processed frames and commands from `SystemOrchestrator`.

## Outputs
- Native high-performance desktop display window.

## Tools / Libraries
- OpenCV (`cv2.imshow`, `cv2.waitKey`, `cv2.destroyAllWindows`).

## Workflow
1. Initialize desktop skill with `SystemOrchestrator`.
2. Start camera and open window.
3. In loop:
   - Call `orchestrator.process_cycle()`.
   - Render frame via `cv2.imshow`.
   - Read keypress and dispatch commands to orchestrator.
4. On exit, destroy window and call `orchestrator.stop()`.

## Commands
- `run()`: Starts desktop surveillance loop.

## Hotkeys
- `R`: Interactive webcam enrollment.
- `D`: Toggle DIP 4-way inspector.
- `S`: Toggle audio alerts.
- `F`: Toggle horizontal mirror.
- `L`: Print audit logs to terminal.
- `Q` / `ESC`: Quit.

## Error Handling
- Safe teardown via `finally` block ensuring all OpenCV windows and camera devices are freed.

## Performance Requirements
- Target: 30+ FPS native hardware refresh.

## Dependencies
- `skills.system_orchestrator`
- OpenCV

## Example
```python
from skills.system_orchestrator.implementation import SystemOrchestrator
from skills.desktop_ui_skill.implementation import DesktopUISkill

orch = SystemOrchestrator()
ui = DesktopUISkill(orchestrator=orch)
ui.run()
```

## Rules
- Must release all OpenCV windows and camera resources upon exiting.
