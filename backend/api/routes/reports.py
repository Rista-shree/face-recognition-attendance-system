# ─────────────────────────────────────────────
#  backend/api/routes/reports.py
# ─────────────────────────────────────────────

from datetime import date
from typing import Optional
from fastapi           import APIRouter
from fastapi.responses import StreamingResponse
import io

from api.dependencies  import DBSession, CurrentUser
from services          import report_service

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/export/csv")
async def export_csv(
    db:    DBSession,
    _:     CurrentUser,
    start: Optional[date] = None,
    end: Optional[date] = None,
):
    """
    Download attendance records as a CSV file.
    Defaults to today if no date range is provided.
    """
    today = date.today()
    start = start or today
    end   = end   or today

    csv_data = await report_service.generate_csv(db, start, end)

    filename = f"attendance_{start}_to_{end}.csv"
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/department-summary")
async def department_summary(
    db:          DBSession,
    _:           CurrentUser,
      target_date: Optional[date] = None,
):
    """
    Return per-department attendance counts.
    Defaults to today.
    """
    target_date = target_date or date.today()
    return await report_service.get_department_summary(db, target_date)