# ─────────────────────────────────────────────
#  desktop/core/camera.py
#  Webcam capture – runs in a background thread
#  and exposes the latest frame via a property.
# ─────────────────────────────────────────────

import threading
import cv2
import logging
import time
from config.settings import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT, CAMERA_FPS

logger = logging.getLogger(__name__)


class Camera:
    """
    Thread-safe webcam wrapper.

    Usage:
        cam = Camera()
        cam.start()
        frame = cam.frame          # numpy array (BGR) or None
        cam.stop()
    """

    def __init__(self, index: int = CAMERA_INDEX):
        self._index = index
        self._cap = None
        self._frame = None
        self._running = False
        self._lock = threading.Lock()
        self._thread = None

    # ── Public API ─────────────────────────────────────────────

    def start(self) -> bool:
        """Open the camera and start the capture thread."""
        self._cap = cv2.VideoCapture(self._index)

        if not self._cap or not self._cap.isOpened():
            logger.error("Cannot open camera index %d", self._index)
            self._cap = None
            return False

        # Set camera properties
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self._cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

        logger.info(
            "Camera %d started (%dx%d @ %d fps)",
            self._index,
            FRAME_WIDTH,
            FRAME_HEIGHT,
            CAMERA_FPS,
        )

        return True

    def stop(self):
        """Stop the capture thread and release the camera."""
        self._running = False

        if self._thread:
            self._thread.join(timeout=2)

        if self._cap:
            self._cap.release()
            self._cap = None

        logger.info("Camera %d stopped", self._index)

    @property
    def frame(self):
        """Return the most recent BGR frame, or None if not yet available."""
        with self._lock:
            if self._frame is None:
                return None
            return self._frame.copy()

    @property
    def is_running(self) -> bool:
        return self._running

    # ── Internal ───────────────────────────────────────────────

    def _capture_loop(self):
        """Continuously read frames from the webcam."""
        while self._running:
            if self._cap is None or not self._cap.isOpened():
                logger.error("Camera is not initialized properly")
                break

            ret, frame = self._cap.read()

            if not ret or frame is None:
                logger.warning("Failed to read frame – retrying...")
                time.sleep(0.01)
                continue

            with self._lock:
                self._frame = frame

            # Small delay to reduce CPU usage
            time.sleep(0.01)