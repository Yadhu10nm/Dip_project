import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_DIR = os.path.join(DATA_DIR, "dataset")
MODELS_DIR = os.path.join(DATA_DIR, "models")
INTRUDERS_DIR = os.path.join(DATA_DIR, "intruders")
EVIDENCE_DIR = os.path.join(DATA_DIR, "evidence")
USERS_FILE = os.path.join(DATA_DIR, "authorized_users.json")
AUDIT_LOG_FILE = os.path.join(DATA_DIR, "audit_log.json")
MODEL_FILE = os.path.join(MODELS_DIR, "lbph_model.yml")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")

# Ensure required directories exist
for directory in [DATA_DIR, DATASET_DIR, MODELS_DIR, INTRUDERS_DIR, EVIDENCE_DIR, CHROMA_DIR]:
    os.makedirs(directory, exist_ok=True)

# Camera Configuration
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "640"))
FRAME_HEIGHT = int(os.getenv("FRAME_HEIGHT", "480"))
TARGET_FPS = int(os.getenv("TARGET_FPS", "30"))
CAMERA_NAME = os.getenv("CAMERA_NAME", "CAM-01 [FRONT GATEWAY]")
CAMERA_FLIP = os.getenv("CAMERA_FLIP", "True").lower() in ("true", "1", "yes")
CAMERA_FLIP_CODE = int(os.getenv("CAMERA_FLIP_CODE", "1"))  # 1: Horizontal mirror, 0: Vertical, -1: Both

# Face Detection Configuration (Ensemble: Deep YuNet Primary + Haar Fallback)
YUNET_MODEL_PATH = os.getenv("YUNET_MODEL_PATH", os.path.join(MODELS_DIR, "face_detection_yunet_2023mar.onnx"))
YUNET_CONFIDENCE_THRESHOLD = float(os.getenv("YUNET_CONFIDENCE_THRESHOLD", "0.6"))
USE_YUNET_PRIMARY = os.getenv("USE_YUNET_PRIMARY", "True").lower() in ("true", "1", "yes")

FACE_MIN_SIZE = (45, 45)
HAAR_SCALE_FACTOR = 1.10
HAAR_MIN_NEIGHBORS = 4
STANDARD_FACE_SIZE = (200, 200)
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# ChromaDB & RAG-Based Vector Search Configuration
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "authorized_faces")
RAG_ENABLED = True
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_MIN_CONSENSUS = float(os.getenv("RAG_MIN_CONSENSUS", "0.40"))  # At least 40% of top-k must agree on identity
FACE_MATCH_THRESHOLD = float(os.getenv("FACE_MATCH_THRESHOLD", "0.42"))  # SFace landmark-calibrated threshold
COSINE_SIMILARITY_THRESHOLD = FACE_MATCH_THRESHOLD  # Backward compatibility alias
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", os.path.join(MODELS_DIR, "face_recognition_sface.onnx"))
RECOGNITION_BACKEND = os.getenv("RECOGNITION_BACKEND", "chroma_rag")  # "chroma_rag", "chroma_cosine", or "lbph"

# Local Binary Patterns Histograms (LBPH) Parameters (Dual Engine / Fallback)
LBPH_RADIUS = 1
LBPH_NEIGHBORS = 8
LBPH_GRID_X = 8
LBPH_GRID_Y = 8
RECOGNITION_THRESHOLD = 68.0

# Access Control & Enrollment Configuration
SAMPLES_PER_USER = int(os.getenv("SAMPLES_PER_USER", "25"))
ENROLLMENT_REQUIRE_EXACTLY_ONE_FACE = True

# Alert, TTS & Security Notifications
ENABLE_VOICE_ALERT = os.getenv("ENABLE_VOICE_ALERT", "True").lower() in ("true", "1", "yes")
ENABLE_AUDIO_CHIME = os.getenv("ENABLE_AUDIO_CHIME", "True").lower() in ("true", "1", "yes")
TTS_COOLDOWN_SECONDS = float(os.getenv("TTS_COOLDOWN_SECONDS", "7.0"))
ALERT_COOLDOWN_SECONDS = TTS_COOLDOWN_SECONDS
INTRUDER_SNAPSHOT_COOLDOWN = float(os.getenv("INTRUDER_SNAPSHOT_COOLDOWN", "10.0"))

# Locator Configuration
PERSON_LOCATOR_TIMEOUT = float(os.getenv("PERSON_LOCATOR_TIMEOUT", "10.0"))
