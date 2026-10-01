import time
import math
from typing import List, Optional, Tuple
import config
from skills.common.types import RecognitionResult
from skills.turret_skill.implementation.types import TurretStatus
from skills.turret_skill.implementation.controller import TurretController
from skills.turret_skill.implementation.calibration import TurretCalibrationManager


class TurretTracker:
    """
    Intelligent Tracking & Sentry Aiming Engine.
    Filters candidate detections strictly for unauthorized intruders, selects closest threat,
    applies deadzone hysteresis and exponential motion smoothing, and commands ESP32 servos and laser.
    """

    def __init__(
        self,
        controller: TurretController,
        calibration_manager: TurretCalibrationManager,
    ):
        self.controller = controller
        self.calib_mgr = calibration_manager

        # Dynamic state
        self.current_pan = self.calib_mgr.calibration.pan_center
        self.current_tilt = self.calib_mgr.calibration.tilt_center
        self.target_pan = self.current_pan
        self.target_tilt = self.current_tilt

        self.last_target_pixel: Optional[Tuple[float, float]] = None
        self.last_intruder_seen_time = 0.0
        self.grace_period_seconds = 1.0  # Keep pointing briefly if face drops for 1-2 frames
        self.return_to_center_delay = 2.0  # Return to center after intruder leaves

    def update(
        self,
        recognitions: List[RecognitionResult],
        frame_width: int = config.FRAME_WIDTH,
        frame_height: int = config.FRAME_HEIGHT,
        force_mode: Optional[str] = None,
    ) -> TurretStatus:
        """
        Processes frame detections and drives pan-tilt-laser hardware.
        """
        now = time.time()
        mode = force_mode or self.controller.status.mode

        if mode == "OFF":
            # Turret disabled - laser off and keep status idle
            if self.controller.status.laser:
                self.controller.send_laser(False)
            self.controller.status.target_locked = False
            return self.controller.status

        if mode == "MANUAL":
            # Operator manually controls sliders, skip automatic tracking
            return self.controller.status

        # AUTO Mode: Filter strictly for unauthorized intruders / unknown persons
        intruders = [r for r in recognitions if not r.authorized]

        if len(intruders) > 0:
            self.last_intruder_seen_time = now

            # Threat Prioritization: Select intruder with largest bounding box area (closest to camera)
            primary_target = max(intruders, key=lambda r: r.bbox[2] * r.bbox[3])
            bx, by, bw, bh = primary_target.bbox

            # Aim at center of intruder's face
            target_px = bx + bw / 2.0
            target_py = by + bh / 2.0

            # Apply deadband / deadzone hysteresis to avoid servo micro-jitter
            deadzone = self.calib_mgr.calibration.deadzone_pixels
            if self.last_target_pixel is not None:
                dx = target_px - self.last_target_pixel[0]
                dy = target_py - self.last_target_pixel[1]
                pixel_dist = math.hypot(dx, dy)
                if pixel_dist < deadzone:
                    # Target has barely moved, preserve existing target angles
                    target_px, target_py = self.last_target_pixel
                else:
                    self.last_target_pixel = (target_px, target_py)
            else:
                self.last_target_pixel = (target_px, target_py)

            # Map pixel coordinate to physical servo angles
            calc_pan, calc_tilt = self.calib_mgr.pixel_to_servo_angles(
                target_px, target_py, frame_width=frame_width, frame_height=frame_height
            )
            self.target_pan = calc_pan
            self.target_tilt = calc_tilt

            # Exponential moving average filter for smooth physical servo motion
            alpha = max(0.05, min(1.0, self.calib_mgr.calibration.smoothing))
            self.current_pan += alpha * (self.target_pan - self.current_pan)
            self.current_tilt += alpha * (self.target_tilt - self.current_tilt)

            # Fire Laser towards intruder
            laser_on = True

            self.controller.send_aim(self.current_pan, self.current_tilt, laser=laser_on)

            self.controller.status.target_locked = True
            self.controller.status.target_name = primary_target.name
            self.controller.status.target_bbox = primary_target.bbox
            self.controller.status.pan = self.current_pan
            self.controller.status.tilt = self.current_tilt

        else:
            # No intruders in frame (either empty room or only authorized personnel)
            time_since_last_intruder = now - self.last_intruder_seen_time

            if time_since_last_intruder < self.grace_period_seconds and self.controller.status.target_locked:
                # Brief grace period: keep laser on last known spot without jumping
                self.controller.send_aim(self.current_pan, self.current_tilt, laser=True)
            elif time_since_last_intruder < self.return_to_center_delay:
                # Intruder left: immediately turn off laser
                self.controller.send_laser(False)
                self.controller.status.target_locked = False
                self.controller.status.target_name = None
                self.controller.status.target_bbox = None
                self.last_target_pixel = None
            else:
                # Standby: smoothly return servos to calibrated center position
                self.controller.send_laser(False)
                self.controller.status.target_locked = False
                self.controller.status.target_name = None
                self.controller.status.target_bbox = None
                self.last_target_pixel = None

                home_pan = self.calib_mgr.calibration.pan_center
                home_tilt = self.calib_mgr.calibration.tilt_center

                # Gentle return to center (alpha = 0.12)
                if abs(self.current_pan - home_pan) > 0.5 or abs(self.current_tilt - home_tilt) > 0.5:
                    self.current_pan += 0.12 * (home_pan - self.current_pan)
                    self.current_tilt += 0.12 * (home_tilt - self.current_tilt)
                    self.controller.send_aim(self.current_pan, self.current_tilt, laser=False)

        return self.controller.status

    def aim_at_pixel(
        self,
        pixel_x: float,
        pixel_y: float,
        frame_width: int = config.FRAME_WIDTH,
        frame_height: int = config.FRAME_HEIGHT,
        laser: bool = True,
    ) -> Tuple[float, float]:
        """
        Directly aims turret at a specific screen pixel (e.g. from mouse click).
        """
        pan, tilt = self.calib_mgr.pixel_to_servo_angles(pixel_x, pixel_y, frame_width, frame_height)
        self.current_pan = pan
        self.current_tilt = tilt
        self.target_pan = pan
        self.target_tilt = tilt
        self.controller.send_aim(pan, tilt, laser=laser)
        return pan, tilt
