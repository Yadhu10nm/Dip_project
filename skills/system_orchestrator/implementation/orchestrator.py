import time
from typing import Optional, List, Dict, Any, Tuple
import cv2
import numpy as np
import config
from skills.common.types import (
    SystemState,
    Command,
    LocatePersonCommand,
    PersonLocation,
    RecognitionResult,
    SecurityEvent,
)
from skills.common.events import EventBus, EventType, Event
from skills.camera_skill.implementation import CameraSkill
from skills.face_detection_skill.implementation import FaceDetectionSkill
from skills.face_preprocessing_skill.implementation import FacePreprocessingSkill
from skills.face_embedding_skill.implementation import FaceEmbeddingSkill
from skills.vector_database_skill.implementation import VectorDatabaseSkill
from skills.face_recognition_skill.implementation import FaceRecognitionSkill
from skills.person_locator_skill.implementation import PersonLocatorSkill
from skills.command_skill.implementation import CommandSkill
from skills.surveillance_skill.implementation import SurveillanceSkill
from skills.alert_skill.implementation import AlertSkill
from skills.tts_skill.implementation import TTSSkill
from skills.evidence_skill.implementation import EvidenceSkill
from skills.hud_skill.implementation import HUDSkill
from skills.dip_inspector_skill.implementation import DIPInspectorSkill
from skills.enrollment_skill.implementation import EnrollmentSkill
from skills.audit_skill.implementation import AuditSkill


class SystemOrchestrator:
    """
    Central Coordinator & Event-Driven System Orchestrator.
    Manages application state, injects and coordinates all individual agentic skills,
    executes commands, and drives the complete surveillance vision loop.
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        camera: Optional[CameraSkill] = None,
        vector_db: Optional[VectorDatabaseSkill] = None,
    ):
        self.bus = event_bus or EventBus()
        self.state = SystemState()

        # Instantiate Skills
        self.camera = camera or CameraSkill()
        self.detector = FaceDetectionSkill()
        self.preprocessor = FacePreprocessingSkill()
        self.embedder = FaceEmbeddingSkill()
        self.vector_db = vector_db or VectorDatabaseSkill()
        self.recognizer = FaceRecognitionSkill(
            embedding_skill=self.embedder,
            vector_db_skill=self.vector_db,
            match_threshold=config.FACE_MATCH_THRESHOLD,
            top_k=config.RAG_TOP_K,
            min_consensus=config.RAG_MIN_CONSENSUS,
        )

        # Self-healing: auto-sync vector database if collection is empty
        if self.vector_db.count() == 0:
            self.vector_db.sync_from_dataset(embedding_skill=self.embedder)
        self.surveillance = SurveillanceSkill(
            detector=self.detector,
            preprocessor=self.preprocessor,
            recognizer=self.recognizer,
        )
        self.locator = PersonLocatorSkill()
        self.command_parser = CommandSkill()
        self.alerter = AlertSkill(event_bus=self.bus, cooldown_seconds=config.ALERT_COOLDOWN_SECONDS)
        self.tts = TTSSkill(enabled=config.ENABLE_VOICE_ALERT, cooldown_seconds=config.TTS_COOLDOWN_SECONDS)
        self.evidence = EvidenceSkill(storage_dir=config.INTRUDERS_DIR, cooldown_seconds=config.INTRUDER_SNAPSHOT_COOLDOWN)
        self.hud = HUDSkill(camera_name=config.CAMERA_NAME)
        self.dip_inspector = DIPInspectorSkill()
        self.enroller = EnrollmentSkill(
            detector=self.detector,
            preprocessor=self.preprocessor,
            embedder=self.embedder,
            vector_db=self.vector_db,
        )
        self.audit = AuditSkill(log_file=config.AUDIT_LOG_FILE)

        # Telemetry
        self._last_frame_time = time.time()
        self._fps_smoothed = 30.0
        self._active_frame: Optional[np.ndarray] = None
        self._locate_was_found: Optional[bool] = None
        self._locate_missing_frames = 0

        # Register Event Handlers
        self._register_event_handlers()

    def _register_event_handlers(self):
        """Wires inter-skill communication via EventBus."""
        self.bus.subscribe(EventType.TTS_REQUESTED, self._on_tts_requested)
        self.bus.subscribe(EventType.EVIDENCE_REQUESTED, self._on_evidence_requested)
        self.bus.subscribe(EventType.UNAUTHORIZED_PERSON, self._on_unauthorized_person)

    def _on_tts_requested(self, event: Event):
        msg = event.data.get("message", "")
        if msg:
            self.tts.speak(msg)

    def _on_evidence_requested(self, event: Event):
        sec_evt: Optional[SecurityEvent] = event.data.get("security_event")
        if self._active_frame is not None:
            path = self.evidence.capture_evidence(self._active_frame, sec_evt)
            if path and sec_evt:
                self.audit.log_event(
                    event_type="UNAUTHORIZED_INTRUSION",
                    person_name=sec_evt.person_name,
                    similarity=sec_evt.similarity,
                    camera_id=sec_evt.camera_id,
                    threat_level="HIGH",
                    evidence_path=path,
                )

    def _on_unauthorized_person(self, event: Event):
        self.state.last_alert_time = time.time()

    def execute_command(self, command_text_or_obj) -> Dict[str, Any]:
        """
        Executes an agent command received via voice, REST API, or desktop hotkey.
        """
        if isinstance(command_text_or_obj, str):
            cmd = self.command_parser.parse(command_text_or_obj)
        elif isinstance(command_text_or_obj, Command):
            cmd = command_text_or_obj
        else:
            return {"success": False, "error": "Invalid command format"}

        if not cmd:
            return {"success": False, "error": "Empty command"}

        # Dispatch command type
        if cmd.type == "LOCATE_PERSON":
            target = cmd.target or ""
            self.state.locate_target = target
            self.locator.set_target(target)
            self._locate_was_found = None
            self._locate_missing_frames = 0
            self.tts.speak(f"Locating target {target}", force=True)
            return {"success": True, "action": "LOCATE_PERSON", "target": target}

        elif cmd.type == "STOP_LOCATING":
            self.state.locate_target = None
            self.locator.clear_target()
            self._locate_was_found = None
            self._locate_missing_frames = 0
            self.tts.speak("Target tracking canceled", force=True)
            return {"success": True, "action": "STOP_LOCATING"}

        elif cmd.type == "TOGGLE_DIP":
            self.state.dip_mode = not self.state.dip_mode
            return {"success": True, "action": "TOGGLE_DIP", "dip_mode": self.state.dip_mode}

        elif cmd.type == "TOGGLE_SOUND":
            if "enabled" in cmd.params:
                self.state.sound_enabled = bool(cmd.params["enabled"])
            else:
                self.state.sound_enabled = not self.state.sound_enabled
            self.tts.set_enabled(self.state.sound_enabled)
            return {"success": True, "action": "TOGGLE_SOUND", "sound_enabled": self.state.sound_enabled}

        elif cmd.type == "SHOW_AUDIT_LOG":
            logs = self.audit.get_logs(limit=20)
            return {"success": True, "action": "SHOW_AUDIT_LOG", "logs": logs}

        elif cmd.type == "GET_STATUS":
            return {"success": True, "status": self.get_status()}

        return {"success": False, "error": f"Unhandled command type: {cmd.type}"}

    def process_cycle(self) -> Tuple[np.ndarray, List[RecognitionResult], Optional[PersonLocation]]:
        """
        Executes one full synchronous surveillance cycle:
        1. Capture frame
        2. Detect, preprocess, and recognize faces
        3. Evaluate locator target if active
        4. Trigger alert events
        5. Render HUD or DIP Inspector view
        Returns:
            (rendered_frame, recognitions, person_location)
        """
        now = time.time()
        dt = max(1e-4, now - self._last_frame_time)
        self._last_frame_time = now
        inst_fps = 1.0 / dt
        self._fps_smoothed = 0.9 * self._fps_smoothed + 0.1 * inst_fps
        self.state.fps = self._fps_smoothed

        # 1. Frame Acquisition
        success, raw_frame = self.camera.get_frame()
        self._active_frame = raw_frame

        # 2. Multi-Face Surveillance Pipeline
        recognitions = self.surveillance.process_frame(raw_frame)
        self.state.detected_people = [r.to_dict() for r in recognitions]

        # 3. Person Locator (State-Change Transition Logic - Feature 7)
        person_loc: Optional[PersonLocation] = None
        if self.state.locate_target:
            person_loc = self.locator.locate_in_detections(recognitions, target_name=self.state.locate_target)
            is_found = person_loc.found

            if is_found:
                self._locate_missing_frames = 0
                if self._locate_was_found is not True:
                    self._locate_was_found = True
                    self.tts.speak(f"{person_loc.name} located.", force=True)
                    self.bus.emit(EventType.PERSON_LOCATED, person_location=person_loc)
                    self.audit.log_event(
                        event_type="PERSON_LOCATED",
                        person_name=person_loc.name,
                        similarity=person_loc.similarity,
                        camera_id=config.CAMERA_NAME,
                        threat_level="INFO",
                    )
            else:
                if self._locate_was_found is True:
                    self._locate_missing_frames += 1
                    # Debounce absence across 15 frames to prevent audio chatter on quick head turns
                    if self._locate_missing_frames >= 15:
                        self._locate_was_found = False
                        self.tts.speak(f"{self.state.locate_target} not found.", force=True)
                        self.bus.emit(EventType.PERSON_NOT_FOUND, person_name=self.state.locate_target)
                        self.audit.log_event(
                            event_type="PERSON_NOT_FOUND",
                            person_name=self.state.locate_target,
                            similarity=0.0,
                            camera_id=config.CAMERA_NAME,
                            threat_level="INFO",
                        )

        # 4. Alert & Security Breach Evaluation
        self.alerter.evaluate_detections(recognitions, frame_timestamp=now)

        # 5. Visual Rendering (HUD or DIP Mode)
        if self.state.dip_mode:
            display_frame = self.dip_inspector.create_quad_view(raw_frame)
        else:
            display_frame = self.hud.render(
                raw_frame,
                recognitions,
                person_location=person_loc,
                fps=self._fps_smoothed,
                is_dip_mode=self.state.dip_mode,
            )

        return display_frame, recognitions, person_loc

    def get_status(self) -> Dict[str, Any]:
        """Returns consolidated orchestrator health and telemetry dictionary."""
        return {
            "state": self.state.to_dict(),
            "enrolled_users_count": len(self.enroller.list_users()),
            "chroma_vectors_count": self.vector_db.count(),
            "camera_open": self.camera.is_opened(),
            "evidence_count": len(self.evidence.list_evidence()),
        }

    def start_camera(self) -> bool:
        self.state.camera_active = self.camera.start()
        return self.state.camera_active

    def stop(self):
        """Stops camera and background threads safely."""
        self.camera.stop()
        self.tts.stop()
        self.state.camera_active = False
