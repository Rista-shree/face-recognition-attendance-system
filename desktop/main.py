# ─────────────────────────────────────────────
#  desktop/main.py
#  Entry point – configure logging and launch
#  the Tkinter application window.
# ─────────────────────────────────────────────

import logging
import sys
from pathlib import Path

# Allow imports from the desktop/ package root
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("attendance_desktop.log", encoding="utf-8"),
        ],
    )


if __name__ == "__main__":
    _setup_logging()
    app = MainWindow()
    app.run()