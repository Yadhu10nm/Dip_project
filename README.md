# 🛡️ AI Security CCTV & Face Recognition System
### Modular Agentic Skill Architecture with YuNet DNN, SFace Embeddings, ChromaDB & RAG Consensus

An enterprise-grade, modular, agentic surveillance station built with **Python**, **OpenCV**, **YuNet DNN Face Detection**, **SFace Facial Metric Embeddings**, **ChromaDB Vector Database (HNSW Cosine)**, **Retrieval-Augmented Generation (RAG) Consensus Voting**, **Flask**, and asynchronous local **TTS** (`pyttsx3`).

---

## 📑 Table of Contents
1. [Core Principle & Vision Pipeline](#-1-core-principle--vision-pipeline)
2. [Agentic Skill Architecture](#-2-agentic-skill-architecture)
3. [How It Works (Technical Deep Dive)](#-3-how-it-works-technical-deep-dive)
4. [Strict Security Rules](#-4-strict-security-rules)
5. [Prerequisites & Installation](#-5-prerequisites--installation)
6. [How to Execute the Project](#-6-how-to-execute-the-project)
7. [Configuration Reference (config.py)](#-7-configuration-reference-configpy)
8. [REST API Documentation](#-8-rest-api-documentation)
9. [Running Automated Tests](#-9-running-automated-tests)

---

## 🏗️ 1. Core Principle & Vision Pipeline

The system processes real-time camera frames through a deterministic, strictly segregated computer vision and retrieval pipeline:

```text
                     WEBCAM / CCTV STREAM
                              ↓
              FRAME ACQUISITION (camera_skill)
                              ↓
      ENSEMBLE FACE DETECTION: YuNet DNN + Haar Fallback
                   (face_detection_skill)
                              ↓
               FACE ROI CROPPING & MARGIN PADDING
                   (face_preprocessing_skill)
                              ↓
        5-POINT FACIAL LANDMARK AFFINE ALIGNMENT & SFACE
                    (face_embedding_skill)
                              ↓
           CHROMADB HNSW COSINE DENSE VECTOR SEARCH
                   (vector_database_skill)
                              ↓
        TOP-K RAG CONSENSUS VOTING & EVIDENCE TRACKING
                   (face_recognition_skill)
                              ↓
             CENTRAL ORCHESTRATION & ACCESS DECISION
                      (system_orchestrator)
                              ↓
      ┌───────────────────────┬────────────────────────┬───────────────────────┐
      │  Authorized Personnel │  Locate Person Search  │  Intruder / Stranger  │
      └───────────────────────┴────────────────────────┴───────────────────────┘
                  ↓                       ↓                        ↓
             Emerald HUD              Amber Reticle            Red Warning
                  ↓                       ↓                        ↓
             Audit Record         State-Change TTS         Audio Alarm + Snap
```

### 🚨 Strict Rule:
> **ONLY HUMAN FACE REGIONS may enter the recognition pipeline.**  
> Never generate embeddings from full CCTV frames or arbitrary objects. The embedding engine accepts exclusively localized face crops produced by the face detection pipeline.

---

## 🧩 2. Agentic Skill Architecture

The system is organized into **19 self-contained, decoupled, discoverable skills**. Every skill contains its own `SKILL.md` specification, `implementation/`, `tests/`, and `examples/`:

```text
skills/
├── common/                     # EventBus pub/sub and dataclasses (FaceDetection, RecognitionResult, etc.)
├── camera_skill/               # Hardware acquisition, frame rate throttling, mirror inversion
├── face_detection_skill/       # YuNet DNN primary detector + Haar Cascade multi-scale fallback
├── face_preprocessing_skill/   # Margin padding, canonical resizing, illumination normalization
├── face_embedding_skill/       # 5-point landmark affine alignment & 128-D SFace unit vector extraction
├── vector_database_skill/      # Persistent ChromaDB HNSW Cosine vector store with RAG search & auto-sync
├── face_recognition_skill/     # RAG consensus classifier, explainable evidence & threshold verification
├── person_locator_skill/       # Target search, pinpoint tracking, and multi-face spatial resolution
├── command_skill/              # Natural language command parser (e.g., "locate Yadhu", "toggle DIP")
├── surveillance_skill/         # Multi-face end-to-end vision pipeline coordinator
├── alert_skill/                # Intruder breach detection & state debouncing
├── tts_skill/                  # Asynchronous, non-blocking local speech synthesis worker
├── evidence_skill/             # Watermarked incident snapshot vault with duplicate suppression
├── hud_skill/                  # Military/cyber surveillance HUD with target reticles & laser callouts
├── dip_inspector_skill/        # Educational 4-quadrant pipeline inspector (Raw, Gray, CLAHE, LBP)
├── enrollment_skill/           # Strict single-face enrollment (0 reject, 1 accept, 2+ reject)
├── audit_skill/                # Persistent JSON audit logging of all security events
├── web_dashboard_skill/        # Flask cyber control room with MJPEG streaming & locate interface
├── desktop_ui_skill/           # Native OpenCV desktop window with interactive hotkeys
└── system_orchestrator/        # Central event-driven coordinator & application state manager
```

---

## 🔬 3. How It Works (Technical Deep Dive)

### A. Ensemble Multi-Face Detection
- **Primary Detector**: OpenCV **YuNet DNN** (`cv2.FaceDetectorYN`). Highly resilient to arbitrary head pitch, roll, yaw, low lighting, and facial occlusions. Computes 15 values: 4-D bounding box `(x, y, w, h)`, 5 facial landmarks `(x, y)` for both eyes, nose tip, and mouth corners, plus confidence score.
- **Fallback Detector**: Classical **Haar Feature Cascade Classifier** with adaptive CLAHE contrast enhancement for low-resource environments.

### B. 5-Point Landmark Affine Alignment & SFace Embedding
- To achieve high intra-person similarity (>0.75) and low inter-person similarity (<0.18), the face crop is normalized using **OpenCV's affine transformation** (`cv2.FaceRecognizerSF.alignCrop`).
- Eyes and mouth are aligned to exact canonical coordinates within a canonical `(112, 112)` frame.
- **SFace** extracts a **128-dimensional unit-normalized feature vector** ($\|v\|_2 = 1.0$).

### C. RAG-Based Vector Search & Consensus Scoring
Instead of naive 1-Nearest-Neighbor matching, the system executes **Retrieval-Augmented Generation (RAG)**:
1. **Dense Retrieval**: Retrieves top-$K$ ($K=5$) nearest neighbors from ChromaDB using Cosine distance:
   $$\text{Similarity} = 1.0 - \text{Cosine Distance}$$
2. **Identity Clustering & Consensus Voting**: Matches are grouped by `person_id`.
   $$\text{Consensus Ratio} = \frac{\text{Candidate Hits in Top-}K}{K}$$
3. **Decision Verification**: A subject is marked **Authorized** if and only if:
   $$\text{Similarity}_{\max} \ge 0.42 \quad \text{AND} \quad \text{Consensus Ratio} \ge 0.40$$
   Otherwise, the subject is classified as **Unknown / Unauthorized Intruder**.
4. **Explainable Evidence**: Every recognition result includes documentary evidence containing matched sample IDs, distances, and individual similarities.

### D. Active Person Locator & State-Change Audio
- The system continuously scans all detected faces in the scene for a target requested by the user.
- **Debounced Audio Feedback**:
  - Target appears $\implies$ Speaks *"Target located"* **once**.
  - Target stays in frame $\implies$ Silent visual tracking (prevents audio chatter).
  - Target leaves frame $\implies$ Speaks *"Target not found"* **once**.

---

## 📜 4. Strict Security Rules

1. **Rule 1**: Only human face regions may enter the recognition pipeline.
2. **Rule 2**: Never generate embeddings from a full CCTV frame or non-face objects.
3. **Rule 3**: Never enroll an image containing multiple faces (exactly 1 face required; 0 or 2+ rejected).
4. **Rule 4**: Process each detected face independently in multi-face scenes.
5. **Rule 5**: Never authorize an identity below the configured threshold (`FACE_MATCH_THRESHOLD = 0.42`).
6. **Rule 6**: Audio alarms and TTS notifications must respect configured cooldown timers.
7. **Rule 7**: Suppress duplicate incident snapshots during ongoing security breaches.

---

## 💻 5. Prerequisites & Installation

### Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: Version `3.10`, `3.11`, or `3.12`
- **Camera**: Standard USB Webcam, Built-in Camera, or RTSP CCTV stream

### Step-by-Step Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd dip_project_demo
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Model Verification**:
   The required pre-trained ONNX models (`face_detection_yunet_2023mar.onnx` and `face_recognition_sface_2021dec.onnx`) are automatically downloaded from OpenCV Zoo on the very first startup into `data/models/`.

---

## 🚀 6. How to Execute the Project

### Execution Mode 1: Web Surveillance Dashboard (Recommended)

Launch the full web-based surveillance command center:
```bash
python main.py --mode web --port 5000
```
*(Alternatively: `python -m web.app`)*

Open your browser to:
```text
http://127.0.0.1:5000
```

#### Web Dashboard Features:
- **Live Video Feed**: Low-latency MJPEG video stream with tactical cyber HUD.
- **Locate Person Card**: Type a name (e.g. `yadhu` or `amith`) to track them with laser pointer graphics and voice updates.
- **Authorized Whitelist**: View registered personnel, their enrollment sample counts, and photo thumbnails.
- **Photo Upload & Camera Enrollment**: Register new personnel with instant ChromaDB vector indexing.
- **Intrusion Log & Evidence Vault**: Real-time intruder breach log with captured snapshot thumbnails.
- **Controls**: Toggle Voice Alerts, Flip Camera Mirroring, and toggle the 4-quadrant DIP Inspector.

---

### Execution Mode 2: Desktop CCTV HUD (Native OpenCV Window)

Launch the native desktop OpenCV GUI:
```bash
python main.py --mode desktop
```
*(Alternatively: `python desktop_app.py`)*

#### Desktop Keyboard Hotkeys:
| Key | Action |
|:---:|:---|
| `[R]` | **Register User**: Captures rapid face burst from webcam and indexes to ChromaDB. |
| `[D]` | **Toggle DIP Mode**: Switches between Tactical HUD and 4-Quadrant DIP view. |
| `[S]` | **Toggle Sound**: Mutes or un-mutes TTS voice announcements. |
| `[F]` | **Toggle Flip**: Mirrors the camera feed horizontally. |
| `[L]` | **Show Audit Log**: Prints the most recent security events to the console. |
| `[Q]` / `[ESC]` | **Quit**: Releases the camera and exits safely. |

---

### Execution Mode 3: Standalone Multi-Face & RAG Verification

Execute a headless verification test on real dataset composite images:
```bash
python -c "import sys; sys.path.insert(0, '.'); from scratch.verify_multiface_rag import run_multiface_rag_verification; run_multiface_rag_verification()"
```

---

## ⚙️ 7. Configuration Reference (`config.py`)

All parameters can be customized directly in `config.py` or through environment variables:

| Variable | Default | Description |
|:---|:---:|:---|
| `CAMERA_INDEX` | `0` | Default video capture device index (0 for default webcam). |
| `FRAME_WIDTH` | `640` | Captured frame width in pixels. |
| `FRAME_HEIGHT` | `480` | Captured frame height in pixels. |
| `CAMERA_FLIP` | `True` | Horizontally mirror webcam feed. |
| `USE_YUNET_PRIMARY` | `True` | Use YuNet DNN face detector as primary. |
| `YUNET_CONFIDENCE_THRESHOLD` | `0.6` | Minimum face detection score threshold. |
| `FACE_MATCH_THRESHOLD` | `0.42` | Calibrated SFace cosine similarity threshold for access. |
| `RAG_TOP_K` | `5` | Number of nearest neighbors retrieved from ChromaDB. |
| `RAG_MIN_CONSENSUS` | `0.40` | Minimum consensus fraction of top-k (e.g. 2 out of 5). |
| `ENABLE_VOICE_ALERT` | `True` | Enable spoken alerts for intrusions and target tracking. |
| `TTS_COOLDOWN_SECONDS` | `7.0` | Minimum interval between voice announcements. |
| `INTRUDER_SNAPSHOT_COOLDOWN`| `10.0` | Minimum interval between incident snapshot captures. |

---

## 📡 8. REST API Documentation

The Web Dashboard exposes a REST API for remote integration:

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/video_feed` | Multipart MJPEG live video stream. |
| `GET` | `/api/status` | System telemetry (FPS, face count, authorized count, target). |
| `POST` | `/api/command` | Dispatches command string (e.g. `{"command": "locate yadhu"}`). |
| `POST` | `/api/toggle_dip` | Toggles 4-Quadrant DIP view on/off. |
| `POST` | `/api/toggle_voice` | Toggles speech synthesis on/off. |
| `POST` | `/api/toggle_flip` | Toggles horizontal camera mirroring. |
| `GET` | `/api/users` | Lists registered authorized users. |
| `POST` | `/api/users` | Registers a new authorized user profile. |
| `POST` | `/api/upload_photos`| Uploads image files to extract embeddings into ChromaDB. |
| `GET` | `/api/intruders` | Retrieves recent security breach logs. |
| `POST` | `/api/clear_intruders`| Clears the security incident audit log. |

---

## 🧪 9. Running Automated Tests

Run the comprehensive automated test suite with `pytest`:
```bash
pytest tests/
```

### Test Coverage Summary:
- **`test_face_detection.py`**: YuNet DNN multi-face detection, Haar fallback, and bounding box resolution.
- **`test_preprocessing.py`**: Face ROI cropping, padding margins, and landmark translation.
- **`test_embedding.py`**: 128-D SFace feature extraction, unit normalization, and fallback descriptors.
- **`test_vector_database.py`**: ChromaDB upsert, delete, HNSW cosine search, and RAG consensus.
- **`test_recognition.py`**: Authorized classification, unknown rejection, and multi-identity matching.
- **`test_locator.py`**: Person Locator target resolution and non-existent target handling.
- **`test_enrollment.py`**: Single-face constraint verification (0 reject, 1 accept, 2+ reject).
- **`test_evidence.py`**: Snapshot storage, incident watermarking, and cooldown throttling.
- **`test_tts.py`**: Thread-safe audio generation and debouncing.
- **`test_commands.py`**: Natural language command parsing.
- **`test_orchestrator.py`**: End-to-end vision loop and state dispatching.
- **`test_dip_pipeline.py`**: Digital image processing transforms (Grayscale, CLAHE, Bilateral, LBP).
