# ─────────────────────────────────────────────
#  desktop/ui/components/status_panel.py
#  Right-side panel: live log + stat counters
# ─────────────────────────────────────────────

import tkinter as tk
from tkinter import ttk
from datetime import datetime


class StatusPanel(ttk.Frame):
    """
    Displays:
      • Today's running attendance count
      • Sync status badge
      • Scrollable live recognition log
    """

    MAX_LOG_LINES = 200

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build_ui()

    # ── Public API ─────────────────────────────────────────────────────────────

    def log_recognition(self, name: str, confidence: float, logged: bool):
        """
        Append an entry to the live log.

        Args:
            name:       Recognised person's name (or "Unknown").
            confidence: Match confidence 0–1.
            logged:     True if an attendance record was written.
        """
        ts     = datetime.now().strftime("%H:%M:%S")
        status = "✓ Logged" if logged else "· Cooldown"
        color  = "green"    if logged else "gray"
        line   = f"[{ts}]  {name:<20}  {confidence:.0%}  {status}\n"

        self._log_text.config(state=tk.NORMAL)
        self._log_text.insert(tk.END, line, color)
        self._log_text.see(tk.END)

        # Trim old lines
        lines = int(self._log_text.index("end-1c").split(".")[0])
        if lines > self.MAX_LOG_LINES:
            self._log_text.delete("1.0", f"{lines - self.MAX_LOG_LINES}.0")

        self._log_text.config(state=tk.DISABLED)

    def set_today_count(self, count: int):
        self._count_var.set(str(count))

    def set_sync_status(self, pending: int):
        if pending == 0:
            self._sync_var.set("✓  All synced")
            self._sync_lbl.config(foreground="green")
        else:
            self._sync_var.set(f"↑  {pending} pending")
            self._sync_lbl.config(foreground="orange")

    def set_known_faces(self, count: int):
        self._faces_var.set(str(count))

    # ── UI Build ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Stats row ───────────────────────────────────────────────────────
        stats = ttk.Frame(self)
        stats.pack(fill=tk.X, padx=10, pady=(10, 4))

        self._count_var = tk.StringVar(value="0")
        self._faces_var = tk.StringVar(value="0")
        self._sync_var  = tk.StringVar(value="✓  All synced")

        self._make_stat(stats, "Today", self._count_var).pack(side=tk.LEFT, padx=8)
        self._make_stat(stats, "Known", self._faces_var).pack(side=tk.LEFT, padx=8)

        sync_frame = ttk.Frame(stats)
        ttk.Label(sync_frame, text="Sync", font=("Helvetica", 9),
                  foreground="grey").pack()
        self._sync_lbl = ttk.Label(sync_frame, textvariable=self._sync_var,
                                   font=("Helvetica", 11, "bold"),
                                   foreground="green")
        self._sync_lbl.pack()
        sync_frame.pack(side=tk.LEFT, padx=8)

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)

        # ── Log ─────────────────────────────────────────────────────────────
        ttk.Label(self, text="Live Log", font=("Helvetica", 10, "bold")).pack(
            anchor=tk.W, padx=10)

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._log_text = tk.Text(
            frame, state=tk.DISABLED,
            font=("Courier", 10), wrap=tk.NONE,
            yscrollcommand=scrollbar.set,
            bg="#1e1e1e", fg="#d4d4d4",
            selectbackground="#264f78",
        )
        self._log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._log_text.yview)

        # Tag colours
        self._log_text.tag_config("green", foreground="#4ec9b0")
        self._log_text.tag_config("gray",  foreground="#808080")

    @staticmethod
    def _make_stat(parent, label: str, var: tk.StringVar) -> ttk.Frame:
        f = ttk.Frame(parent)
        ttk.Label(f, text=label, font=("Helvetica", 9),
                  foreground="grey").pack()
        ttk.Label(f, textvariable=var,
                  font=("Helvetica", 22, "bold")).pack()
        return f