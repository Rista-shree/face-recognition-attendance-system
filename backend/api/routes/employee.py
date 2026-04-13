# ─────────────────────────────────────────────
#  backend/api/routes/employees.py
# ─────────────────────────────────────────────

from fastapi import APIRouter, status
from typing  import List

from api.dependencies    import DBSession, CurrentUser, AdminUser
from schemas.employee    import EmployeeCreate, EmployeeUpdate, EmployeeOut
from services            import employee_service

router = APIRouter(prefix="/api/employees", tags=["Employees"])


@router.get("/", response_model=List[EmployeeOut])
async def list_employees(db: DBSession, _: CurrentUser):
    """Return all employees. Requires authentication."""
    return await employee_service.get_all_employees(db)


@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: str, db: DBSession, _: CurrentUser):
    return await employee_service.get_employee(db, employee_id)


@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate, db: DBSession,_:AdminUser):
    """Create a new employee. Admin only."""
    return await employee_service.create_employee(db, payload)


@router.patch("/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: str, payload: EmployeeUpdate,
                           db: DBSession, _: AdminUser):
    """Update employee fields. Admin only."""
    return await employee_service.update_employee(db, employee_id, payload)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee_id: str, db: DBSession, _: AdminUser):
    """Delete an employee and all their attendance records. Admin only."""
    await employee_service.delete_employee(db, employee_id)