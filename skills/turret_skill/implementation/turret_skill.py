import time
import threading
from typing import List, Optional, Tuple, Dict, Any
import config
from skills.common.types import RecognitionResult
from skills.turret_skill.implementation.types import TurretStatus, TurretCalibration
from skills.turret_skill.implementation.controller import TurretController
from skills.turret_skill.implementation.calibration import TurretCalibrationManager
from skills.turret_skill.implementation.tracker import TurretTracker


class TurretSkill:
    """
    Unified ESP32 Laser Turret & Calibration Skill.
    Coordinates physical SG90 pan-tilt servos, laser firing, automatic intruder tracking,
    and interactive calibration routines.
    """

    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: Optional[int] = None,
        calibration_file: Optional[str] = None,
        auto_connect: bool = True,
    ):
        target_port = port or getattr(config, "TURRET_PORT", "AUTO")
        target_baud = baudrate or getattr(config, "TURRET_BAUD", 115200)

        self.calibration_mgr = TurretCalibrationManager(calibration_file)
        self.controller = TurretController(port=target_port, baudrate=target_baud)
        self.tracker = TurretTracker(self.controller, self.calibration_mgr)

        if auto_connect:
            self.controller.connect()

    @property
    def calibration(self) -> TurretCalibration:
        return self.calibration_mgr.calibration

    @property
    def status(self) -> TurretStatus:
        return self.controller.status

    def track_frame(
        self,
        recognitions: List[RecognitionResult],
        frame_width: int = config.FRAME_WIDTH,
        frame_height: int = config.FRAME_HEIGHT,
    ) -> TurretStatus:
        """
        Main pipeline hook: scans recognitions for unknown intruders and aims sentry laser.
        """
        return self.tracker.update(
            recognitions=recognitions,
            frame_width=frame_width,
            frame_height=frame_height,
        )

    def aim_at_pixel(
        self,
        pixel_x: float,
        pixel_y: float,
        frame_width: int = config.FRAME_WIDTH,
        frame_height: int = config.FRAME_HEIGHT,
        laser: bool = True,
    ) -> Dict[str, Any]:
        """
        Interactive aiming at specific screen coordinate (e.g. from mouse click).
        """
        pan, tilt = self.tracker.aim_at_pixel(pixel_x, pixel_y, frame_width, frame_height, laser=laser)
        return {
            "success": True,
            "pan": round(pan, 1),
            "tilt": round(tilt, 1),
            "laser": laser,
            "pixel": [pixel_x, pixel_y],
        }

    def manual_move(self, pan: float, tilt: float, laser: Optional[bool] = None) -> Dict[str, Any]:
        """
        Manual servo positioning with optional laser state override.
        """
        self.controller.status.mode = "MANUAL"
        laser_state = self.controller.status.laser if laser is None else bool(laser)
        ok = self.controller.send_aim(pan, tilt, laser=laser_state)
        self.tracker.current_pan = pan
        self.tracker.current_tilt = tilt
        return {
            "success": ok,
            "pan": pan,
            "tilt": tilt,
            "laser": laser_state,
            "mode": "MANUAL",
        }

    def set_mode(self, mode: str) -> Dict[str, Any]:
        """
        Switches operating mode: 'AUTO' (track intruders), 'MANUAL', or 'OFF'.
        """
        mode = mode.upper()
        if mode not in ("AUTO", "MANUAL", "OFF"):
            return {"success": False, "error": f"Invalid mode: {mode}"}

        self.controller.status.mode = mode
        if mode == "OFF":
            self.controller.send_laser(False)
        elif mode == "AUTO":
            # Return tracker to center and prepare for incoming intruders
            self.tracker.current_pan = self.calibration.pan_center
            self.tracker.current_tilt = self.calibration.tilt_center

        return {"success": True, "mode": mode}

    def set_laser(self, laser_state: bool) -> Dict[str, Any]:
        """Direct manual laser toggle."""
        ok = self.controller.send_laser(laser_state)
        return {"success": ok, "laser": self.controller.status.laser}

    def pulse_laser(self, duration_seconds: float = 1.5):
        """Fires laser for a brief diagnostic test burst in background thread."""
        def _pulse():
            self.controller.send_laser(True)
            time.sleep(duration_seconds)
            # Only turn off if not actively locking on an intruder
            if not self.controller.status.target_locked:
                self.controller.send_laser(False)

        threading.Thread(target=_pulse, daemon=True).start()
        return {"success": True, "duration": duration_seconds}

    def calibrate_center_current(self) -> Dict[str, Any]:
        """
        Sets the current servo positions as the calibrated optical center.
        """
        curr_pan = self.controller.status.pan
        curr_tilt = self.controller.status.tilt
        self.calibration_mgr.calibrate_center(curr_pan, curr_tilt)
        return {
            "success": True,
            "pan_center": self.calibration.pan_center,
            "tilt_center": self.calibration.tilt_center,
            "message": f"Center calibrated to Pan {self.calibration.pan_center:.1f}°, Tilt {self.calibration.tilt_center:.1f}°",
        }

    def update_calibration(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates calibration parameters (FOV, limits, inversion) and persists to disk.
        """
        self.calibration_mgr.update_settings(settings)
        return {
            "success": True,
            "calibration": self.calibration.to_dict(),
        }

    def reset_calibration(self) -> Dict[str, Any]:
        """Resets calibration to factory defaults."""
        self.calibration_mgr.reset_to_defaults()
        return {
            "success": True,
            "calibration": self.calibration.to_dict(),
        }

    def reconnect(self, port: Optional[str] = None) -> Dict[str, Any]:
        """Attempts to reconnect or switch serial ports."""
        ok = self.controller.connect(target_port=port)
        return {
            "success": ok,
            "connected": self.controller.is_connected,
            "port": self.controller.status.port,
            "is_mock": self.controller.is_mock,
        }

    def list_ports(self) -> List[dict]:
        """Lists all system serial COM ports."""
        return self.controller.list_available_ports()

    def get_status(self) -> Dict[str, Any]:
        """Consolidated telemetry and state dictionary."""
        st = self.controller.status.to_dict()
        st["calibration"] = self.calibration.to_dict()
        return st

    def stop(self):
        """Safely stops hardware on application shutdown."""
        try:
            self.controller.send_laser(False)
            self.controller.send_home()
            self.controller.close()
        except Exception:
            pass
