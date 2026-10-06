import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from build_project_report import (
    add_styled_heading, add_body_p, add_bullet_p, add_styled_table, 
    add_figure_with_caption, add_code_block
)

def add_chapter4(doc):
    """Add Chapter 4: IMPLEMENTATION."""
    doc.add_page_break()
    p_ch = add_styled_heading(doc, "Chapter 4", level=1, space_before=18, space_after=6)
    p_ch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title = add_styled_heading(doc, "IMPLEMENTATION", level=1, space_before=0, space_after=18)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 4.1 Project Setup
    add_styled_heading(doc, "4.1 Project Setup", level=2)
    add_body_p(doc,
        "The project implementation is organized into a modular skill architecture under `skills/` alongside a high-performance `core/` package. "
        "The workspace is configured within a dedicated Python virtual environment (`.venv`). Key environment variables and algorithmic "
        "hyperparameters are centralized in `config.py`, summarized in Table 4.1."
    )

    # Table 4.1
    cfg_headers = ["Configuration Parameter", "Default Value", "Type", "Operational Impact & Role"]
    cfg_data = [
        ["FRAME_WIDTH / HEIGHT", "640 / 480", "Integer", "Native camera sensor capture resolution"],
        ["TARGET_FPS", "30", "Integer", "Target frame acquisition and display refresh rate"],
        ["CAMERA_FLIP", "True", "Boolean", "Enables horizontal mirror inversion for natural interaction"],
        ["YUNET_CONFIDENCE_THRESHOLD", "0.60", "Float", "Minimum confidence for YuNet DNN face acceptance"],
        ["FACE_MIN_SIZE", "(45, 45)", "Tuple", "Minimum pixel dimension for valid face candidates"],
        ["CLAHE_CLIP_LIMIT", "2.0", "Float", "Contrast threshold clipping limit for local equalization"],
        ["CLAHE_TILE_GRID_SIZE", "(8, 8)", "Tuple", "Number of contextual spatial grid blocks across ROI"],
        ["FACE_MATCH_THRESHOLD", "0.42", "Float", "Cosine similarity boundary for authorized identification"],
        ["RAG_TOP_K", "5", "Integer", "Number of nearest neighbors retrieved from ChromaDB"],
        ["RAG_MIN_CONSENSUS", "0.40", "Float", "Minimum percentage of top-K matches agreeing on identity"],
        ["TURRET_PORT / BAUD", "COM5 / 115200", "String/Int", "Serial port and baud rate for ESP32 turret interface"],
        ["TURRET_FAILSAFE_TIMEOUT", "2.5", "Float", "Seconds of lost tracking before turret auto-parks laser"],
        ["TTS_COOLDOWN_SECONDS", "7.0", "Float", "Minimum interval between consecutive spoken audio alerts"],
    ]
    add_styled_table(doc, cfg_headers, cfg_data, [Inches(1.8), Inches(1.1), Inches(0.9), Inches(3.0)],
                     caption="Table 4.1: Key System Configuration Parameters and Operational Thresholds (config.py)")

    # 4.2 Input Data Preparation
    add_styled_heading(doc, "4.2 Input Data Preparation", level=2)
    add_body_p(doc,
        "Ensuring the integrity of the enrolled biometric database is fundamental to preventing false positives. The `EnrollmentSkill` "
        "and `AccessManager` enforce a strict Single-Face Validation Rule during registration:"
    )
    add_bullet_p(doc, "Zero Faces Detected", "If the subject steps away or the lighting drops below detection limits, the frame is rejected.")
    add_bullet_p(doc, "Two or More Faces Detected", "If multiple people enter the camera view during enrollment, the frame is instantly rejected to avoid vector contamination.")
    add_bullet_p(doc, "Exactly One Face Detected", "The single localized face is validated, preprocessed, aligned, and accepted.")
    add_body_p(doc,
        "During enrollment, a burst of 25 consecutive valid face frames is captured. Each frame is normalized through the DIP pipeline, "
        "aligned into canonical 112×112 geometry, converted to a 128-D unit vector via SFace, and indexed into the ChromaDB `authorized_faces` "
        "collection with metadata: `person_id`, `name`, `role`, and `sample_idx`."
    )

    # 4.3 Implementation of DIP Techniques
    add_styled_heading(doc, "4.3 Implementation of DIP Techniques", level=2)
    add_body_p(doc,
        "The Digital Image Processing engine is encapsulated within `core/dip_engine.py` (`DIPEngine`). It provides standardized methods:"
    )
    add_bullet_p(doc, "`to_grayscale(bgr_image)`", "Converts BGR image arrays to single-channel 8-bit Grayscale using OpenCV color conversion.")
    add_bullet_p(doc, "`apply_clahe(gray_image)`", "Applies `cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))` to normalize localized ambient lighting.")
    add_bullet_p(doc, "`apply_bilateral_filter(gray_image)`", "Executes `cv2.bilateralFilter(gray_image, d=5, sigmaColor=40, sigmaSpace=40)` to smooth noise while preserving sharp facial edges.")
    add_bullet_p(doc, "`compute_lbp(gray_image)`", "Implements an optimized vectorized 8-neighbor sliding window kernel in NumPy to compute Local Binary Patterns micro-texture codes.")

    # 4.4 Module 1 – Ensemble Face Detection and Alignment
    add_styled_heading(doc, "4.4 Module 1 – Ensemble Face Detection and Alignment", level=2)
    add_body_p(doc,
        "Module 1 is implemented across `core/detector.py` and `skills/face_detection_skill`. The primary detector is OpenCV's YuNet DNN, "
        "initialized via `cv2.FaceDetectorYN.create()`. YuNet dynamically adapts to incoming frame dimensions (640×480) and outputs a 15-parameter "
        "array per face containing bounding boxes and 5 facial landmarks (right eye, left eye, nose tip, right mouth corner, left mouth corner)."
    )
    add_body_p(doc,
        "If YuNet confidence falls below 0.60 or fails due to severe sensor underexposure, the pipeline triggers an automated fallback to the "
        "Haar feature cascade classifier (`haarcascade_frontalface_default.xml`). The Haar fallback preprocesses the entire frame with CLAHE "
        "prior to multi-scale evaluation (`scaleFactor=1.10`, `minNeighbors=4`, `minSize=(45, 45)`), ensuring continuous detection reliability."
    )
    add_body_p(doc,
        "Following detection, the 5-point facial landmarks are fed to `cv2.FaceRecognizerSF.alignCrop()`, which applies an affine transformation "
        "matrix to rotate, scale, and crop the face into a canonical 112×112 dimensional image where the eye line is strictly horizontal."
    )

    # 4.5 Module 2 – SFace Feature Embeddings and ChromaDB Vector RAG
    add_styled_heading(doc, "4.5 Module 2 – SFace Feature Embeddings and ChromaDB Vector RAG", level=2)
    add_body_p(doc,
        "Module 2 is implemented across `core/embedding_engine.py`, `core/vector_store.py`, and `skills/face_recognition_skill`. "
        "The aligned 112×112 face array is passed to the SFace convolutional network (`face_recognition_sface.onnx`), yielding a raw "
        "128-dimensional embedding. The vector is normalized under L2 norm so that its length equals 1.0."
    )
    add_body_p(doc,
        "The embedding is queried against ChromaDB's persistent collection using the Cosine distance space. ChromaDB executes an approximate "
        "nearest neighbor search across its HNSW index in under 2 milliseconds, returning the Top-5 nearest matches along with their cosine "
        "distances and associated user metadata."
    )
    add_body_p(doc,
        "The RAG consensus classifier computes the candidate identity with the maximum similarity. It evaluates two gating conditions: "
        "(1) Maximum Cosine Similarity ≥ 0.42, and (2) Consensus Ratio (candidate hits in top-5 / 5) ≥ 0.40. If both conditions are satisfied, "
        "the subject is confirmed as Authorized Personnel; otherwise, the subject is flagged as an Unauthorized Intruder."
    )

    # 4.6 Module 3 – Hardware Surveillance, Sentry Turret & Alert Engine
    add_styled_heading(doc, "4.6 Module 3 – Hardware Surveillance, Sentry Turret & Alert Engine", level=2)
    add_body_p(doc,
        "Module 3 integrates physical actuation, audio synthesis, and security telemetry. The ESP32 sentry turret is controlled over USB CDC "
        "Serial at 115200 baud via a compact ASCII packet protocol, summarized in Table 4.2."
    )

    # Table 4.2
    cmd_headers = ["Command Packet", "Parameters", "Direction", "Microcontroller Action & Response"]
    cmd_data = [
        ["PING", "None", "Host -> ESP32", "Health check; ESP32 responds with 'PONG'"],
        ["AIM,<pan>,<tilt>,<laser>", "pan: 10-170, tilt: 20-160, laser: 0/1", "Host -> ESP32", "Repositions SG90 servos and sets KY-008 laser state; responds 'ACK,AIM'"],
        ["LASER,<state>", "state: 0 (OFF), 1 (ON)", "Host -> ESP32", "Overrides laser diode without moving servos; responds 'ACK,LASER'"],
        ["STATUS", "None", "Host -> ESP32", "Queries current hardware status; responds 'STATUS,pan,tilt,laser'"],
    ]
    add_styled_table(doc, cmd_headers, cmd_data, [Inches(1.8), Inches(2.2), Inches(1.1), Inches(1.9)],
                     caption="Table 4.2: ESP32 Sentry Turret Serial Communication Packet Protocol")

    add_body_p(doc,
        "Figure 4.1 displays the hardware schematic and electrical wiring connecting the ESP32 microcontroller, dual SG90 micro-servos, "
        "KY-008 laser diode module, and dedicated 5V power distribution rails."
    )
    add_figure_with_caption(doc, "data/report_figures/turret_hardware_schematic.png", 
                            "Figure 4.1: ESP32 Dual-Servo Pan-Tilt Laser Sentry Turret Hardware Wiring Schematic", 
                            width_inches=5.8)

    add_body_p(doc,
        "To map 2D video pixel coordinates (x_c, y_c) to physical servo angles (theta_pan, theta_tilt), the turret controller applies proportional mapping:"
    )
    add_body_p(doc,
        "        norm_x = x_c / W_frame,    norm_y = y_c / H_frame", bold=True
    )
    add_body_p(doc,
        "        theta_pan  = PAN_MIN  + (1.0 - norm_x) * (PAN_MAX  - PAN_MIN)", bold=True
    )
    add_body_p(doc,
        "        theta_tilt = TILT_MIN + norm_y * (TILT_MAX - TILT_MIN)", bold=True
    )
    add_body_p(doc,
        "A central deadband (epsilon = 0.03) prevents micro-jitter when a subject stands still. An automated hardware failsafe timer "
        "parks the servos and disables the laser diode if no target is detected for 2.5 seconds."
    )

    # 4.7 User Interface
    add_styled_heading(doc, "4.7 User Interface", level=2)
    add_body_p(doc,
        "The project provides two interactive user interface modes:"
    )
    add_bullet_p(doc, "1. Native OpenCV Tactical Desktop HUD (`core/cctv_hud.py` & `desktop_app.py`)",
        "Renders a real-time cyber surveillance overlay directly on the video window. Features animated corner brackets, targeting crosshairs, "
        "color-coded status badges (Emerald Green for Authorized, Crimson Red for Intruder, Amber Yellow for Person Locator Target), confidence "
        "meters, live FPS counters, and interactive keyboard shortcuts (`Q` to quit, `E` to enroll, `D` to toggle DIP inspector, `T` to test turret)."
    )
    add_bullet_p(doc, "2. Flask Web Dashboard (`web/app.py` & `web/templates/index.html`)",
        "A responsive browser-based cyber control room serving live MJPEG video streaming at `/video_feed`. Provides interactive REST API controls "
        "for live batch photo enrollment, turret manual aiming sliders, audio alert muting, target person locator search, and an incident timeline "
        "displaying watermarked intruder snapshot captures."
    )

    # 4.8 Important Code Snippets
    add_styled_heading(doc, "4.8 Important Code Snippets", level=2)
    add_body_p(doc, "Listing 4.1: Vectorized Local Binary Patterns (LBP) Micro-Texture Kernel (`core/dip_engine.py`):")
    add_code_block(doc,
"""def compute_lbp(self, gray_image: np.ndarray) -> np.ndarray:
    \"\"\"Vectorized computation of 8-neighbor Local Binary Patterns (LBP).\"\"\"
    if len(gray_image.shape) == 3:
        gray = self.to_grayscale(gray_image)
    else:
        gray = gray_image
    h, w = gray.shape
    if h < 3 or w < 3:
        return np.zeros_like(gray, dtype=np.uint8)

    center = gray[1:h-1, 1:w-1].astype(np.int16)
    # Extract 8 circular/square neighbors via array slicing
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

    add_body_p(doc, "Listing 4.2: ChromaDB RAG Consensus Decision Logic (`core/recognizer.py`):")
    add_code_block(doc,
"""def recognize_face_rag(self, face_embedding: np.ndarray):
    \"\"\"Query ChromaDB and evaluate Top-K RAG consensus voting.\"\"\"
    results = self.vector_store.query_similar(face_embedding, n_results=config.RAG_TOP_K)
    if not results or not results.get("distances") or len(results["distances"][0]) == 0:
        return {"matched": False, "name": "Unknown", "role": "Intruder", "similarity": 0.0}

    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    similarities = [max(0.0, 1.0 - d) for d in distances]
    max_sim = max(similarities)
    best_idx = similarities.index(max_sim)
    candidate_id = metadatas[best_idx].get("person_id")

    # Consensus voting across top-k
    hits = sum(1 for m in metadatas if m.get("person_id") == candidate_id)
    consensus_ratio = hits / len(metadatas)

    is_authorized = (max_sim >= config.FACE_MATCH_THRESHOLD and 
                     consensus_ratio >= config.RAG_MIN_CONSENSUS)
    return {
        "matched": is_authorized,
        "person_id": candidate_id if is_authorized else None,
        "name": metadatas[best_idx].get("name", "Unknown") if is_authorized else "Unknown",
        "role": metadatas[best_idx].get("role", "Intruder") if is_authorized else "Unauthorized",
        "similarity": round(float(max_sim), 4),
        "consensus_ratio": round(float(consensus_ratio), 2)
    }"""
    )

    add_body_p(doc, "Listing 4.3: Hardware LEDC PWM Servo Positioning (`hardware/esp32_laser_turret.ino`):")
    add_code_block(doc,
"""void setServoAngle(int channel, float angle, float min_deg, float max_deg) {
    // Clamp angle within mechanical safety limits
    angle = constrain(angle, min_deg, max_deg);
    // Linear interpolation: angle -> pulse width in microseconds (500us to 2400us)
    float pulse_us = SERVO_MIN_US + (angle / 180.0f) * (SERVO_MAX_US - SERVO_MIN_US);
    // Convert pulse width to 14-bit duty cycle: (pulse_us / 20000us) * 16383
    uint32_t duty = (uint32_t)((pulse_us / 20000.0f) * 16383.0f);
    ledcWrite(channel, duty);
}"""
    )

print("Chapter 4 module loaded.")
