# Camera Skill

## Purpose
Manages hardware webcam and CCTV stream acquisition, lifecycle management, frame throttling, and optional mirror inversion.

## Responsibilities
- Open webcam or CCTV camera stream via OpenCV.
- Capture frames reliably at target framerate.
- Handle camera disconnection gracefully with synthetic standby fallback frames.
- Perform horizontal mirror inversion for natural user positioning.
- Release video capture hardware safely on shutdown.

## Inputs
- Camera configuration: device index, resolution width/height, target FPS, and flip mode.

## Outputs
- Raw or mirrored BGR video frame (`numpy.ndarray`) with status flag `(success: bool, frame: np.ndarray)`.

## Tools / Libraries
- OpenCV (`cv2.VideoCapture`, `cv2.flip`)
- NumPy

## Workflow
1. Initialize device index and desired resolution.
2. Call `camera.start()` to open hardware capture.
3. Call `camera.get_frame()` in real-time loops to acquire frames throttled to target FPS.
4. Call `camera.stop()` to release hardware resources.

## Commands
- `start`: Initialize and open video stream.
- `get_frame`: Acquire next video frame.
- `toggle_flip`: Toggle horizontal mirroring.
- `stop`: Release hardware device.

## Error Handling
- If camera device index is invalid or busy, `start()` returns `False` and `get_frame()` serves a standby diagnostic image without raising unhandled exceptions.

## Performance Requirements
- Target: 30 FPS at 640x480 resolution with frame throttling to avoid CPU spinning.

## Dependencies
- None. This is a root acquisition skill.

## Example
```python
from skills.camera_skill.implementation import CameraSkill

camera = CameraSkill(camera_index=0)
if camera.start():
    success, frame = camera.get_frame()
    camera.stop()
```

## Rules
- Do NOT perform face detection or face recognition inside this skill.
- Must cleanly release hardware resources upon stopping.
