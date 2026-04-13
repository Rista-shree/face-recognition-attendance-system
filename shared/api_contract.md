API Contract
Base URL: http://localhost:8000
Auth Endpoints
POST /api/auth/login
No authentication required.
Request body:
{
  "username": "admin",
  "password": "admin123"
}
Response:
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
POST /api/auth/refresh
No authentication required.
Request body:
{
  "refresh_token": "eyJhbGci..."
}
Response:
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer"
}
GET /api/auth/me
Requires Bearer token.
Header:
Authorization: Bearer <access_token>
Response:
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true
}
POST /api/auth/register
No authentication required.
Request body:
{
  "username": "john",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "staff"
}
Role must be either "admin" or "staff".
Response:
{
  "id": 2,
  "username": "john",
  "email": "john@example.com",
  "role": "staff",
  "is_active": true
}
Employee Endpoints
GET /api/employees/
Requires Bearer token.
Header:
Authorization: Bearer <access_token>
Response:
[
  {
    "employee_id": "emp001",
    "name": "Alice Smith",
    "department": "Engineering",
    "email": "alice@example.com",
    "is_active": true,
    "created_at": "2025-04-07T09:00:00"
  }
]
GET /api/employees/{employee_id}
Requires Bearer token.
Example: GET /api/employees/emp001
Response:
{
  "employee_id": "emp001",
  "name": "Alice Smith",
  "department": "Engineering",
  "email": "alice@example.com",
  "is_active": true,
  "created_at": "2025-04-07T09:00:00"
}
POST /api/employees/
Requires Bearer token with admin role.
Header:
Authorization: Bearer <access_token>
Request body:
{
  "employee_id": "emp001",
  "name": "Alice Smith",
  "department": "Engineering",
  "email": "alice@example.com"
}
Department and email are optional.
Response: 201 Created
{
  "employee_id": "emp001",
  "name": "Alice Smith",
  "department": "Engineering",
  "email": "alice@example.com",
  "is_active": true,
  "created_at": "2025-04-07T09:00:00"
}
PATCH /api/employees/{employee_id}
Requires Bearer token with admin role.
All fields are optional. Only send the fields you want to update.
Request body:
{
  "name": "Alice Johnson",
  "department": "HR",
  "email": "alicejohnson@example.com",
  "is_active": true
}
Response: Updated employee object.
DELETE /api/employees/{employee_id}
Requires Bearer token with admin role.
Response: 204 No Content
Note: Deleting an employee also deletes all their attendance records due to CASCADE.
Attendance Endpoints
POST /api/attendance/bulk
Used by the desktop app to sync records. Does not use Bearer token.
Header:
X-API-Key: dev-api-key-change-me
Request body is a list of records:
[
  {
    "employee_id": "emp001",
    "name": "Alice Smith",
    "timestamp": "2025-04-07T09:14:32",
    "confidence": 0.87
  },
  {
    "employee_id": "emp002",
    "name": "Bob Johnson",
    "timestamp": "2025-04-07T09:15:01",
    "confidence": 0.85
  }
]
Response:
{
  "inserted": 2
}
GET /api/attendance/today
Requires Bearer token.
Response:
{
  "date": "2025-04-07",
  "total_present": 5,
  "records": [
    {
      "id": 1,
      "employee_id": "emp001",
      "name": "Alice Smith",
      "timestamp": "2025-04-07T09:14:32",
      "confidence": 0.87
    }
  ]
}
GET /api/attendance/date/{date}
Requires Bearer token.
Date format: YYYY-MM-DD
Example: GET /api/attendance/date/2025-04-07
Response: Same structure as /today but for the specified date.
GET /api/attendance/employee/{employee_id}
Requires Bearer token.
Optional query parameter: limit (default 100, max 500)
Example: GET /api/attendance/employee/emp001?limit=50
Response:
[
  {
    "id": 1,
    "employee_id": "emp001",
    "name": "Alice Smith",
    "timestamp": "2025-04-07T09:14:32",
    "confidence": 0.87
  }
]
GET /api/attendance/monthly/{year}/{month}
Requires Bearer token.
Example: GET /api/attendance/monthly/2025/4
Response:
[
  {
    "day": "2025-04-01",
    "present": 8
  },
  {
    "day": "2025-04-02",
    "present": 11
  }
]
Used by the monthly chart in the web dashboard.
Report Endpoints
GET /api/reports/export/csv
Requires Bearer token.
Query parameters:
start   YYYY-MM-DD   Start date (defaults to today)
end     YYYY-MM-DD   End date (defaults to today)
Example: GET /api/reports/export/csv?start=2025-04-01&end=2025-04-07
Response: CSV file download with headers:
ID, Employee ID, Name, Timestamp, Confidence
GET /api/reports/department-summary
Requires Bearer token.
Query parameter:
target_date   YYYY-MM-DD   Defaults to today
Example: GET /api/reports/department-summary?target_date=2025-04-07
Response:
[
  {
    "department": "Engineering",
    "present": 5
  },
  {
    "department": "HR",
    "present": 3
  }
]
Health Check
GET /health
No authentication required.
Response:
{
  "status": "ok",
  "version": "1.0.0"
}
Error Responses
All errors follow this structure:
{
  "detail": "Error message here"
}
Common status codes:
200   Success
201   Created
204   No Content (delete)
400   Bad Request
401   Unauthorized (missing or invalid token)
403   Forbidden (wrong role or wrong API key)
404   Not Found
409   Conflict (duplicate employee ID or username)
422   Validation Error (wrong data types or missing fields)
500   Internal Server Error
Authentication Types
Bearer token    Used by the web dashboard for all protected endpoints
                Header: Authorization: Bearer <access_token>

X-API-Key       Used by the desktop app for the bulk sync endpoint only
                Header: X-API-Key: <DESKTOP_API_KEY from .env>

Admin role      Some endpoints require the user to have role = "admin"
                Staff users get 403 Forbidden on those endpoints