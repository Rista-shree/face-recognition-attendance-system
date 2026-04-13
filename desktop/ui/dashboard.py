# ─────────────────────────────────────────────
#  desktop/ui/dashboard.py
#  Main dashboard tab: camera feed + status
# ─────────────────────────────────────────────


import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import logging
import ttkbootstrap as ttk
import cv2
import numpy as np

from core.camera          import Camera
from core.encoder         import FaceEncoder
from core.face_detector   import FaceDetector
from core.face_recognizer import FaceRecognizer
from services.attendance_service import AttendanceService
from services.sync_service       import SyncService
from ui.components.camera_feed   import CameraFeedWidget
from ui.components.status_panel  import StatusPanel

logger = logging.getLogger(__name__)


class DashboardTab(ttk.Frame):
    """
    Main live-recognition dashboard.

    Layout:
        [  Camera Feed (left)  |  Status Panel (right)  ]
        [  Bottom toolbar: Start / Stop / Register       ]
    """

    def __init__(self, parent,
                 camera:   Camera,
                 encoder:  FaceEncoder,
                 svc:      AttendanceService,
                 sync_svc: SyncService,
                 **kwargs):
        super().__init__(parent, **kwargs)
        self._camera   = camera
        self._encoder  = encoder
        self._svc      = svc
        self._sync_svc = sync_svc

        self._recognizer   = FaceRecognizer(encoder)
        self._running      = False
        self._latest_frame = None   # annotated frame shown by the feed widget

        self._build_ui()

    # ── Public API ─────────────────────────────────────────────────────────────

    def start_recognition(self):
        if self._running:
            return
        self._running = True
        self._btn_start.config(state=tk.DISABLED)
        self._btn_stop.config(state=tk.NORMAL)
        self._feed.start()
        threading.Thread(target=self._recognition_loop,
                         daemon=True, name="RecognitionLoop").start()
        logger.info("Recognition started")

    def stop_recognition(self):
        self._running = False
        self._feed.stop()
        self._btn_start.config(state=tk.NORMAL)
        self._btn_stop.config(state=tk.DISABLED)
        logger.info("Recognition stopped")

    def register_face(self):
        """Prompt the user to register a new employee from the live camera."""
        emp_id = simpledialog.askstring("Register", "Employee ID:")
        if not emp_id:
            return
        name = simpledialog.askstring("Register", "Full Name:")
        if not name:
            return

        frame = self._camera.frame
        if frame is None:
            messagebox.showerror("Error", "Camera not available")
            return

        ok = self._encoder.encode_from_frame(emp_id.strip(), name.strip(), frame)
        if ok:
            self._svc.upsert_employee(emp_id.strip(), name.strip())
            self._status.set_known_faces(self._encoder.employee_count)
            messagebox.showinfo("Success", f"{name} registered successfully!")
        else:
            messagebox.showerror("Error",
                "No face detected. Ensure your face is clearly visible "
                "and well-lit, then try again.")

    # ── UI Build ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._feed = CameraFeedWidget(
            pane,
            get_frame_cb=lambda: self._latest_frame,
            width=640, height=480
        )
        pane.add(self._feed, )

        self._status = StatusPanel(pane)
        pane.add(self._status, )
        self._status.set_known_faces(self._encoder.employee_count)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=8, pady=(0, 8))

        self._btn_start = ttk.Button(toolbar, text="▶  Start",
                                     command=self.start_recognition,
                                     bootstyle="success")
        self._btn_start.pack(side=tk.LEFT, padx=4)

        self._btn_stop = ttk.Button(toolbar, text="■  Stop",
                                    command=self.stop_recognition,
                                    state=tk.DISABLED,
                                    bootstyle="danger")
        self._btn_stop.pack(side=tk.LEFT, padx=4)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=8)

        ttk.Button(toolbar, text="＋  Register Face",
                   command=self.register_face,
                   bootstyle="primary-outline").pack(side=tk.LEFT, padx=4)

        ttk.Button(toolbar, text="↑  Sync Now",
                   command=self._manual_sync,
                   bootstyle="secondary-outline").pack(side=tk.RIGHT, padx=4)

    # ── Recognition loop ───────────────────────────────────────────────────────

    def _recognition_loop(self):
        """
        Runs in a daemon thread.
        Grabs a frame → recognises faces → logs attendance →
        annotates frame → stores for the UI widget.
        """
        while self._running:
            frame = self._camera.frame
            if frame is None:
                continue

            results = self._recognizer.recognize(frame)

            locations = []
            labels    = []

            for r in results:
                if r.employee_id is None:
                    logged=False
                else:
                 logged = self._svc.log_attendance(
                    r.employee_id , r.name, r.confidence
                )
                label = f"{r.name} ({r.confidence:.0%})"
                labels.append(label)
                locations.append(r.location)   # (x, y, w, h)

                self.after(0, self._status.log_recognition,
                           r.name, r.confidence, logged)

            # Update counters
            today_count = len(self._svc.get_today())
            pending     = len(self._svc.get_unsynced())
            self.after(0, self._status.set_today_count, today_count)
            self.after(0, self._status.set_sync_status, pending)

            # Annotate and store frame
            self._latest_frame = FaceDetector.draw_boxes(
                frame, locations, labels
            )

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _manual_sync(self):
        count   = self._sync_svc.sync_now()
        pending = len(self._svc.get_unsynced())
        self._status.set_sync_status(pending)
        if count:
            messagebox.showinfo("Sync", f"{count} record(s) synced.")
        else:
            messagebox.showinfo("Sync", "Nothing to sync or backend offline.")