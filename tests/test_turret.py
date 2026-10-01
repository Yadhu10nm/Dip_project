import os
import tempfile
import pytest
from skills.common.types import RecognitionResult
from skills.turret_skill.implementation.types import TurretCalibration, TurretStatus
from skills.turret_skill.implementation.calibration import TurretCalibrationManager
from skills.turret_skill.implementation.controller import TurretController
from skills.turret_skill.implementation.tracker import TurretTracker
from skills.turret_skill.implementation.turret_skill import TurretSkill


def test_turret_calibration_defaults():
    calib = TurretCalibration()
    assert calib.pan_center == 90.0
    assert calib.tilt_center == 90.0
    assert calib.pan_fov == 60.0
    assert calib.tilt_fov == 45.0
    assert not calib.pan_inverted
    assert not calib.tilt_inverted


def test_turret_calibration_persistence():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_path = tf.name

    try:
        calib = TurretCalibration(pan_center=95.5, tilt_center=82.0, pan_inverted=True)
        calib.save_to_file(temp_path)

        loaded = TurretCalibration.load_from_file(temp_path)
        assert loaded.pan_center == 95.5
        assert loaded.tilt_center == 82.0
        assert loaded.pan_inverted is True
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_pixel_to_servo_mapping():
    calib = TurretCalibration(
        pan_center=90.0,
        tilt_center=90.0,
        pan_fov=60.0,
        tilt_fov=40.0,
        pan_inverted=False,
        tilt_inverted=False,
    )
    mgr = TurretCalibrationManager()
    mgr.calibration = calib

    # Center of 640x480 frame should map exactly to (90.0, 90.0)
    pan, tilt = mgr.pixel_to_servo_angles(320, 240, frame_width=640, frame_height=480)
    assert pytest.approx(pan, 0.1) == 90.0
    assert pytest.approx(tilt, 0.1) == 90.0

    # Right edge (640, 240) should map to 90 + (60/2) = 120.0
    pan_r, _ = mgr.pixel_to_servo_angles(640, 240, frame_width=640, frame_height=480)
    assert pytest.approx(pan_r, 0.1) == 120.0

    # Left edge (0, 240) should map to 90 - (60/2) = 60.0
    pan_l, _ = mgr.pixel_to_servo_angles(0, 240, frame_width=640, frame_height=480)
    assert pytest.approx(pan_l, 0.1) == 60.0

    # Bottom edge (320, 480) should map to 90 + (40/2) = 110.0
    _, tilt_b = mgr.pixel_to_servo_angles(320, 480, frame_width=640, frame_height=480)
    assert pytest.approx(tilt_b, 0.1) == 110.0


def test_axis_inversion():
    calib = TurretCalibration(
        pan_center=90.0,
        tilt_center=90.0,
        pan_fov=60.0,
        tilt_fov=40.0,
        pan_inverted=True, # INVERTED
        tilt_inverted=True, # INVERTED
    )
    mgr = TurretCalibrationManager()
    mgr.calibration = calib

    # Right edge (640) with inversion should DECREASE pan to 60.0 instead of 120.0
    pan_r, _ = mgr.pixel_to_servo_angles(640, 240, frame_width=640, frame_height=480)
    assert pytest.approx(pan_r, 0.1) == 60.0

    # Top edge (0) with inversion should INCREASE tilt to 110.0
    _, tilt_t = mgr.pixel_to_servo_angles(320, 0, frame_width=640, frame_height=480)
    assert pytest.approx(tilt_t, 0.1) == 110.0


def test_controller_mock_mode():
    controller = TurretController(port="NON_EXISTENT_PORT_99")
    ok = controller.connect()
    assert not ok
    assert controller.is_mock is True
    assert controller.status.is_mock is True

    # Aim command should update simulated status
    res = controller.send_aim(110.0, 75.0, laser=True)
    assert res is True
    assert controller.status.pan == 110.0
    assert controller.status.tilt == 75.0
    assert controller.status.laser is True

    # Laser off
    controller.send_laser(False)
    assert controller.status.laser is False


def test_intruder_tracking_and_laser_firing():
    controller = TurretController(port="MOCK")
    controller.connect()
    calib_mgr = TurretCalibrationManager()
    tracker = TurretTracker(controller, calib_mgr)

    # 1. Authorized user in frame -> Laser MUST NOT fire!
    auth_user = RecognitionResult(
        name="Alice",
        person_id="AUTH_001",
        similarity=0.85,
        authorized=True,
        bbox=(200, 150, 100, 100),
    )
    status = tracker.update([auth_user], frame_width=640, frame_height=480)
    assert status.laser is False
    assert status.target_locked is False

    # 2. Unauthorized intruder detected -> Laser MUST fire and lock target!
    intruder = RecognitionResult(
        name="Unknown",
        person_id="INTRUDER",
        similarity=0.20,
        authorized=False,
        bbox=(400, 200, 120, 120),  # Centered at (460, 260) -> right of center
    )
    status = tracker.update([intruder], frame_width=640, frame_height=480)
    assert status.laser is True
    assert status.target_locked is True
    assert status.target_name == "Unknown"
    # Target is to the right of center (460 > 320), so pan angle should move > 90
    assert status.pan > 90.0


def test_threat_prioritization_multiple_intruders():
    controller = TurretController(port="MOCK")
    controller.connect()
    calib_mgr = TurretCalibrationManager()
    tracker = TurretTracker(controller, calib_mgr)

    small_intruder = RecognitionResult(
        name="Intruder Far",
        person_id="INT_01",
        similarity=0.1,
        authorized=False,
        bbox=(100, 100, 50, 50),  # Area = 2500
    )
    large_intruder = RecognitionResult(
        name="Intruder Close",
        person_id="INT_02",
        similarity=0.1,
        authorized=False,
        bbox=(400, 200, 150, 150),  # Area = 22500 (Closest)
    )

    status = tracker.update([small_intruder, large_intruder], frame_width=640, frame_height=480)
    assert status.laser is True
    assert status.target_name == "Intruder Close"
    assert status.target_bbox == (400, 200, 150, 150)


def test_turret_skill_interface():
    skill = TurretSkill(port="MOCK", auto_connect=True)
    status = skill.get_status()
    assert "pan" in status
    assert "tilt" in status
    assert "laser" in status
    assert "calibration" in status

    # Manual move
    res = skill.manual_move(105.0, 85.0, laser=True)
    assert res["success"] is True
    assert res["pan"] == 105.0
    assert res["laser"] is True

    # Aim at pixel
    aim_res = skill.aim_at_pixel(320, 240, 640, 480, laser=True)
    assert aim_res["success"] is True

    # Reset calibration
    calib_res = skill.reset_calibration()
    assert calib_res["success"] is True
    assert calib_res["calibration"]["pan_center"] == 90.0

    skill.stop()
