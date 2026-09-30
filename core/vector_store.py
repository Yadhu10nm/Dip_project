import os
import chromadb
import numpy as np
import config

class ChromaFaceStore:
    """
    ChromaDB Vector Store for Facial Feature Embeddings.
    Indexes high-dimensional facial embeddings and performs fast similarity search
    using the Cosine Metric (HNSW Cosine Space).
    """

    def __init__(self, persist_dir: str = None, collection_name: str = None):
        self.persist_dir = persist_dir or config.CHROMA_DIR
        self.collection_name = collection_name or config.CHROMA_COLLECTION_NAME
        os.makedirs(self.persist_dir, exist_ok=True)

        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_face_embedding(self, user_id: str, name: str, embedding: np.ndarray,
                           sample_id: str, metadata: dict = None) -> str:
        """
        Adds or updates a single face embedding in ChromaDB.
        """
        if embedding is None:
            return None

        emb_list = embedding.flatten().astype(float).tolist()
        doc_id = f"{user_id}_{sample_id}"
        meta = {
            "user_id": str(user_id),
            "name": str(name),
            "sample_id": str(sample_id)
        }
        if metadata:
            meta.update(metadata)

        self.collection.upsert(
            ids=[doc_id],
            embeddings=[emb_list],
            metadatas=[meta],
            documents=[f"Face vector for {name} ({user_id}) - {sample_id}"]
        )
        return doc_id

    def add_face_embeddings_batch(self, user_id: str, name: str,
                                  embeddings: list, sample_ids: list,
                                  metadatas: list = None) -> int:
        """
        Adds multiple face embeddings in a single batched upsert.
        """
        if not embeddings or len(embeddings) == 0:
            return 0

        doc_ids = []
        emb_lists = []
        meta_list = []
        doc_texts = []

        for idx, (emb, sid) in enumerate(zip(embeddings, sample_ids)):
            if emb is None:
                continue
            doc_id = f"{user_id}_{sid}"
            doc_ids.append(doc_id)
            emb_lists.append(emb.flatten().astype(float).tolist())
            meta = {
                "user_id": str(user_id),
                "name": str(name),
                "sample_id": str(sid)
            }
            if metadatas and idx < len(metadatas):
                meta.update(metadatas[idx])
            meta_list.append(meta)
            doc_texts.append(f"Face vector for {name} ({user_id}) - {sid}")

        if not doc_ids:
            return 0

        self.collection.upsert(
            ids=doc_ids,
            embeddings=emb_lists,
            metadatas=meta_list,
            documents=doc_texts
        )
        return len(doc_ids)

    def search_similar(self, query_embedding: np.ndarray, top_k: int = 5) -> list:
        """
        Performs Cosine Similarity search against all stored facial vectors in ChromaDB.
        Returns:
            list of dicts sorted by highest Cosine Similarity:
            [{
                'user_id': str,
                'name': str,
                'similarity': float,  # Cosine similarity in range [-1.0, 1.0]
                'distance': float,    # Cosine distance = 1 - similarity
                'id': str,
                'metadata': dict
            }]
        """
        total = self.count()
        if total == 0 or query_embedding is None:
            return []

        k = min(top_k, total)
        q_emb = query_embedding.flatten().astype(float).tolist()

        try:
            results = self.collection.query(
                query_embeddings=[q_emb],
                n_results=k,
                include=["metadatas", "distances", "documents"]
            )
        except Exception as e:
            print(f"[ChromaDB] Query error: {e}")
            return []

        matches = []
        if results and "ids" in results and len(results["ids"]) > 0:
            ids = results["ids"][0]
            metadatas = results["metadatas"][0] if ("metadatas" in results and results["metadatas"]) else [{}] * len(ids)
            distances = results["distances"][0] if ("distances" in results and results["distances"]) else [1.0] * len(ids)

            for doc_id, meta, dist in zip(ids, metadatas, distances):
                # In ChromaDB cosine space: distance = 1 - cosine_similarity
                # Therefore: cosine_similarity = 1.0 - distance
                cos_sim = max(-1.0, min(1.0, 1.0 - float(dist)))
                matches.append({
                    "id": doc_id,
                    "user_id": meta.get("user_id"),
                    "name": meta.get("name", "Authorized User"),
                    "similarity": round(float(cos_sim), 4),
                    "distance": round(float(dist), 4),
                    "metadata": meta
                })

        matches.sort(key=lambda m: m["similarity"], reverse=True)
        return matches

    def delete_user(self, user_id: str):
        """Removes all stored vectors for an authorized user."""
        try:
            self.collection.delete(where={"user_id": str(user_id)})
            print(f"[ChromaDB] Deleted all face embeddings for user {user_id}")
        except Exception as e:
            print(f"[ChromaDB] Error deleting user {user_id}: {e}")

    def count(self) -> int:
        """Returns total vector embeddings stored in ChromaDB."""
        try:
            return self.collection.count()
        except Exception:
            return 0

    def get_user_sample_counts(self) -> dict:
        """Returns mapping of user_id to count of stored face vectors."""
        try:
            all_records = self.collection.get(include=["metadatas"])
            counts = {}
            if all_records and "metadatas" in all_records:
                for meta in all_records["metadatas"]:
                    uid = meta.get("user_id")
                    if uid:
                        counts[uid] = counts.get(uid, 0) + 1
            return counts
        except Exception:
            return {}

    def reset_collection(self):
        """Purges and recreates the collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
