# ─────────────────────────────────────────────
#  desktop/core/encoder.py
#
#  Stack: Pure OpenCV (opencv-contrib-python)
#  ✅ Python 3.14 compatible
#  ✅ No dlib / no InsightFace / no TensorFlow
#  ✅ Pre-built wheels — just pip install
#
#  Approach:
#    Detection  → Haar Cascade (built into OpenCV)
#    Recognition → LBPH (cv2.face.LBPHFaceRecognizer)
#    Storage    → one .yml model file per employee
#                 + a JSON index mapping IDs to names
# ─────────────────────────────────────────────

import json
import logging
import pickle
from pathlib import Path
from typing  import Dict, List, Optional, Tuple

import cv2
import numpy as np

from config.settings import MODELS_DIR, EMBEDDINGS_FILE

logger = logging.getLogger(__name__)

# Haar Cascade ships inside the opencv-contrib-python package
_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml" # type: ignore

# Confidence threshold: LOWER = stricter match (LBPH distance, not similarity)
LBPH_THRESHOLD = 80.0   # tune between 60–100 depending on lighting


class FaceEncoder:
    """
    Manages per-employee LBPH face models on disk.

    Each employee gets their own trained LBPHFaceRecognizer saved as
    a .yml file.  A JSON sidecar (index.json) maps employee_id → name.

    Flow:
        register  → collect N face crops → train LBPH → save .yml
        recognize → load all models → predict → return best match
    """

    def __init__(self, models_dir: Path = MODELS_DIR):
        self._dir      = models_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        self._index_path = self._dir / "index.json"

        # {employee_id: name}
        self._index: Dict[str, str] = self._load_index()

        # Haar Cascade for face detection during encoding
        self._cascade = cv2.CascadeClassifier(_CASCADE_PATH)
        if self._cascade.empty():
            raise RuntimeError(
                f"Failed to load Haar Cascade from: {_CASCADE_PATH}\n"
                "Make sure opencv-contrib-python is installed, not opencv-python."
            )

        logger.info("FaceEncoder ready – %d employee(s) registered", len(self._index))

    # ── Public API ─────────────────────────────────────────────────────────────

    def encode_from_file(self, employee_id: str, name: str,
                         image_path: str) -> bool:
        """Load an image file and encode the face inside it."""
        bgr = cv2.imread(image_path)
        if bgr is None:
            logger.error("Cannot read: %s", image_path)
            return False
        return self._encode_and_train(employee_id, name, bgr)

    def encode_from_frame(self, employee_id: str, name: str,
                           bgr_frame: np.ndarray) -> bool:
        """Encode a face from a live BGR camera frame."""
        return self._encode_and_train(employee_id, name, bgr_frame)

    def remove_employee(self, employee_id: str) -> bool:
        """Delete the employee's model and index entry."""
        model_path = self._model_path(employee_id)
        if model_path.exists():
            model_path.unlink()
        if employee_id in self._index:
            del self._index[employee_id]
            self._save_index()
            return True
        return False

    def recognize_frame(self, bgr_frame: np.ndarray
                        ) -> List[Tuple[Optional[str], str, float, tuple]]:
        """
        Detect all faces in *bgr_frame* and identify each one.

        Returns a list of tuples:
            (employee_id, name, confidence, (x, y, w, h))

        employee_id is None and name is "Unknown" when no match is found.
        confidence is 0.0–1.0 (converted from LBPH distance).
        """
        gray  = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        rects = self._cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )

        if not len(rects):
            return []

        models = self._load_all_models()
        results = []

        for (x, y, w, h) in rects:
            face_roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            best_id   = None
            best_name = "Unknown"
            best_conf = 0.0

            for emp_id, recognizer in models.items():
                label, distance = recognizer.predict(face_roi)
                if distance < LBPH_THRESHOLD:
                    # Convert distance to 0–1 confidence (lower distance = higher conf)
                    conf = round(1.0 - (distance / LBPH_THRESHOLD), 3)
                    if conf > best_conf:
                        best_conf = conf
                        best_id   = emp_id
                        best_name = self._index.get(emp_id, emp_id)

            results.append((best_id, best_name, best_conf, (x, y, w, h)))

        return results

    def get_face_crops(self, bgr_frame: np.ndarray
                       ) -> List[Tuple[np.ndarray, tuple]]:
        """
        Return (grayscale face crop, (x,y,w,h)) for every detected face.
        Used during registration to collect training samples.
        """
        gray  = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
        rects = self._cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )
        crops = []
        for (x, y, w, h) in rects:
            crop = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            crops.append((crop, (x, y, w, h)))
        return crops

    def get_name(self, employee_id: str) -> Optional[str]:
        return self._index.get(employee_id)

    def get_all_encodings(self):
        """Compatibility shim — not used with LBPH but keeps interface stable."""
        return [], []

    @property
    def employee_count(self) -> int:
        return len(self._index)

    # ── Internal ───────────────────────────────────────────────────────────────

    def _encode_and_train(self, employee_id: str, name: str,
                          bgr_frame: np.ndarray) -> bool:
        crops = self.get_face_crops(bgr_frame)
        if not crops:
            logger.warning("No face found for %s – skipping", name)
            return False

        # Use only the largest detected face
        crop, _ = max(crops, key=lambda c: c[1][2] * c[1][3])

        # Load existing model to add samples (incremental training)
        recognizer = self._load_model(employee_id)

        # LBPH update() appends new samples to an already-trained model
        recognizer.update([crop], np.array([0]))
        recognizer.save(str(self._model_path(employee_id)))

        self._index[employee_id] = name
        self._save_index()
        logger.info("Trained LBPH model for %s (%s)", name, employee_id)
        return True

    def _load_model(self, employee_id: str) -> cv2.face.LBPHFaceRecognizer:
        path = self._model_path(employee_id)
        recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=2, neighbors=16, grid_x=8, grid_y=8,
            threshold=LBPH_THRESHOLD
        )
        if path.exists():
            recognizer.read(str(path))
        else:
            # Bootstrap with a dummy sample so .update() works
            dummy = np.zeros((200, 200), dtype=np.uint8)
            recognizer.train([dummy], np.array([0]))
        return recognizer

    def _load_all_models(self) -> Dict[str, cv2.face.LBPHFaceRecognizer]:
        models = {}
        for emp_id in self._index:
            path = self._model_path(emp_id)
            if path.exists():
                rec = cv2.face.LBPHFaceRecognizer_create(
                    threshold=LBPH_THRESHOLD
                )
                rec.read(str(path))
                models[emp_id] = rec
        return models

    def _model_path(self, employee_id: str) -> Path:
        safe_id = employee_id.replace("/", "_").replace("\\", "_")
        return self._dir / f"{safe_id}.yml"

    def _load_index(self) -> Dict[str, str]:
        if self._index_path.exists():
            with open(self._index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(self._index_path, "w", encoding="utf-8") as f:
            json.dump(self._index, f, indent=2)