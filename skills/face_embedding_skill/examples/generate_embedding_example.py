import numpy as np
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill


def main():
    embedder = FaceEmbeddingSkill()
    face_crop = np.random.randint(50, 200, (112, 112, 3), dtype=np.uint8)
    vec = embedder.generate_embedding(face_crop)
    print(f"[FaceEmbeddingSkill] Embedding dimension: {vec.shape}, L2-norm: {np.linalg.norm(vec):.4f}")


if __name__ == "__main__":
    main()
