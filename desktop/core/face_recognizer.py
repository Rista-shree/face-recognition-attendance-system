# ─────────────────────────────────────────────
#  desktop/core/face_recognizer.py
#
#  Thin wrapper — with LBPH, detection AND
#  recognition both happen inside FaceEncoder.
#  This class just calls encoder.recognize_frame()
#  and converts the result to RecognitionResult
#  objects for the rest of the app to consume.
# ─────────────────────────────────────────────

import logging
from dataclasses import dataclass
from typing      import List, Optional

import numpy as np

from core.encoder import FaceEncoder

logger = logging.getLogger(__name__)

# (x, y, w, h) bounding box — OpenCV convention
FaceLocation = tuple


@dataclass
class RecognitionResult:
    employee_id: Optional[str]   # None = unknown
    name:        str              # "Unknown" if not identified
    confidence:  float            # 0.0 – 1.0
    location:    FaceLocation     # (x, y, w, h)


class FaceRecognizer:
    """
    Wraps FaceEncoder.recognize_frame() and returns typed RecognitionResult
    objects. Keeping this class maintains the same interface as the rest
    of the desktop app (dashboard.py, etc.) without changes.
    """

    def __init__(self, encoder: FaceEncoder):
        self._encoder = encoder

    def recognize(self, bgr_frame: np.ndarray) -> List[RecognitionResult]:
        """
        Detect and recognize all faces in *bgr_frame*.

        Returns:
            List of RecognitionResult — one per detected face.
        """
        raw = self._encoder.recognize_frame(bgr_frame)
        results = []

        for emp_id, name, confidence, location in raw:
            results.append(RecognitionResult(
                employee_id=emp_id,
                name=name,
                confidence=confidence,
                location=location,
            ))
            if emp_id:
                logger.debug("Recognised %s  conf=%.2f", name, confidence)

        return results