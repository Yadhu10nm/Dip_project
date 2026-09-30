from typing import List, Optional
import numpy as np
from skills.common.types import RecognitionResult
from skills.face_detection_skill.implementation import FaceDetectionSkill
from skills.face_preprocessing_skill.implementation import FacePreprocessingSkill
from skills.face_recognition_skill.implementation import FaceRecognitionSkill


class SurveillanceSkill:
    """
    Real-Time Surveillance Pipeline Skill.
    Coordinates the multi-stage face detection, preprocessing, and recognition
    pipeline across multiple candidate faces in a single video frame.

    STRICT RULES ENFORCED:
    - Rule 2: Never generate embeddings from a full frame.
    - Rule 3: Only process detected face regions.
    - Rule 6: Process each detected face independently.
    """

    def __init__(
        self,
        detector: Optional[FaceDetectionSkill] = None,
        preprocessor: Optional[FacePreprocessingSkill] = None,
        recognizer: Optional[FaceRecognitionSkill] = None,
    ):
        self.detector = detector or FaceDetectionSkill()
        self.preprocessor = preprocessor or FacePreprocessingSkill()
        self.recognizer = recognizer or FaceRecognitionSkill()

    def process_frame(self, frame: np.ndarray) -> List[RecognitionResult]:
        """
        Executes end-to-end multi-face surveillance cycle on a frame.
        Input:
            frame: Video frame (np.ndarray)
        Output:
            List[RecognitionResult] for all detected faces.
        """
        if frame is None or frame.size == 0:
            return []

        # 1. Human Face Detection (Candidate ROIs only)
        detections = self.detector.detect_faces(frame)
        if not detections:
            return []

        results: List[RecognitionResult] = []

        # 2. Process each detected face independently (Rule 6)
        for det in detections:
            try:
                # Preprocess localized face (Rule 3)
                processed_face = self.preprocessor.preprocess_face(frame, det)

                # Classify via SFace + ChromaDB Cosine
                rec_result = self.recognizer.recognize_face(processed_face)
                results.append(rec_result)
            except Exception as e:
                # Isolate individual face errors so other faces in frame continue
                print(f"[SurveillanceSkill] Warning processing face at {det.bbox}: {e}")

        return results
