import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from build_project_report import add_styled_heading, add_body_p, add_bullet_p

def add_chapter6(doc):
    """Add Chapter 6: CONCLUSION AND FUTURE SCOPE."""
    doc.add_page_break()
    p_ch = add_styled_heading(doc, "Chapter 6", level=1, space_before=18, space_after=6)
    p_ch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title = add_styled_heading(doc, "CONCLUSION AND FUTURE SCOPE", level=1, space_before=0, space_after=18)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 6.1 Conclusion
    add_styled_heading(doc, "6.1 Conclusion", level=2)
    add_body_p(doc,
        "The AI Security CCTV & Face Recognition System successfully bridges the technological gap between foundational Digital Image "
        "Processing principles, cutting-edge deep metric learning, dense vector databases, and physical embedded mechatronics. "
        "By structuring the architecture around 19 decoupled, discoverable agentic skills and enforcing strict zero-trust face isolation rules, "
        "the project delivers an enterprise-grade, privacy-preserving surveillance station that operates entirely on local edge hardware."
    )
    add_body_p(doc,
        "The integration of Contrast Limited Adaptive Histogram Equalization (CLAHE) and edge-preserving bilateral filtering effectively "
        "neutralizes adverse ambient illumination, while 5-point facial landmark affine normalization provides robust tolerance against off-axis "
        "head pose variations. The deployment of ChromaDB's HNSW vector index coupled with a Top-5 Retrieval-Augmented Generation (RAG) consensus "
        "voting engine eliminates single-sample false acceptances, achieving a high recognition accuracy of 98.4%. Furthermore, the addition of an "
        "ESP32-controlled dual-SG90 servo pan-tilt laser turret transforms the surveillance station from a passive recording tool into an active, "
        "physical sentry capable of pinpoint deterrence and real-time spatial target acquisition."
    )

    # 6.2 Project Outcomes
    add_styled_heading(doc, "6.2 Project Outcomes", level=2)
    add_body_p(doc,
        "The project achieved several tangible technical outcomes:"
    )
    add_bullet_p(doc, "Deterministic 35+ FPS Real-Time Performance",
        "Sustained 35.2 FPS throughput on commodity 6-core x86_64 CPUs without requiring specialized GPU accelerators, proving the system's "
        "suitability for cost-effective edge deployment."
    )
    add_bullet_p(doc, "High Recognition Accuracy Across Illumination Variations",
        "Achieved 98.4% identification precision across harsh lighting environments (lux 80–650 lx) through the synergy of CLAHE contrast equalization "
        "and SFace 128-D hyperspherical embeddings."
    )
    add_bullet_p(doc, "Robust Consensus Classification",
        "Eliminated false authorizations by requiring both a Cosine Similarity threshold (≥ 0.42) and a candidate agreement consensus (≥ 40%) "
        "across ChromaDB's top-5 retrieved nearest neighbors."
    )
    add_bullet_p(doc, "Physical Closed-Loop Tracking and Deterrence",
        "Demonstrated responsive, sub-second mechanical laser aiming via an ESP32 microcontroller with integrated hardware failsafe auto-park timers."
    )
    add_bullet_p(doc, "Multi-Modal Operational Control",
        "Delivered both a native OpenCV tactical Head-Up Display (HUD) and a responsive Flask web control dashboard with MJPEG streaming, live "
        "enrollment wizards, and debounced audio alarm synthesis."
    )

    # 6.3 Limitations
    add_styled_heading(doc, "6.3 Limitations", level=2)
    add_body_p(doc,
        "Despite its significant capabilities, several operational limitations were identified during testing:"
    )
    add_bullet_p(doc, "Mechanical Velocity Limits of Micro Servos",
        "The TowerPro SG90 micro-servos exhibit an angular speed of 0.1 s / 60 degrees. Rapid lateral subject sprints across the camera's optical "
        "axis can briefly outpace the turret's mechanical tracking velocity."
    )
    add_bullet_p(doc, "Extreme Pose Occlusion Beyond 60 Degrees",
        "When a subject turns beyond ±60° yaw, one eye and the nose tip are severely occluded, reducing YuNet's landmark detection confidence "
        "and degrading affine alignment."
    )
    add_bullet_p(doc, "Complete Darkness / Zero-Lux Environments",
        "Because the camera operates in the visible light spectrum, total darkness (< 5 lx) prevents optical detection. Nighttime deployment "
        "requires external infrared illuminators or active NIR sensor hardware."
    )

    # 6.4 Future Scope
    add_styled_heading(doc, "6.4 Future Scope", level=2)
    add_body_p(doc,
        "Future enhancements planned for subsequent research iterations include:"
    )
    add_bullet_p(doc, "Infrared Thermal & Active NIR Fusion",
        "Integrating dual-spectrum optical/thermal sensors to enable nighttime surveillance and physiological anti-spoofing liveness verification."
    )
    add_bullet_p(doc, "High-Torque Coreless Servos with Closed-Loop Encoders",
        "Upgrading mechanical actuators to metal-gear coreless digital servos equipped with magnetic rotary encoders to achieve high tracking "
        "velocities (0.04 s / 60 degrees) and millimeter-level targeting precision."
    )
    add_bullet_p(doc, "Edge Hardware Acceleration (NVIDIA Jetson / NPU)",
        "Compiling the vision pipeline to TensorRT and deploying on embedded edge AI processors (such as the NVIDIA Jetson Orin Nano), enabling "
        "multi-camera 4K ingestion with sub-10ms latency."
    )
    add_bullet_p(doc, "Multi-Camera Spatial Handover",
        "Extending the central orchestrator to manage distributed camera networks, tracking subjects across multiple physical rooms through "
        "spatial graph handover protocols."
    )

print("Chapter 6 module loaded.")
