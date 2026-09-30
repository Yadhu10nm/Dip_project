# Tech Stack

## Overview
This project is a Python-based AI security surveillance system that combines computer vision, digital image processing, and a lightweight web dashboard to detect, classify, and monitor authorized versus unauthorized people in real time.

## Core Technologies

### 1. Programming Language
- Python 3
- Used for the full application pipeline, model training, webcam processing, alert logic, and web services.

### 2. Computer Vision & Image Processing
- OpenCV (`opencv-contrib-python`)
- Core vision library used for:
  - webcam capture
  - frame manipulation
  - face detection
  - image preprocessing
  - drawing overlays and HUD graphics
  - MJPEG streaming
- NumPy
  - used for efficient image array operations and feature extraction

### 3. Face Detection & Recognition
- Haar Cascade Classifier
  - used for face localization in each video frame
- ChromaDB Vector Store & 128-D Facial Feature Embeddings
  - primary recognition engine using persistent HNSW collection with Cosine distance metric
  - converts face images to 128-dimensional unit-normalized embeddings
  - performs fast Cosine Similarity nearest-neighbor classification
- Local Binary Patterns Histograms (LBPH)
  - secondary / dual recognition engine for micro-texture histogram matching
- Digital Image Processing (DIP) pipeline:
  - grayscale conversion
  - CLAHE illumination normalization
  - bilateral filtering
  - LBP spatial texture extraction
  - cosine similarity vector search
  - real-time camera feed inversion (`cv2.flip`)

### 4. Web Application
- Flask
  - powers the browser-based security dashboard
  - serves the UI, batch photo enrollment endpoints, and live camera stream
- HTML / CSS / JavaScript
  - dashboard frontend
  - real-time UI telemetry, multi-image upload wizard, and camera flip toggle

### 5. Audio & Alerts
- pyttsx3
  - text-to-speech engine used for security warnings
- system alert logic and chime notifications

### 6. Data Storage & Vector Databases
- ChromaDB (`chromadb`)
  - persistent vector store in `data/chroma_db/`
  - stores 128-D face embeddings with metadata for rapid Cosine Similarity matching
- JSON files
  - `authorized_users.json`
  - `audit_log.json`
- Filesystem-based user dataset & models
  - `data/dataset/`
  - `data/models/`
  - `data/intruders/`
  - `data/chroma_db/`

## Project Architecture

### Backend / Core Modules
- `config.py`
  - central configuration for camera settings, thresholds, and paths
- `core/dip_engine.py`
  - image processing operations
- `core/detector.py`
  - face detection logic
- `core/embedding_engine.py`
  - 128-D facial feature embedding extraction (SFace ONNX & DIP spatial texture fallback)
- `core/vector_store.py`
  - ChromaDB persistent vector storage & Cosine Similarity search
- `core/recognizer.py`
  - ChromaDB Cosine Similarity classification and LBPH dual-engine
- `core/access_manager.py`
  - user enrollment (webcam burst & batch images), dataset management, and ChromaDB sync
- `core/alert_system.py`
  - alerts, logging, and security snapshots
- `core/cctv_hud.py`
  - tactical overlay rendering for the live surveillance view
- `core/surveillance_system.py`
  - orchestrates capture, processing, recognition, and alert pipelines

### Interfaces
- `desktop_app.py`
  - standalone OpenCV-based desktop CCTV window
- `main.py`
  - app launcher for desktop/web modes
- `web/app.py`
  - Flask server and streaming endpoints
- `web/templates/index.html`
  - dashboard UI
- `web/static/css/style.css` and `web/static/js/app.js`
  - styling and frontend logic

## Dependency List
From `requirements.txt`:
- `opencv-contrib-python>=4.8.0`
- `numpy>=1.24.0`
- `Flask>=3.0.0`
- `pyttsx3>=2.90`
- `pillow>=9.5.0`

## Why This Stack
This combination is well-suited for a real-time CCTV and access-control prototype because it balances:
- fast local image processing with OpenCV
- reliable face detection and recognition using traditional CV techniques
- a simple browser UI using Flask
- lightweight local persistence with JSON and filesystem storage
- minimal infrastructure requirements for a demo or academic project

## Typical Runtime Flow
1. Camera captures a live frame.
2. The frame is processed through the DIP pipeline.
3. Face detection locates regions of interest.
4. LBPH recognition compares each face against enrolled personnel.
5. Authorized users are marked as valid; intruders trigger alerts.
6. The HUD and web dashboard display live security telemetry and status.

## Summary
The project uses a classic computer vision stack built around Python and OpenCV, enhanced with Flask for user interaction and pyttsx3 for audio alerts, making it a strong example of an AI-powered security and access-control system.
