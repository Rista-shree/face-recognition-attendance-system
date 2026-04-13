# ─────────────────────────────────────────────
#  desktop/core/face_detector.py
#
#  Draws annotated bounding boxes on frames.
#  Face detection is handled inside FaceEncoder
#  via OpenCV Haar Cascade.
# ─────────────────────────────────────────────

from typing import List, Tuple, Optional

import cv2
import numpy as np

# (x, y, w, h) — standard OpenCV bounding box
FaceLocation = Tuple[int, int, int, int]


class FaceDetector:
    """
    Utility for drawing annotated bounding boxes onto frames.
    Actual face detection lives in FaceEncoder.get_face_crops().
    """

    @staticmethod
    def draw_boxes(bgr_frame: np.ndarray,
                   locations: List[FaceLocation],
                   labels:    Optional[List[str]] = None,
                   color:     Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Draw bounding boxes and name labels on a copy of the frame.

        Args:
            bgr_frame: Original BGR frame.
            locations: List of (x, y, w, h) tuples.
            labels:    Optional label per box.
            color:     BGR colour for the rectangle.

        Returns:
            Annotated copy of the frame.
        """
        frame = bgr_frame.copy()

        for i, (x, y, w, h) in enumerate(locations):
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

            if labels and i < len(labels):
                label = labels[i]
                # Filled label background strip
                cv2.rectangle(frame, (x, y + h - 28), (x + w, y + h),
                              color, cv2.FILLED)
                cv2.putText(frame, label,
                            (x + 6, y + h - 8),
                            cv2.FONT_HERSHEY_DUPLEX,
                            0.55, (0, 0, 0), 1)
        return frame