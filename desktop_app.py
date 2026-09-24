import sys
import time
import cv2
import config
from core.surveillance_system import SurveillanceSystem

def run_desktop_app():
    """
    Launches high-framerate standalone OpenCV CCTV Surveillance application
    with on-screen tactical HUD and hotkey controls.
    """
    print("\n" + "=" * 65)
    print("  AI SECURITY CCTV — SURVEILLANCE & INTRUSION SYSTEM (DESKTOP)")
    print("=" * 65)
    print("  Controls:")
    print("    [R] - Register New Authorized Person (Webcam Capture)")
    print("    [D] - Toggle DIP Pipeline Inspector (4-Quadrant View)")
    print("    [S] - Toggle Voice / Sound Alert On/Off")
    print("    [L] - Display Recent Intrusion Logs")
    print("    [Q] / [ESC] - Exit System")
    print("=" * 65 + "\n")

    system = SurveillanceSystem(config.CAMERA_INDEX)
    system.start_camera()

    window_name = "AI SECURITY CCTV SURVEILLANCE STATION"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 960, 720)

    try:
        while system.is_running:
            raw_frame = system.read_raw_frame()
            display_frame = system.process_frame(raw_frame)

            cv2.imshow(window_name, display_frame)
            key = cv2.waitKey(1) & 0xFF

            if key in [ord('q'), ord('Q'), 27]:  # 27 = ESC
                print("[CCTV System] Shutting down...")
                break

            elif key in [ord('d'), ord('D')]:
                is_dip = system.toggle_dip_mode()
                mode_str = "DIP 4-QUAD INSPECTOR" if is_dip else "CCTV HUD"
                print(f"[CCTV System] Switched display mode -> {mode_str}")

            elif key in [ord('s'), ord('S')]:
                system.alert_system.voice_enabled = not system.alert_system.voice_enabled
                v_state = "ENABLED" if system.alert_system.voice_enabled else "MUTED"
                print(f"[CCTV System] Voice Alert -> {v_state}")

            elif key in [ord('l'), ord('L')]:
                logs = system.alert_system.get_audit_logs()
                print(f"\n--- RECENT INTRUSION AUDIT LOG ({len(logs)} Events) ---")
                for item in logs[:5]:
                    print(f"  [{item['timestamp']}] {item['type']} on {item['camera']} - Threat: {item['threat_level']}")
                print("----------------------------------------------------\n")

            elif key in [ord('r'), ord('R')]:
                _handle_desktop_enrollment(system, window_name)

    finally:
        system.stop_camera()
        cv2.destroyAllWindows()

def _handle_desktop_enrollment(system: SurveillanceSystem, window_name: str):
    """Interactive webcam capture wizard directly inside OpenCV window."""
    # Temporarily pause normal feed
    print("\n--- ENROLL NEW AUTHORIZED PERSONNEL ---")
    
    # Try using tkinter for simple dialog if available
    name = None
    try:
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        name = simpledialog.askstring("Enroll Personnel", "Enter Full Name of Authorized Person:", parent=root)
        root.destroy()
    except Exception:
        pass

    if not name:
        try:
            name = input("Enter Full Name of Authorized Person (or press Enter to cancel): ").strip()
        except Exception:
            return

    if not name:
        print("[Enrollment] Cancelled.")
        return

    # Create User
    user = system.access_manager.add_user(name, "Authorized Resident")
    user_id = user["id"]
    print(f"[Enrollment] Registered profile for {name} with ID: {user_id}")
    print("[Enrollment] Capturing 25 face samples from webcam. Please look at camera...")

    samples_collected = 0
    target_samples = 25

    while samples_collected < target_samples:
        frame = system.read_raw_frame()
        canvas = frame.copy()

        # Detect face
        faces = system.detector.detect_faces(frame)
        status_msg = "LOOK DIRECTLY AT CAMERA"

        if len(faces) > 0:
            largest = max(faces, key=lambda f: f[2] * f[3])
            face_roi, safe_bbox = system.detector.extract_face_roi(frame, largest)
            if face_roi.size > 0:
                system.access_manager.save_sample_with_augmentations(user_id, face_roi)
                samples_collected += 2
                status_msg = f"CAPTURING: {min(target_samples, samples_collected)} / {target_samples}"

            # Draw green capture box
            x, y, w, h = safe_bbox
            cv2.rectangle(canvas, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # On-screen instruction banner
        h_canv, w_canv = canvas.shape[:2]
        cv2.rectangle(canvas, (0, h_canv - 50), (w_canv, h_canv), (20, 20, 20), -1)
        cv2.putText(canvas, f"ENROLLING: {name.upper()} | {status_msg}", (20, h_canv - 20),
                    cv2.FONT_HERSHEY_DUPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow(window_name, canvas)
        cv2.waitKey(120)

    print(f"[Enrollment] Training LBPH model on new dataset...")
    success, message = system.access_manager.retrain()
    system._refresh_user_cache()
    print(f"[Enrollment] {message}\n")

if __name__ == "__main__":
    run_desktop_app()
