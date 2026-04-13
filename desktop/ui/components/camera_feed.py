# ─────────────────────────────────────────────
#  desktop/ui/components/camera_feed.py
#  Tkinter widget that shows the live camera
#  stream with annotated face bounding boxes.
# ─────────────────────────────────────────────

import tkinter as tk
from tkinter import ttk
from typing  import Callable, Optional

import cv2
from PIL import Image, ImageTk
import numpy as np


class CameraFeedWidget(ttk.Frame):
    """
    A self-refreshing canvas that pulls the latest annotated frame
    from a callback and displays it inside a Tkinter Frame.

    Args:
        parent:        Parent Tkinter widget.
        get_frame_cb:  Callable[[], np.ndarray | None]
                       Returns the current BGR frame (already annotated),
                       or None when the camera isn't ready.
        width/height:  Display dimensions.
        fps:           Refresh rate for the UI.
    """

    def __init__(self,
                 parent,
                 get_frame_cb: Callable[[], Optional[np.ndarray]],
                 width:  int = 640,
                 height: int = 480,
                 fps:    int = 20,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self._get_frame = get_frame_cb
        self._width     = width
        self._height    = height
        self._delay_ms  = 1000 // fps
        self._running   = False
        self._photo     = None   # keep a reference so GC doesn't collect it

        self._canvas = tk.Canvas(self, width=width, height=height,
                                 bg="black", highlightthickness=0)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        # Placeholder text until camera is ready
        self._canvas.create_text(
            width // 2, height // 2,
            text="Camera initialising…",
            fill="grey", font=("Helvetica", 14),
            tags="placeholder"
        )

    # ── Public API ─────────────────────────────────────────────────────────────

    def start(self):
        """Begin the refresh loop."""
        self._running = True
        self._refresh()

    def stop(self):
        """Halt the refresh loop."""
        self._running = False

    # ── Internal ───────────────────────────────────────────────────────────────

    def _refresh(self):
        if not self._running:
            return

        frame = self._get_frame()
        if frame is not None:
            self._canvas.delete("placeholder")
            self._draw_frame(frame)

        # Schedule next update on the Tkinter event loop
        self.after(self._delay_ms, self._refresh)

    def _draw_frame(self, bgr_frame: np.ndarray):
        # Convert BGR → RGB → PIL → ImageTk
        rgb   = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        img   = Image.fromarray(rgb).resize(
                    (self._width, self._height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        self._canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self._photo = photo   # prevent garbage collection....