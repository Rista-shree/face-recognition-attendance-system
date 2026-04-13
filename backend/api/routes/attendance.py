# ─────────────────────────────────────────────
#  backend/api/routes/attendance.py
# ─────────────────────────────────────────────

from datetime import date
from typing   import List

from fastapi import APIRouter, Query

from api.dependencies    import DBSession, CurrentUser, DesktopAuth
from schemas.attendance  import AttendanceOut, AttendanceRecord, AttendanceSummary
from services            import attendance_service

router = APIRouter(prefix="/api/attendance", tags=["Attendance"])


@router.post("/bulk", status_code=201)
async def bulk_create(records: List[AttendanceRecord],
                      db: DBSession,
                      _: DesktopAuth):
    """
    Receive a batch of attendance records from the desktop app.
    Authenticated via the static X-API-Key header.
    """
    count = await attendance_service.bulk_create(db, records)
    return {"inserted": count}


@router.get("/today", response_model=AttendanceSummary)
async def today(db: DBSession, _: CurrentUser):
    """Return today's attendance summary for the dashboard."""
    summary = await attendance_service.get_today_summary(db)
    return AttendanceSummary(
        date=summary["date"],
        total_present=summary["total_present"],
        records=summary["records"],
    )


@router.get("/date/{target_date}", response_model=AttendanceSummary)
async def by_date(target_date: date, db: DBSession, _: CurrentUser):
    """Return attendance for a specific date (YYYY-MM-DD)."""
    records = await attendance_service.get_by_date(db, target_date)
    unique  = len({r.employee_id for r in records})
    return AttendanceSummary(
        date=target_date.isoformat(),
        total_present=unique,
         records=[AttendanceOut.model_validate(r) for r in records]
)


@router.get("/employee/{employee_id}", response_model=List[AttendanceOut])
async def by_employee(employee_id: str, db: DBSession, _: CurrentUser,
                       limit: int = Query(default=100, le=500)):
    """Return attendance history for a specific employee."""
    return await attendance_service.get_by_employee(db, employee_id, limit)


@router.get("/monthly/{year}/{month}")
async def monthly_counts(year: int, month: int,
                          db: DBSession, _: CurrentUser):
    """
    Return daily present-counts for a given month.
    Used by the monthly chart in the web dashboard.
    """
    return await attendance_service.get_monthly_counts(db, year, month)