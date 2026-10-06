import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from build_project_report import add_styled_heading, add_body_p, add_bullet_p, add_styled_table

def add_chapter2(doc):
    """Add Chapter 2: PROJECT REQUIREMENTS."""
    doc.add_page_break()
    p_ch = add_styled_heading(doc, "Chapter 2", level=1, space_before=18, space_after=6)
    p_ch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title = add_styled_heading(doc, "PROJECT REQUIREMENTS", level=1, space_before=0, space_after=18)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 2.1 Hardware Requirements
    add_styled_heading(doc, "2.1 Hardware Requirements", level=2)
    add_body_p(doc,
        "The system is designed to strike an optimal balance between computational efficiency, real-time response, and affordability. "
        "The architecture operates across two distinct hardware tiers: the primary Host Processing Workstation (responsible for high-speed "
        "video ingestion, computer vision inference, vector database management, and UI rendering) and the Embedded Hardware Sentry Turret "
        "(responsible for real-time mechatronic servo positioning and laser actuation)."
    )
    add_body_p(doc,
        "The specific hardware components and their technical specifications are detailed below:"
    )
    add_bullet_p(doc, "Host Processing Workstation",
        "Requires a multi-core x86_64 or ARM64 processor (Intel Core i5/i7 8th Gen or AMD Ryzen 5/7 equivalent minimum, operating at ≥ 2.4 GHz). "
        "A minimum of 8 GB of DDR4 system RAM (16 GB recommended) is required to comfortably accommodate frame buffers, neural ONNX runtime "
        "allocations, and in-memory ChromaDB vector indexes. High-speed USB 3.0 ports are required for camera and serial communications."
    )
    add_bullet_p(doc, "Video Capture Sensor (CCTV / Webcam)",
        "Standard High-Definition (HD) USB webcam or RTSP-enabled IP security camera capable of capturing at a minimum native resolution of "
        "640×480 pixels (VGA) up to 1920×1080 (Full HD) at a steady frame rate of 30 frames per second. Optical field of view between 65° and 90°."
    )
    add_bullet_p(doc, "Microcontroller Unit (MCU)",
        "Espressif ESP32 or ESP32-S3 development board powered by a dual-core Xtensa 32-bit LX7/LX6 microprocessor clocked at 240 MHz. Features "
        "512 KB of internal SRAM, native hardware LEDC PWM timers for micro-servo control, and integrated USB CDC / UART hardware bridge."
    )
    add_bullet_p(doc, "Actuators (Pan & Tilt Servos)",
        "Two TowerPro SG90 9g micro-servos arranged in an orthogonal 2-axis gimbal configuration. The Pan servo controls horizontal azimuth rotation "
        "(10° to 170°), while the Tilt servo controls vertical elevation pitch (20° to 160°). Stall torque: 1.8 kgf·cm at 4.8V; operating speed: "
        "0.1 s / 60 degrees."
    )
    add_bullet_p(doc, "Optical Target Indicator (Laser Diode)",
        "KY-008 650nm red dot laser diode module operating at 3.3V–5V with a current draw of ≤ 30 mA and optical output power of < 5 mW (Class 3R). "
        "Controlled digitally via GPIO pin for intruder pinpointing and deterrent marking."
    )
    add_bullet_p(doc, "Power Supply and Interconnects",
        "Dedicated external 5V 2A DC regulated power supply or powered USB bus. SG90 servos can draw peak stall currents between 500mA and 1A each; "
        "powering servos from the ESP32 3.3V logic regulator causes severe brownouts and resets. A common ground (GND) rail between the ESP32, "
        "external PSU, and servos is mandatory."
    )

    # Table 2.1
    hw_headers = ["Component", "Model / Specification", "Operating Voltage", "Key Function"]
    hw_data = [
        ["Host Processor", "Intel Core i5 / AMD Ryzen 5 (6 Cores, 3.8 GHz)", "120V / 230V AC", "Computer vision, ONNX models, ChromaDB, Web UI"],
        ["System Memory", "16 GB DDR4 RAM @ 3200 MHz", "1.2V DC", "Frame buffering, ChromaDB HNSW vector index"],
        ["Camera Sensor", "HD USB 2.0 Webcam (640×480 @ 30 FPS)", "5.0V USB", "Real-time BGR optical video stream capture"],
        ["Microcontroller", "ESP32-S3 DevKit (Dual-Core Xtensa @ 240MHz)", "5.0V USB / VIN", "Hardware LEDC PWM timers, serial command parsing"],
        ["Pan-Tilt Servos", "2× TowerPro SG90 9g Micro Servos", "4.8V – 6.0V DC (Ext)", "2-Axis mechanical gimbal positioning (Yaw/Pitch)"],
        ["Laser Module", "KY-008 650nm Red Dot Diode (<5mW)", "3.3V – 5.0V DC", "Visual intruder targeting and physical deterrence"],
        ["External PSU", "5V 2.0A Regulated DC Power Adapter", "100V – 240V AC", "Clean inductive current supply for servo motors"],
    ]
    add_styled_table(doc, hw_headers, hw_data, [Inches(1.5), Inches(2.2), Inches(1.3), Inches(1.8)], 
                     caption="Table 2.1: Hardware Component Specifications and Electrical Ratings")

    # 2.2 Software Requirements
    add_styled_heading(doc, "2.2 Software Requirements", level=2)
    add_body_p(doc,
        "The software architecture is engineered to run seamlessly across standard operating systems with minimal overhead:"
    )
    add_bullet_p(doc, "Operating System",
        "Microsoft Windows 10 / 11 (64-bit), Linux (Ubuntu 20.04 LTS or newer), or macOS (12.0 Monterey or newer). Development and empirical "
        "benchmarking were conducted on Windows 11 64-bit."
    )
    add_bullet_p(doc, "Python Environment",
        "Python 3.10, 3.11, or 3.12 (64-bit). Managed within an isolated virtual environment (`.venv`) to ensure pristine dependency segregation."
    )
    add_bullet_p(doc, "Microcontroller Firmware Platform",
        "Arduino IDE 2.x with the official `esp32` board support package by Espressif Systems (v2.0.x / v3.0.x). USB CDC on Boot enabled for ESP32-S3."
    )
    add_bullet_p(doc, "Web Client Environment",
        "Modern HTML5-compliant web browser supporting WebSocket and MJPEG video streaming, such as Google Chrome (v110+), Microsoft Edge (v110+), "
        "or Mozilla Firefox (v108+)."
    )

    # 2.3 Programming Language
    add_styled_heading(doc, "2.3 Programming Language", level=2)
    add_body_p(doc,
        "The system strategically employs two primary programming languages, leveraging the distinct strengths of each for high-level computing "
        "and low-level embedded actuation:"
    )
    add_body_p(doc,
        "1. Python 3 (Backend & Vision Pipeline): Chosen as the primary language due to its unmatched ecosystem in computer vision, numerical "
        "computing, and machine learning. Python provides native bindings for OpenCV (`cv2`), high-performance array operations via NumPy, "
        "seamless ONNX runtime integration, lightweight web micro-frameworks (Flask), and native OS text-to-speech integration (`pyttsx3`). "
        "Its rapid prototyping capabilities and expressive syntax enabled the creation of the 19 modular agentic skills."
    )
    add_body_p(doc,
        "2. C++ / Arduino Wiring (Firmware): Employed for the ESP32 microcontroller firmware. C++ enables direct, bare-metal access to the ESP32's "
        "hardware registers and LEDC peripheral timers. Generating high-precision 50 Hz PWM signals with 14-bit duty cycle resolution requires "
        "sub-microsecond timing accuracy that cannot be reliably achieved through interpreted languages."
    )

    # 2.4 Libraries and Tools Used
    add_styled_heading(doc, "2.4 Libraries and Tools Used", level=2)
    add_body_p(doc,
        "The software stack integrates several battle-tested, open-source libraries that collectively form the end-to-end intelligence pipeline:"
    )
    add_bullet_p(doc, "OpenCV (opencv-contrib-python ≥ 4.8.0)",
        "The core computer vision foundation. Powers video capture, color conversions, CLAHE equalization, bilateral filtering, deep YuNet DNN face "
        "detection (`cv2.FaceDetectorYN`), SFace metric embedding extraction (`cv2.FaceRecognizerSF`), LBPH model training, affine warping, and HUD drawing."
    )
    add_bullet_p(doc, "NumPy (≥ 1.24.0)",
        "Underpins all mathematical computations, vectorized LBP sliding window operations, Euclidean/Cosine distance metrics, and multi-dimensional "
        "frame transformations."
    )
    add_bullet_p(doc, "ChromaDB (chromadb)",
        "Open-source embedded AI vector database. Provides persistent storage of 128-dimensional SFace embeddings in `data/chroma_db/`, utilizing "
        "Hierarchical Navigable Small World (HNSW) graphs to execute sub-millisecond approximate nearest neighbor searches under Cosine similarity."
    )
    add_bullet_p(doc, "Flask (≥ 3.0.0)",
        "Lightweight WSGI Python web server framework. Implements the REST API endpoints and streams live multipart/x-mixed-replace MJPEG video frames "
        "to browser clients."
    )
    add_bullet_p(doc, "pyttsx3 (≥ 2.90)",
        "Completely offline text-to-speech synthesis engine interfacing with Microsoft Speech API (SAPI5) on Windows. Operates in an asynchronous "
        "background thread to generate audible spoken alerts without dropping video frames."
    )
    add_bullet_p(doc, "PySerial (≥ 3.5)",
        "Provides asynchronous bidirectional serial communication between the host Python application and the ESP32 microcontroller at 115200 baud."
    )

    # Table 2.2
    sw_headers = ["Library / Tool", "Version", "Ecosystem", "Role in System Architecture"]
    sw_data = [
        ["OpenCV Contrib", ">= 4.8.0", "Python C++", "Camera capture, YuNet DNN, SFace ONNX, CLAHE, Bilateral Filter"],
        ["NumPy", ">= 1.24.0", "Python C", "Vectorized array calculations, vectorized LBP kernel, distance metrics"],
        ["ChromaDB", "Latest", "Python Rust", "Persistent HNSW Cosine vector store, Top-K RAG retrieval"],
        ["Flask", ">= 3.0.0", "Python", "Web dashboard server, RESTful API endpoints, MJPEG video streaming"],
        ["pyttsx3", ">= 2.90", "Python SAPI5", "Asynchronous non-blocking offline text-to-speech audio alerts"],
        ["PySerial", ">= 3.5", "Python C", "Serial telemetry and command exchange with ESP32 at 115200 baud"],
        ["Pillow (PIL)", ">= 9.5.0", "Python", "High-resolution raster image manipulation and evidence saving"],
        ["Arduino IDE", ">= 2.3.0", "C++ / Wiring", "ESP32 hardware firmware development, flashing, and serial monitor"],
    ]
    add_styled_table(doc, sw_headers, sw_data, [Inches(1.5), Inches(1.1), Inches(1.2), Inches(3.0)], 
                     caption="Table 2.2: Software Environment, Frameworks, and Dependent Libraries")

    # 2.5 Dataset / Input Images
    add_styled_heading(doc, "2.5 Dataset / Input Images", level=2)
    add_body_p(doc,
        "The project manages two primary image repositories within the local filesystem:"
    )
    add_body_p(doc,
        "1. Authorized Personnel Dataset (`data/dataset/`): Structured hierarchically by unique subject identifier (e.g., `AUTH_001`, `AUTH_002`). "
        "During user registration, an automated burst enrollment captures exactly 25 canonical 200×200 normalized face crops per individual. "
        "Each facial crop is extracted from live video, filtered through CLAHE and bilateral filtering, aligned using 5-point landmark affine warping, "
        "and transformed into a 128-D vector embedding stored in ChromaDB. Accompanying user metadata (Full Name, Role, Enrollment Timestamp, "
        "Sample Count, Thumbnail Path) is persisted in `data/authorized_users.json`."
    )
    add_body_p(doc,
        "2. Security Incident Audit Vault (`data/intruders/`): Whenever an unauthorized individual is detected in the video stream, the system "
        "automatically captures a full-frame 640×480 incident snapshot. The snapshot is permanently tagged with an ISO-8601 timestamp "
        "(e.g., `intruder_20261001_140006.jpg`), stored in `data/intruders/`, and logged in `data/audit_log.json` along with detection bounding "
        "boxes, max similarity scores, and classification evidence. A 10-second snapshot cooldown is enforced to prevent disk saturation during "
        "prolonged security breaches."
    )

print("Chapter 2 module loaded.")
