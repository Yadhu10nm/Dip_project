import time
import threading
import cv2
import numpy as np
import config
from core.dip_engine import DIPEngine
from core.detector import FaceDetector
from core.recognizer import LBPHFaceRecognizer
from core.access_manager import AccessManager
from core.alert_system import AlertSystem
from core.cctv_hud import CCTVHUD

class SurveillanceSystem:
    """
    Central Surveillance Controller integrating:
    - Camera capture
    - DIP preprocessing & Haar face localization
    - LBPH identity classification
    - CCTV HUD overlay & intruder point-out
    - Voice alerting & intrusion snapshot logging
    """

    def __init__(self, camera_index: int = config.CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False
        self.is_dip_mode = False

        # Core subsystems
        self.dip_engine = DIPEngine()
        self.detector = FaceDetector(self.dip_engine)
        self.recognizer = LBPHFaceRecognizer(self.dip_engine)
        self.access_manager = AccessManager(self.recognizer, self.detector)
        self.alert_system = AlertSystem()
        self.cctv_hud = CCTVHUD()

        # Telemetry
        self.fps = 0.0
        self.last_frame_time = time.time()
        self.current_detections = []
        self.lock = threading.Lock()

        # User lookup cache
        self.user_cache = {}
        self._refresh_user_cache()

    def _refresh_user_cache(self):
        """Builds quick in-memory mapping from user_id to user record."""
        users = self.access_manager.list_users()
        self.user_cache = {u["id"]: u for u in users}

    def start_camera(self):
        """Initializes video capture device."""
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, config.TARGET_FPS)
        self.is_running = True

    def stop_camera(self):
        """Releases video capture."""
        self.is_running = False
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def read_raw_frame(self):
        """Reads a single frame from webcam, applying mirror inversion if enabled."""
        if self.cap is None or not self.cap.isOpened():
            self.start_camera()

        ret, frame = self.cap.read()
        if not ret or frame is None:
            # Fallback black canvas with warning text if camera is unavailable
            blank = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH, 3), dtype=np.uint8)
            cv2.putText(blank, "CAMERA FEED OFFLINE", (160, 240),
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)
            return blank

        # Invert camera feed horizontally (mirror mode) like cv2.flip(frame, 1)
        if getattr(config, "CAMERA_FLIP", False):
            frame = cv2.flip(frame, getattr(config, "CAMERA_FLIP_CODE", 1))

        return frame

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Runs the full detection, recognition, and rendering pipeline.
        """
        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now
        if dt > 0:
            self.fps = 0.9 * self.fps + 0.1 * (1.0 / dt)

        # 1. Face Detection with Haar + CLAHE
        face_rects = self.detector.detect_faces(frame)
        detections = []
        unauthorized_list = []

        # Ensure user cache is synced
        self._refresh_user_cache()

        for rect in face_rects:
            face_roi, safe_bbox = self.detector.extract_face_roi(frame, rect)
            if face_roi.size == 0:
                continue

            # 2. LBPH Identity Classification
            is_auth, user_id, dist, score = self.recognizer.predict(face_roi)

            user_name = "Intruder"
            if is_auth and user_id in self.user_cache:
                user_name = self.user_cache[user_id]["name"]

            det_info = {
                "bbox": safe_bbox,
                "is_authorized": is_auth,
                "user_id": user_id or "UNREGISTERED",
                "name": user_name,
                "distance": dist,
                "score": score
            }
            detections.append(det_info)

            if not is_auth:
                unauthorized_list.append(det_info)

        with self.lock:
            self.current_detections = detections

        # 3. Trigger Security Alerts for Unauthorized Targets
        if len(unauthorized_list) > 0:
            self.alert_system.trigger_intruder_alert(frame, unauthorized_list, config.CAMERA_NAME)

        # 4. Render Visual Output
        if self.is_dip_mode:
            # Educational 4-Quadrant DIP view
            return self.dip_engine.create_dip_quad_view(frame)
        else:
            # Tactical Security CCTV HUD
            return self.cctv_hud.draw_hud(
                frame, detections, self.fps, config.CAMERA_NAME, self.is_dip_mode
            )

    def toggle_dip_mode(self) -> bool:
        """Toggles between CCTV HUD and DIP Quad Visualizer."""
        self.is_dip_mode = not self.is_dip_mode
        return self.is_dip_mode

    def toggle_camera_flip(self) -> bool:
        """Toggles horizontal camera mirror inversion."""
        config.CAMERA_FLIP = not getattr(config, "CAMERA_FLIP", True)
        return config.CAMERA_FLIP

    def get_status_summary(self) -> dict:
        """Returns live system telemetry for dashboard."""
        with self.lock:
            total_faces = len(self.current_detections)
            unauthorized = sum(1 for d in self.current_detections if not d["is_authorized"])
            authorized = sum(1 for d in self.current_detections if d["is_authorized"])

        chroma_count = 0
        if hasattr(self.recognizer, "vector_store") and self.recognizer.vector_store:
            chroma_count = self.recognizer.vector_store.count()

        return {
            "fps": round(self.fps, 1),
            "total_faces": total_faces,
            "authorized_count": authorized,
            "unauthorized_count": unauthorized,
            "is_dip_mode": self.is_dip_mode,
            "camera_flipped": getattr(config, "CAMERA_FLIP", True),
            "voice_enabled": self.alert_system.voice_enabled,
            "chime_enabled": self.alert_system.chime_enabled,
            "is_model_trained": self.recognizer.is_trained,
            "chroma_embeddings": chroma_count,
            "backend": getattr(config, "RECOGNITION_BACKEND", "chroma_cosine"),
            "registered_users": len(self.access_manager.list_users())
        }

    def generate_mjpeg_stream(self):
        """Yields JPEG encoded video frames for Flask streaming."""
        self.start_camera()
        while self.is_running:
            raw_frame = self.read_raw_frame()
            processed = self.process_frame(raw_frame)

            ret, buffer = cv2.imencode(".jpg", processed, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.015)
