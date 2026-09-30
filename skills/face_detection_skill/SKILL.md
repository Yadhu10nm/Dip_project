# Face Detection Skill

## Purpose
Identifies and localizes candidate human facial regions within raw video frames using Haar Feature-based Cascade Classifiers and CLAHE illumination compensation.

## Responsibilities
- Convert color BGR frames into single-channel grayscale.
- Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) to handle poor or uneven lighting.
- Detect human face bounding boxes using `detectMultiScale`.
- Return structured `FaceDetection` objects containing coordinates and dimensions.

## Inputs
- Video frame (`numpy.ndarray`) in BGR or Grayscale format.

## Outputs
- List of `FaceDetection` dataclasses with `(x, y, width, height, confidence)`.

## Tools / Libraries
- OpenCV (`cv2.CascadeClassifier`, `cv2.createCLAHE`, `cv2.cvtColor`)
- NumPy

## Workflow
1. Accept raw camera frame.
2. Convert frame to grayscale.
3. Apply CLAHE enhancement to equalize local contrast.
4. Run Haar Cascade detection multi-scale search.
5. Wrap detected bounding coordinates into `FaceDetection` objects.

## Commands
- `detect_faces(frame)`: Detects all human faces in the given frame.

## Error Handling
- Checks for empty or None frames and returns an empty list `[]`.
- Validates the Haar Cascade XML path during initialization and raises `FileNotFoundError` if missing.

## Performance Requirements
- Sub-15ms execution on standard 640x480 resolution frames.

## Dependencies
- `skills.common.types.FaceDetection`

## Example
```python
from skills.face_detection_skill.implementation import FaceDetectionSkill

detector = FaceDetectionSkill()
detections = detector.detect_faces(frame)
for det in detections:
    print(f"Face at ({det.x}, {det.y}, {det.width}, {det.height})")
```

## Rules
- **STRICT RULE**: Only identifies candidate HUMAN FACE regions.
- Never detect arbitrary non-face objects.
- Do NOT pass the complete frame to downstream embedding or recognition skills.
