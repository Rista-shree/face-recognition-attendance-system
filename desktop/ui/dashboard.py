# ─────────────────────────────────────────────
#  desktop/ui/dashboard.py
#  Main dashboard tab: camera feed + status
# ─────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import logging
import time
from datetime import datetime

import ttkbootstrap as ttk

from core.face_recognizer import FaceRecognizer
from core.face_detector import FaceDetector

from ui.components.camera_feed import CameraFeedWidget
from ui.components.status_panel import StatusPanel

logger = logging.getLogger(__name__)

COOLDOWN = 10  # seconds
UNKNOWN_COOLDOWN = 3  # seconds


class DashboardTab(ttk.Frame):

    def __init__(self, parent, camera, encoder, svc, sync_svc, **kwargs):
        super().__init__(parent, **kwargs)

        self._camera = camera
        self._encoder = encoder
        self._svc = svc
        self._sync_svc = sync_svc

        self._recognizer = FaceRecognizer(encoder)

        self._running = False
        self._latest_frame = None

        self._last_logged = {}  # stores cooldown timestamps
        self._last_ui_update={}#dictionary to track ui timing
        self._build_ui()

    # ─────────────────────────────

    def _build_ui(self):
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        self._feed = CameraFeedWidget(
            pane,
            get_frame_cb=lambda: self._latest_frame
        )
        pane.add(self._feed)

        self._status = StatusPanel(pane)
        pane.add(self._status)
        self._status.set_known_faces(self._encoder.employee_count)
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X)

        self._btn_start = ttk.Button(toolbar, text="Start", command=self.start_recognition)
        self._btn_start.pack(side=tk.LEFT)

        self._btn_stop = ttk.Button(toolbar, text="Stop", command=self.stop_recognition)
        self._btn_stop.pack(side=tk.LEFT)

        ttk.Button(toolbar, text="Register", command=self.register_face).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Sync Now", command=self._manual_sync).pack(side=tk.RIGHT)

    # ─────────────────────────────

    def start_recognition(self):
        if self._running:
            return

        self._running = True
        self._feed.start()

        threading.Thread(target=self._loop, daemon=True).start()

    def stop_recognition(self):
        self._running = False
        self._feed.stop()

    # ─────────────────────────────

    def _loop(self):
        while self._running:
            frame = self._camera.frame

            if frame is None:
                time.sleep(0.02)
                continue

            results = self._recognizer.recognize(frame)

            locations = []
            labels = []

            for r in results:
                now = datetime.now()

                if r.employee_id is None:
                    # UNKNOWN cooldown
                    last = self._last_logged.get("UNKNOWN")

                    if last is None or (now - last).total_seconds() > UNKNOWN_COOLDOWN:
                        self._last_logged["UNKNOWN"] = now

                        self.after(0, self._status.log_recognition,
                                   r.name, r.confidence, False)

                    logged = False

                else:
                    last = self._last_logged.get(r.employee_id)

                    if last is None or (now - last).total_seconds() >= COOLDOWN:
                        logged = self._svc.log_attendance(
                            r.employee_id, r.name, r.confidence
                        )

                        if logged:
                         self._last_logged[r.employee_id] = now
                    else:
                        logged = False

                    # prevents  show known faces from being spammy
                    last_ui= self._last_ui_update.get(r.employee_id)
                    if last_ui is None or (now-last_ui).total_seconds()>1:
                          self.after(0,self._status.log_recognition , r.name, r.confidence, logged)
                          self._last_ui_update[r.employee_id]=now

                labels.append(f"{r.name} ({r.confidence:.0%})")
                locations.append(r.location)

            self._latest_frame = FaceDetector.draw_boxes(frame, locations, labels)
            #updating ui stats (known, today)
            today_count= len(self._svc.get_today())
            pending=len(self._svc.get_unsynced())

            self.after(0,self._status.set_today_count,today_count)
            self.after(0,self._status.set_sync_status,pending)
            time.sleep(0.03)

    # ─────────────────────────────

    def register_face(self):
        emp_id = simpledialog.askstring("ID", "Employee ID")
        name = simpledialog.askstring("Name", "Name")

        if not emp_id or not name:
            return

        collected = 0

        while collected < 30:
            frame = self._camera.frame
            if frame is None:
                continue

            if self._encoder.add_training_frame(emp_id, name, frame):
                collected += 1

            time.sleep(0.05)

        if self._encoder.train_employee(emp_id, name):
            self._svc.upsert_employee(emp_id, name)
            messagebox.showinfo("Done", "Registered successfully")

    # ─────────────────────────────

    def _manual_sync(self):
        self._sync_svc.sync_now()