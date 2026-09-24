import cv2
import time
import numpy as np
from datetime import datetime
import config

class CCTVHUD:
    """
    Renders high-visibility Security CCTV overlays, tactical targeting reticles,
    intruder pointing callouts, and telemetry directly onto video frames.
    """

    def __init__(self):
        self.frame_count = 0

    def draw_hud(self, frame: np.ndarray, detections: list, fps: float = 0.0,
                 camera_name: str = config.CAMERA_NAME, is_dip_mode: bool = False) -> np.ndarray:
        """
        Draws the complete CCTV Security Surveillance interface:
        - CCTV header (REC indicator, timestamp, camera tag, telemetry)
        - Point-out targeting reticles and callouts for authorized and unauthorized subjects
        - Screen-wide threat alert banners when intruders are present
        """
        self.frame_count += 1
        canvas = frame.copy()
        h, w = canvas.shape[:2]

        has_unauthorized = any(not d.get("is_authorized", False) for d in detections)
        has_authorized = any(d.get("is_authorized", False) for d in detections)

        # 1. Draw top & bottom tactical CCTV telemetry bars
        self._draw_cctv_chrome(canvas, fps, camera_name, has_unauthorized, has_authorized, is_dip_mode)

        # 2. Draw detections (Point-out reticles, targeting brackets, name tags)
        for det in detections:
            bbox = det["bbox"]
            is_authorized = det.get("is_authorized", False)
            user_name = det.get("name", "Unknown")
            user_id = det.get("user_id", "")
            distance = det.get("distance", 0.0)
            score = det.get("score", 0.0)

            if is_authorized:
                self._draw_authorized_target(canvas, bbox, user_name, user_id, score)
            else:
                self._draw_intruder_target(canvas, bbox, distance)

        # 3. Flashing screen-edge security border when an intruder is in frame
        if has_unauthorized:
            self._draw_perimeter_warning(canvas)

        return canvas

    def _draw_cctv_chrome(self, canvas: np.ndarray, fps: float, camera_name: str,
                          has_unauthorized: bool, has_authorized: bool, is_dip_mode: bool):
        """Top and bottom telemetry overlay."""
        h, w = canvas.shape[:2]
        now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

        # Top dark banner
        cv2.rectangle(canvas, (0, 0), (w, 36), (10, 10, 10), -1)
        cv2.line(canvas, (0, 36), (w, 36), (45, 45, 45), 1)

        # Bottom dark banner
        cv2.rectangle(canvas, (0, h - 28), (w, h), (10, 10, 10), -1)
        cv2.line(canvas, (0, h - 28), (w, h - 28), (45, 45, 45), 1)

        # Flashing REC symbol (Blinks every ~15 frames)
        rec_visible = (self.frame_count // 15) % 2 == 0
        if rec_visible:
            cv2.circle(canvas, (18, 18), 6, (0, 0, 240), -1)
        else:
            cv2.circle(canvas, (18, 18), 6, (60, 60, 60), -1)
        cv2.putText(canvas, "REC", (32, 23), cv2.FONT_HERSHEY_DUPLEX, 0.5, (230, 230, 230), 1, cv2.LINE_AA)

        # Camera Name & Location
        cv2.putText(canvas, camera_name, (90, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 220, 255), 1, cv2.LINE_AA)

        # Live Timestamp
        cv2.putText(canvas, now_str, (w - 220, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

        # Status text in bottom bar
        if has_unauthorized:
            # Pulsing red warning
            alert_color = (0, 0, 255) if (self.frame_count // 8) % 2 == 0 else (0, 140, 255)
            status_text = "[!] SECURITY BREACH: UNAUTHORIZED INTRUDER POINTED OUT"
            cv2.putText(canvas, status_text, (15, h - 9), cv2.FONT_HERSHEY_DUPLEX, 0.48, alert_color, 1, cv2.LINE_AA)
        elif has_authorized:
            status_text = "[OK] IDENTITY VERIFIED // ACCESS GRANTED"
            cv2.putText(canvas, status_text, (15, h - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 120), 1, cv2.LINE_AA)
        else:
            status_text = "[O] MONITORING ZONE SECURE // NO TARGET DETECTED"
            cv2.putText(canvas, status_text, (15, h - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

        # Telemetry info on bottom right
        mode_str = "DIP: ACTIVE" if is_dip_mode else "CCTV HUD"
        telemetry_str = f"FPS: {fps:.1f} | {mode_str} | LBPH-DIP"
        cv2.putText(canvas, telemetry_str, (w - 260, h - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1, cv2.LINE_AA)

    def _draw_authorized_target(self, canvas: np.ndarray, bbox: tuple, name: str, user_id: str, score: float):
        """Draws calm emerald tactical corner brackets and verified access badge."""
        x, y, w, h = bbox
        color = (0, 230, 115)  # Tactical Green

        # Tactical corner brackets
        self._draw_corner_brackets(canvas, bbox, color, length=int(min(w, h) * 0.28), thickness=2)

        # Subtle center target cross
        cx, cy = x + w // 2, y + h // 2
        cv2.drawMarker(canvas, (cx, cy), color, cv2.MARKER_CROSS, 12, 1)

        # Badge Box above the head
        badge_y = max(42, y - 10)
        label_primary = f"ACCESS GRANTED: {name}"
        label_sub = f"ID: {user_id} | MATCH: {score}%"

        # Background badge pill
        cv2.rectangle(canvas, (x - 2, badge_y - 28), (x + max(w, 200), badge_y), (15, 35, 15), -1)
        cv2.rectangle(canvas, (x - 2, badge_y - 28), (x + max(w, 200), badge_y), color, 1)

        cv2.putText(canvas, label_primary, (x + 6, badge_y - 14), cv2.FONT_HERSHEY_DUPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, label_sub, (x + 6, badge_y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)

    def _draw_intruder_target(self, canvas: np.ndarray, bbox: tuple, distance: float):
        """
        Draws high-visibility red targeting reticle, flashing corner brackets,
        and an explicit pointing callout arrow/bracket locking onto the unauthorized person.
        """
        x, y, w, h = bbox
        cx, cy = x + w // 2, y + h // 2

        # Flashing red/yellow accent for urgency
        is_flash = (self.frame_count // 6) % 2 == 0
        primary_color = (0, 0, 255) if is_flash else (0, 69, 255)  # Bright Red to Red-Orange

        # 1. Heavy tactical corner brackets
        self._draw_corner_brackets(canvas, bbox, primary_color, length=int(min(w, h) * 0.32), thickness=3)

        # 2. Circular targeting reticle around center
        radius = int(min(w, h) * 0.45)
        cv2.circle(canvas, (cx, cy), radius, primary_color, 1, cv2.LINE_AA)
        # Reticle crosshair lines
        cv2.line(canvas, (cx - radius - 8, cy), (cx + radius + 8, cy), primary_color, 1)
        cv2.line(canvas, (cx, cy - radius - 8), (cx, cy + radius + 8), primary_color, 1)

        # 3. Explicit Pointing Callout Banner (Points directly to intruder's face)
        callout_x = x + w + 15
        callout_y = y + 10
        # If too close to right edge, place callout on the left
        if callout_x + 230 > canvas.shape[1]:
            callout_x = max(10, x - 245)

        # Pointing Laser Line from face center to callout
        anchor_x = x + w if callout_x > x else x
        cv2.line(canvas, (cx, cy), (anchor_x, y + 20), primary_color, 2, cv2.LINE_AA)
        cv2.circle(canvas, (anchor_x, y + 20), 4, primary_color, -1)

        # Callout card box
        card_w, card_h = 240, 56
        cv2.rectangle(canvas, (callout_x, callout_y), (callout_x + card_w, callout_y + card_h), (10, 10, 45), -1)
        cv2.rectangle(canvas, (callout_x, callout_y), (callout_x + card_w, callout_y + card_h), primary_color, 2)

        # Warning icon and text inside callout
        cv2.putText(canvas, "[!] UNAUTHORIZED PERSON", (callout_x + 8, callout_y + 18),
                    cv2.FONT_HERSHEY_DUPLEX, 0.46, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "TARGET: NOT IN WHITELIST", (callout_x + 8, callout_y + 34),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, primary_color, 1, cv2.LINE_AA)
        cv2.putText(canvas, f"THREAT: HIGH | DIST: {distance:.1f}", (callout_x + 8, callout_y + 49),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1, cv2.LINE_AA)

        # Top alert banner over the head
        top_y = max(42, y - 8)
        cv2.rectangle(canvas, (x - 2, top_y - 20), (x + max(w, 180), top_y), (0, 0, 180), -1)
        cv2.putText(canvas, "TARGET LOCKED: INTRUDER", (x + 5, top_y - 5),
                    cv2.FONT_HERSHEY_DUPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

    def _draw_corner_brackets(self, canvas: np.ndarray, bbox: tuple, color: tuple, length: int = 20, thickness: int = 2):
        """Draws tactical HUD corner brackets `[ ]` around bounding box."""
        x, y, w, h = bbox

        # Top-Left
        cv2.line(canvas, (x, y), (x + length, y), color, thickness)
        cv2.line(canvas, (x, y), (x, y + length), color, thickness)

        # Top-Right
        cv2.line(canvas, (x + w, y), (x + w - length, y), color, thickness)
        cv2.line(canvas, (x + w, y), (x + w, y + length), color, thickness)

        # Bottom-Left
        cv2.line(canvas, (x, y + h), (x + length, y + h), color, thickness)
        cv2.line(canvas, (x, y + h), (x, y + h - length), color, thickness)

        # Bottom-Right
        cv2.line(canvas, (x + w, y + h), (x + w - length, y + h), color, thickness)
        cv2.line(canvas, (x + w, y + h), (x + w, y + h - length), color, thickness)

    def _draw_perimeter_warning(self, canvas: np.ndarray):
        """Draws flashing red perimeter indicator around entire frame border."""
        h, w = canvas.shape[:2]
        if (self.frame_count // 5) % 2 == 0:
            border_thickness = 4
            cv2.rectangle(canvas, (0, 0), (w - 1, h - 1), (0, 0, 255), border_thickness)
