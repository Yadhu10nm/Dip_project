import numpy as np
import cv2
from skills.face_detection_skill.implementation import FaceDetectionSkill


def main():
    detector = FaceDetectionSkill()
    # Create synthetic test canvas
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)
    detections = detector.detect_faces(canvas)
    print(f"[FaceDetectionSkill] Detections on blank canvas: {len(detections)}")


if __name__ == "__main__":
    main()
