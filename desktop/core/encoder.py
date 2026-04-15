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
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from config.settings import MODELS_DIR

logger = logging.getLogger(__name__)

_CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
LBPH_THRESHOLD = 90.0


class FaceEncoder:
    def __init__(self, models_dir: Path = MODELS_DIR):
        self._dir = models_dir
        self._dir.mkdir(parents=True, exist_ok=True)

        self._index_path = self._dir / "index.json"
        self._index: Dict[str, str] = self._load_index()

        self._cascade = cv2.CascadeClassifier(_CASCADE_PATH)

        self._samples: Dict[str, List[np.ndarray]] = {}

        #  load models once at startup (NO lag)
        self._model_cache: Dict[str, cv2.face.LBPHFaceRecognizer] = {}
        self._reload_model_cache()

        logger.info("Loaded %d face models", len(self._model_cache))

    # ─────────────────────────────────────────────

    def add_training_frame(self, emp_id, name, frame):
        crops = self.get_face_crops(frame)
        if not crops:
            return False

        crop, _ = max(crops, key=lambda c: c[1][2] * c[1][3])

        self._samples.setdefault(emp_id, []).append(crop)
        return True

    def train_employee(self, emp_id, name):
        samples = self._samples.get(emp_id, [])

        if len(samples) < 20:
            return False

        model = cv2.face.LBPHFaceRecognizer_create()
        model.setThreshold(LBPH_THRESHOLD)

        labels = np.zeros(len(samples), dtype=np.int32)
        model.train(samples, labels)

        model.save(str(self._model_path(emp_id)))

        self._index[emp_id] = name
        self._save_index()

        self._samples[emp_id] = []

        #  reload cache after training
        self._reload_model_cache()

        return True

    # ─────────────────────────────────────────────

    def recognize_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = self._cascade.detectMultiScale(
            gray, 1.1, 5, minSize=(60, 60)
        )

        results = []

        for (x, y, w, h) in rects:
            face = cv2.resize(gray[y:y+h, x:x+w], (200, 200))

            best_id = None
            best_name = "Unknown"
            best_conf = 0.0

            for emp_id, model in self._model_cache.items():
                _, dist = model.predict(face)

                if dist < LBPH_THRESHOLD:
                    conf = 1 - (dist / LBPH_THRESHOLD)

                    if conf > best_conf:
                        best_conf = conf
                        best_id = emp_id
                        best_name = self._index.get(emp_id, "Unknown")

            results.append((best_id, best_name, best_conf, (x, y, w, h)))

        return results

    # ─────────────────────────────────────────────

    def get_face_crops(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        rects = self._cascade.detectMultiScale(
            gray, 1.1, 5, minSize=(60, 60)
        )

        crops = []
        for (x, y, w, h) in rects:
            crop = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            crops.append((crop, (x, y, w, h)))

        return crops

    # ─────────────────────────────────────────────

    def _reload_model_cache(self):
        self._model_cache = {}

        for emp_id in self._index:
            path = self._model_path(emp_id)

            if path.exists():
                model = cv2.face.LBPHFaceRecognizer_create()
                model.read(str(path))
                model.setThreshold(LBPH_THRESHOLD)
                self._model_cache[emp_id] = model

    def _model_path(self, emp_id):
        return self._dir / f"{emp_id}.yml"

    def _load_index(self):
        if not self._index_path.exists():
            return {}

        try:
            with open(self._index_path, "r") as f:
                return json.load(f)
        except:
            return {}

    def _save_index(self):
        with open(self._index_path, "w") as f:
            json.dump(self._index, f, indent=2)

    @property
    def employee_count(self):
        return len(self._index)