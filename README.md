# 🛡️ AI Security CCTV — Unauthorized Intruder Detection & Access Control System
### Digital Image Processing (DIP) & Computer Vision Project

An automated **Security CCTV Surveillance Station** built with Python and OpenCV. The system monitors the laptop webcam in real time, classifies individuals as **Authorized** or **Unauthorized (Intruders)**, points them out on-screen with tactical targeting reticles, announces audible voice security warnings, and provides full administrative access control to whitelist personnel.

---

## 📸 Key Features

- **Live Tactical CCTV Feed**: Authentic security surveillance HUD featuring `[● REC]` indicator, camera tag (`CAM-01 [FRONT GATEWAY]`), live timestamp, FPS telemetry, and threat alert banners.
- **Real-Time Target Point-Out**:
  - **Unauthorized Intruder**: Locked onto with flashing **RED** corner brackets, circular targeting reticle, threat callout banner, and laser-style pointing line pointing out the intruder's face in the live video.
  - **Authorized Personnel**: Marked with tactical **GREEN** brackets and verified identity badges (`[ACCESS GRANTED: Name]`).
- **Audible Security Warnings**: Multi-threaded, non-blocking voice announcements using `pyttsx3` (*"Warning! Security alert! Unauthorized person detected on camera one!"*) plus acoustic security chimes.
- **Evidence Vault (Incident Logger)**: Automatically captures high-resolution photographic evidence of unauthorized intruders with timestamps and logs them to the audit database.
- **Access Control Whitelist**:
  - Add authorized individuals via rapid webcam capture (auto-bursts 25 face samples across head angles) or photo upload.
  - View authorized personnel records with photo thumbnails.
  - Revoke/delete access with 1-click automatic model retraining.
- **DIP Educational Pipeline Inspector**: 4-quadrant split-screen mode visually demonstrating the step-by-step image processing stages (Raw BGR $\to$ Grayscale $\to$ CLAHE $\to$ LBP Texture Map).
- **Dual Interface**:
  - **Web Dashboard**: Modern cyber-security control room accessible via any browser (`http://localhost:5000`).
  - **Standalone Desktop HUD**: High-framerate OpenCV window with keyboard shortcuts (`R`, `D`, `S`, `L`, `Q`).

---

## 🔬 Digital Image Processing (DIP) Pipeline

```
[Webcam BGR Frame]
        │
        ▼ (Stage 1)
[Grayscale Conversion] ──> Eliminates chrominance redundancy; extracts luminance Y-channel
        │
        ▼ (Stage 2)
[CLAHE Illumination Normalization] ──> Equalizes local contrast; handles shadows and backlighting
        │
        ▼ (Stage 3)
[Haar Cascade Localization] ──> Integral image feature detection to locate facial Region of Interest (ROI)
        │
        ▼ (Stage 4)
[Bilateral Noise Filtering] ──> Smooths sensor noise while preserving sharp edge boundaries
        │
        ▼ (Stage 5)
[Local Binary Patterns (LBP)] ──> Extracts 8-neighbor micro-texture histograms:
                                  LBP(x_c, y_c) = Σ s(i_p - i_c) * 2^p
        │
        ▼ (Stage 6)
[Chi-Square Distance Classification]
        │
   ┌────┴──────────────────────────┐
   ▼                               ▼
Distance <= 68.0             Distance > 68.0
[AUTHORIZED PERSONNEL]       [UNAUTHORIZED INTRUDER]
Green Reticle                Red Reticle + Voice Alert + Snapshot
```

---

## 📁 Project Structure

```
c:\dip_project_demo\
├── config.py                 # Central configuration (thresholds, camera ID, paths)
├── core/
│   ├── dip_engine.py         # Grayscale, CLAHE, Bilateral filtering, LBP map generation
│   ├── detector.py           # Haar Cascade face detector with CLAHE enhancement
│   ├── recognizer.py         # LBPH model training, serialization, and distance prediction
│   ├── access_manager.py     # Whitelist database, webcam sample capture, auto-retraining
│   ├── alert_system.py       # Threaded voice warnings (pyttsx3), chimes, snapshot logger
│   ├── cctv_hud.py           # Tactical HUD overlay, targeting reticles, intruder pointer
│   └── surveillance_system.py# Main pipeline orchestrator connecting all modules
├── web/
│   ├── app.py                # Flask server, MJPEG streaming, REST API endpoints
│   ├── templates/index.html  # Cyber CCTV surveillance web dashboard
│   └── static/
│       ├── css/style.css     # Dark mode tactical security styling
│       └── js/app.js         # Real-time state polling & enrollment wizard
├── desktop_app.py            # Standalone OpenCV HUD window with hotkeys
├── main.py                   # Master entry point launcher
├── tests/
│   └── test_dip_pipeline.py  # Automated unit test suite
├── data/
│   ├── dataset/              # Enrolled face samples organized by User ID
│   ├── models/               # Serialized LBPH model (lbph_model.yml) & label map
│   ├── authorized_users.json # Personnel database
│   └── intruders/            # Saved intruder evidence snapshots
├── requirements.txt          # Python dependencies
└── README.md                 # Complete documentation
```

---

## 🚀 Quick Start Guide

### 1. Requirements
Ensure your Python environment has the required packages:
```bash
pip install -r requirements.txt
```

### 2. Launch Web Surveillance Dashboard (Recommended)
```bash
python main.py --mode web
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### 3. Launch Standalone Desktop OpenCV Window
```bash
python main.py --mode desktop
```

**Desktop Hotkeys**:
- `[R]`: Register a new authorized person (launches webcam sample capture).
- `[D]`: Toggle DIP Pipeline Inspector (4-Quadrant view).
- `[S]`: Toggle Voice/Sound Alert on or off.
- `[L]`: Print recent intrusion logs in terminal.
- `[Q]` or `[ESC]`: Exit.

---

## 🎓 How to Demonstrate for Project Evaluation / Viva

1. **Initial State (Intruder Detection)**:
   - Start the system before registering any faces.
   - Look into the camera: The system immediately detects your face, flags you in **RED** with `[!] UNAUTHORIZED PERSON`, draws the targeting reticle with pointing callout line, sounds an audible voice alert (*"Warning! Security alert! Unauthorized person detected on camera one!"*), and saves an incident snapshot.
2. **Access Control Enrollment (Whitelist)**:
   - Click **"Whitelist Person"** (or press `R` in Desktop mode).
   - Enter your name (e.g. *"Student / Yadhu"*).
   - Click **"Capture 25 Face Samples (Auto-Burst)"**. Look into the webcam while slightly moving your head.
   - The system captures 25 preprocessed samples and retrains the LBPH model in under 2 seconds.
3. **Verified Access**:
   - Look into the webcam again: The bounding box instantly turns **GREEN**, displaying `[ACCESS GRANTED: Student / Yadhu]`, Match Confidence (e.g. `92.4%`), and silent confirmation.
4. **DIP Pipeline Demonstration**:
   - Click **"DIP Inspector (4-Way)"** (or press `D`).
   - The screen splits into 4 live quadrants:
     - **Quad 1**: Raw BGR Sensor Feed.
     - **Quad 2**: Grayscale Luminance Map ($Y$-channel).
     - **Quad 3**: CLAHE Local Contrast Enhancement.
     - **Quad 4**: LBP (Local Binary Patterns) Micro-Texture Map in pseudo-color.
   - Explain to the examiner how each stage contributes to robust facial recognition under changing lighting!
5. **Revocation & Evidence Audit**:
   - Check the **"Intruders"** tab to view saved snapshot evidence with timestamps.
   - Click the delete icon on an authorized user to revoke their access; verify that the system immediately reverts to marking them as an unauthorized intruder.

---

## 🧠 Common DIP Viva Questions & Answers

**Q1: Why is CLAHE used instead of standard Global Histogram Equalization?**
> *Answer*: Standard histogram equalization computes a global transfer function across the entire image. If an image has bright backgrounds or localized shadows, global equalization over-amplifies noise and washes out facial features. CLAHE divides the image into contextual tiles ($8 \times 8$), equalizes each tile adaptively, and clips high histogram bins (clip limit $2.5$) before using bilinear interpolation to eliminate tile boundary artifacts.

**Q2: What is the mathematical formulation of Local Binary Patterns (LBP)?**
> *Answer*: For a center pixel $(x_c, y_c)$ with intensity $i_c$ and $P$ circularly distributed neighbors at radius $R$:
> $$\text{LBP}_{P, R}(x_c, y_c) = \sum_{p=0}^{P-1} s(i_p - i_c) \cdot 2^p \quad \text{where } s(x) = \begin{cases} 1 & x \ge 0 \\ 0 & x < 0 \end{cases}$$
> This produces an 8-bit invariant descriptor representing micro-edges, corners, and texture spots.

**Q3: Why is LBPH robust against illumination variations?**
> *Answer*: LBP relies only on the sign of the difference between neighboring pixels ($i_p \ge i_c$). Any monotonic shift in illumination (e.g. overall dimming or brightening) preserves the relative ordering of pixel intensities, leaving the binary pattern unchanged.

**Q4: How does the system distinguish between Authorized and Unauthorized persons?**
> *Answer*: The facial ROI's extracted LBP histogram is compared against registered authorized histograms using the Chi-Square ($\chi^2$) distance metric:
> $$\chi^2(H_1, H_2) = \sum_{i} \frac{(H_1(i) - H_2(i))^2}{H_1(i) + H_2(i)}$$
> If $\chi^2 \le 68.0$, identity is confirmed as Authorized. If $\chi^2 > 68.0$, the person does not match any enrolled personnel and is classified as an Unauthorized Intruder.
