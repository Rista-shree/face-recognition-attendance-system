# ─────────────────────────────────────────────
#  backend/models/user.py
#  Web dashboard login accounts (admins/staff).
#  Separate from Employee — an employee is a
#  person tracked by the system; a user is
#  someone who can log into the dashboard.
# ─────────────────────────────────────────────

from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from database.connection import Base


class User(Base):
    __tablename__ = "users"

    id:         Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    username:   Mapped[str]  = mapped_column(String(50), unique=True, nullable=False)
    email:      Mapped[str]  = mapped_column(String(150), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role:       Mapped[str]  = mapped_column(String(20), default="staff")
    # Roles: "admin" | "staff"
    is_active:  Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"