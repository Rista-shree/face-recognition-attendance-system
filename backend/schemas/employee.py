# ─────────────────────────────────────────────
#  backend/schemas/employee.py
# ─────────────────────────────────────────────

from datetime import datetime
from typing   import Optional
from pydantic import BaseModel, EmailStr


class EmployeeCreate(BaseModel):
    employee_id: str
    name:        str
    department:  Optional[str] = None
    email:       Optional[EmailStr] = None


class EmployeeUpdate(BaseModel):
    name:       Optional[str] = None
    department: Optional[str] = None
    email:      Optional[EmailStr] = None
    is_active:  Optional[bool] = None


class EmployeeOut(BaseModel):
    employee_id: str
    name:        str
    department:  Optional[str]
    email:       Optional[str]
    is_active:   bool
    created_at:  datetime

    class Config:
        from_attributes = True