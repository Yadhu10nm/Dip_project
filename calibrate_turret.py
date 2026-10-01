"""
AI CCTV Sentry Turret — Interactive Calibration & Alignment Tool
=================================================================
Visual calibration utility for ESP32 2x SG90 Pan-Tilt Turret with Laser.

Controls:
  [Click Screen] - Aim laser turret directly at clicked pixel coordinate
  [W / S / Up / Down] - Nudge Tilt angle up/down
  [A / D / Left / Right] - Nudge Pan angle left/right
  [SPACE]        - Toggle Laser ON / OFF
  [C]            - Set current position as CENTER alignment (Home)
  [I]            - Toggle Pan Inversion (Left <-> Right)
  [K]            - Toggle Tilt Inversion (Up <-> Down)
  [+ / -]        - Increase / Decrease Horizontal FOV sensitivity
  [R]            - Reset to factory default calibration (90, 90)
  [ENTER / S]    - Save calibration to disk
  [Q / ESC]      - Quit calibration tool
"""

import sys
import os
import cv2
import numpy as np

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from skills.camera_skill.implementation import CameraSkill
from skills.turret_skill.implementation import TurretSkill


def run_calibration_tool():
    print("\n" + "=" * 65)
    print("  ESP32 SENTRY TURRET — INTERACTIVE CALIBRATION STATION")
    print("=" * 65)
    print("  Click anywhere on video feed to aim laser at target object.")
    print("  Align laser with center crosshair, then press [C] to lock center.")
    print("  Press [S] to save calibration, [Q] to exit.")
    print("=" * 65 + "\n")

    camera = CameraSkill()
    camera.start()

    turret = TurretSkill(auto_connect=True)
    calib = turret.calibration

    window_name = "TURRET CALIBRATION & OPTICAL ALIGNMENT [CLICK TO AIM]"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, config.FRAME_WIDTH, config.FRAME_HEIGHT)

    current_pan = calib.pan_center
    current_tilt = calib.tilt_center
    laser_on = False
    status_msg = "Ready. Click on screen or use W/A/S/D to aim."

    # Move to initial center
    turret.controller.send_aim(current_pan, current_tilt, laser=laser_on)

    def on_mouse_click(event, x, y, flags, param):
        nonlocal current_pan, current_tilt, laser_on, status_msg
        if event == cv2.EVENT_LBUTTONDOWN:
            laser_on = True
            pan, tilt = turret.calibration_mgr.pixel_to_servo_angles(
                x, y, frame_width=config.FRAME_WIDTH, frame_height=config.FRAME_HEIGHT
            )
            current_pan = pan
            current_tilt = tilt
            turret.controller.send_aim(pan, tilt, laser=True)
            status_msg = f"Aiming at ({x}, {y}) -> Pan: {pan:.1f}°, Tilt: {tilt:.1f}° [LASER ON]"

    cv2.setMouseCallback(window_name, on_mouse_click)

    try:
        while True:
            success, frame = camera.get_frame()
            if not success or frame is None:
                continue

            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2

            # Draw Optical Calibration Crosshairs
            cv2.line(frame, (cx, 0), (cx, h), (40, 40, 40), 1)
            cv2.line(frame, (0, cy), (w, cy), (40, 40, 40), 1)
            cv2.circle(frame, (cx, cy), 35, (0, 255, 255), 1, cv2.LINE_AA)
            cv2.drawMarker(frame, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 1)

            # Draw Current Aim Reticle
            aim_px, aim_py = turret.calibration_mgr.servo_angles_to_pixel(
                current_pan, current_tilt, frame_width=w, frame_height=h
            )
            ax, ay = int(aim_px), int(aim_py)
            reticle_color = (0, 0, 255) if laser_on else (255, 128, 0)
            cv2.circle(frame, (ax, ay), 18, reticle_color, 2, cv2.LINE_AA)
            cv2.line(frame, (ax - 24, ay), (ax + 24, ay), reticle_color, 1)
            cv2.line(frame, (ax, ay - 24), (ax, ay + 24), reticle_color, 1)

            # Header Banner
            cv2.rectangle(frame, (0, 0), (w, 36), (15, 15, 15), -1)
            cv2.line(frame, (0, 36), (w, 36), (60, 60, 60), 1)
            port_text = turret.controller.status.port
            conn_text = f"PORT: {port_text} {'[SIM]' if turret.controller.is_mock else '[HARDWARE]'}"
            cv2.putText(frame, conn_text, (12, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 220, 255), 1, cv2.LINE_AA)

            angles_text = f"PAN: {current_pan:.1f}° | TILT: {current_tilt:.1f}° | LASER: {'FIRING' if laser_on else 'OFF'}"
            cv2.putText(frame, angles_text, (w - 380, 23), cv2.FONT_HERSHEY_DUPLEX, 0.48, (0, 255, 120), 1, cv2.LINE_AA)

            # Footer Banner & Calibration Parameters
            cv2.rectangle(frame, (0, h - 50), (w, h), (15, 15, 15), -1)
            cv2.line(frame, (0, h - 50), (w, h - 50), (60, 60, 60), 1)

            calib_info = (
                f"CENTER: ({calib.pan_center:.1f}°, {calib.tilt_center:.1f}°) | "
                f"FOV: ({calib.pan_fov:.0f}°, {calib.tilt_fov:.0f}°) | "
                f"INV: [P:{'Y' if calib.pan_inverted else 'N'} T:{'Y' if calib.tilt_inverted else 'N'}]"
            )
            cv2.putText(frame, calib_info, (12, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1, cv2.LINE_AA)
            cv2.putText(frame, status_msg, (12, h - 10), cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 255, 255), 1, cv2.LINE_AA)

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(20) & 0xFF

            if key in (ord('q'), ord('Q'), 27):  # Q or ESC
                break

            elif key == ord(' '):  # SPACE: Toggle laser
                laser_on = not laser_on
                turret.controller.send_aim(current_pan, current_tilt, laser=laser_on)
                status_msg = f"Laser {'ACTIVATED' if laser_on else 'MUTED'}"

            elif key in (ord('w'), ord('W'), 82):  # W or UP arrow: Tilt up
                current_tilt = max(calib.tilt_min, current_tilt - 1.0)
                turret.controller.send_aim(current_pan, current_tilt, laser=laser_on)
                status_msg = f"Nudge Tilt -> {current_tilt:.1f}°"

            elif key in (ord('s'), ord('S'), 84):  # S or DOWN arrow: Tilt down
                current_tilt = min(calib.tilt_max, current_tilt + 1.0)
                turret.controller.send_aim(current_pan, current_tilt, laser=laser_on)
                status_msg = f"Nudge Tilt -> {current_tilt:.1f}°"

            elif key in (ord('a'), ord('A'), 81):  # A or LEFT arrow: Pan left
                current_pan = max(calib.pan_min, current_pan - 1.0)
                turret.controller.send_aim(current_pan, current_tilt, laser=laser_on)
                status_msg = f"Nudge Pan -> {current_pan:.1f}°"

            elif key in (ord('d'), ord('D'), 83):  # D or RIGHT arrow: Pan right
                current_pan = min(calib.pan_max, current_pan + 1.0)
                turret.controller.send_aim(current_pan, current_tilt, laser=laser_on)
                status_msg = f"Nudge Pan -> {current_pan:.1f}°"

            elif key in (ord('c'), ord('C')):  # C: Calibrate Center
                calib.pan_center = current_pan
                calib.tilt_center = current_tilt
                turret.calibration_mgr.save()
                status_msg = f"CENTER LOCKED at Pan {current_pan:.1f}°, Tilt {current_tilt:.1f}°! Saved to disk."
                print(f"[Calibration] {status_msg}")

            elif key in (ord('i'), ord('I')):  # I: Invert Pan
                calib.pan_inverted = not calib.pan_inverted
                turret.calibration_mgr.save()
                status_msg = f"Pan Inversion: {'ON' if calib.pan_inverted else 'OFF'}"

            elif key in (ord('k'), ord('K')):  # K: Invert Tilt
                calib.tilt_inverted = not calib.tilt_inverted
                turret.calibration_mgr.save()
                status_msg = f"Tilt Inversion: {'ON' if calib.tilt_inverted else 'OFF'}"

            elif key in (ord('+'), ord('=')):  # Increase FOV
                calib.pan_fov = min(120.0, calib.pan_fov + 2.0)
                turret.calibration_mgr.save()
                status_msg = f"Horizontal FOV scaled to {calib.pan_fov:.0f}°"

            elif key in (ord('-'), ord('_')):  # Decrease FOV
                calib.pan_fov = max(20.0, calib.pan_fov - 2.0)
                turret.calibration_mgr.save()
                status_msg = f"Horizontal FOV scaled to {calib.pan_fov:.0f}°"

            elif key in (ord('r'), ord('R')):  # Reset
                turret.reset_calibration()
                calib = turret.calibration
                current_pan = calib.pan_center
                current_tilt = calib.tilt_center
                status_msg = "Calibration reset to factory defaults (90, 90)."

            elif key in (13, 10):  # Enter: Save
                turret.calibration_mgr.save()
                status_msg = "Calibration saved successfully to disk!"

    finally:
        print("[Calibration] Saving and closing turret...")
        turret.controller.send_aim(calib.pan_center, calib.tilt_center, laser=False)
        turret.stop()
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    run_calibration_tool()
