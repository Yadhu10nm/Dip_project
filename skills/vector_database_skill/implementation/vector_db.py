import os
import json
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
import chromadb
import config


class VectorDatabaseSkill:
    """
    Vector Database Skill using ChromaDB.
    Maintains persistent storage of 128-dimensional facial embeddings and performs
    HNSW Cosine Similarity search.
    """

    def __init__(
        self,
        persist_dir: str = config.CHROMA_DIR,
        collection_name: str = config.CHROMA_COLLECTION_NAME,
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        os.makedirs(self.persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_person(
        self,
        person_id: str,
        name: str,
        embeddings: List[np.ndarray],
        sample_ids: Optional[List[str]] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Stores one or more face embeddings for a person.
        Returns:
            Number of successfully inserted embedding vectors.
        """
        if not embeddings:
            return 0

        doc_ids = []
        vectors = []
        metadatas = []
        documents = []

        if sample_ids is None or len(sample_ids) != len(embeddings):
            sample_ids = [f"sample_{i:04d}" for i in range(len(embeddings))]

        for idx, (emb, sid) in enumerate(zip(embeddings, sample_ids)):
            if emb is None:
                continue
            doc_id = f"{person_id}_{sid}"
            meta = {
                "person_id": str(person_id),
                "name": str(name),
                "sample_id": str(sid),
            }
            if extra_metadata:
                meta.update(extra_metadata)

            doc_ids.append(doc_id)
            vectors.append(emb.flatten().astype(float).tolist())
            metadatas.append(meta)
            documents.append(f"Face vector for {name} ({person_id}) - {sid}")

        if doc_ids:
            self.collection.upsert(
                ids=doc_ids,
                embeddings=vectors,
                metadatas=metadatas,
                documents=documents,
            )

        return len(doc_ids)

    def search_face(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        r"""
        Performs Cosine Similarity search against all stored facial vectors.
        Cosine distance $d \in [0, 2]$, Cosine similarity $= 1.0 - d$.
        Returns list of matching dicts sorted by highest similarity:
        [{
            'person_id': str,
            'name': str,
            'similarity': float,
            'distance': float
        }]
        """
        if query_embedding is None or self.collection.count() == 0:
            return []

        q_vec = query_embedding.flatten().astype(float).tolist()
        try:
            results = self.collection.query(
                query_embeddings=[q_vec],
                n_results=min(top_k, self.collection.count()),
                include=["metadatas", "distances"]
            )
        except Exception as e:
            print(f"[VectorDatabaseSkill] Query error: {e}")
            return []

        hits = []
        if results and results.get("metadatas") and len(results["metadatas"]) > 0:
            metas = results["metadatas"][0]
            distances = results["distances"][0] if results.get("distances") else [1.0] * len(metas)

            for meta, dist in zip(metas, distances):
                # Cosine distance = 1 - cosine_similarity
                similarity = max(0.0, min(1.0, 1.0 - dist))
                hits.append({
                    "person_id": meta.get("person_id", ""),
                    "name": meta.get("name", "Unknown"),
                    "similarity": float(similarity),
                    "distance": float(dist),
                    "sample_id": meta.get("sample_id", "")
                })

        hits.sort(key=lambda x: x["similarity"], reverse=True)
        return hits

    def search_face_rag(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        min_consensus: float = 0.40,
    ) -> Optional[Dict[str, Any]]:
        """
        RAG-based Dense Retrieval and Consensus Verification.
        Retrieves top_k nearest neighbors from ChromaDB, groups hits by person_id,
        calculates consensus score, max similarity, and returns ranked candidate with evidence.

        Returns:
            Dict containing:
                - 'person_id': str
                - 'name': str
                - 'similarity': float (max similarity among top_k matches)
                - 'mean_similarity': float
                - 'weighted_score': float
                - 'consensus_ratio': float
                - 'has_consensus': bool
                - 'votes': int
                - 'total_hits': int
                - 'evidence': List[Dict]
                - 'all_candidates': Dict[str, Any]
            or None if no records or no query embedding.
        """
        if query_embedding is None or self.collection.count() == 0:
            return None

        # Dense retrieval of top-K vectors
        hits = self.search_face(query_embedding, top_k=top_k)
        if not hits:
            return None

        # Group hits by person_id
        candidates: Dict[str, List[Dict[str, Any]]] = {}
        for h in hits:
            pid = h.get("person_id")
            if not pid:
                continue
            if pid not in candidates:
                candidates[pid] = []
            candidates[pid].append(h)

        if not candidates:
            return None

        # Rank each candidate identity
        ranked_candidates = []
        total_hits = len(hits)

        for pid, candidate_hits in candidates.items():
            vote_count = len(candidate_hits)
            consensus_ratio = vote_count / total_hits
            max_sim = max(h["similarity"] for h in candidate_hits)
            mean_sim = sum(h["similarity"] for h in candidate_hits) / vote_count
            weighted_score = 0.7 * max_sim + 0.3 * mean_sim

            ranked_candidates.append({
                "person_id": pid,
                "name": candidate_hits[0].get("name", "Unknown"),
                "similarity": float(max_sim),
                "mean_similarity": float(mean_sim),
                "weighted_score": float(weighted_score),
                "consensus_ratio": float(consensus_ratio),
                "votes": vote_count,
                "total_hits": total_hits,
                "evidence": [
                    {
                        "sample_id": h.get("sample_id", ""),
                        "similarity": round(h.get("similarity", 0.0), 4),
                        "distance": round(h.get("distance", 1.0), 4),
                    }
                    for h in candidate_hits
                ],
            })

        # Sort candidates primarily by highest similarity, then consensus
        ranked_candidates.sort(key=lambda c: (c["similarity"], c["consensus_ratio"]), reverse=True)
        best = ranked_candidates[0]

        # Consensus verification rule:
        # If total_hits <= 2, relax consensus requirement (e.g. newly enrolled user with few samples)
        has_consensus = (best["consensus_ratio"] >= min_consensus) or (total_hits <= 2)
        best["has_consensus"] = has_consensus
        best["all_candidates"] = {
            c["person_id"]: {
                "name": c["name"],
                "votes": c["votes"],
                "similarity": c["similarity"]
            }
            for c in ranked_candidates
        }

        return best

    def delete_person(self, person_id: str) -> bool:
        """Deletes all facial embedding vectors associated with a person_id."""
        try:
            self.collection.delete(where={"person_id": str(person_id)})
            return True
        except Exception as e:
            print(f"[VectorDatabaseSkill] Delete error: {e}")
            return False

    def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves metadata and count of vectors for a specific person."""
        try:
            results = self.collection.get(
                where={"person_id": str(person_id)},
                include=["metadatas"]
            )
            metas = results.get("metadatas", [])
            if metas:
                first = metas[0]
                return {
                    "person_id": str(person_id),
                    "name": first.get("name", "Unknown"),
                    "sample_count": len(metas),
                }
        except Exception as e:
            print(f"[VectorDatabaseSkill] Get error: {e}")
        return None

    def list_people(self) -> List[Dict[str, Any]]:
        """Aggregates all unique registered individuals with sample counts."""
        try:
            all_records = self.collection.get(include=["metadatas"])
            metas = all_records.get("metadatas", [])
            people_map = {}
            for m in metas:
                pid = m.get("person_id")
                if pid not in people_map:
                    people_map[pid] = {
                        "person_id": pid,
                        "name": m.get("name", "Unknown"),
                        "sample_count": 0
                    }
                people_map[pid]["sample_count"] += 1
            return list(people_map.values())
        except Exception as e:
            print(f"[VectorDatabaseSkill] List error: {e}")
            return []

    def count(self) -> int:
        """Returns the total number of facial vectors in the collection."""
        return self.collection.count()

    def reset_collection(self):
        """Drops and recreates the collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def sync_from_dataset(self, embedding_skill=None, force_reindex: bool = False) -> int:
        """
        Self-healing synchronization of ChromaDB vectors from data/authorized_users.json
        and data/dataset/. If collection is missing embeddings for any authorized user,
        this embeds their registered face samples and populates the database.
        Returns total vector count after sync.
        """
        if not os.path.exists(config.USERS_FILE) or not os.path.exists(config.DATASET_DIR):
            return self.count()

        if force_reindex:
            self.reset_collection()

        try:
            with open(config.USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception as e:
            print(f"[VectorDatabaseSkill] Could not read {config.USERS_FILE}: {e}")
            return self.count()

        if embedding_skill is None:
            from skills.face_embedding_skill.implementation import FaceEmbeddingSkill
            embedding_skill = FaceEmbeddingSkill()

        for user in users:
            pid = user.get("id")
            name = user.get("name", "Unknown")
            if not pid:
                continue

            user_dir = os.path.join(config.DATASET_DIR, pid)
            if not os.path.isdir(user_dir):
                continue

            img_files = sorted([
                f for f in os.listdir(user_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))
            ])
            if not img_files:
                continue

            existing = self.get_person(pid)
            # If force_reindex or user not in Chroma or has fewer samples than on disk, re-index
            if force_reindex or existing is None or existing.get("sample_count", 0) < len(img_files):
                embeddings = []
                sample_ids = []
                for fname in img_files:
                    img_path = os.path.join(user_dir, fname)
                    img = cv2.imread(img_path)
                    if img is None:
                        continue
                    sid = os.path.splitext(fname)[0]
                    try:
                        emb = embedding_skill.generate_embedding(img)
                        if emb is not None and len(emb) == 128:
                            embeddings.append(emb)
                            sample_ids.append(sid)
                    except Exception as err:
                        pass

                if embeddings:
                    self.add_person(pid, name, embeddings, sample_ids=sample_ids)
                    print(f"[VectorDatabaseSkill] Successfully synced {len(embeddings)} vectors for {name} ({pid}).")

        return self.count()
