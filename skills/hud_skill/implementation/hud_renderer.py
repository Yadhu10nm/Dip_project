from datetime import datetime
from typing import List, Optional
import cv2
import numpy as np
import config
from skills.common.types import RecognitionResult, PersonLocation


class HUDSkill:
    """
    Tactical CCTV Heads-Up Display (HUD) Skill.
    Renders military/cyber-security style surveillance graphics, targeting reticles,
    intruder pointing callouts, person locator highlights, and status telemetry.
    """

    def __init__(self, camera_name: str = config.CAMERA_NAME):
        self.camera_name = camera_name
        self.frame_count = 0

    def render(
        self,
        frame: np.ndarray,
        recognition_results: List[RecognitionResult],
        person_location: Optional[PersonLocation] = None,
        fps: float = 0.0,
        is_dip_mode: bool = False,
    ) -> np.ndarray:
        """
        Overlays complete tactical HUD elements onto frame.
        """
        if frame is None or frame.size == 0:
            return frame

        self.frame_count += 1
        canvas = frame.copy()
        h, w = canvas.shape[:2]

        has_unauthorized = any(not r.authorized for r in recognition_results)
        has_authorized = any(r.authorized for r in recognition_results)

        # 1. CCTV Chrome Top and Bottom Banners
        self._draw_chrome(canvas, fps, has_unauthorized, has_authorized, is_dip_mode)

        # 2. Render Detections
        for r in recognition_results:
            # Check if this face is the active located person
            is_located_target = (
                person_location is not None
                and person_location.found
                and person_location.name.lower() in r.name.lower()
            )

            if is_located_target:
                self._draw_located_target(canvas, r, person_location)
            elif r.authorized:
                self._draw_authorized_target(canvas, r)
            else:
                self._draw_intruder_target(canvas, r)

        # 3. Flashing perimeter alarm if intruder present
        if has_unauthorized:
            self._draw_perimeter_warning(canvas)

        return canvas

    def _draw_chrome(
        self,
        canvas: np.ndarray,
        fps: float,
        has_unauthorized: bool,
        has_authorized: bool,
        is_dip_mode: bool,
    ):
        h, w = canvas.shape[:2]
        now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")

        # Top Dark Banner
        cv2.rectangle(canvas, (0, 0), (w, 36), (10, 10, 10), -1)
        cv2.line(canvas, (0, 36), (w, 36), (45, 45, 45), 1)

        # Bottom Dark Banner
        cv2.rectangle(canvas, (0, h - 28), (w, h), (10, 10, 10), -1)
        cv2.line(canvas, (0, h - 28), (w, h - 28), (45, 45, 45), 1)

        # Blinking REC dot
        rec_on = (self.frame_count // 15) % 2 == 0
        rec_color = (0, 0, 240) if rec_on else (60, 60, 60)
        cv2.circle(canvas, (18, 18), 6, rec_color, -1)
        cv2.putText(canvas, "REC", (32, 23), cv2.FONT_HERSHEY_DUPLEX, 0.5, (230, 230, 230), 1, cv2.LINE_AA)

        # Camera Tag
        cv2.putText(canvas, self.camera_name, (90, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 220, 255), 1, cv2.LINE_AA)

        # Timestamp
        cv2.putText(canvas, now_str, (w - 220, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

        # Status text
        if has_unauthorized:
            alert_color = (0, 0, 255) if (self.frame_count // 8) % 2 == 0 else (0, 140, 255)
            status_text = "[!] SECURITY BREACH: UNAUTHORIZED INTRUDER"
            cv2.putText(canvas, status_text, (15, h - 9), cv2.FONT_HERSHEY_DUPLEX, 0.48, alert_color, 1, cv2.LINE_AA)
        elif has_authorized:
            status_text = "[OK] IDENTITY VERIFIED // ACCESS GRANTED"
            cv2.putText(canvas, status_text, (15, h - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 120), 1, cv2.LINE_AA)
        else:
            status_text = "[O] MONITORING ZONE SECURE // NO TARGET DETECTED"
            cv2.putText(canvas, status_text, (15, h - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1, cv2.LINE_AA)

        telemetry = f"FPS: {fps:.1f} | DIP: {'ON' if is_dip_mode else 'OFF'} | CHROMA-RAG"
        cv2.putText(canvas, telemetry, (w - 300, h - 9), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 180, 180), 1, cv2.LINE_AA)

    def _draw_authorized_target(self, canvas: np.ndarray, res: RecognitionResult):
        x, y, w, h = res.bbox
        color = (0, 230, 115)  # Emerald green

        self._draw_corner_brackets(canvas, res.bbox, color, length=int(min(w, h) * 0.28), thickness=2)
        cx, cy = x + w // 2, y + h // 2
        cv2.drawMarker(canvas, (cx, cy), color, cv2.MARKER_CROSS, 12, 1)

        # Badge pill
        badge_y = max(42, y - 10)
        label_top = f"[{res.name.upper()}]"
        rag_pct = int(res.consensus * 100) if hasattr(res, 'consensus') and res.consensus is not None else 100
        label_sub = f"SIM: {res.similarity:.2f} | RAG: {rag_pct}% | AUTHORIZED"

        cv2.rectangle(canvas, (x - 2, badge_y - 28), (x + max(w, 220), badge_y), (15, 35, 15), -1)
        cv2.rectangle(canvas, (x - 2, badge_y - 28), (x + max(w, 220), badge_y), color, 1)
        cv2.putText(canvas, label_top, (x + 6, badge_y - 14), cv2.FONT_HERSHEY_DUPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, label_sub, (x + 6, badge_y - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)

    def _draw_intruder_target(self, canvas: np.ndarray, res: RecognitionResult):
        x, y, w, h = res.bbox
        cx, cy = x + w // 2, y + h // 2
        color = (0, 0, 255) if (self.frame_count // 6) % 2 == 0 else (0, 69, 255)

        self._draw_corner_brackets(canvas, res.bbox, color, length=int(min(w, h) * 0.32), thickness=3)

        # Reticle circle
        radius = int(min(w, h) * 0.45)
        cv2.circle(canvas, (cx, cy), radius, color, 1, cv2.LINE_AA)
        cv2.line(canvas, (cx - radius - 8, cy), (cx + radius + 8, cy), color, 1)
        cv2.line(canvas, (cx, cy - radius - 8), (cx, cy + radius + 8), color, 1)

        # Pointer Laser Callout
        callout_x = x + w + 15
        callout_y = y + 10
        if callout_x + 230 > canvas.shape[1]:
            callout_x = max(10, x - 245)

        anchor_x = x + w if callout_x > x else x
        cv2.line(canvas, (cx, cy), (anchor_x, y + 20), color, 2, cv2.LINE_AA)
        cv2.circle(canvas, (anchor_x, y + 20), 4, color, -1)

        cv2.rectangle(canvas, (callout_x, callout_y), (callout_x + 240, callout_y + 56), (10, 10, 45), -1)
        cv2.rectangle(canvas, (callout_x, callout_y), (callout_x + 240, callout_y + 56), color, 2)

        cv2.putText(canvas, "[!] UNAUTHORIZED PERSON", (callout_x + 8, callout_y + 18), cv2.FONT_HERSHEY_DUPLEX, 0.46, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "TARGET: NOT IN WHITELIST", (callout_x + 8, callout_y + 34), cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1, cv2.LINE_AA)
        cv2.putText(canvas, f"THREAT: HIGH | SIM: {res.similarity:.2f}", (callout_x + 8, callout_y + 49), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 200, 200), 1, cv2.LINE_AA)

    def _draw_located_target(self, canvas: np.ndarray, res: RecognitionResult, loc: PersonLocation):
        x, y, w, h = res.bbox
        cx, cy = x + w // 2, y + h // 2
        # Bright Emerald Green with Gold tactical highlights
        color = (0, 255, 128)
        gold_color = (0, 215, 255)

        # 1. Corner Brackets
        self._draw_corner_brackets(canvas, res.bbox, color, length=int(min(w, h) * 0.35), thickness=3)

        # 2. Concentric Target Reticle with Crosshairs
        radius = int(min(w, h) * 0.48)
        cv2.circle(canvas, (cx, cy), radius, color, 2, cv2.LINE_AA)
        cv2.circle(canvas, (cx, cy), radius + 8, gold_color, 1, cv2.LINE_AA)
        cv2.line(canvas, (cx - radius - 10, cy), (cx + radius + 10, cy), color, 1)
        cv2.line(canvas, (cx, cy - radius - 10), (cx, cy + radius + 10), color, 1)

        # 3. Callout Pointer Line & Card
        callout_x = x + w + 20
        callout_y = y - 10
        if callout_x + 230 > canvas.shape[1]:
            callout_x = max(10, x - 245)

        anchor_x = x + w if callout_x > x else x
        cv2.line(canvas, (cx, cy), (anchor_x, y + 15), gold_color, 2, cv2.LINE_AA)
        cv2.circle(canvas, (anchor_x, y + 15), 4, color, -1)

        # Tactical Card
        cv2.rectangle(canvas, (callout_x, callout_y), (callout_x + 225, callout_y + 54), (10, 30, 15), -1)
        cv2.rectangle(canvas, (callout_x, callout_y), (callout_x + 225, callout_y + 54), color, 2)
        cv2.putText(canvas, f"TARGET: {loc.name.upper()}", (callout_x + 8, callout_y + 18), cv2.FONT_HERSHEY_DUPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "STATUS: LOCATED", (callout_x + 8, callout_y + 34), cv2.FONT_HERSHEY_SIMPLEX, 0.40, color, 1, cv2.LINE_AA)
        cv2.putText(canvas, f"SIMILARITY: {int(loc.similarity * 100)}%", (callout_x + 8, callout_y + 48), cv2.FONT_HERSHEY_SIMPLEX, 0.38, gold_color, 1, cv2.LINE_AA)

        # 4. Target Indicator Badge below the face
        bottom_y = min(canvas.shape[0] - 10, y + h + 20)
        cv2.rectangle(canvas, (x - 2, bottom_y - 14), (x + max(w, 140), bottom_y + 2), (0, 60, 20), -1)
        cv2.putText(canvas, f"▲ TARGET: {loc.name.upper()}", (x + 4, bottom_y - 2), cv2.FONT_HERSHEY_DUPLEX, 0.38, (0, 255, 128), 1, cv2.LINE_AA)

    def _draw_corner_brackets(self, canvas: np.ndarray, bbox: tuple, color: tuple, length: int = 20, thickness: int = 2):
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
        h, w = canvas.shape[:2]
        if (self.frame_count // 5) % 2 == 0:
            cv2.rectangle(canvas, (0, 0), (w - 1, h - 1), (0, 0, 255), 4)
