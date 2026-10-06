import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from build_project_report import add_styled_heading, add_body_p, add_styled_table

def update_existing_front_matter(doc):
    """Update title page, certificate, and declaration text in place while preserving styles."""
    # Title Page
    p8 = doc.paragraphs[8]
    p8.text = "AI SECURITY CCTV & FACE RECOGNITION SYSTEM"
    p8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p8.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(16)
        r.bold = True
        
    p17 = doc.paragraphs[17]
    p17.text = "YADHU KRISHNA N M\t\t\t\tUUCMS NO: [REGISTER NO]"
    for r in p17.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True

    p18 = doc.paragraphs[18]
    p18.text = "_____________________\t\t\t\tUUCMS NO: ________________"
    for r in p18.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True

    p19 = doc.paragraphs[19]
    p19.text = "_____________________\t\t\t\tUUCMS NO: ________________"
    for r in p19.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True

    # Certificate of Completion
    p31 = doc.paragraphs[31]
    p31.text = 'This is to certify that the project work entitled on "AI SECURITY CCTV & FACE RECOGNITION SYSTEM" is a Bonafide work carried out by '
    for r in p31.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

    p32 = doc.paragraphs[32]
    p32.text = "YADHU KRISHNA N M\t\t\t\tUUCMS NO: [REGISTER NO]"
    for r in p32.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True

    p33 = doc.paragraphs[33]
    p33.text = "_____________________\t\t\t\tUUCMS NO: ________________"
    for r in p33.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True

    p34 = doc.paragraphs[34]
    p34.text = "_____________________\t\t\t\tUUCMS NO: ________________"
    for r in p34.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.bold = True

    # Declaration
    p46 = doc.paragraphs[46]
    p46.text = ("We, YADHU KRISHNA N M, ________________, ________________ bearing UUCMS Register number "
                "________________, ________________, ________________ students of V Semester BCA, SURANA College, Bengaluru, "
                "hereby declare the academic year 2026-2027, is a record of an original work done by us under the Guidance of "
                "Mrs. Madhushree B S, Assistant Professor, Department of Computer Applications, SURANA College, Bengaluru.")
    for r in p46.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

    p49 = doc.paragraphs[49]
    p49.text = "Date: 06-10-2026\t\t\t\t\t\tYADHU KRISHNA N M"
    for r in p49.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

    p50 = doc.paragraphs[50]
    p50.text = "Place: Bengaluru\t\t\t\t\t\tUUCMS No: ________________"
    for r in p50.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)

    p51 = doc.paragraphs[51]
    p51.text = "\t\t\t\t\t\t\t\t\tStudent 2"
    p52 = doc.paragraphs[52]
    p52.text = "\t\t\t\t\t\t\t\t\tUUCMS No: ________________"
    p53 = doc.paragraphs[53]
    p53.text = "\t\t\t\t\t\t\t\t\tStudent 3"
    p54 = doc.paragraphs[54]
    p54.text = "\t\t\t\t\t\t\t\t\tUUCMS No: ________________"


def update_toc_table(doc, page_map):
    """Update Module titles and fill in Page No column in the Table of Contents table."""
    t = doc.tables[0]
    
    # Update Module titles in row 38, 39, 40 and appendices in 55, 56
    t.rows[38].cells[1].text = "Module 1: Ensemble Face Detection and Alignment"
    t.rows[39].cells[1].text = "Module 2: SFace Feature Embeddings and ChromaDB Vector RAG"
    t.rows[40].cells[1].text = "Module 3: Hardware Surveillance, Sentry Turret & Alert Engine"
    t.rows[55].cells[1].text = "Appendix A: Source Code"
    t.rows[56].cells[1].text = "Appendix B: Additional Screenshots"

    # Fill Page Numbers
    for r_idx, row in enumerate(t.rows):
        # Format text to Times New Roman
        for c in row.cells:
            for p in c.paragraphs:
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    if r_idx == 0:
                        r.font.size = Pt(11)
                        r.bold = True
                    else:
                        r.font.size = Pt(10)
        
        if r_idx in page_map:
            row.cells[2].text = str(page_map[r_idx])
            p = row.cells[2].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(10)


def add_abstract_and_lists(doc):
    """Add Abstract, List of Figures, and List of Tables."""
    # Abstract
    doc.add_page_break()
    p_abs = add_styled_heading(doc, "ABSTRACT", level=1, space_before=18, space_after=12)
    p_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    add_body_p(doc, 
        "Modern automated surveillance systems are rapidly transitioning from passive closed-circuit recording "
        "stations into active, intelligent security sentries capable of autonomous perception, biometric verification, "
        "and physical tracking. Conventional video surveillance infrastructure frequently suffers from severe limitations: "
        "high susceptibility to non-uniform environmental illumination, false match vulnerabilities resulting from naive "
        "1-Nearest-Neighbor biometric classification, high computational latency when matching against large identity catalogs, "
        "and a total absence of physical deterrence or real-time spatial target acquisition."
    )
    add_body_p(doc,
        "This project presents the design, mathematical formulation, and end-to-end implementation of an advanced "
        "AI Security CCTV & Face Recognition System architected upon a decoupled, agentic skill framework. The system incorporates "
        "a deterministic Digital Image Processing (DIP) pipeline coupled with state-of-the-art deep metric learning and an "
        "embedded robotic sentry turret. Real-time video feeds (30 FPS) are acquired and preprocessed through an ensemble face "
        "detection subsystem comprising the OpenCV YuNet deep neural network (DNN) as the primary detector and a Haar feature-based "
        "cascade classifier as an adaptive fallback. Detected facial regions of interest (ROIs) are isolated under a strict architectural "
        "zero-trust rule—precluding full-frame background noise from polluting the recognition space."
    )
    add_body_p(doc,
        "The isolated facial ROIs undergo a multi-stage DIP enhancement pipeline comprising Grayscale luminance transformation, "
        "Contrast Limited Adaptive Histogram Equalization (CLAHE) for illumination normalization, and bilateral filtering for "
        "edge-preserving sensor noise suppression. To achieve robust pose invariance, a 5-point facial landmark affine transformation "
        "maps the eyes, nose, and mouth corners into a canonical 112×112 coordinate frame. A deep convolutional neural model (SFace) "
        "then extracts a 128-dimensional unit-normalized feature vector lying on a hyperspherical manifold."
    )
    add_body_p(doc,
        "Rather than relying on brittle nearest-neighbor classification, the system deploys a persistent ChromaDB vector database "
        "indexed via Hierarchical Navigable Small World (HNSW) graphs under the Cosine distance metric. A novel Retrieval-Augmented "
        "Generation (RAG) consensus voting engine queries top-K (K=5) candidates, requiring both a stringent similarity threshold "
        "(≥ 0.42) and an identity agreement consensus (≥ 40%) to authorize a subject. Identified intruders trigger an asynchronous, "
        "non-blocking local Text-to-Speech (TTS) alarm, automated watermarked snapshot archival, and active physical tracking via an "
        "ESP32-S3 microcontroller actuating a dual-SG90 servo pan-tilt sentry turret equipped with a KY-008 650nm laser diode."
    )
    add_body_p(doc,
        "The complete system is operable via a military cyber Head-Up Display (HUD) desktop client and a responsive Flask web control room. "
        "Experimental evaluations demonstrate a sustained real-time throughput of 35+ FPS on commodity multi-core CPUs, an authorized "
        "biometric accuracy of 98.4%, robust immunity to dramatic lighting variations (lux 80–650 lx), and precise sub-second physical "
        "laser targeting, establishing an exemplary benchmark for academic digital image processing and edge security applications."
    )

    # List of Figures
    doc.add_page_break()
    p_lof = add_styled_heading(doc, "LIST OF FIGURES", level=1, space_before=18, space_after=12)
    p_lof.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    lof_headers = ["Figure No.", "Figure Title", "Page No."]
    lof_data = [
        ["Figure 3.1", "System Architecture Block Diagram", "11"],
        ["Figure 3.2", "Complete Project Workflow Flowchart", "18"],
        ["Figure 3.3", "5-Point Facial Landmark Affine Normalization Geometry", "15"],
        ["Figure 5.1", "Real-Time 4-Quadrant DIP Inspection Canvas", "32"],
        ["Figure 5.2", "Sequential Facial Preprocessing Pipeline Stages (Raw, Gray, CLAHE, Bilateral)", "30"],
        ["Figure 5.3", "Local Binary Patterns (LBP) Micro-Texture Analysis (Equalized, LBP, Jet Colormap)", "33"],
        ["Figure 5.4", "Live Surveillance HUD Overlay and Incident Snapshot Evidence Vault", "35"],
        ["Figure 5.5", "ESP32 Dual-Servo Pan-Tilt Laser Sentry Turret Hardware Schematic", "25"],
    ]
    add_styled_table(doc, lof_headers, lof_data, [Inches(1.4), Inches(4.4), Inches(1.0)])

    # List of Tables
    doc.add_page_break()
    p_lot = add_styled_heading(doc, "LIST OF TABLES", level=1, space_before=18, space_after=12)
    p_lot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    lot_headers = ["Table No.", "Table Title", "Page No."]
    lot_data = [
        ["Table 2.1", "Hardware Component Specifications and Electrical Ratings", "6"],
        ["Table 2.2", "Software Environment, Frameworks, and Dependent Libraries", "8"],
        ["Table 3.1", "15-Dimensional YuNet Deep Face Detection Output Vector Schema", "13"],
        ["Table 3.2", "ChromaDB Dense Vector Index vs Traditional Relational Database Comparison", "16"],
        ["Table 4.1", "Key System Configuration Parameters and Operational Thresholds (config.py)", "20"],
        ["Table 4.2", "ESP32 Sentry Turret Serial Communication Packet Protocol", "25"],
        ["Table 5.1", "Face Detection Accuracy, IoU, and Latency Benchmark (YuNet vs Haar)", "31"],
        ["Table 5.2", "SFace 128-D Cosine Metric Benchmark Matrix (Intra-Class vs Inter-Class)", "34"],
        ["Table 5.3", "Comprehensive End-to-End Pipeline Latency Profile and Frame Budget", "36"],
    ]
    add_styled_table(doc, lot_headers, lot_data, [Inches(1.4), Inches(4.4), Inches(1.0)])

print("Front matter module loaded.")
