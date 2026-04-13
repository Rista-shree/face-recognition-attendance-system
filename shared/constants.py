# ─────────────────────────────────────────────
#  shared/constants.py
#  Constants shared between desktop and backend.
#  Import from here to keep values in sync.
# ─────────────────────────────────────────────

# Attendance
RECOGNITION_COOLDOWN_SECONDS = 30    # minimum gap between two logs for same person
MIN_CONFIDENCE_TO_LOG        = 0.4   # ignore recognitions below this confidence

# Employee roles (mirrors backend User.role)
ROLE_ADMIN = "admin"
ROLE_STAFF = "staff"

# API endpoint paths (keep in sync with backend routers)
API_ATTENDANCE_BULK   = "/api/attendance/bulk"
API_ATTENDANCE_TODAY  = "/api/attendance/today"
API_EMPLOYEES         = "/api/employees"
API_AUTH_LOGIN        = "/api/auth/login"
API_AUTH_REFRESH      = "/api/auth/refresh"
API_REPORTS_CSV       = "/api/reports/export/csv"