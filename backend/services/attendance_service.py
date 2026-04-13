# ─────────────────────────────────────────────
#  backend/services/attendance_service.py
# ─────────────────────────────────────────────

from datetime import datetime, date
from typing   import List, Optional

from sqlalchemy         import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.attendance  import Attendance
from schemas.attendance import AttendanceRecord


async def bulk_create(db: AsyncSession,
                      records: List[AttendanceRecord]) -> int:
    """
    Insert a batch of attendance records sent by the desktop app.
    Returns the number of records inserted.
    """
    rows = [
        Attendance(
            employee_id=r.employee_id,
            name=r.name,
            timestamp=r.timestamp,
            confidence=r.confidence,
        )
        for r in records
    ]
    db.add_all(rows)
    await db.flush()
    return len(rows)


async def get_by_date(db: AsyncSession,
                      target_date: date) -> List[Attendance]:
    start = datetime.combine(target_date, datetime.min.time())
    end   = datetime.combine(target_date, datetime.max.time())
    result = await db.execute(
        select(Attendance)
        .where(and_(Attendance.timestamp >= start,
                    Attendance.timestamp <= end))
        .order_by(Attendance.timestamp.desc())
    )
    return list(result.scalars().all())


async def get_by_employee(db: AsyncSession,
                           employee_id: str,
                           limit: int = 100) -> List[Attendance]:
    result = await db.execute(
        select(Attendance)
        .where(Attendance.employee_id == employee_id)
        .order_by(Attendance.timestamp.desc())
        .limit(limit)
    )
    return list (result.scalars().all())


async def get_today_summary(db: AsyncSession) -> dict:
    today = date.today()
    records = await get_by_date(db, today)

    # Unique employees present today
    unique_ids = {r.employee_id for r in records}

    return {
        "date":          today.isoformat(),
        "total_present": len(unique_ids),
        "total_records": len(records),
        "records":       records,
    }


async def get_monthly_counts(db: AsyncSession,
                              year: int, month: int) -> List[dict]:
    """Return daily present-count for a given month (for chart data)."""
    result = await db.execute(
        select(
            func.date(Attendance.timestamp).label("day"),
            func.count(func.distinct(Attendance.employee_id)).label("present"),
        )
        .where(
            and_(
                func.strftime("%Y", Attendance.timestamp) == str(year),
                func.strftime("%m", Attendance.timestamp) == f"{month:02d}",
            )
        )
        .group_by(func.date(Attendance.timestamp))
        .order_by("day")
    )
    return [{"day": row.day, "present": row.present}for row in result]