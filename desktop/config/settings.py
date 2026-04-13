# ─────────────────────────────────────────────
#  desktop/config/settings.py
#  Central configuration for the desktop app
# ─────────────────────────────────────────────

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).resolve().parent.parent
MODELS_DIR      = BASE_DIR / "models" / "known_faces"
EMBEDDINGS_FILE = MODELS_DIR / "embeddings.pkl"
DB_PATH         = BASE_DIR.parent / "database" / "attendance.db"

# Make sure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR.parent / "database").mkdir(parents=True, exist_ok=True)

# ── Camera ─────────────────────────────────────────────────────────────────────
CAMERA_INDEX     = 0          # 0 = default webcam
FRAME_WIDTH      = 640
FRAME_HEIGHT     = 480
CAMERA_FPS       = 30

# ── Face Recognition ───────────────────────────────────────────────────────────
RECOGNITION_TOLERANCE   = 0.5   # Lower = stricter match (0.0 – 1.0)
DETECTION_MODEL         = "hog" # "hog" (fast/CPU) | "cnn" (accurate/GPU)
MIN_FACE_CONFIDENCE     = 0.6   # Minimum confidence to accept a detection
RECOGNITION_COOLDOWN_S  = 30    # Seconds before re-logging the same person

# ── Backend API ────────────────────────────────────────────────────────────────
API_BASE_URL   = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY        = os.getenv("DESKTOP_API_KEY", "dev-api-key-change-me")
SYNC_INTERVAL_S = 60            # How often to push pending records to server

# ── UI ─────────────────────────────────────────────────────────────────────────
APP_TITLE   = "Face Attendance System"
WINDOW_SIZE = "1100x680"
THEME       = "darkly"          # ttkbootstrap theme