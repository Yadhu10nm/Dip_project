import os

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_DIR = os.path.join(DATA_DIR, "dataset")
MODELS_DIR = os.path.join(DATA_DIR, "models")
INTRUDERS_DIR = os.path.join(DATA_DIR, "intruders")
USERS_FILE = os.path.join(DATA_DIR, "authorized_users.json")
AUDIT_LOG_FILE = os.path.join(DATA_DIR, "audit_log.json")
MODEL_FILE = os.path.join(MODELS_DIR, "lbph_model.yml")

# Ensure directories exist
for directory in [DATA_DIR, DATASET_DIR, MODELS_DIR, INTRUDERS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Camera Configuration
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 30
CAMERA_NAME = "CAM-01 [FRONT GATEWAY]"

# DIP & Face Detection Configuration
FACE_MIN_SIZE = (60, 60)
HAAR_SCALE_FACTOR = 1.15
HAAR_MIN_NEIGHBORS = 5
STANDARD_FACE_SIZE = (200, 200)

# Local Binary Patterns Histograms (LBPH) Parameters
LBPH_RADIUS = 1
LBPH_NEIGHBORS = 8
LBPH_GRID_X = 8
LBPH_GRID_Y = 8

# Recognition Threshold (LBPH distance: lower means closer match)
# Matches <= RECOGNITION_THRESHOLD are considered AUTHORIZED
# Matches > RECOGNITION_THRESHOLD are classified as UNAUTHORIZED INTRUDER
RECOGNITION_THRESHOLD = 68.0

# Access Control Registration
SAMPLES_PER_USER = 25

# Alert & Notification Configuration
ENABLE_VOICE_ALERT = True
ENABLE_AUDIO_CHIME = True
ALERT_COOLDOWN_SECONDS = 7.0  # Minimum time between voice warnings to avoid spam
INTRUDER_SNAPSHOT_COOLDOWN = 10.0  # Minimum time between auto-saving intruder snapshots
