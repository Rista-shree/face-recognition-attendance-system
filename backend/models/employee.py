# ─────────────────────────────────────────────
#  backend/models/employee.py
# ─────────────────────────────────────────────
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
if TYPE_CHECKING:
    from models.attendance import Attendance
class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name:        Mapped[str] = mapped_column(String(100), nullable=False)
    department:  Mapped[str] = mapped_column(String(100), nullable=True)
    email:       Mapped[str] = mapped_column(String(150), nullable=True, unique=True)
    is_active:   Mapped[bool] = mapped_column(default=True)
    created_at:  Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationship to attendance records
    attendance_records: Mapped[list["Attendance"]] = relationship(  # noqa: F821
        back_populates="employee", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Employee {self.employee_id} – {self.name}>"