# API Documentation

Base URL: http://localhost:8000

Interactive docs: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

---

## Table of Contents

- [Authentication](#authentication)
- [Employees](#employees)
- [Attendance](#attendance)
- [Reports](#reports)
- [Health](#health)
- [Error Reference](#error-reference)

---

## Authentication

### Login

```
POST /api/auth/login
```

No token required.

Request:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Refresh Token

```
POST /api/auth/refresh
```

No token required.

Request:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Get Current User

```
GET /api/auth/me
```

Requires Bearer token.

Header:

```
Authorization: Bearer <access_token>
```

Response:

```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin",
  "is_active": true
}
```

---

### Register New User

```
POST /api/auth/register
```

No token required.

Request:

```json
{
  "username": "john",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "staff"
}
```

Role options: `admin` or `staff`

Response 201:

```json
{
  "id": 2,
  "username": "john",
  "email": "john@example.com",
  "role": "staff",
  "is_active": true
}
```

---

## Employees

### List All Employees

```
GET /api/employees/
```

Requires Bearer token.

Response:

```json
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
```

---

### Get Single Employee

```
GET /api/employees/{employee_id}
```

Requires Bearer token.

Example: `GET /api/employees/emp001`

Response:

```json
{
  "employee_id": "emp001",
  "name": "Alice Smith",
  "department": "Engineering",
  "email": "alice@example.com",
  "is_active": true,
  "created_at": "2025-04-07T09:00:00"
}
```

---

### Create Employee

```
POST /api/employees/
```

Requires Bearer token with admin role.

Request:

```json
{
  "employee_id": "emp001",
  "name": "Alice Smith",
  "department": "Engineering",
  "email": "alice@example.com"
}
```

`department` and `email` are optional.

Response 201:

```json
{
  "employee_id": "emp001",
  "name": "Alice Smith",
  "department": "Engineering",
  "email": "alice@example.com",
  "is_active": true,
  "created_at": "2025-04-07T09:00:00"
}
```

---

### Update Employee

```
PATCH /api/employees/{employee_id}
```

Requires Bearer token with admin role.

All fields are optional. Only include what you want to change.

Request:

```json
{
  "name": "Alice Johnson",
  "department": "HR",
  "is_active": false
}
```

Response: Updated employee object.

---

### Delete Employee

```
DELETE /api/employees/{employee_id}
```

Requires Bearer token with admin role.

Response: 204 No Content

Note: All attendance records for this employee are also deleted.

---

## Attendance

### Bulk Sync from Desktop

```
POST /api/attendance/bulk
```

Requires X-API-Key header. Used only by the desktop app.

Header:

```
X-API-Key: dev-api-key-change-me
```

Request body is a list:

```json
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
```

Response 201:

```json
{
  "inserted": 2
}
```

---

### Get Today's Attendance

```
GET /api/attendance/today
```

Requires Bearer token.

Response:

```json
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
```

---

### Get Attendance by Date

```
GET /api/attendance/date/{date}
```

Requires Bearer token.

Date format: `YYYY-MM-DD`

Example: `GET /api/attendance/date/2025-04-07`

Response: Same structure as `/today`.

---

### Get Employee Attendance History

```
GET /api/attendance/employee/{employee_id}
```

Requires Bearer token.

Query parameter: `limit` (default 100, max 500)

Example: `GET /api/attendance/employee/emp001?limit=50`

Response:

```json
[
  {
    "id": 1,
    "employee_id": "emp001",
    "name": "Alice Smith",
    "timestamp": "2025-04-07T09:14:32",
    "confidence": 0.87
  }
]
```

---

### Get Monthly Chart Data

```
GET /api/attendance/monthly/{year}/{month}
```

Requires Bearer token.

Example: `GET /api/attendance/monthly/2025/4`

Response:

```json
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
```

---

## Reports

### Export CSV

```
GET /api/reports/export/csv
```

Requires Bearer token.

Query parameters:

```
start   YYYY-MM-DD   Start date (defaults to today)
end     YYYY-MM-DD   End date (defaults to today)
```

Example: `GET /api/reports/export/csv?start=2025-04-01&end=2025-04-07`

Response: CSV file download.

CSV columns: `ID, Employee ID, Name, Timestamp, Confidence`

---

### Department Summary

```
GET /api/reports/department-summary
```

Requires Bearer token.

Query parameter: `target_date` (YYYY-MM-DD, defaults to today)

Example: `GET /api/reports/department-summary?target_date=2025-04-07`

Response:

```json
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
```

---

## Health

### Health Check

```
GET /health
```

No authentication required.

Response:

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## Error Reference

All errors return this structure:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Status codes:

```
200   OK
201   Created
204   No Content
400   Bad Request - invalid input data
401   Unauthorized - token missing, expired, or invalid
403   Forbidden - correct token but wrong role, or wrong API key
404   Not Found - resource does not exist
409   Conflict - duplicate employee ID or username
422   Unprocessable Entity - wrong data types or missing required fields
500   Internal Server Error
```

---

## Authentication Reference

```
Bearer token   Web dashboard endpoints
               Header: Authorization: Bearer <access_token>
               Expires: 60 minutes (configurable in .env)

Refresh token  Used to get a new access token when it expires
               Expires: 7 days (configurable in .env)

X-API-Key      Desktop app bulk sync endpoint only
               Header: X-API-Key: <value from backend .env DESKTOP_API_KEY>

Admin role     Required for create, update, delete employee endpoints
               Users with role "staff" get 403 on these endpoints
```