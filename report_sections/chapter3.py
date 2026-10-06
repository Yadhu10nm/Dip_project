import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from build_project_report import (
    add_styled_heading, add_body_p, add_bullet_p, add_styled_table, 
    add_figure_with_caption, add_code_block
)

def add_chapter3(doc):
    """Add Chapter 3: PROPOSED SYSTEM AND METHODOLOGY."""
    doc.add_page_break()
    p_ch = add_styled_heading(doc, "Chapter 3", level=1, space_before=18, space_after=6)
    p_ch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title = add_styled_heading(doc, "PROPOSED SYSTEM AND METHODOLOGY", level=1, space_before=0, space_after=18)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 3.1 Overview of the Proposed Project
    add_styled_heading(doc, "3.1 Overview of the Proposed Project", level=2)
    add_body_p(doc,
        "The proposed system is an intelligent, multi-layered surveillance station that synthesizes digital image processing (DIP), "
        "ensemble deep learning, dense vector databases, and physical robotics. Designed around a decoupled, agentic skill architecture, "
        "the system continuously ingests real-time video frames from a security camera, executes high-speed face detection, isolates "
        "facial regions of interest, enhances image quality via adaptive equalization, aligns facial landmarks to a canonical geometry, "
        "computes deep metric embeddings, queries a vector database using consensus voting, and coordinates multi-modal responses "
        "(tactical HUD rendering, spoken audio warnings, incident logging, and pan-tilt laser tracking)."
    )

    # 3.2 Proposed Solution
    add_styled_heading(doc, "3.2 Proposed Solution", level=2)
    add_body_p(doc,
        "To resolve the limitations of conventional surveillance systems, the proposed solution introduces four critical architectural innovations:"
    )
    add_bullet_p(doc, "Zero-Trust Face Isolation Rule",
        "Full video frames or arbitrary background scene elements are strictly prohibited from entering the recognition engine. The system enforces "
        "an inviolable architectural rule: ONLY human facial regions of interest localized by the detection engine may enter downstream processing. "
        "This prevents environmental clutter and false triggers."
    )
    add_bullet_p(doc, "Multi-Stage Illumination & Pose Invariance Pipeline",
        "Raw face crops are normalized using Contrast Limited Adaptive Histogram Equalization (CLAHE) and edge-preserving bilateral filtering to "
        "neutralize shadows and sensor noise. Crucially, 5-point facial landmark affine warping maps eyes, nose, and mouth corners into canonical "
        "coordinates, eliminating pose misalignment before metric extraction."
    )
    add_bullet_p(doc, "ChromaDB RAG Consensus Voting Engine",
        "Rather than relying on naive 1-Nearest-Neighbor matching, the system queries the Top-K (K=5) nearest neighbors in ChromaDB using Cosine distance. "
        "An identity is confirmed if and only if both the maximum similarity exceeds 0.42 AND at least 40% of top-K matches agree on the candidate's "
        "identity, drastically reducing single-sample false acceptances."
    )
    add_bullet_p(doc, "Active Hardware Deterrence & Tracking",
        "An ESP32-controlled dual-SG90 pan-tilt laser turret physically swivels to track unauthorized subjects in real time, projecting a focused "
        "650nm red laser marker and emitting spoken warnings, closing the gap between computational vision and physical deterrence."
    )

    # 3.3 System Architecture / Block Diagram
    add_styled_heading(doc, "3.3 System Architecture / Block Diagram", level=2)
    add_body_p(doc,
        "The system architecture is structured into six decoupled operational subsystems communicating via an event-driven publish/subscribe "
        "message bus (EventBus). Figure 3.1 illustrates the structural block diagram and dataflow paths."
    )
    
    add_figure_with_caption(doc, "data/report_figures/system_architecture.png", 
                            "Figure 3.1: System Architecture Block Diagram Depicting Dataflow Across Vision, Vector DB, and Hardware Actuation Subsystems", 
                            width_inches=6.0)

    add_body_p(doc,
        "The six major architectural subsystems comprise:"
    )
    add_bullet_p(doc, "Perception & Ingestion Subsystem",
        "Captures 640×480 BGR frames at 30 FPS, applies thread-safe frame buffering, and performs optional horizontal mirror inversion (`cv2.flip`)."
    )
    add_bullet_p(doc, "Ensemble Detection Subsystem",
        "Deploys OpenCV YuNet DNN (`cv2.FaceDetectorYN`) as the primary detector to produce 15-D bounding boxes and 5-point landmarks, falling back "
        "to a Haar feature cascade classifier with CLAHE preprocessing if DNN confidence falls below threshold."
    )
    add_bullet_p(doc, "DIP Enhancement & Alignment Subsystem",
        "Expands bounding box margins by 8%, transforms crops to Grayscale luminance, executes CLAHE contrast normalization, applies bilateral filtering, "
        "and computes affine transformation matrices to generate canonical 112×112 aligned face arrays."
    )
    add_bullet_p(doc, "Dense Vector Retrieval & RAG Subsystem",
        "SFace convolutional network computes 128-D unit-normalized feature embeddings. ChromaDB performs HNSW Cosine distance vector search, and the "
        "RAG consensus classifier evaluates Top-5 candidate distributions."
    )
    add_bullet_p(doc, "Orchestration & Decision Subsystem",
        "Dispatches centralized security events, manages debounced state transitions (Authorized vs Unknown Intruder vs Person Locator Target), "
        "and writes structured JSON audit logs."
    )
    add_bullet_p(doc, "Actuation & User Interface Subsystem",
        "Renders tactical overlays (Military HUD and Flask Web Control Room), generates asynchronous TTS speech notifications, and transmits serial "
        "pan-tilt servo coordinates (`AIM,<pan>,<tilt>,<laser>`) to the ESP32 turret."
    )

    # 3.4 Input Image Acquisition
    add_styled_heading(doc, "3.4 Input Image Acquisition", level=2)
    add_body_p(doc,
        "Video ingestion is managed by the `CameraSkill` class wrapping OpenCV's `cv2.VideoCapture`. Camera frames are ingested in BGR (Blue-Green-Red) "
        "interleaved format at a resolution of 640×480 pixels. A target framerate of 30 FPS is enforced using high-resolution monotonic time deltas."
    )
    add_body_p(doc,
        "To provide a natural, mirror-like experience during user interaction and enrollment, the video stream undergoes horizontal coordinate "
        "inversion using the OpenCV transformation:"
    )
    add_body_p(doc,
        "        I_flipped(x, y) = I_original(W - 1 - x, y)", bold=True
    )
    add_body_p(doc,
        "where W represents the frame width (640 pixels). The acquisition module buffers incoming frames in a thread-safe queue, ensuring that "
        "downstream vision inference never blocks the video ingestion loop."
    )

    # 3.5 Image Preprocessing
    add_styled_heading(doc, "3.5 Image Preprocessing", level=2)
    add_body_p(doc,
        "Raw detected bounding boxes [x, y, w, h] tightly enclose facial features, frequently truncating forehead, ear, and jawline contours. "
        "To ensure complete facial feature retention for metric embedding, the preprocessing subsystem applies a dynamic margin expansion "
        "ratio (m = 0.08, or 8% padding):"
    )
    add_body_p(doc,
        "        pad_x = round(w * 0.08),    pad_y = round(h * 0.08)", bold=True
    )
    add_body_p(doc,
        "        x1 = max(0, x - pad_x),     y1 = max(0, y - pad_y)", bold=True
    )
    add_body_p(doc,
        "        x2 = min(W_frame, x + w + pad_x),  y2 = min(H_frame, y + h + pad_y)", bold=True
    )
    add_body_p(doc,
        "This boundary-safe cropping guarantees that extracted regions of interest (ROIs) never exceed image sensor boundaries while providing "
        "ample context for subsequent affine transformation."
    )

    # 3.6 Image Enhancement
    add_styled_heading(doc, "3.6 Image Enhancement", level=2)
    add_body_p(doc,
        "Environmental lighting variations represent the single greatest source of failure in optical biometric verification. "
        "The project applies two complementary DIP enhancement techniques:"
    )
    add_bullet_p(doc, "Contrast Limited Adaptive Histogram Equalization (CLAHE)",
        "Traditional global histogram equalization computes a single intensity transformation across the entire image, frequently washing out highlights "
        "and over-amplifying sensor noise in dark regions. CLAHE overcomes this by partitioning the grayscale face image into an 8×8 grid of localized "
        "contextual tiles. For each tile, a local histogram is calculated and clipped at a predefined contrast limit (beta = 2.0). The clipped pixels "
        "are redistributed uniformly across all histogram bins before calculating cumulative distribution functions (CDF). Finally, to eliminate artificial "
        "tile boundaries, bilinear interpolation is applied between tile center points, producing a smooth, uniformly illuminated facial image."
    )
    add_bullet_p(doc, "Edge-Preserving Bilateral Filtering",
        "While standard Gaussian filtering blurs high-frequency noise, it indiscriminately softens critical facial edge boundaries (eye contours, "
        "nasal bridge, lips). Bilateral filtering resolves this by weighting neighboring pixels according to both geometric spatial closeness and "
        "photometric intensity similarity. Mathematically, for a pixel p and neighborhood Omega:"
    )
    add_body_p(doc,
        "        I_filtered(p) = (1 / W_p) * sum_{q in Omega} I(q) * G_sigma_s(||p - q||) * G_sigma_r(|I(p) - I(q)|)", bold=True
    )
    add_body_p(doc,
        "where G_sigma_s is the spatial Gaussian kernel (sigma_space = 40), G_sigma_r is the radiometric range Gaussian kernel (sigma_color = 40), "
        "and W_p is the normalization constant. This formulation ensures that high-frequency sensor grain is smoothed while sharp edge transitions "
        "(where |I(p) - I(q)| is large) are strictly preserved."
    )

    # 3.7 Image Processing Techniques Used
    add_styled_heading(doc, "3.7 Image Processing Techniques Used", level=2)
    add_body_p(doc,
        "The complete DIP suite employed across the system encompasses five foundational operations:"
    )
    add_bullet_p(doc, "1. Color Space Transformation (BGR to Grayscale)",
        "Transforms 3-channel 24-bit BGR color arrays into single-channel 8-bit luminance representations using the standard ITU-R BT.601 formula: "
        "Y = 0.299*R + 0.587*G + 0.114*B. This reduces memory footprint by 66% and isolates illumination intensity from chromatic hue."
    )
    add_bullet_p(doc, "2. Contrast Limited Adaptive Histogram Equalization",
        "Normalizes non-uniform illumination across facial contours using 8×8 contextual grid tiles and clip limit beta = 2.0."
    )
    add_bullet_p(doc, "3. Non-Linear Bilateral Edge Smoothing",
        "Filters high-frequency camera sensor noise while maintaining sharp structural facial gradients."
    )
    add_bullet_p(doc, "4. 5-Point Facial Landmark Affine Normalization",
        "Computes a 2D affine transformation matrix mapping detected fiducial landmarks (right eye, left eye, nose tip, right mouth corner, "
        "left mouth corner) into canonical coordinates within a standardized 112×112 pixel canvas. Figure 3.3 illustrates this geometric alignment."
    )

    add_figure_with_caption(doc, "data/report_figures/landmark_alignment_geometry.png", 
                            "Figure 3.3: 5-Point Facial Landmark Affine Normalization: (a) Unaligned Rotated Head Pose; (b) Canonical Aligned 112×112 Frame", 
                            width_inches=5.8)

    add_bullet_p(doc, "5. Local Binary Patterns (LBP) Micro-Texture Descriptor",
        "Computes localized 8-neighbor binary relationships around every central pixel c:"
    )
    add_body_p(doc,
        "        LBP(x_c, y_c) = sum_{p=0}^7 s(i_p - i_c) * 2^p,    where s(x) = 1 if x >= 0 else 0", bold=True
    )
    add_body_p(doc,
        "This produces an 8-bit texture code (0–255) invariant to monotonic illumination changes, capturing micro-textural skin details."
    )

    # 3.8 Image Segmentation / Feature Extraction
    add_styled_heading(doc, "3.8 Image Segmentation / Feature Extraction", level=2)
    add_body_p(doc,
        "The project formulates face localization as a semantic spatial segmentation task. Face regions are localized using the OpenCV YuNet DNN "
        "model (`face_detection_yunet_2023mar.onnx`), a lightweight, anchor-based convolutional network optimized for real-time mobile and edge "
        "inference. YuNet outputs a 15-dimensional floating-point vector for every detected face, as detailed in Table 3.1."
    )

    # Table 3.1
    yunet_headers = ["Index Range", "Feature Description", "Coordinate Space", "Functional Role"]
    yunet_data = [
        ["0 to 3", "Bounding Box [x, y, w, h]", "Pixel Coordinates", "Spatial localization and ROI cropping"],
        ["4 to 5", "Right Eye Landmark (x, y)", "Pixel Coordinates", "Canonical eye baseline orientation"],
        ["6 to 7", "Left Eye Landmark (x, y)", "Pixel Coordinates", "Inter-pupillary distance scaling"],
        ["8 to 9", "Nose Tip Landmark (x, y)", "Pixel Coordinates", "Central facial vertical axis anchor"],
        ["10 to 11", "Right Mouth Corner (x, y)", "Pixel Coordinates", "Lower facial geometry alignment"],
        ["12 to 13", "Left Mouth Corner (x, y)", "Pixel Coordinates", "Mouth baseline orientation"],
        ["14", "Detection Confidence Score", "Probability [0.0, 1.0]", "Threshold gating (reject if < 0.60)"],
    ]
    add_styled_table(doc, yunet_headers, yunet_data, [Inches(1.2), Inches(2.2), Inches(1.6), Inches(1.8)],
                     caption="Table 3.1: 15-Dimensional YuNet Deep Face Detection Output Vector Schema")

    add_body_p(doc,
        "Following affine normalization, the canonical 112×112 face crop is passed to the SFace deep metric network (`face_recognition_sface.onnx`). "
        "SFace produces a 128-dimensional hyperspherical feature embedding v in R^128, normalized under the Euclidean L2 norm:"
    )
    add_body_p(doc,
        "        ||v||_2 = sqrt( sum_{i=1}^{128} v_i^2 ) = 1.0", bold=True
    )
    add_body_p(doc,
        "Because all embeddings are unit-normalized, the Cosine Similarity between an enrolled vector u and a probe vector v simplifies "
        "directly to the dot product:"
    )
    add_body_p(doc,
        "        Cosine Similarity(u, v) = u . v = sum_{i=1}^{128} u_i * v_i", bold=True
    )
    add_body_p(doc,
        "Cosine Distance is correspondingly defined as: Cosine Distance(u, v) = 1.0 - Cosine Similarity(u, v)."
    )

    # Table 3.2
    add_styled_heading(doc, "Vector Storage Architecture: ChromaDB HNSW", level=3)
    add_body_p(doc,
        "The project integrates ChromaDB as an embedded vector database. Table 3.2 highlights why ChromaDB was chosen over traditional relational stores."
    )
    chroma_headers = ["Evaluation Metric", "Traditional Relational DB (SQL)", "ChromaDB Vector Store"]
    chroma_data = [
        ["Data Representation", "Scalar columns, strings, integers", "128-D Dense floating-point vectors + Metadata"],
        ["Indexing Algorithm", "B-Tree / Hash Tables (Exact)", "Hierarchical Navigable Small World (HNSW) graphs"],
        ["Query Mechanism", "Exact equality / range matching", "Approximate Nearest Neighbor (ANN) Cosine search"],
        ["Time Complexity", "O(N * D) full-table scan for vectors", "O(log N) logarithmic graph traversal"],
        ["Search Latency", "120 ms – 450 ms (10,000 vectors)", "< 2.5 ms (10,000 vectors)"],
        ["Persistence Engine", "Heavyweight client-server daemon", "Embedded local SQLite / Parquet filesystem"],
    ]
    add_styled_table(doc, chroma_headers, chroma_data, [Inches(1.8), Inches(2.5), Inches(2.5)],
                     caption="Table 3.2: ChromaDB Dense Vector Index vs Traditional Relational Database Comparison")

    # 3.9 Complete Project Workflow
    add_styled_heading(doc, "3.9 Complete Project Workflow", level=2)
    add_body_p(doc,
        "The operational lifecycle for every ingested video frame executes through nine deterministic stages:"
    )
    add_bullet_p(doc, "Stage 1: Ingestion & Mirroring", "Frame captured at 640×480 @ 30 FPS; horizontally mirrored if configured.")
    add_bullet_p(doc, "Stage 2: Ensemble Detection", "YuNet DNN infers faces. If confident, yields 15-D vector; otherwise Haar cascade fallback activates.")
    add_bullet_p(doc, "Stage 3: Boundary-Safe ROI Cropping", "Expands bounding box by 8% margin padding and slices safe sub-array.")
    add_bullet_p(doc, "Stage 4: DIP Preprocessing", "Transforms crop to Grayscale, executes CLAHE equalization, and applies bilateral filtering.")
    add_bullet_p(doc, "Stage 5: 5-Point Affine Alignment", "Maps eyes, nose, and mouth to canonical coordinates in 112×112 canvas.")
    add_bullet_p(doc, "Stage 6: 128-D Metric Embedding", "SFace deep network computes unit-normalized hyperspherical feature vector.")
    add_bullet_p(doc, "Stage 7: ChromaDB RAG Vector Search", "Queries Top-5 nearest neighbors under Cosine distance metric.")
    add_bullet_p(doc, "Stage 8: Consensus Classification", "Evaluates Top-5 distribution. If Max Similarity ≥ 0.42 and Consensus ≥ 40%, authorizes subject; otherwise flags Intruder.")
    add_bullet_p(doc, "Stage 9: Actuation & Alerting", "Renders HUD overlay, queues asynchronous TTS speech, writes audit logs, and commands ESP32 turret.")

    # 3.10 Algorithm / Step-by-Step Procedure
    add_styled_heading(doc, "3.10 Algorithm / Step-by-Step Procedure", level=2)
    add_body_p(doc, "Algorithm 1 details the ensemble face detection and DIP normalization procedure:")
    add_code_block(doc,
"""Algorithm 1: Ensemble Face Detection & DIP Preprocessing
Input:  BGR Video Frame F in R^(H x W x 3)
Output: List of Aligned Faces A = {A_1, A_2, ..., A_m}, Bounding Boxes B

1.  Initialize empty lists A <- [], B <- []
2.  If CAMERA_FLIP is True: F <- HorizontalFlip(F)
3.  Execute YuNet DNN: D_raw <- cv2.FaceDetectorYN.detect(F)
4.  If D_raw is None or Empty:
5.      F_gray <- cv2.cvtColor(F, BGR2GRAY)
6.      F_clahe <- CLAHE(F_gray, clipLimit=2.0)
7.      D_haar <- HaarCascade.detectMultiScale(F_clahe, scale=1.1, minNeighbors=4)
8.      For each bbox (x, y, w, h) in D_haar:
9.          Crop ROI with 8% margin: ROI <- SafeCrop(F, x, y, w, h)
10.         A_i <- cv2.resize(ROI, (112, 112))
11.         Append A_i to A, Append bbox to B
12. Else:
13.     For each face row d in D_raw:
14.         Extract confidence conf <- d[14]
15.         If conf < 0.60: Continue
16.         bbox <- (d[0], d[1], d[2], d[3]), landmarks <- d[4:14]
17.         A_i <- cv2.FaceRecognizerSF.alignCrop(F, d)  // 5-point affine warp to 112x112
18.         Append A_i to A, Append bbox to B
19. Return A, B"""
    )

    add_body_p(doc, "Algorithm 2 details the SFace embedding and ChromaDB RAG consensus decision logic:")
    add_code_block(doc,
"""Algorithm 2: SFace Embedding & ChromaDB RAG Consensus Decision
Input:  Aligned 112x112 Face Crop A_i, Vector Store DB, Top-K = 5
Output: Recognition Decision (Identity, Role, Confidence, Evidence)

1.  Extract 128-D feature vector: v_raw <- cv2.FaceRecognizerSF.feature(A_i)
2.  Normalize vector: v <- v_raw / ||v_raw||_2
3.  Query ChromaDB: Results <- DB.query(query_embeddings=[v], n_results=5)
4.  If Results are Empty: Return Decision("Unknown Intruder", Similarity=0.0)
5.  Extract distances Dist = [d_1, ..., d_5], Metadatas Meta = [m_1, ..., m_5]
6.  Compute Similarities: Sim = [1.0 - d for d in Dist]
7.  Max_Sim <- max(Sim), Best_Index <- argmax(Sim)
8.  Candidate_ID <- Meta[Best_Index]['person_id']
9.  Count hits: Hits <- sum(1 for m in Meta if m['person_id'] == Candidate_ID)
10. Consensus_Ratio <- Hits / 5.0
11. If Max_Sim >= 0.42 AND Consensus_Ratio >= 0.40:
12.     Identity <- Meta[Best_Index]['name']
13.     Role <- Meta[Best_Index]['role']
14.     Status <- "Authorized Personnel"
15. Else:
16.     Identity <- "Unknown Intruder"
17.     Role <- "Unauthorized"
18.     Status <- "Intruder Alert"
19. Return Decision(Identity, Role, Max_Sim, Consensus_Ratio, Status)"""
    )

    # 3.11 Flowchart
    add_styled_heading(doc, "3.11 Flowchart", level=2)
    add_body_p(doc,
        "Figure 3.2 illustrates the complete decision flow of the surveillance pipeline, including detection branching, "
        "consensus voting, intruder state debouncing, and sentry turret tracking."
    )
    
    add_figure_with_caption(doc, "data/report_figures/workflow_flowchart.png", 
                            "Figure 3.2: Complete Project Workflow Flowchart Depicting Frame Capture, Detection, Vector Search, and Hardware Response", 
                            width_inches=5.8)

print("Chapter 3 module loaded.")
