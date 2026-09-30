# Face Preprocessing Skill

## Purpose
Prepares detected face regions for embedding models through cropping, margin padding, canonical resizing, CLAHE contrast equalization, and edge-preserving bilateral filtering.

## Responsibilities
- Crop face Region of Interest (ROI) with safe boundary margins.
- Resize face image to canonical dimensions (e.g., 200x200 or 112x112).
- Apply CLAHE illumination equalization.
- Apply bilateral filtering to reduce sensor noise without blurring edges.
- Package output into a standardized `ProcessedFace` object.

## Inputs
- Full video frame (`numpy.ndarray`)
- Detected bounding box coordinates (`FaceDetection` or `(x, y, w, h)`)

## Outputs
- `ProcessedFace` object containing normalized face image, bounding box, and frame dimensions.

## Tools / Libraries
- OpenCV (`cv2.resize`, `cv2.cvtColor`, `cv2.bilateralFilter`, `cv2.createCLAHE`)
- NumPy

## Workflow
1. Verify frame and face bounding box validity.
2. Calculate margin-expanded coordinates clamped to frame boundaries.
3. Slice the face Region of Interest (ROI) from the frame.
4. Scale ROI to target dimensions.
5. Apply CLAHE and bilateral filtering to normalize lighting and remove noise.
6. Return `ProcessedFace`.

## Commands
- `preprocess_face(frame, detection)`: Preprocesses a single localized face.

## Error Handling
- Raises `ValueError` if frame is empty, bounding box dimensions are $\le 0$, or cropped region is empty.
- Raises `TypeError` if input detection is not `FaceDetection` or valid 4-tuple.

## Performance Requirements
- Sub-2ms processing per face ROI.

## Dependencies
- `skills.common.types.FaceDetection`
- `skills.common.types.ProcessedFace`

## Example
```python
from skills.face_preprocessing_skill.implementation import FacePreprocessingSkill
from skills.common.types import FaceDetection

preprocessor = FacePreprocessingSkill()
det = FaceDetection(x=100, y=80, width=120, height=120)
processed = preprocessor.preprocess_face(frame, det)
```

## Rules
- **STRICT RULE**: Never accept arbitrary image regions as valid faces without going through the face detection stage.
- Do NOT generate embeddings inside this skill.
