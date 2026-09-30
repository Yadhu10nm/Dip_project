# Enrollment Skill

## Purpose
Registers authorized personnel with strict validation rules, ensuring exactly one face per enrollment image, extracting embeddings, and persisting records into ChromaDB and disk datasets.

## Responsibilities
- Validate input enrollment images.
- Enforce strict single-face detection rule.
- Reject images with 0 faces.
- Reject images with multiple faces ($>1$).
- Generate 128-D facial embeddings and upsert into ChromaDB.
- Persist face samples to `data/dataset/<person_id>/` and maintain `authorized_users.json`.

## Inputs
- Person metadata: `person_id` (str), `name` (str).
- One or more images (`numpy.ndarray`).

## Outputs
- Status tuple `(success: bool, message: str)`.

## Tools / Libraries
- OpenCV, ChromaDB, JSON, NumPy

## Workflow
1. Accept image and candidate identity.
2. Run `face_detection_skill.detect_faces(image)`.
3. If detections $== 0 \implies$ reject with error.
4. If detections $> 1 \implies$ reject with error (Rule 4).
5. Preprocess the single localized face.
6. Generate 128-D unit embedding via `face_embedding_skill`.
7. Upsert embedding vector into ChromaDB.
8. Persist thumbnail and update user records.

## Commands
- `enroll_single_image(person_id, name, image)`: Enrolls 1 image.
- `enroll_batch_images(person_id, name, images)`: Enrolls multiple images.
- `delete_person(person_id)`: Removes person.
- `list_users()`: Returns authorized user records.

## Error Handling
- Rejects empty, multi-face, or unparseable images gracefully with user-friendly messages.

## Performance Requirements
- Sub-50ms per single face enrollment.

## Dependencies
- `skills.face_detection_skill`
- `skills.face_preprocessing_skill`
- `skills.face_embedding_skill`
- `skills.vector_database_skill`

## Example
```python
from skills.enrollment_skill.implementation import EnrollmentSkill

enroller = EnrollmentSkill()
success, msg = enroller.enroll_single_image("u_01", "Yadhu", face_photo)
print(msg)
```

## Rules
- **Rule 4**: Never enroll an image containing multiple faces. Exactly one face required.
- Reject zero-face images.
