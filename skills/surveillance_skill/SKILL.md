# Surveillance Skill

## Purpose
Coordinates the real-time computer vision pipeline for video frames, extracting human faces, independently preprocessing each Region of Interest, and producing recognition decisions across multiple subjects simultaneously.

## Responsibilities
- Accept raw video frame from camera skill.
- Call `face_detection_skill` to detect candidate face regions.
- Iterate over each detected face independently.
- Call `face_preprocessing_skill` to crop and normalize each face.
- Call `face_recognition_skill` to identify the subject.
- Aggregate recognition decisions and return list of `RecognitionResult`.

## Inputs
- BGR video frame (`numpy.ndarray`).

## Outputs
- List of `RecognitionResult` objects (one for each detected face).

## Tools / Libraries
- Python, NumPy

## Workflow
1. Receive camera frame.
2. Detect faces. If 0 faces $\implies$ return `[]`.
3. For each detected face bounding box:
   - Extract and preprocess face ROI.
   - Run SFace embedding and ChromaDB vector search.
   - Tag identity and authorization status.
4. Return collected decisions.

## Commands
- `process_frame(frame)`: Processes an entire frame across multiple faces.

## Error Handling
- Isolates errors per face: if one face fails preprocessing, other faces in the same frame continue uninterrupted.

## Performance Requirements
- Target: 20-30 FPS on multi-core CPU.

## Dependencies
- `skills.face_detection_skill`
- `skills.face_preprocessing_skill`
- `skills.face_recognition_skill`
- `skills.common.types.RecognitionResult`

## Example
```python
from skills.surveillance_skill.implementation import SurveillanceSkill

surveillance = SurveillanceSkill()
results = surveillance.process_frame(camera_frame)
for res in results:
    print(f"Detected: {res.name} (Authorized: {res.authorized})")
```

## Rules
- **Rule 2**: Never generate embeddings from a full frame.
- **Rule 3**: Only process detected face regions.
- **Rule 6**: Process each detected face independently.
