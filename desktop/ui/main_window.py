# ─────────────────────────────────────────────
#  desktop/ui/main_window.py
#  Root Tkinter window with tabbed layout
# ─────────────────────────────────────────────

import tkinter as tk
from tkinter import ttk, messagebox
import logging

import ttkbootstrap as tbs

from config.settings             import APP_TITLE, WINDOW_SIZE, THEME
from core.camera                 import Camera
from core.encoder                import FaceEncoder
from services.attendance_service import AttendanceService
from services.sync_service       import SyncService
from ui.dashboard                import DashboardTab

logger = logging.getLogger(__name__)


class MainWindow:
    """
    Application shell.
    Owns the lifecycle of all services and the camera,
    and hosts a Notebook with tabs:
      1. Live Dashboard
      (more tabs – Reports, Employees – to be added in future sprints)
    """

    def __init__(self):
        self._root = tbs.Window(themename=THEME)
        self._root.title(APP_TITLE)
        self._root.geometry(WINDOW_SIZE)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Services ────────────────────────────────────────────────────────
        self._encoder  = FaceEncoder()
        self._svc      = AttendanceService()
        self._sync_svc = SyncService(
            self._svc,
            on_sync=lambda n: logger.info("Auto-synced %d records", n)
        )

        # ── Camera ──────────────────────────────────────────────────────────
        self._camera = Camera()
        if not self._camera.start():
            messagebox.showerror(
                "Camera Error",
                "Could not open webcam.\n"
                "Check that it is connected and not in use by another app."
            )

        # ── Sync ────────────────────────────────────────────────────────────
        self._sync_svc.start()

        # ── UI ──────────────────────────────────────────────────────────────
        self._build_ui()

    # ── Public ─────────────────────────────────────────────────────────────────

    def run(self):
        self._root.mainloop()

    # ── Internal ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        notebook = ttk.Notebook(self._root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Tab 1 – Live Dashboard
        self._dashboard = DashboardTab(
            notebook,
            camera=self._camera,
            encoder=self._encoder,
            svc=self._svc,
            sync_svc=self._sync_svc,
        )
        notebook.add(self._dashboard, text="  📷  Live  ")

        # Tab 2 – placeholder for Reports
        reports_tab = ttk.Frame(notebook)
        ttk.Label(reports_tab,
                  text="Reports – coming soon",
                  font=("Helvetica", 14)).pack(expand=True)
        notebook.add(reports_tab, text="  📊  Reports  ")

        # Tab 3 – placeholder for Employee management
        emp_tab = ttk.Frame(notebook)
        ttk.Label(emp_tab,
                  text="Employee Management – coming soon",
                  font=("Helvetica", 14)).pack(expand=True)
        notebook.add(emp_tab, text="  👤  Employees  ")

    def _on_close(self):
        """Graceful shutdown."""
        logger.info("Shutting down…")
        if self._dashboard:
            self._dashboard.stop_recognition()
        self._sync_svc.stop()
        self._camera.stop()
        self._svc.close()
        self._root.destroy()