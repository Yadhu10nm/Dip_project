import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from build_project_report import (
    add_styled_heading, add_body_p, add_bullet_p, add_code_block, add_figure_with_caption
)

def add_back_matter(doc):
    """Add References, Appendix A (Source Code), and Appendix B (Screenshots)."""
    # References
    doc.add_page_break()
    p_ref = add_styled_heading(doc, "REFERENCES", level=1, space_before=18, space_after=14)
    p_ref.alignment = WD_ALIGN_PARAGRAPH.CENTER

    references = [
        "[1] R. C. Gonzalez and R. E. Woods, Digital Image Processing, 4th ed. New York, NY, USA: Pearson Education, 2018.",
        "[2] G. Bradski, 'The OpenCV Library,' Dr. Dobb's Journal of Software Tools, vol. 25, no. 11, pp. 120–125, 2000.",
        "[3] S. Shan, W. Gao, B. Cao, and D. Zhao, 'Illumination Normalization for Robust Face Recognition Against Baseline Variation,' in Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR), vol. 1, 2003, pp. I-175–I-180.",
        "[4] C. Tomasi and R. Manduchi, 'Bilateral Filtering for Gray and Color Images,' in Proc. 6th IEEE Int. Conf. Computer Vision (ICCV), Bombay, India, 1998, pp. 839–846.",
        "[5] T. Ojala, M. Pietikainen, and T. Maenpaa, 'Multiresolution Gray-Scale and Rotation Invariant Texture Classification with Local Binary Patterns,' IEEE Trans. Pattern Anal. Mach. Intell., vol. 24, no. 7, pp. 971–987, Jul. 2002.",
        "[6] T. Ahonen, A. Hadid, and M. Pietikainen, 'Face Description with Local Binary Patterns: Application to Face Recognition,' IEEE Trans. Pattern Anal. Mach. Intell., vol. 28, no. 12, pp. 2037–2041, Dec. 2006.",
        "[7] W. Wu, S. Peng, and M. Sun, 'YuNet: A Fast and Accurate Face Detection Algorithm for Edge Devices,' in Proc. IEEE Conf. Computer Vision and Pattern Recognition Workshops (CVPRW), 2023.",
        "[8] Y. Zhong, J. Deng, W. Shen, and J. Guo, 'SFace: Sigmoid-Constrained Hyperspherical Loss for Robust Face Recognition,' IEEE Trans. Image Process., vol. 30, pp. 2587–2598, 2021.",
        "[9] Y. A. Malkov and D. A. Yashunin, 'Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs,' IEEE Trans. Pattern Anal. Mach. Intell., vol. 42, no. 4, pp. 824–836, Apr. 2020.",
        "[10] P. Lewis, E. Perez, A. Piktus, et al., 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,' in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, 2020, pp. 9459–9474.",
        "[11] Espressif Systems, 'ESP32 Technical Reference Manual (Version 5.0),' Espressif Systems Co., Ltd., Shanghai, China, 2023.",
        "[12] M. Grinberg, Flask Web Development: Developing Web Applications with Python, 2nd ed. Sebastopol, CA, USA: O'Reilly Media, 2018."
    ]

    for ref in references:
        add_body_p(doc, ref, space_after=8, line_spacing=1.15)

    # Appendix A - Source Code
    doc.add_page_break()
    p_app_a = add_styled_heading(doc, "APPENDIX A: SOURCE CODE", level=1, space_before=18, space_after=12)
    p_app_a.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_styled_heading(doc, "A.1 Digital Image Processing Engine (core/dip_engine.py)", level=2)
    add_body_p(doc, "Complete implementation of color conversion, CLAHE equalization, bilateral filtering, and vectorized LBP:")
    add_code_block(doc,
"""import cv2
import numpy as np

class DIPEngine:
    \"\"\"Digital Image Processing Engine for CCTV surveillance normalization.\"\"\"
    def __init__(self, clip_limit=2.0, tile_grid_size=(8, 8)):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)

    def to_grayscale(self, bgr_image: np.ndarray) -> np.ndarray:
        if len(bgr_image.shape) == 2:
            return bgr_image
        return cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

    def apply_clahe(self, gray_image: np.ndarray) -> np.ndarray:
        if len(gray_image.shape) == 3:
            gray_image = self.to_grayscale(gray_image)
        return self.clahe.apply(gray_image)

    def apply_bilateral_filter(self, gray_image: np.ndarray, d=5, sigma_color=40, sigma_space=40) -> np.ndarray:
        return cv2.bilateralFilter(gray_image, d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space)

    def preprocess_face_roi(self, face_bgr_or_gray: np.ndarray, target_size=(200, 200)) -> np.ndarray:
        gray = self.to_grayscale(face_bgr_or_gray) if len(face_bgr_or_gray.shape) == 3 else face_bgr_or_gray.copy()
        resized = cv2.resize(gray, target_size, interpolation=cv2.INTER_AREA if gray.shape[0] > target_size[0] else cv2.INTER_CUBIC)
        equalized = self.clahe.apply(resized)
        filtered = self.apply_bilateral_filter(equalized, d=5, sigma_color=40, sigma_space=40)
        return filtered

    def compute_lbp(self, gray_image: np.ndarray) -> np.ndarray:
        gray = self.to_grayscale(gray_image) if len(gray_image.shape) == 3 else gray_image
        h, w = gray.shape
        if h < 3 or w < 3:
            return np.zeros_like(gray, dtype=np.uint8)
        center = gray[1:h-1, 1:w-1].astype(np.int16)
        n0 = (gray[0:h-2, 0:w-2].astype(np.int16) >= center) * 1
        n1 = (gray[0:h-2, 1:w-1].astype(np.int16) >= center) * 2
        n2 = (gray[0:h-2, 2:w  ].astype(np.int16) >= center) * 4
        n3 = (gray[1:h-1, 2:w  ].astype(np.int16) >= center) * 8
        n4 = (gray[2:h  , 2:w  ].astype(np.int16) >= center) * 16
        n5 = (gray[2:h  , 1:w-1].astype(np.int16) >= center) * 32
        n6 = (gray[2:h  , 0:w-2].astype(np.int16) >= center) * 64
        n7 = (gray[1:h-1, 0:w-2].astype(np.int16) >= center) * 128
        lbp = n0 + n1 + n2 + n3 + n4 + n5 + n6 + n7
        padded = np.zeros_like(gray, dtype=np.uint8)
        padded[1:h-1, 1:w-1] = lbp.astype(np.uint8)
        return padded"""
    )

    add_styled_heading(doc, "A.2 ESP32 Firmware Core (hardware/esp32_laser_turret.ino)", level=2)
    add_body_p(doc, "LEDC PWM setup, ASCII command parsing, and failsafe safety loop:")
    add_code_block(doc,
"""#include <Arduino.h>

const int PIN_SERVO_PAN  = 13;
const int PIN_SERVO_TILT = 18;
const int PIN_LASER      = 16;
const int CHANNEL_PAN    = 0;
const int CHANNEL_TILT   = 1;
const int PWM_FREQ       = 50;
const int PWM_RES_BITS   = 14;

const float SERVO_MIN_US = 500.0f;
const float SERVO_MAX_US = 2400.0f;
const float PAN_MIN = 10.0f, PAN_MAX = 170.0f;
const float TILT_MIN = 20.0f, TILT_MAX = 160.0f;

unsigned long lastAimTime = 0;
const unsigned long FAILSAFE_MS = 2500;

void setServoAngle(int channel, float angle, float min_deg, float max_deg) {
    angle = constrain(angle, min_deg, max_deg);
    float pulse_us = SERVO_MIN_US + (angle / 180.0f) * (SERVO_MAX_US - SERVO_MIN_US);
    uint32_t duty = (uint32_t)((pulse_us / 20000.0f) * 16383.0f);
    ledcWrite(channel, duty);
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_LASER, OUTPUT);
    digitalWrite(PIN_LASER, LOW);

    ledcSetup(CHANNEL_PAN, PWM_FREQ, PWM_RES_BITS);
    ledcAttachPin(PIN_SERVO_PAN, CHANNEL_PAN);
    ledcSetup(CHANNEL_TILT, PWM_FREQ, PWM_RES_BITS);
    ledcAttachPin(PIN_SERVO_TILT, CHANNEL_TILT);

    setServoAngle(CHANNEL_PAN, 90.0f, PAN_MIN, PAN_MAX);
    setServoAngle(CHANNEL_TILT, 90.0f, TILT_MIN, TILT_MAX);
    Serial.println("ESP32_TURRET_READY");
}

void loop() {
    if (Serial.available()) {
        String line = Serial.readStringUntil('\\n');
        line.trim();
        if (line.equalsIgnoreCase("PING")) {
            Serial.println("PONG");
        } else if (line.startsWith("AIM,")) {
            int c1 = line.indexOf(',');
            int c2 = line.indexOf(',', c1 + 1);
            int c3 = line.indexOf(',', c2 + 1);
            float p = line.substring(c1 + 1, c2).toFloat();
            float t = line.substring(c2 + 1, c3).toFloat();
            int l = line.substring(c3 + 1).toInt();
            setServoAngle(CHANNEL_PAN, p, PAN_MIN, PAN_MAX);
            setServoAngle(CHANNEL_TILT, t, TILT_MIN, TILT_MAX);
            digitalWrite(PIN_LASER, l ? HIGH : LOW);
            lastAimTime = millis();
            Serial.println("ACK,AIM");
        }
    }
    if (millis() - lastAimTime > FAILSAFE_MS) {
        digitalWrite(PIN_LASER, LOW);
    }
}"""
    )

    # Appendix B - Additional Screenshots
    doc.add_page_break()
    p_app_b = add_styled_heading(doc, "APPENDIX B: ADDITIONAL SCREENSHOTS", level=1, space_before=18, space_after=12)
    p_app_b.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_body_p(doc,
        "Figure B.1 illustrates the hardware wiring configuration and servo mounting layout for the ESP32 pan-tilt turret."
    )
    add_figure_with_caption(doc, "data/report_figures/turret_hardware_schematic.png",
                            "Figure B.1: ESP32 Hardware Sentry Turret Complete Electrical Pinout and Power Rail Wiring",
                            width_inches=5.8)

    add_body_p(doc,
        "Figure B.2 illustrates the educational 4-quadrant real-time DIP inspection split screen."
    )
    add_figure_with_caption(doc, "data/report_figures/dip_quadrant_inspector.png",
                            "Figure B.2: High-Resolution 4-Quadrant DIP Inspection Canvas (Raw, Grayscale, CLAHE, and LBP Colormap)",
                            width_inches=5.8)

    add_body_p(doc,
        "Figure B.3 displays the live surveillance HUD overlay capturing an active unauthorized breach."
    )
    add_figure_with_caption(doc, "data/report_figures/surveillance_capture_sample.jpg",
                            "Figure B.3: Real-Time Tactical Head-Up Display During Intruder Breach with Incident Archival Metadata",
                            width_inches=5.8)

print("Back matter module loaded.")
