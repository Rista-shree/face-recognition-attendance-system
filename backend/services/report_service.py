# ─────────────────────────────────────────────
#  backend/services/report_service.py
#  Generate CSV and summary reports.
# ─────────────────────────────────────────────

import csv
import io
from datetime import date
from typing   import List

from sqlalchemy         import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.attendance import Attendance


async def generate_csv(db: AsyncSession,
                        start: date, end: date) -> str:
    """
    Return attendance records between *start* and *end* as a CSV string.
    """
    from datetime import datetime

    start_dt = datetime.combine(start, datetime.min.time())
    end_dt   = datetime.combine(end,   datetime.max.time())

    result = await db.execute(
        select(Attendance)
        .where(and_(Attendance.timestamp >= start_dt,
                    Attendance.timestamp <= end_dt))
        .order_by(Attendance.timestamp)
    )
    records: List[Attendance] = list(result.scalars().all())

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Employee ID", "Name", "Timestamp", "Confidence"])

    for r in records:
        writer.writerow([
            r.id,
            r.employee_id,
            r.name,
            r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            f"{r.confidence:.2f}",
        ])

    return output.getvalue()


async def get_department_summary(db: AsyncSession,
                                  target_date: date) -> List[dict]:
    """
    Return per-department attendance count for a given day.
    Joins attendance with employees to get department info.
    """
    from datetime import datetime
    from sqlalchemy import func
    from models.employee import Employee

    start = datetime.combine(target_date, datetime.min.time())
    end   = datetime.combine(target_date, datetime.max.time())

    result = await db.execute(
        select(
            Employee.department,
            func.count(func.distinct(Attendance.employee_id)).label("present"),
        )
        .join(Employee, Attendance.employee_id == Employee.employee_id)
        .where(and_(Attendance.timestamp >= start,
                    Attendance.timestamp <= end))
        .group_by(Employee.department)
    )

    return [
        {"department": row.department or "Unassigned", "present": row.present}
        for row in result
    ]