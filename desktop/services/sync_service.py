# ─────────────────────────────────────────────
#  desktop/services/sync_service.py
#  Periodically push unsynced attendance records
#  to the FastAPI backend in a background thread.
# ─────────────────────────────────────────────

import logging
import threading
import time
from typing import Callable, Optional

import requests

from config.settings          import API_BASE_URL, API_KEY, SYNC_INTERVAL_S
from services.attendance_service import AttendanceService

logger = logging.getLogger(__name__)


class SyncService:
    """
    Background worker that reads unsynced records from SQLite and POSTs
    them to the backend API every SYNC_INTERVAL_S seconds.

    The desktop app stays fully functional even when the API is offline –
    records accumulate locally and are sent once connectivity is restored.
    """

    def __init__(self,
                 attendance_service: AttendanceService,
                 on_sync: Optional[Callable[[int], None]] = None):
        """
        Args:
            attendance_service: Shared AttendanceService instance.
            on_sync: Optional callback called with the number of records synced.
        """
        self._svc      = attendance_service
        self._on_sync  = on_sync
        self._running  = False
        self._thread   = None
        self._session  = requests.Session()
        self._session.headers.update({
            "X-API-Key":    API_KEY,
            #"Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        })

    # ── Public API ─────────────────────────────────────────────────────────────

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True,
                                         name="SyncWorker")
        self._thread.start()
        logger.info("SyncService started (interval=%ds)", SYNC_INTERVAL_S)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("SyncService stopped")

    def sync_now(self) -> int:
        """Manually trigger a sync. Returns number of records pushed."""
        return self._push_pending()

    # ── Internal ───────────────────────────────────────────────────────────────

    def _loop(self):
        while self._running:
            try:
                self._push_pending()
            except Exception:
                logger.exception("Sync error – will retry next cycle")
            time.sleep(SYNC_INTERVAL_S)

    def _push_pending(self) -> int:
        records = self._svc.get_unsynced()
        if not records:
            return 0

        payload = [
            {
                "employee_id": r["employee_id"],
                "name":        r["name"],
                "timestamp":   r["timestamp"],
                #"timestamp": r["timestamp"].isoformat() if hasattr(r["timestamp"], "isoformat") else r["timestamp"],
                "confidence":  r["confidence"],
            }
            for r in records
        ]

        try:
            resp = self._session.post(
                f"{API_BASE_URL}/api/attendance/bulk",
                json=payload,
                timeout=10
            )
            resp.raise_for_status()
            ids = [r["id"] for r in records]
            self._svc.mark_synced(ids)
            count = len(ids)
            logger.info("Synced %d record(s) to backend", count)
            if self._on_sync:
                self._on_sync(count)
            return count

        except requests.ConnectionError:
            logger.warning("Backend unreachable – records will sync later")
        except requests.HTTPError as e:
            logger.error("Backend returned error: %s", e)

        return 0