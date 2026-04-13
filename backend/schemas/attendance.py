# ─────────────────────────────────────────────
#  backend/schemas/attendance.py
# ─────────────────────────────────────────────

from datetime import datetime
from typing   import Optional, List
from pydantic import BaseModel


class AttendanceRecord(BaseModel):
    """Single record pushed by the desktop app."""
    employee_id: str
    name:        str
    timestamp:   datetime
    confidence:  float = 0.0


class AttendanceBulkCreate(BaseModel):
    """Batch of records from the desktop sync."""
    records: List[AttendanceRecord]


class AttendanceOut(BaseModel):
    id:          int
    employee_id: str
    name:        str
    timestamp:   datetime
    confidence:  float

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    """Used by the reports endpoint."""
    date:          str           # YYYY-MM-DD
    total_present: int
    records:       List[AttendanceOut]