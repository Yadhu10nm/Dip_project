import time
from datetime import datetime
from typing import List, Optional
import config
from skills.common.types import RecognitionResult, SecurityEvent
from skills.common.events import EventBus, EventType


class AlertSkill:
    """
    Alert Management Skill.
    Monitors recognition decisions, detects unauthorized intruder events,
    enforces cooldown policies, and publishes SecurityEvent instances to the EventBus.

    RULES:
    - Rule 7: Do not repeatedly trigger alerts for the same event without cooldown.
    - Decoupled: Does not directly manipulate hardware; communicates via EventBus.
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        cooldown_seconds: float = config.ALERT_COOLDOWN_SECONDS,
        camera_id: str = config.CAMERA_NAME,
    ):
        self.event_bus = event_bus
        self.cooldown_seconds = cooldown_seconds
        self.camera_id = camera_id
        self.last_alert_time = 0.0

    def evaluate_detections(
        self,
        recognition_results: List[RecognitionResult],
        frame_timestamp: Optional[float] = None,
    ) -> Optional[SecurityEvent]:
        """
        Evaluates recognition results. If unauthorized face is found and cooldown
        has elapsed, creates and publishes a SecurityEvent.
        """
        now = frame_timestamp or time.time()
        unauthorized = [r for r in recognition_results if not r.authorized]

        if not unauthorized:
            return None

        # Check cooldown
        if (now - self.last_alert_time) < self.cooldown_seconds:
            return None

        self.last_alert_time = now
        primary_intruder = unauthorized[0]
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        event = SecurityEvent(
            type="UNAUTHORIZED_PERSON",
            timestamp=time_str,
            bbox=primary_intruder.bbox,
            similarity=primary_intruder.similarity,
            person_name="Unauthorized Intruder",
            camera_id=self.camera_id,
        )

        # Publish to event bus if connected
        if self.event_bus:
            self.event_bus.emit(
                EventType.UNAUTHORIZED_PERSON,
                security_event=event,
                intruder_count=len(unauthorized),
            )
            self.event_bus.emit(
                EventType.TTS_REQUESTED,
                message="Warning! Security alert! Unauthorized person detected on camera one.",
            )
            self.event_bus.emit(
                EventType.EVIDENCE_REQUESTED,
                security_event=event,
            )

        return event

    def reset_cooldown(self):
        self.last_alert_time = 0.0
