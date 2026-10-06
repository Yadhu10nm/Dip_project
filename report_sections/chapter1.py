import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from build_project_report import add_styled_heading, add_body_p, add_bullet_p

def add_chapter1(doc):
    """Add Chapter 1: INTRODUCTION."""
    doc.add_page_break()
    p_ch = add_styled_heading(doc, "Chapter 1", level=1, space_before=18, space_after=6)
    p_ch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title = add_styled_heading(doc, "INTRODUCTION", level=1, space_before=0, space_after=18)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 1.1 Introduction
    add_styled_heading(doc, "1.1 Introduction", level=2)
    add_body_p(doc,
        "In the contemporary landscape of digital security, physical access control, and automated infrastructure protection, "
        "video surveillance systems have emerged as one of the most vital layers of defense. Traditional Closed-Circuit Television (CCTV) "
        "networks, which have formed the backbone of facility monitoring for decades, remain fundamentally passive in their operational "
        "paradigm. Standard CCTV cameras capture continuous streams of video data and record them onto storage media such as Network Video "
        "Recorders (NVRs) or Digital Video Recorders (DVRs). The burden of identifying unauthorized individuals, detecting security breaches, "
        "and coordinating responses has historically rested entirely upon human operators tasked with monitoring multi-screen control rooms."
    )
    add_body_p(doc,
        "Human vigilance, however, suffers from inherent cognitive constraints. Empirical psychological studies in human-computer interaction "
        "have demonstrated that human monitoring efficiency drops precipitously after only twenty to thirty minutes of continuous observation, "
        "leading to severe oversight, missed security breaches, and unacceptably sluggish reaction times. Consequently, contemporary security "
        "engineering is undergoing a radical paradigm shift: the transformation of passive visual recording devices into active, autonomous, "
        "and intelligent computational sentry stations."
    )
    add_body_p(doc,
        "An intelligent surveillance station integrates foundational Digital Image Processing (DIP) techniques, machine vision algorithms, "
        "deep metric learning, and embedded physical actuation to autonomously perceive human presence, verify identity against authorized "
        "databases, and execute real-time deterrence protocols. By delegating real-time detection, facial landmark normalization, vector "
        "similarity retrieval, and physical tracking to high-speed algorithmic pipelines, intelligent surveillance systems offer uninterrupted, "
        "objective, and mathematically rigorous security auditing twenty-four hours a day."
    )

    # 1.2 Project Background
    add_styled_heading(doc, "1.2 Project Background", level=2)
    add_body_p(doc,
        "The technological lineage of automated facial analysis spans more than five decades, evolving through three distinct historical epochs: "
        "geometric template matching, appearance-based statistical subspace modeling, and deep convolutional metric representation."
    )
    add_body_p(doc,
        "In the foundational era of computer vision (1970s–1990s), facial recognition was dominated by geometric models based on Euclidean "
        "distances between fiducial facial landmarks, followed by statistical appearance modeling. Seminal techniques such as Eigenfaces "
        "(based on Principal Component Analysis, or PCA) and Fisherfaces (based on Linear Discriminant Analysis, or LDA) sought to project "
        "high-dimensional pixel arrays into low-dimensional orthogonal subspaces that maximized intra-subject clustering or inter-subject "
        "variance. While mathematically elegant, these global subspace techniques were notorious for catastrophic degradation under slight "
        "variations in ambient lighting, facial expression, and head orientation."
    )
    add_body_p(doc,
        "To mitigate illumination sensitivity, researchers introduced localized texture descriptors, most notably Local Binary Patterns (LBP) "
        "and Local Binary Patterns Histograms (LBPH) by Ahonen et al. in 2006. By encoding micro-texture relationships between neighboring pixels "
        "rather than raw intensity values, LBPH achieved robust invariance against monotonic illumination shifts and became the standard for "
        "lightweight, resource-constrained facial biometric platforms."
    )
    add_body_p(doc,
        "The contemporary era (2014–present) has been defined by the deep learning revolution. Deep Convolutional Neural Networks (CNNs) trained "
        "with angular margin loss functions (such as CosFace, ArcFace, and SFace) map facial crops into high-dimensional hyperspherical manifolds "
        "where Euclidean and Cosine distances directly quantify semantic identity similarities. Furthermore, the advent of high-performance "
        "approximate nearest neighbor (ANN) vector databases, such as ChromaDB, has revolutionized the retrieval stage, enabling sub-millisecond "
        "similarity search across extensive vector embeddings."
    )
    add_body_p(doc,
        "This project bridges the gap between traditional digital image processing and modern deep neural architectures. By fusing classical "
        "DIP operators (Contrast Limited Adaptive Histogram Equalization, bilateral filtering, and LBP) with YuNet deep face detection, SFace "
        "deep metric embeddings, ChromaDB vector indexing, and physical ESP32 robotics, the project constructs a robust, explainable, and "
        "fully local surveillance architecture that exemplifies the modern state of the art in vision engineering."
    )

    # 1.3 Problem Statement
    add_styled_heading(doc, "1.3 Problem Statement", level=2)
    add_body_p(doc,
        "Despite significant commercial advancements in biometric surveillance, conventional implementations deployed in real-world environments "
        "continue to grapple with severe practical deficiencies, including:"
    )
    add_bullet_p(doc, "Environmental Illumination Vulnerability",
        "Natural and artificial lighting environments exhibit dynamic non-uniformity, ranging from extreme shadows and backlighting to severe "
        "underexposure. Without disciplined illumination normalization, standard recognition algorithms misclassify authorized individuals or fail "
        "to detect faces entirely."
    )
    add_bullet_p(doc, "Pose and Orientation Misalignment",
        "Subjects captured in wild surveillance feeds rarely look straight into the camera lens. Off-axis head yaw, pitch, and roll drastically "
        "distort facial proportions, causing severe recognition failures in systems that lack canonical 5-point landmark affine normalization."
    )
    add_bullet_p(doc, "Fragility of 1-Nearest-Neighbor Classification",
        "Conventional vector search engines query only the single closest database sample (Top-1 nearest neighbor). If a single enrolled image "
        "contains motion blur, occlusions, or sensor artifacts, naive 1-NN matching results in high false-acceptance or false-rejection rates. "
        "Robust security demands consensus-based verification across multiple nearest neighbors."
    )
    add_bullet_p(doc, "Lack of Physical Deterrence and Tracking",
        "Standard CCTV systems remain entirely passive observers. When an intruder breaches a secured perimeter, the camera provides no "
        "immediate physical feedback, direction tracking, or localized targeting to deter the intruder or guide security responders."
    )
    add_bullet_p(doc, "Cloud Latency and Privacy Concerns",
        "Many commercial biometric systems stream private video feeds to remote cloud servers, incurring network latency, bandwidth overhead, "
        "recurring subscription costs, and severe data privacy vulnerabilities."
    )

    # 1.4 Motivation
    add_styled_heading(doc, "1.4 Motivation", level=2)
    add_body_p(doc,
        "The driving motivation behind this project is the creation of a fully self-contained, real-time, privacy-preserving AI surveillance "
        "workstation that executes entirely on edge hardware without external cloud dependencies. By engineering an end-to-end pipeline that combines "
        "deterministic digital image processing with deep metric vector retrieval and physical mechatronics, this project aims to demonstrate that "
        "enterprise-grade biometric security and active sentry tracking can be achieved using accessible, cost-effective computational components."
    )
    add_body_p(doc,
        "Furthermore, from an academic and pedagogical perspective in Computer Science and Digital Image Processing, this project serves as a "
        "complete practical testbed. It vividly illustrates how fundamental image processing concepts—such as grayscale luminance conversion, "
        "adaptive histogram equalization, spatial domain filtering, and texture analysis—directly interact with and enhance cutting-edge deep "
        "neural network models, creating an explainable, deterministic, and highly resilient defense pipeline."
    )

    # 1.5 Objectives
    add_styled_heading(doc, "1.5 Objectives", level=2)
    add_body_p(doc,
        "The core objectives governing the development of this project are as follows:"
    )
    add_bullet_p(doc, "Real-Time Video Ingestion",
        "Construct an optimized camera ingestion engine capable of capturing and buffering live video frames at a sustained 30 frames per second "
        "(FPS) with configurable horizontal mirroring."
    )
    add_bullet_p(doc, "Ensemble Multi-Face Detection",
        "Implement an ensemble face detection pipeline deploying OpenCV's deep YuNet neural network as the primary detector (yielding 15-D bounding "
        "boxes and 5-point landmarks) alongside a classical Haar Cascade classifier as an adaptive fallback."
    )
    add_bullet_p(doc, "Rigorous DIP Enhancement Pipeline",
        "Develop an educational, deterministic DIP engine comprising grayscale conversion, Contrast Limited Adaptive Histogram Equalization (CLAHE), "
        "edge-preserving bilateral filtering, and vectorized Local Binary Patterns (LBP) micro-texture descriptor extraction."
    )
    add_bullet_p(doc, "Canonical Facial Alignment",
        "Implement a 5-point facial landmark affine transformation mapping detected eyes, nose, and mouth corners into canonical 112×112 "
        "coordinates, eliminating rotational head pose variance."
    )
    add_bullet_p(doc, "Deep Metric Feature Extraction",
        "Deploy the SFace deep neural network model to extract 128-dimensional unit-normalized facial embeddings lying on a hyperspherical manifold."
    )
    add_bullet_p(doc, "Dense Vector Storage & Retrieval",
        "Implement a persistent ChromaDB vector database utilizing Hierarchical Navigable Small World (HNSW) graph indexing and Cosine distance metric."
    )
    add_bullet_p(doc, "Retrieval-Augmented Consensus Verification",
        "Formulate a novel RAG consensus voting algorithm that queries the Top-5 nearest neighbors, requiring both a stringent similarity threshold "
        "(≥ 0.42) and an identity agreement ratio (≥ 40%) before authorizing access."
    )
    add_bullet_p(doc, "Hardware Sentry Turret Actuation",
        "Design, build, and integrate an ESP32-controlled dual-SG90 servo pan-tilt turret equipped with a KY-008 650nm red laser diode to provide "
        "real-time physical aiming and target tracking with debounced failsafe timers."
    )
    add_bullet_p(doc, "Dual User Interfaces and Audible Alerts",
        "Develop both a native OpenCV tactical Head-Up Display (HUD) and a Flask-based cyber control room with MJPEG live streaming, real-time "
        "telemetry, and asynchronous local Text-to-Speech (TTS) security alerts."
    )

    # 1.6 Scope of the Project
    add_styled_heading(doc, "1.6 Scope of the Project", level=2)
    add_body_p(doc,
        "The operational scope of the project encompasses real-time video surveillance in indoor and controlled outdoor settings. The system "
        "is specifically designed to manage multi-face scenes, identifying multiple individuals simultaneously within a single frame while processing "
        "each face crop independently through the recognition pipeline."
    )
    add_body_p(doc,
        "The scope includes complete enrollment management, enforcing a strict single-face verification rule during photo registration to ensure "
        "uncontaminated vector databases. It also encompasses physical laser aiming across a 160-degree horizontal azimuth and a 140-degree vertical "
        "elevation, localized target tracking, watermarked incident snapshot archiving, and audit log generation."
    )
    add_body_p(doc,
        "The project purposefully excludes massive cloud deployments handling thousands of concurrent cameras, 3D facial volumetric mesh modeling, "
        "and thermal infrared vision, focusing instead on delivering optimal performance, zero cloud reliance, and maximal responsiveness on "
        "localized edge workstations."
    )

    # 1.7 Applications
    add_styled_heading(doc, "1.7 Applications", level=2)
    add_body_p(doc,
        "The AI Security CCTV & Face Recognition System is directly applicable to a broad spectrum of commercial, institutional, and residential domains:"
    )
    add_bullet_p(doc, "Corporate & High-Security Access Control",
        "Can be deployed at entry turnstiles, server room doorways, and restricted research facilities to guarantee hands-free biometric access "
        "while automatically triggering audible alarms and physical laser aiming at unauthorized intruders."
    )
    add_bullet_p(doc, "Educational & Campus Attendance Auditing",
        "Provides touchless, high-throughput identification of enrolled students and faculty members at gate entrances while maintaining "
        "timestamped JSON audit records and alerting administrative personnel to unknown trespassers."
    )
    add_bullet_p(doc, "Smart Home & Perimeter Defense",
        "Offers residential homeowners an intelligent perimeter sentry that operates completely offline, safeguarding family privacy by storing "
        "all biometric vectors locally while deterring prowlers through directional laser tracking and spoken deterrent warnings."
    )
    add_bullet_p(doc, "Academic & Pedagogical Demonstration",
        "Serves as an interactive educational platform for digital image processing and computer vision curricula, allowing students and researchers "
        "to visually inspect intermediate DIP operations (Raw vs Gray vs CLAHE vs LBP) via the real-time split-screen inspector."
    )

print("Chapter 1 module loaded.")
