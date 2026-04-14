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
from datetime import datetime   # ✅ ADDED

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
        self._latest_frame = None

        self._last_logged = {}   # ✅ ADDED (cooldown memory)

        self._build_ui()

    # ── Public API ─────────────────────────────────────────

    def start_recognition(self):
        if self._running:
            return
        self._running = True
        self._btn_start.config(state=tk.DISABLED)
        self._btn_stop.config(state=tk.NORMAL)
        self._feed.start()
        threading.Thread(
            target=self._recognition_loop,
            daemon=True,
            name="RecognitionLoop"
        ).start()
        logger.info("Recognition started")

    def stop_recognition(self):
        self._running = False
        self._feed.stop()
        self._btn_start.config(state=tk.NORMAL)
        self._btn_stop.config(state=tk.DISABLED)
        logger.info("Recognition stopped")

    def register_face(self):
        emp_id = simpledialog.askstring("Register", "Employee ID:")
        if not emp_id:
            return

        name = simpledialog.askstring("Register", "Full Name:")
        if not name:
            return

        emp_id = emp_id.strip()
        name = name.strip()

        messagebox.showinfo(
            "Info",
            "Look at the camera.\nWe will capture 30 samples automatically."
        )

        collected = 0

        while collected < 30:
            frame = self._camera.frame

            if frame is None:
                continue

            ok = self._encoder.add_training_frame(emp_id, name, frame)

            if ok:
                collected += 1
                print(f"Collecting samples:{collected}/30")

            cv2.waitKey(50)

        trained = self._encoder.train_employee(emp_id, name)

        if trained:
            self._svc.upsert_employee(emp_id, name)
            self._status.set_known_faces(self._encoder.employee_count)

            messagebox.showinfo(
                "Success",
                f"{name} registered successfully!"
            )
        else:
            messagebox.showerror(
                "Error",
                "Training failed. Try again."
            )

    # ── UI Build ─────────────────────────────────────────

    def _build_ui(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._feed = CameraFeedWidget(
            pane,
            get_frame_cb=lambda: self._latest_frame,
            width=640,
            height=480
        )
        pane.add(self._feed)

        self._status = StatusPanel(pane)
        pane.add(self._status)
        self._status.set_known_faces(self._encoder.employee_count)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=8, pady=(0, 8))

        self._btn_start = ttk.Button(
            toolbar,
            text="▶  Start",
            command=self.start_recognition,
            bootstyle="success"
        )
        self._btn_start.pack(side=tk.LEFT, padx=4)

        self._btn_stop = ttk.Button(
            toolbar,
            text="■  Stop",
            command=self.stop_recognition,
            state=tk.DISABLED,
            bootstyle="danger"
        )
        self._btn_stop.pack(side=tk.LEFT, padx=4)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=8
        )

        ttk.Button(
            toolbar,
            text="＋  Register Face",
            command=self.register_face,
            bootstyle="primary-outline"
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            toolbar,
            text="↑  Sync Now",
            command=self._manual_sync,
            bootstyle="secondary-outline"
        ).pack(side=tk.RIGHT, padx=4)

    # ── Recognition loop ─────────────────────────────────

    def _recognition_loop(self):
        while self._running:
            frame = self._camera.frame
            if frame is None:
                continue

            results = self._recognizer.recognize(frame)

            locations = []
            labels = []

            for r in results:
                if r.employee_id is None:
                    logged = False
                else:
                    # ✅ FIX: cooldown logic
                    now = datetime.now()
                    last_time = self._last_logged.get(r.employee_id)

                    if last_time is None or (now - last_time).seconds > 10:
                        logged = self._svc.log_attendance(
                            r.employee_id, r.name, r.confidence
                        )
                        self._last_logged[r.employee_id] = now
                    else:
                        logged = False

                label = f"{r.name} ({r.confidence:.0%})"
                labels.append(label)
                locations.append(r.location)

                self.after(
                    0,
                    self._status.log_recognition,
                    r.name,
                    r.confidence,
                    logged
                )

            today_count = len(self._svc.get_today())
            pending = len(self._svc.get_unsynced())

            self.after(0, self._status.set_today_count, today_count)
            self.after(0, self._status.set_sync_status, pending)

            self._latest_frame = FaceDetector.draw_boxes(
                frame, locations, labels
            )

    # ── Helpers ─────────────────────────────────────────

    def _manual_sync(self):
        count = self._sync_svc.sync_now()
        pending = len(self._svc.get_unsynced())
        self._status.set_sync_status(pending)

        if count:
            messagebox.showinfo("Sync", f"{count} record(s) synced.")
        else:
            messagebox.showinfo(
                "Sync",
                "Nothing to sync or backend offline."
            )