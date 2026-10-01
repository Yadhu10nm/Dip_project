from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Dict, Any
import numpy as np


@dataclass
class FaceDetection:
    """Represents a human face bounding box localized by face_detection_skill."""
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0
    landmarks: Optional[List[float]] = None
    raw_face: Optional[Any] = None

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "confidence": self.confidence,
            "landmarks": self.landmarks,
        }


@dataclass
class ProcessedFace:
    """Cropped, normalized face region prepared strictly for embedding models."""
    image: np.ndarray
    bbox: Tuple[int, int, int, int]
    original_shape: Tuple[int, int]
    is_aligned: bool = False
    raw_face: Optional[Any] = None

    def __post_init__(self):
        if not isinstance(self.image, np.ndarray) or self.image.size == 0:
            raise ValueError("ProcessedFace must contain a non-empty numpy image array.")


@dataclass
class RecognitionResult:
    """Identity decision produced by face_recognition_skill."""
    name: str
    person_id: str
    similarity: float
    authorized: bool
    bbox: Tuple[int, int, int, int]
    backend: str = "chroma_cosine"
    consensus: float = 1.0
    evidence: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "person_id": self.person_id,
            "similarity": round(float(self.similarity), 4),
            "authorized": self.authorized,
            "bbox": list(self.bbox),
            "backend": self.backend,
            "consensus": round(float(self.consensus), 4),
            "evidence": self.evidence,
        }


@dataclass
class LocatePersonCommand:
    """Request to find and track a specific person in the video feed."""
    person_name: str


@dataclass
class PersonLocation:
    """Result of person_locator_skill search."""
    found: bool
    name: str
    bbox: Optional[Tuple[int, int, int, int]] = None
    similarity: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "found": self.found,
            "name": self.name,
            "bbox": list(self.bbox) if self.bbox else None,
            "similarity": round(float(self.similarity), 4),
        }


@dataclass
class Command:
    """Structured command parsed by command_skill."""
    type: str
    target: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityEvent:
    """Security alert event triggered for unauthorized access or security breach."""
    type: str
    timestamp: str
    bbox: Tuple[int, int, int, int]
    similarity: float
    person_name: str = "Unknown"
    camera_id: str = "CAM-01"
    evidence_file: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "timestamp": self.timestamp,
            "bbox": list(self.bbox),
            "similarity": round(float(self.similarity), 4),
            "person_name": self.person_name,
            "camera_id": self.camera_id,
            "evidence_file": self.evidence_file,
        }


@dataclass
class SystemState:
    """Lightweight application state maintained by orchestrator."""
    camera_active: bool = True
    sound_enabled: bool = True
    locate_target: Optional[str] = None
    dip_mode: bool = False
    camera_flipped: bool = True
    detected_people: List[Dict[str, Any]] = field(default_factory=list)
    last_alert_time: float = 0.0
    last_snapshot_time: float = 0.0
    fps: float = 0.0
    turret_connected: bool = False
    turret_pan: float = 90.0
    turret_tilt: float = 90.0
    turret_laser: bool = False
    turret_target_locked: bool = False
    turret_port: str = "DISCONNECTED"
    turret_is_mock: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "camera_active": self.camera_active,
            "sound_enabled": self.sound_enabled,
            "locate_target": self.locate_target,
            "dip_mode": self.dip_mode,
            "camera_flipped": self.camera_flipped,
            "detected_count": len(self.detected_people),
            "people": self.detected_people,
            "fps": round(self.fps, 1),
            "turret_connected": self.turret_connected,
            "turret_pan": round(self.turret_pan, 1),
            "turret_tilt": round(self.turret_tilt, 1),
            "turret_laser": self.turret_laser,
            "turret_target_locked": self.turret_target_locked,
            "turret_port": self.turret_port,
            "turret_is_mock": self.turret_is_mock,
        }

