# Face Recognition Skill

## Purpose
Classifies preprocessed human face regions by generating 128-D feature embeddings, performing RAG-based Dense Retrieval and Consensus Verification in ChromaDB, and applying threshold verification to classify subjects as Authorized or Unauthorized.

## Responsibilities
- Validate input as `ProcessedFace`.
- Query `face_embedding_skill` to extract a 128-D unit vector.
- Query `vector_database_skill.search_face_rag()` for top-K dense retrieval and candidate consensus.
- Evaluate match similarity against `FACE_MATCH_THRESHOLD` and consensus against `RAG_MIN_CONSENSUS`.
- Return a structured `RecognitionResult` enriched with similarity, consensus ratio, and retrieval evidence.

## Inputs
- `ProcessedFace` object.

## Outputs
- `RecognitionResult` containing `(name, person_id, similarity, authorized, bbox, backend, consensus, evidence)`.

## Tools / Libraries
- Python, NumPy, ChromaDB

## Workflow
1. Accept `ProcessedFace` (strictly cropped face ROI).
2. Extract 128-D embedding via `embedding_skill.generate_embedding()`.
3. Query `vector_db_skill.search_face_rag(embedding, top_k=RAG_TOP_K, min_consensus=RAG_MIN_CONSENSUS)`.
4. If similarity $\ge$ match threshold AND consensus is confirmed $\implies$ return `authorized=True`.
5. If similarity $<$ match threshold or consensus fails or no matches $\implies$ return `authorized=False` (Unknown/Unauthorized).

## Commands
- `recognize_face(processed_face)`: Classifies a face ROI.

## Error Handling
- Rejects non-`ProcessedFace` input with `TypeError`.
- Handles empty database scenarios by returning safe default Unknown recognition result.

## Performance Requirements
- Sub-15ms recognition cycle per face.

## Dependencies
- `skills.face_embedding_skill`
- `skills.vector_database_skill`
- `skills.common.types.ProcessedFace`
- `skills.common.types.RecognitionResult`

## Example
```python
from skills.face_recognition_skill.implementation import FaceRecognitionSkill

recognizer = FaceRecognitionSkill()
result = recognizer.recognize_face(processed_face)
if result.authorized:
    print(f"Welcome {result.name} (Sim: {result.similarity:.2f})")
else:
    print("Security Alert: Unauthorized person detected!")
```

## Rules
- **STRICT RULE**: Only preprocessed human face regions may enter the recognition pipeline.
- Threshold values must be configurable and loaded from `config.py` (`FACE_MATCH_THRESHOLD`).
