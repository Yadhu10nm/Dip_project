import os
from typing import Tuple, Optional, Dict, Any
import config
from skills.turret_skill.implementation.types import TurretCalibration


class TurretCalibrationManager:
    """
    Manages geometric calibration, coordinate transformations, and persistence
    for mapping 2D video pixel coordinates into 3D Pan-Tilt servo angles.
    """

    def __init__(self, calibration_file: Optional[str] = None):
        self.filepath = calibration_file or getattr(
            config, "TURRET_CALIBRATION_FILE", os.path.join(config.DATA_DIR, "turret_calibration.json")
        )
        self.calibration: TurretCalibration = TurretCalibration.load_from_file(self.filepath)

    def reload(self) -> TurretCalibration:
        """Reloads calibration settings from disk."""
        self.calibration = TurretCalibration.load_from_file(self.filepath)
        return self.calibration

    def save(self):
        """Persists current calibration to disk."""
        self.calibration.save_to_file(self.filepath)

    def pixel_to_servo_angles(
        self,
        pixel_x: float,
        pixel_y: float,
        frame_width: int = config.FRAME_WIDTH,
        frame_height: int = config.FRAME_HEIGHT,
    ) -> Tuple[float, float]:
        """
        Maps a 2D camera pixel coordinate (x, y) to absolute servo angles (pan, tilt).

        Coordinate Reference:
        - (0, 0) is top-left of image
        - (frame_width/2, frame_height/2) is image center
        - pan increases/decreases left-to-right depending on pan_inverted
        - tilt increases/decreases top-to-bottom depending on tilt_inverted
        """
        cx0 = frame_width / 2.0
        cy0 = frame_height / 2.0

        # Normalized coordinates from frame center: range [-1.0, +1.0]
        norm_x = (pixel_x - cx0) / max(1.0, cx0)
        norm_y = (pixel_y - cy0) / max(1.0, cy0)

        # Apply axis inversion if configured
        if self.calibration.pan_inverted:
            norm_x = -norm_x
        if self.calibration.tilt_inverted:
            norm_y = -norm_y

        # Compute angular offsets using Field-of-View
        # Note: if camera is mounted statically, moving right increases/decreases pan
        pan_offset = norm_x * (self.calibration.pan_fov / 2.0)
        tilt_offset = norm_y * (self.calibration.tilt_fov / 2.0)

        raw_pan = self.calibration.pan_center + pan_offset
        raw_tilt = self.calibration.tilt_center + tilt_offset

        # Clamp strictly within physical limits to protect SG90 servos
        clamped_pan = max(self.calibration.pan_min, min(self.calibration.pan_max, raw_pan))
        clamped_tilt = max(self.calibration.tilt_min, min(self.calibration.tilt_max, raw_tilt))

        return clamped_pan, clamped_tilt

    def servo_angles_to_pixel(
        self,
        pan: float,
        tilt: float,
        frame_width: int = config.FRAME_WIDTH,
        frame_height: int = config.FRAME_HEIGHT,
    ) -> Tuple[float, float]:
        """
        Inverse projection: Maps servo angles back to estimated pixel coordinate.
        """
        cx0 = frame_width / 2.0
        cy0 = frame_height / 2.0

        d_pan = pan - self.calibration.pan_center
        d_tilt = tilt - self.calibration.tilt_center

        norm_x = d_pan / max(1e-4, (self.calibration.pan_fov / 2.0))
        norm_y = d_tilt / max(1e-4, (self.calibration.tilt_fov / 2.0))

        if self.calibration.pan_inverted:
            norm_x = -norm_x
        if self.calibration.tilt_inverted:
            norm_y = -norm_y

        px = cx0 + norm_x * cx0
        py = cy0 + norm_y * cy0

        return max(0.0, min(float(frame_width), px)), max(0.0, min(float(frame_height), py))

    def calibrate_center(self, pan: float, tilt: float) -> TurretCalibration:
        """
        Calibrates the center/home position where the laser hits the exact center of camera view.
        """
        self.calibration.pan_center = float(max(self.calibration.pan_min, min(self.calibration.pan_max, pan)))
        self.calibration.tilt_center = float(max(self.calibration.tilt_min, min(self.calibration.tilt_max, tilt)))
        self.save()
        return self.calibration

    def update_settings(self, updates: Dict[str, Any]) -> TurretCalibration:
        """
        Updates calibration fields with validation and persists to disk.
        """
        for k, v in updates.items():
            if hasattr(self.calibration, k):
                attr_type = type(getattr(self.calibration, k))
                if attr_type == bool:
                    val = bool(v)
                elif attr_type == int:
                    val = int(v)
                elif attr_type == float:
                    val = float(v)
                else:
                    val = v
                setattr(self.calibration, k, val)

        # Enforce sanity limits
        self.calibration.pan_min = max(0.0, min(80.0, self.calibration.pan_min))
        self.calibration.pan_max = max(100.0, min(180.0, self.calibration.pan_max))
        self.calibration.tilt_min = max(0.0, min(80.0, self.calibration.tilt_min))
        self.calibration.tilt_max = max(100.0, min(180.0, self.calibration.tilt_max))
        self.calibration.pan_fov = max(15.0, min(120.0, self.calibration.pan_fov))
        self.calibration.tilt_fov = max(15.0, min(120.0, self.calibration.tilt_fov))

        self.save()
        return self.calibration

    def reset_to_defaults(self) -> TurretCalibration:
        """Resets calibration to standard defaults."""
        self.calibration = TurretCalibration()
        self.save()
        return self.calibration
