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
        if self._cascade.empty():
            raise RuntimeError("Failed to load Haar Cascade")

        self._samples: Dict[str, List[np.ndarray]] = {}

        logger.info("FaceEncoder ready – %d employee(s)", len(self._index))

    # ─────────────── PUBLIC METHODS ───────────────

    def add_training_frame(self, employee_id: str, name: str, frame: np.ndarray) -> bool:
        crops = self.get_face_crops(frame)
        if not crops:
            logger.warning("No face detected for %s", name)
            return False

        crop, _ = max(crops, key=lambda c: c[1][2] * c[1][3])

        if employee_id not in self._samples:
            self._samples[employee_id] = []

        self._samples[employee_id].append(crop)

        logger.info("Collected sample %d for %s",
                    len(self._samples[employee_id]), name)

        return True

    def train_employee(self, employee_id: str, name: str) -> bool:
        samples = self._samples.get(employee_id, [])

        if len(samples) < 20:
            logger.warning("Not enough samples for %s (%d/20)", name, len(samples))
            return False

        recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=2, neighbors=16, grid_x=8, grid_y=8,
            threshold=LBPH_THRESHOLD
        )

        # ✅ FIXED HERE
        labels = np.zeros(len(samples), dtype=np.int32)

        recognizer.train(samples, labels)
        recognizer.save(str(self._model_path(employee_id)))

        self._index[employee_id] = name
        self._save_index()

        self._samples[employee_id] = []

        logger.info("Trained model for %s (%s)", name, employee_id)
        return True

    def recognize_frame(self, frame: np.ndarray
                        ) -> List[Tuple[Optional[str], str, float, tuple]]:

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self._cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )

        if len(rects) == 0:
            return []

        models = self._load_all_models()
        results = []

        for (x, y, w, h) in rects:
            face_roi = cv2.resize(gray[y:y+h, x:x+w], (200, 200))

            best_id = None
            best_name = "Unknown"
            best_conf = 0.0

            for emp_id, recognizer in models.items():
                label, distance = recognizer.predict(face_roi)

                if distance < LBPH_THRESHOLD:
                    conf = round(1.0 - (distance / LBPH_THRESHOLD), 3)

                    if conf > best_conf:
                        best_conf = conf
                        best_id = emp_id
                        best_name = self._index.get(emp_id, emp_id)

            results.append((best_id, best_name, best_conf, (x, y, w, h)))

        return results

    def get_face_crops(self, frame: np.ndarray):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = self._cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )

        crops = []
        for (x, y, w, h) in rects:
            crop = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
            crops.append((crop, (x, y, w, h)))

        return crops

    def remove_employee(self, employee_id: str) -> bool:
        path = self._model_path(employee_id)

        if path.exists():
            path.unlink()

        if employee_id in self._index:
            del self._index[employee_id]
            self._save_index()
            return True

        return False

    @property
    def employee_count(self) -> int:
        return len(self._index)

    # ─────────────── INTERNAL METHODS ───────────────

    def _load_all_models(self):
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

    def _load_index(self):
        if self._index_path.exists():
            with open(self._index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_index(self):
        with open(self._index_path, "w", encoding="utf-8") as f:
            json.dump(self._index, f, indent=2)