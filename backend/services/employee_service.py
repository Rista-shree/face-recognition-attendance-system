# ─────────────────────────────────────────────
#  backend/services/employee_service.py
# ─────────────────────────────────────────────

from typing import List, Optional

from fastapi            import HTTPException, status
from sqlalchemy         import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.employee  import Employee
from schemas.employee import EmployeeCreate, EmployeeUpdate


async def get_all_employees(db: AsyncSession) -> List[Employee]:
    result = await db.execute(select(Employee).order_by(Employee.name))
    return list(result.scalars().all())


async def get_employee(db: AsyncSession, employee_id: str) -> Employee:
    result = await db.execute(
        select(Employee).where(Employee.employee_id == employee_id)
    )
    emp = result.scalar_one_or_none()
    if not emp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee '{employee_id}' not found",
        )
    return emp


async def create_employee(db: AsyncSession, data: EmployeeCreate) -> Employee:
    # Check for duplicate ID
    existing = await db.execute(
        select(Employee).where(Employee.employee_id == data.employee_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee ID '{data.employee_id}' already exists",
        )

    emp = Employee(**data.model_dump())
    db.add(emp)
    await db.flush()
    await db.refresh(emp)
    return emp


async def update_employee(db: AsyncSession, employee_id: str,
                           data: EmployeeUpdate) -> Employee:
    emp = await get_employee(db, employee_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(emp, field, value)
    await db.flush()
    await db.refresh(emp)
    return emp


async def delete_employee(db: AsyncSession, employee_id: str) -> None:
    emp = await get_employee(db, employee_id)
    await db.delete(emp)
    await db.flush()