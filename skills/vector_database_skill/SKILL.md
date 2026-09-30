# Vector Database Skill

## Purpose
Manages persistent storage, nearest-neighbor indexing, and Cosine Similarity retrieval of 128-dimensional facial embeddings using ChromaDB.

## Responsibilities
- Maintain persistent ChromaDB collection configured for HNSW Cosine metric (`hnsw:space: cosine`).
- Upsert face embeddings tagged with structured metadata (`person_id`, `name`, `sample_id`).
- Execute nearest-neighbor vector similarity queries.
- Delete individual identities and all associated feature vectors.
- Enumerate enrolled individuals and verify total collection size.

## Inputs
- Embeddings: 128-D `numpy.ndarray` vectors.
- Metadata: `person_id` (str), `name` (str), optional tags.

## Outputs
- Search results: Ordered list of dicts with `person_id`, `name`, `similarity` (float), `distance` (float).

## Tools / Libraries
- ChromaDB (`chromadb.PersistentClient`)
- NumPy

## Workflow
1. Initialize persistent client at `data/chroma_db/`.
2. Provide `add_person` to index batch embeddings.
3. Call `search_face(query_embedding)` to locate nearest identities.
4. Calculate similarity $= 1.0 - \text{cosine\_distance}$.
5. Return ranked candidates.

## Commands
- `add_person(person_id, name, embeddings)`: Upserts face vectors.
- `search_face(query_embedding, top_k)`: Queries vector index for nearest neighbors.
- `search_face_rag(query_embedding, top_k, min_consensus)`: Performs RAG dense retrieval, clusters hits by candidate identity, verifies consensus ratio, and outputs explainable evidence.
- `sync_from_dataset(embedding_skill)`: Self-healing background sync of vectors from `data/authorized_users.json` and `data/dataset/`.
- `delete_person(person_id)`: Removes person vectors.
- `get_person(person_id)`: Checks registration status.
- `list_people()`: Enumerates registered personnel.
- `count()`: Total vector count.

## Error Handling
- Safe fallback if collection is empty: returns `[]`.
- Traps delete/query exceptions and logs warnings without crashing.

## Performance Requirements
- Sub-5ms query response time for collections up to 10,000 vectors using HNSW indexing.

## Dependencies
- ChromaDB, NumPy, `config.py`

## Example
```python
from skills.vector_database_skill.implementation import VectorDatabaseSkill

db = VectorDatabaseSkill()
db.add_person("yadhu_001", "Yadhu", [sample_vector])
matches = db.search_face(query_vector, top_k=1)
if matches and matches[0]["similarity"] >= 0.55:
    print(f"Recognized: {matches[0]['name']}")
```

## Rules
- Always use the cosine similarity metric.
- Centralize persistent directory and collection names in `config.py`.
