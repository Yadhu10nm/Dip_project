import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Tuple, Dict, Any


@dataclass
class TurretCalibration:
    """
    Physical and geometric calibration parameters for Pan-Tilt SG90 sentry turret.
    """
    pan_center: float = 90.0        # Physical servo angle (deg) aiming at camera center X
    tilt_center: float = 90.0       # Physical servo angle (deg) aiming at camera center Y
    pan_min: float = 10.0           # Mechanical safe lower bound
    pan_max: float = 170.0          # Mechanical safe upper bound
    tilt_min: float = 20.0          # Mechanical safe lower bound
    tilt_max: float = 160.0         # Mechanical safe upper bound
    pan_inverted: bool = False      # Invert horizontal servo direction
    tilt_inverted: bool = False     # Invert vertical servo direction
    pan_fov: float = 60.0           # Camera horizontal field of view in degrees
    tilt_fov: float = 45.0          # Camera vertical field of view in degrees
    deadzone_pixels: int = 8        # Minimum pixel displacement to trigger servo movement
    smoothing: float = 0.35         # Exponential smoothing factor [0.05=slow/smooth, 1.0=instant]
    laser_on_target_only: bool = True # Fire laser only when intruder is within targeting reticle

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TurretCalibration":
        fields = {f: data[f] for f in data if f in cls.__annotations__}
        return cls(**fields)

    def save_to_file(self, filepath: str):
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filepath: str) -> "TurretCalibration":
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return cls.from_dict(data)
            except Exception as e:
                print(f"[TurretCalibration] Warning loading {filepath}: {e}. Using defaults.")
        return cls()


@dataclass
class TurretStatus:
    """
    Real-time telemetry and state snapshot of the ESP32 Turret.
    """
    connected: bool = False
    port: str = "DISCONNECTED"
    is_mock: bool = True
    pan: float = 90.0
    tilt: float = 90.0
    target_pan: float = 90.0
    target_tilt: float = 90.0
    laser: bool = False
    target_locked: bool = False
    target_name: Optional[str] = None
    target_bbox: Optional[Tuple[int, int, int, int]] = None
    mode: str = "AUTO"  # "AUTO" (track unknown intruders), "MANUAL", "OFF"
    last_command_time: float = 0.0
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connected": self.connected,
            "port": self.port,
            "is_mock": self.is_mock,
            "pan": round(self.pan, 1),
            "tilt": round(self.tilt, 1),
            "target_pan": round(self.target_pan, 1),
            "target_tilt": round(self.target_tilt, 1),
            "laser": self.laser,
            "target_locked": self.target_locked,
            "target_name": self.target_name,
            "target_bbox": list(self.target_bbox) if self.target_bbox else None,
            "mode": self.mode,
            "last_error": self.last_error,
        }
