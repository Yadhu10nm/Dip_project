from typing import Optional
import config
from skills.common.types import ProcessedFace, RecognitionResult
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill
from skills.vector_database_skill.implementation import VectorDatabaseSkill


class FaceRecognitionSkill:
    """
    RAG-Powered Face Recognition Skill.
    Coordinates Face Embedding Skill and Vector Database Skill to identify
    human face regions via ChromaDB dense retrieval, consensus voting, and cosine similarity.

    Decision Rule:
    similarity >= match_threshold AND consensus >= min_consensus -> AUTHORIZED
    similarity < match_threshold OR consensus < min_consensus   -> UNAUTHORIZED / UNKNOWN
    """

    def __init__(
        self,
        embedding_skill: Optional[FaceEmbeddingSkill] = None,
        vector_db_skill: Optional[VectorDatabaseSkill] = None,
        match_threshold: float = config.FACE_MATCH_THRESHOLD,
        top_k: int = config.RAG_TOP_K,
        min_consensus: float = config.RAG_MIN_CONSENSUS,
    ):
        self.embedding_skill = embedding_skill or FaceEmbeddingSkill()
        self.vector_db_skill = vector_db_skill or VectorDatabaseSkill()
        self.match_threshold = match_threshold
        self.top_k = top_k
        self.min_consensus = min_consensus

    def recognize_face(self, processed_face: ProcessedFace) -> RecognitionResult:
        """
        Classifies a single preprocessed human face using RAG dense retrieval.
        Input:
            processed_face: ProcessedFace object (strictly cropped face ROI)
        Output:
            RecognitionResult dataclass
        """
        if not isinstance(processed_face, ProcessedFace):
            raise TypeError("Expected ProcessedFace instance.")

        bbox = processed_face.bbox

        # 1. Generate 128-D unit embedding strictly from cropped face ROI
        embedding = self.embedding_skill.generate_embedding(processed_face)

        # 2. RAG Dense Retrieval and Consensus Verification
        rag_match = self.vector_db_skill.search_face_rag(
            embedding,
            top_k=self.top_k,
            min_consensus=self.min_consensus,
        )

        if rag_match is not None:
            similarity = float(rag_match.get("similarity", 0.0))
            has_consensus = bool(rag_match.get("has_consensus", True))
            consensus_ratio = float(rag_match.get("consensus_ratio", 1.0))
            evidence = rag_match.get("evidence", [])

            if similarity >= self.match_threshold and has_consensus:
                return RecognitionResult(
                    name=rag_match.get("name", "Authorized"),
                    person_id=rag_match.get("person_id", ""),
                    similarity=similarity,
                    authorized=True,
                    bbox=bbox,
                    backend="chroma_rag",
                    consensus=consensus_ratio,
                    evidence=evidence,
                )
            else:
                return RecognitionResult(
                    name="Unknown",
                    person_id="",
                    similarity=similarity,
                    authorized=False,
                    bbox=bbox,
                    backend="chroma_rag",
                    consensus=consensus_ratio,
                    evidence=evidence,
                )

        # Fallback / No enrolled identities in database
        return RecognitionResult(
            name="Unknown",
            person_id="",
            similarity=0.0,
            authorized=False,
            bbox=bbox,
            backend="chroma_rag",
            consensus=0.0,
            evidence=[],
        )
