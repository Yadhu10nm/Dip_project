import numpy as np
from skills.face_preprocessing_skill.implementation import FacePreprocessingSkill
from skills.common.types import FaceDetection


def main():
    preprocessor = FacePreprocessingSkill()
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    det = FaceDetection(x=150, y=100, width=120, height=120)

    processed = preprocessor.preprocess_face(frame, det)
    print(f"[FacePreprocessingSkill] Processed face shape: {processed.image.shape}")


if __name__ == "__main__":
    main()
