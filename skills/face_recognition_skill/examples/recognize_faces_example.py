import numpy as np
from skills.common.types import ProcessedFace
from skills.face_recognition_skill.implementation import FaceRecognitionSkill


def main():
    recognizer = FaceRecognitionSkill()
    fake_crop = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
    proc = ProcessedFace(image=fake_crop, bbox=(50, 50, 80, 80), original_shape=(480, 640))

    result = recognizer.recognize_face(proc)
    print(f"[FaceRecognitionSkill] Result: {result.to_dict()}")


if __name__ == "__main__":
    main()
