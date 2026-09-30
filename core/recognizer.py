import os
import json
import cv2
import numpy as np
import config
from core.dip_engine import DIPEngine
from core.embedding_engine import EmbeddingEngine
from core.vector_store import ChromaFaceStore

class FaceRecognizer:
    """
    Hybrid Face Recognizer featuring:
    1. ChromaDB Vector Store & Cosine Similarity search over 128-D embeddings.
    2. Local Binary Patterns Histograms (LBPH) Chi-Square fallback/dual engine.
    """

    def __init__(self, dip_engine: DIPEngine = None, vector_store: ChromaFaceStore = None,
                 embedding_engine: EmbeddingEngine = None):
        self.dip_engine = dip_engine or DIPEngine()
        self.vector_store = vector_store or ChromaFaceStore()
        self.embedding_engine = embedding_engine or EmbeddingEngine(self.dip_engine)

        # LBPH Recognizer for compatibility and dual verification
        self.lbph = cv2.face.LBPHFaceRecognizer_create(
            radius=config.LBPH_RADIUS,
            neighbors=config.LBPH_NEIGHBORS,
            grid_x=config.LBPH_GRID_X,
            grid_y=config.LBPH_GRID_Y,
            threshold=300.0
        )
        self.label_map_file = os.path.join(config.MODELS_DIR, "label_map.json")
        self.int_to_user = {}
        self.lbph_is_trained = False
        self.load_lbph_model()

        # Check if vector store has embeddings; if not, attempt auto-sync
        self.is_trained = (self.vector_store.count() > 0)
        if not self.is_trained:
            self._attempt_startup_sync()

    def _attempt_startup_sync(self):
        """Auto-indexes existing dataset images into ChromaDB if collection is fresh."""
        try:
            if os.path.exists(config.USERS_FILE):
                with open(config.USERS_FILE, "r") as f:
                    users = json.load(f)
                if users and os.path.exists(config.DATASET_DIR):
                    print(f"[FaceRecognizer] Indexing existing user dataset into ChromaDB...")
                    self.train_model(config.DATASET_DIR, users)
        except Exception as e:
            print(f"[FaceRecognizer] Startup sync notice: {e}")

    def load_lbph_model(self):
        """Loads LBPH model and label map from disk if available."""
        if os.path.exists(config.MODEL_FILE) and os.path.exists(self.label_map_file):
            try:
                self.lbph.read(config.MODEL_FILE)
                with open(self.label_map_file, "r") as f:
                    raw_map = json.load(f)
                    self.int_to_user = {int(k): v for k, v in raw_map.items()}
                self.lbph_is_trained = True
                return True
            except Exception as e:
                print(f"[FaceRecognizer] LBPH load notice: {e}")
                self.lbph_is_trained = False
        else:
            self.lbph_is_trained = False
        return False

    def train_model(self, dataset_dir: str, users: list) -> tuple:
        """
        Converts all authorized face samples to 128-D embeddings, stores them
        in ChromaDB for Cosine Similarity search, and trains LBPH model.
        """
        lbph_faces = []
        lbph_labels = []
        label_map = {}
        total_embeddings = 0

        # Reset vector store to ensure clean synchronization
        self.vector_store.reset_collection()

        for idx, u in enumerate(users):
            user_id = u["id"]
            user_name = u.get("name", "Authorized User")
            int_label = idx + 1
            label_map[str(int_label)] = user_id
            user_folder = os.path.join(dataset_dir, user_id)

            if not os.path.isdir(user_folder):
                continue

            user_embeddings = []
            sample_ids = []

            for fname in os.listdir(user_folder):
                if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                fpath = os.path.join(user_folder, fname)
                img = cv2.imread(fpath)
                if img is None:
                    continue

                # 1. Compute 128-D embedding for ChromaDB
                emb = self.embedding_engine.compute_embedding(img)
                if emb is not None:
                    user_embeddings.append(emb)
                    sample_ids.append(fname)

                # 2. Preprocess for LBPH
                processed_roi = self.dip_engine.preprocess_face_roi(img, config.STANDARD_FACE_SIZE)
                lbph_faces.append(processed_roi)
                lbph_labels.append(int_label)

            # Upsert user embeddings to ChromaDB
            if user_embeddings:
                added = self.vector_store.add_face_embeddings_batch(
                    user_id=user_id,
                    name=user_name,
                    embeddings=user_embeddings,
                    sample_ids=sample_ids
                )
                total_embeddings += added

        # Train LBPH model
        if len(lbph_faces) > 0:
            self.lbph.train(lbph_faces, np.array(lbph_labels, dtype=np.int32))
            self.lbph.write(config.MODEL_FILE)
            self.int_to_user = {int(k): v for k, v in label_map.items()}
            with open(self.label_map_file, "w") as f:
                json.dump(label_map, f, indent=2)
            self.lbph_is_trained = True
        else:
            self.lbph_is_trained = False
            if os.path.exists(config.MODEL_FILE):
                os.remove(config.MODEL_FILE)
            if os.path.exists(self.label_map_file):
                os.remove(self.label_map_file)

        self.is_trained = (total_embeddings > 0 or self.lbph_is_trained)
        msg = f"Indexed {total_embeddings} face embeddings into ChromaDB for {len(users)} users."
        return True, msg

    def enroll_face_sample(self, user_id: str, name: str, face_roi: np.ndarray, sample_id: str) -> bool:
        """
        Embeds and adds a single face sample into ChromaDB in real-time.
        """
        emb = self.embedding_engine.compute_embedding(face_roi)
        if emb is None:
            return False

        doc_id = self.vector_store.add_face_embedding(user_id, name, emb, sample_id)
        self.is_trained = True
        return doc_id is not None

    def enroll_face_samples_batch(self, user_id: str, name: str, face_rois: list, sample_ids: list) -> int:
        """
        Converts multiple face images to embeddings and adds to ChromaDB in batch.
        """
        embeddings = [self.embedding_engine.compute_embedding(roi) for roi in face_rois]
        valid_embs = []
        valid_ids = []
        for emb, sid in zip(embeddings, sample_ids):
            if emb is not None:
                valid_embs.append(emb)
                valid_ids.append(sid)

        count = self.vector_store.add_face_embeddings_batch(user_id, name, valid_embs, valid_ids)
        self.is_trained = True
        return count

    def remove_user(self, user_id: str):
        """Removes user from ChromaDB vector store."""
        self.vector_store.delete_user(user_id)
        self.is_trained = (self.vector_store.count() > 0)

    def predict_cosine(self, face_roi: np.ndarray) -> tuple:
        """
        Cosine Similarity search in ChromaDB:
        Returns:
            is_authorized: bool
            user_id: str or None
            cosine_similarity: float
            match_score: float (0.0% to 100.0%)
        """
        if self.vector_store.count() == 0:
            return False, None, 0.0, 0.0

        query_emb = self.embedding_engine.compute_embedding(face_roi)
        if query_emb is None:
            return False, None, 0.0, 0.0

        matches = self.vector_store.search_similar(query_emb, top_k=3)
        if not matches:
            return False, None, 0.0, 0.0

        best = matches[0]
        cos_sim = best["similarity"]
        user_id = best["user_id"]

        # Check threshold
        if cos_sim >= config.COSINE_SIMILARITY_THRESHOLD:
            # Authorized match
            score = min(99.9, max(50.0, cos_sim * 100.0))
            return True, user_id, cos_sim, round(score, 1)
        else:
            # Unauthorized intruder
            score = max(0.0, min(49.0, cos_sim * 100.0))
            return False, None, cos_sim, round(score, 1)

    def predict_lbph(self, face_roi: np.ndarray) -> tuple:
        """Fallback LBPH Chi-Square distance classification."""
        if not self.lbph_is_trained or len(self.int_to_user) == 0:
            return False, None, 999.0, 0.0

        processed = self.dip_engine.preprocess_face_roi(face_roi, config.STANDARD_FACE_SIZE)
        label_int, distance = self.lbph.predict(processed)

        if distance <= config.RECOGNITION_THRESHOLD:
            user_id = self.int_to_user.get(label_int)
            match_score = max(55.0, min(99.0, 100.0 - (distance / config.RECOGNITION_THRESHOLD) * 40.0))
            return True, user_id, distance, round(match_score, 1)
        else:
            match_score = max(0.0, min(50.0, 100.0 - (distance / config.RECOGNITION_THRESHOLD) * 50.0))
            return False, None, distance, round(match_score, 1)

    def predict(self, face_roi: np.ndarray) -> tuple:
        """
        Master classification entry point.
        Uses ChromaDB Cosine Similarity by default.
        """
        backend = getattr(config, "RECOGNITION_BACKEND", "chroma_cosine")
        if backend == "chroma_cosine":
            return self.predict_cosine(face_roi)
        else:
            return self.predict_lbph(face_roi)


# Backward-compatible alias for existing imports
LBPHFaceRecognizer = FaceRecognizer
