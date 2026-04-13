# ─────────────────────────────────────────────
#  desktop/services/attendance_service.py
#  Write attendance records to the local SQLite
#  database and enforce the cooldown window so
#  the same person isn't logged twice in N secs.
# ─────────────────────────────────────────────

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib  import Path
from typing   import Dict, List, Optional

from config.settings import DB_PATH, RECOGNITION_COOLDOWN_S

logger = logging.getLogger(__name__)


# ── Schema ─────────────────────────────────────────────────────────────────────
_SCHEMA = """
CREATE TABLE IF NOT EXISTS attendance (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id TEXT    NOT NULL,
    name        TEXT    NOT NULL,
    timestamp   TEXT    NOT NULL,          -- ISO-8601
    confidence  REAL    NOT NULL DEFAULT 0,
    synced      INTEGER NOT NULL DEFAULT 0  -- 0=pending, 1=synced to API
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    department  TEXT,
    created_at  TEXT NOT NULL
);
"""


class AttendanceService:
    """
    Handles all attendance record operations:
      - Logging a check-in (with cooldown guard)
      - Querying history
      - Marking records as synced
    """

    def __init__(self, db_path: Path = DB_PATH):
        self._db_path = db_path
        self._conn    = self._connect()
        self._init_schema()
        # In-memory cooldown tracker: {employee_id: last_logged_datetime}
        self._last_seen: Dict[str, datetime] = {}

    # ── Public API ─────────────────────────────────────────────────────────────

    def log_attendance(self, employee_id: str, name: str,
                       confidence: float) -> bool:
        """
        Insert an attendance record if the cooldown period has elapsed.

        Returns:
            True  – record was inserted.
            False – skipped (still within cooldown, or unknown person).
        """
        if employee_id is None:
            return False

        now = datetime.now()
        last = self._last_seen.get(employee_id)

        if last and (now - last) < timedelta(seconds=RECOGNITION_COOLDOWN_S):
            logger.debug("Cooldown active for %s – skipping", name)
            return False

        self._last_seen[employee_id] = now
        self._insert_record(employee_id, name, now, confidence)
        logger.info("Logged: %s (%s) @ %s  conf=%.2f",
                    name, employee_id, now.strftime("%H:%M:%S"), confidence)
        return True

    def get_today(self) -> List[dict]:
        """Return all attendance records for today."""
        today = datetime.now().date().isoformat()
        cur = self._conn.execute(
            "SELECT * FROM attendance WHERE timestamp LIKE ? ORDER BY timestamp DESC",
            (f"{today}%",)
        )
        return self._rows_to_dicts(cur)

    def get_unsynced(self) -> List[dict]:
        """Return records that haven't been pushed to the backend yet."""
        cur = self._conn.execute(
            "SELECT * FROM attendance WHERE synced = 0 ORDER BY timestamp ASC"
        )
        return self._rows_to_dicts(cur)

    def mark_synced(self, record_ids: List[int]):
        """Mark a batch of records as synced."""
        if not record_ids:
            return
        placeholders = ",".join("?" * len(record_ids))
        self._conn.execute(
            f"UPDATE attendance SET synced = 1 WHERE id IN ({placeholders})",
            record_ids
        )
        self._conn.commit()
        logger.debug("Marked %d records as synced", len(record_ids))

    def upsert_employee(self, employee_id: str, name: str,
                        department: str = "") -> None:
        """Insert or update an employee record."""
        self._conn.execute(
            """
            INSERT INTO employees (employee_id, name, department, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(employee_id) DO UPDATE SET name=excluded.name,
                                                   department=excluded.department
            """,
            (employee_id, name, department, datetime.now().isoformat())
        )
        self._conn.commit()

    def get_all_employees(self) -> List[dict]:
        cur = self._conn.execute("SELECT * FROM employees ORDER BY name")
        return self._rows_to_dicts(cur)

    def close(self):
        self._conn.close()

    # ── Internal ───────────────────────────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self):
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def _insert_record(self, employee_id: str, name: str,
                       timestamp: datetime, confidence: float):
        self._conn.execute(
            "INSERT INTO attendance (employee_id, name, timestamp, confidence) "
            "VALUES (?, ?, ?, ?)",
            (employee_id, name, timestamp.isoformat(), confidence)
        )
        self._conn.commit()

    @staticmethod
    def _rows_to_dicts(cursor: sqlite3.Cursor) -> List[dict]:
        return [dict(row) for row in cursor.fetchall()]