# Web Dashboard Skill

## Purpose
Provides a browser-based cyber-security CCTV surveillance control room with live MJPEG streaming, interactive person locator commands, whitelist management, evidence vault review, and audit trail inspection.

## Responsibilities
- Serve the HTML/CSS/JS frontend dashboard.
- Stream live MJPEG surveillance video (`/video_feed`).
- Route person locate and system commands through `SystemOrchestrator`.
- Expose REST endpoints for enrollment, personnel management, evidence viewing, and audit logs.
- Strictly delegate all CV and decision logic to the orchestrator.

## Inputs
- HTTP GET/POST requests from browser UI.

## Outputs
- HTML templates, JSON responses, and MJPEG multipart image streams.

## Tools / Libraries
- Flask, OpenCV (`cv2.imencode`), JSON

## Workflow
1. Initialize Flask app with `SystemOrchestrator`.
2. Serve dashboard at `http://localhost:5000`.
3. Client polls `/api/status` and streams `/video_feed`.
4. User clicks "Locate Yadhu" $\implies$ client sends POST `/api/command` $\implies$ orchestrator sets locator target.
5. All actions reflect live in HUD and browser telemetry.

## Commands
- `run(host, port, debug)`: Launches Flask web server.

## Error Handling
- Returns HTTP 400 with descriptive error messages on malformed enrollment or command requests.

## Performance Requirements
- MJPEG streaming at 25-30 FPS with sub-50ms web response times.

## Dependencies
- `skills.system_orchestrator`
- Flask, OpenCV

## Example
```python
from skills.system_orchestrator.implementation import SystemOrchestrator
from skills.web_dashboard_skill.implementation import WebDashboardSkill

orch = SystemOrchestrator()
web = WebDashboardSkill(orchestrator=orch)
web.run(port=5000)
```

## Rules
- **RULE**: The web layer should communicate with the orchestrator instead of directly manipulating internal computer vision, audio, or database modules.
