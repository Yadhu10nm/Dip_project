import time
import cv2
import config
from skills.system_orchestrator.implementation import SystemOrchestrator


class DesktopUISkill:
    """
    Standalone Desktop OpenCV GUI Skill.
    Runs high-framerate local CCTV surveillance display with keyboard shortcuts
    and interactive operator controls.
    """

    def __init__(self, orchestrator: SystemOrchestrator, window_name: str = "AI SECURITY CCTV // TACTICAL SURVEILLANCE"):
        self.orchestrator = orchestrator
        self.window_name = window_name

    def run(self):
        """Main OpenCV GUI event loop."""
        print("\n" + "=" * 65)
        print("  AI SECURITY CCTV // DESKTOP TACTICAL STATION")
        print("  Controls:")
        print("    [R]     - Register New Authorized Person (Burst Capture)")
        print("    [D]     - Toggle DIP Inspector (4-Quadrant Pipeline View)")
        print("    [S]     - Toggle Voice / Audio Alert")
        print("    [F]     - Toggle Camera Mirror Inversion")
        print("    [T]     - Test Sentry Laser Pulse (1.5s Diagnostic)")
        print("    [C]     - Center Sentry Turret (90°, 90°)")
        print("    [L]     - Print Recent Intrusion Audit Logs")
        print("    [Q/ESC] - Quit Surveillance System")
        print("=" * 65 + "\n")

        self.orchestrator.start_camera()
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, config.FRAME_WIDTH, config.FRAME_HEIGHT)

        try:
            while True:
                display_frame, _, _ = self.orchestrator.process_cycle()
                if display_frame is None:
                    continue

                cv2.imshow(self.window_name, display_frame)
                key = cv2.waitKey(1) & 0xFF

                if key in (ord('q'), ord('Q'), 27):  # Q or ESC
                    print("\n[DesktopUISkill] Shutting down CCTV stream...")
                    break
                elif key in (ord('d'), ord('D')):
                    self.orchestrator.execute_command("toggle DIP")
                    state = "ENABLED" if self.orchestrator.state.dip_mode else "DISABLED"
                    print(f"[DesktopUISkill] DIP Inspector Mode: {state}")
                elif key in (ord('s'), ord('S')):
                    self.orchestrator.execute_command("toggle sound")
                    state = "ENABLED" if self.orchestrator.state.sound_enabled else "MUTED"
                    print(f"[DesktopUISkill] Audio Alerts: {state}")
                elif key in (ord('f'), ord('F')):
                    self.orchestrator.camera.toggle_flip()
                    self.orchestrator.state.camera_flipped = self.orchestrator.camera.flip_horizontal
                    state = "ON" if self.orchestrator.state.camera_flipped else "OFF"
                    print(f"[DesktopUISkill] Camera Mirror: {state}")
                elif key in (ord('t'), ord('T')):
                    self.orchestrator.turret.pulse_laser(duration_seconds=1.5)
                    print("[DesktopUISkill] Sentry Laser Diagnostic Pulse: FIRED (1.5s)")
                elif key in (ord('c'), ord('C')):
                    self.orchestrator.turret.calibrate_center_current()
                    print(f"[DesktopUISkill] Center Calibrated: ({self.orchestrator.turret.calibration.pan_center}°, {self.orchestrator.turret.calibration.tilt_center}°)")
                elif key in (ord('l'), ord('L')):
                    self._print_audit_logs()
                elif key in (ord('r'), ord('R')):
                    self._handle_interactive_enrollment()


        finally:
            cv2.destroyAllWindows()
            self.orchestrator.stop()

    def _print_audit_logs(self):
        logs = self.orchestrator.audit.get_logs(limit=10)
        print("\n--- RECENT AUDIT LOGS ---")
        for log in logs:
            print(f"[{log.get('timestamp')}] {log.get('event')} - {log.get('person')} (Sim: {log.get('similarity')})")
        print("-------------------------\n")

    def _handle_interactive_enrollment(self):
        print("\n--- INTERACTIVE ENROLLMENT ---")
        name = input("Enter person name to whitelist: ").strip()
        if not name:
            print("Enrollment canceled.")
            return

        user_id = f"AUTH_{len(self.orchestrator.enroller.list_users()) + 1:03d}"
        print(f"Capturing face sample for {name} ({user_id}). Look into the camera...")
        time.sleep(1.0)

        _, raw_frame = self.orchestrator.camera.get_frame()
        ok, msg = self.orchestrator.enroller.enroll_single_image(user_id, name, raw_frame)
        print(f"Result: {msg}\n")
