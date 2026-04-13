# ─────────────────────────────────────────────
#  backend/models/attendance.py
# ────────────────────────────────────────────
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
if TYPE_CHECKING:
    from models.employee import Employee

class Attendance(Base):
    __tablename__ = "attendance"

    id:          Mapped[int]   = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[str]   = mapped_column(
        String(50), ForeignKey("employees.employee_id", ondelete="CASCADE"),
        nullable=False
    )
    name:        Mapped[str]   = mapped_column(String(100), nullable=False)
    timestamp:   Mapped[datetime] = mapped_column(DateTime, nullable=False)
    confidence:  Mapped[float] = mapped_column(Float, default=0.0)
    created_at:  Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationship back to employee
    employee: Mapped["Employee"] = relationship(  # noqa: F821
        back_populates="attendance_records"
    )

    def __repr__(self) -> str:
        return f"<Attendance {self.employee_id} @ {self.timestamp}>"