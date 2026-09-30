# Face Embedding Skill

## Purpose
Converts normalized facial regions into 128-dimensional unit vectors using OpenCV SFace ONNX deep metric embeddings or a resilient DIP spatial multi-region LBP descriptor fallback.

## Responsibilities
- Validate that the input is strictly a localized face crop and not a whole frame.
- Resize and format face ROI to network specifications (112x112).
- Generate 128-dimensional numerical feature representation.
- Compute L2 unit normalization ($\|v\|_2 = 1.0$) for cosine similarity comparison.
- Maintain a DIP spatial texture descriptor fallback for zero-dependency execution.

## Inputs
- `ProcessedFace` or cropped face image (`numpy.ndarray`).

## Outputs
- Unit-normalized 128-dimensional feature embedding (`numpy.ndarray` with shape `(128,)`, `dtype=float32`, norm = 1.0).

## Tools / Libraries
- OpenCV (`cv2.FaceRecognizerSF`, `cv2.resize`, `cv2.cvtColor`)
- NumPy

## Workflow
1. Accept `ProcessedFace` or face crop.
2. Validate dimensions to prevent accidental full-frame processing.
3. Compute SFace deep embedding or run DIP multi-region LBP descriptor.
4. Normalize vector to unit length ($L_2 = 1.0$).
5. Return 128-D vector.

## Commands
- `generate_embedding(face)`: Produces a 128-D normalized embedding vector.

## Error Handling
- Rejects full-frame or excessively large images (>400x400) by raising a `ValueError`.
- Gracefully handles empty faces by returning a 128-D zero vector.

## Performance Requirements
- Sub-10ms embedding generation per face on CPU.

## Dependencies
- `skills.common.types.ProcessedFace`

## Example
```python
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill

embedder = FaceEmbeddingSkill()
vector = embedder.generate_embedding(processed_face)
print(f"Vector shape: {vector.shape}, Norm: {np.linalg.norm(vector)}")
```

## Rules
- **STRICT RULE**: The embedding engine must NEVER receive the complete CCTV frame.
- Only detected and preprocessed face regions may be processed.
