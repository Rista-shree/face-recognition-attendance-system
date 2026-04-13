# Architecture

---

## Overview

The Face Attendance System is a hybrid application with three separate layers that communicate over HTTP.

```
+------------------+         +------------------+         +------------------+
|   Desktop App    |  HTTP   |   Backend API    |  HTTP   |  Web Dashboard   |
|   Python 3.11    | ------> |   FastAPI        | <------ |   React + Vite   |
|   Tkinter        |         |   SQLite         |         |   Recharts       |
|   OpenCV LBPH    |         |   JWT Auth       |         |   Zustand        |
+------------------+         +------------------+         +------------------+
        |                            |                            |
        v                            v                            v
  Local SQLite              Backend SQLite               Browser localStorage
  attendance.db             attendance.db                JWT tokens
  emp001.yml models
```

The desktop app handles all face recognition locally for speed. It syncs records to the backend periodically. The web dashboard reads from the backend to display reports and manage employees.

---

## Layer 1 - Desktop App

### Purpose

Runs on the machine with the webcam. Handles camera capture, face detection, face recognition, and local attendance logging.

### Technology

```
Language     Python 3.11
UI           Tkinter + ttkbootstrap
Detection    OpenCV Haar Cascade
Recognition  OpenCV LBPH (Local Binary Patterns Histograms)
Database     SQLite via sqlite3 (built-in)
HTTP         requests
```

### Folder Structure

```
desktop/
├── main.py                          entry point
├── config/
│   └── settings.py                  all configuration values
├── core/
│   ├── camera.py                    webcam thread
│   ├── encoder.py                   face detection + LBPH recognition
│   ├── face_recognizer.py           wraps encoder, returns typed results
│   └── face_detector.py             draws bounding boxes on frames
├── services/
│   ├── attendance_service.py        writes to local SQLite
│   ├── sync_service.py              pushes records to backend API
│   └── auth_service.py              JWT login + token storage
├── ui/
│   ├── main_window.py               root Tkinter window
│   ├── dashboard.py                 live recognition tab
│   └── components/
│       ├── camera_feed.py           video display widget
│       └── status_panel.py          stats and live log panel
└── models/
    └── known_faces/                 emp001.yml, emp002.yml ...
```

### Face Recognition Approach

Detection uses Haar Cascade which ships inside opencv-contrib-python. No download needed.

Recognition uses LBPH which is a classical machine learning algorithm. Each employee gets their own trained model saved as a .yml file. The model is updated incrementally every time a new face sample is registered.

LBPH was chosen because it works on Python 3.14, requires no GPU, no dlib, no cmake, and no build tools. It installs with a single pip install command.

### Threading Model

```
Main thread       Tkinter event loop, UI updates
Camera thread     Continuously reads webcam frames (daemon)
Recognition thread  Grabs frames, runs detection and recognition (daemon)
Sync thread       Pushes unsynced records to backend every 60s (daemon)
```

All daemon threads automatically stop when the main window is closed.

---

## Layer 2 - Backend API

### Purpose

Receives synced attendance records from the desktop app. Serves data to the web dashboard. Handles user authentication.

### Technology

```
Language     Python 3.11
Framework    FastAPI
ORM          SQLAlchemy (async)
Database     SQLite via aiosqlite
Auth         JWT via python-jose + bcrypt via passlib
Server       Uvicorn
```

### Folder Structure

```
backend/
├── main.py                          FastAPI app, routers, CORS, lifespan
├── config/
│   └── settings.py                  reads from .env via pydantic-settings
├── database/
│   └── connection.py                async engine, session factory, get_db()
├── models/
│   ├── employee.py                  employees table ORM model
│   ├── attendance.py                attendance table ORM model
│   └── user.py                      users table ORM model
├── schemas/
│   ├── auth.py                      login, token, user Pydantic schemas
│   ├── employee.py                  employee request and response schemas
│   └── attendance.py                attendance request and response schemas
├── api/
│   ├── dependencies.py              JWT guard, admin guard, API key guard
│   └── routes/
│       ├── auth.py                  /api/auth/* endpoints
│       ├── employees.py             /api/employees/* endpoints
│       ├── attendance.py            /api/attendance/* endpoints
│       └── reports.py               /api/reports/* endpoints
└── services/
    ├── auth_service.py              bcrypt and JWT logic
    ├── employee_service.py          employee CRUD queries
    ├── attendance_service.py        attendance queries and bulk insert
    └── report_service.py            CSV generation and department summary
```

### Database Tables

```
users
  id               integer primary key
  username         text unique
  email            text unique
  hashed_password  text (bcrypt)
  role             text (admin or staff)
  is_active        integer (0 or 1)
  created_at       text (ISO datetime)

employees
  employee_id      text primary key (e.g. emp001)
  name             text
  department       text
  email            text unique
  is_active        integer
  created_at       text

attendance
  id               integer primary key autoincrement
  employee_id      text (foreign key to employees, cascade delete)
  name             text
  timestamp        text (ISO datetime)
  confidence       real (0.0 to 1.0)
  created_at       text
```

### Request Lifecycle

```
HTTP request arrives
       |
       v
FastAPI router matches URL and method
       |
       v
Dependencies run (get_db, get_current_user, verify_desktop_key)
       |
       v
Route function runs with injected db session and user
       |
       v
Route calls service function with business logic
       |
       v
Service queries or writes to SQLite via SQLAlchemy
       |
       v
Route returns Pydantic schema response
       |
       v
HTTP response sent to client
```

---

## Layer 3 - Web Dashboard

### Purpose

Browser-based interface for admins to view attendance records, manage employees, export reports, and create user accounts.

### Technology

```
Framework    React 18
Build tool   Vite
Routing      react-router-dom
State        Zustand with localStorage persistence
HTTP         Axios with JWT interceptors
Charts       Recharts
Date utils   date-fns
```

### Folder Structure

```
web/src/
├── App.jsx                          router setup and auth guard
├── index.css                        global CSS variables and resets
├── main.jsx                         ReactDOM entry point
├── pages/
│   ├── Login.jsx                    login screen
│   ├── Dashboard.jsx                today's stats, charts, records table
│   ├── Employees.jsx                employee grid with CRUD modal
│   ├── Reports.jsx                  date range search and CSV export
│   └── Settings.jsx                 create dashboard users
├── components/
│   ├── Layout.jsx                   sidebar + outlet wrapper
│   ├── AttendanceTable.jsx          reusable records table
│   ├── EmployeeCard.jsx             employee card with edit and delete
│   └── charts/
│       ├── DailyChart.jsx           bar chart grouped by hour
│       └── MonthlyChart.jsx         line chart grouped by day
├── services/
│   ├── api.js                       Axios instance with auth interceptors
│   ├── attendanceApi.js             attendance endpoint wrappers
│   └── employeeApi.js               employee endpoint wrappers
├── store/
│   ├── authStore.js                 JWT tokens and user profile
│   └── attendanceStore.js           today and monthly attendance data
└── utils/
    ├── formatDate.js                date formatting helpers
    └── exportCSV.js                 triggers CSV file download
```

### Token Refresh Flow

```
Request sent with expired access token
       |
       v
Backend returns 401 Unauthorized
       |
       v
api.js interceptor catches the 401
       |
       v
POST /api/auth/refresh with refresh token
       |
       v
New access token received and saved to localStorage
       |
       v
Original request retried with new token
       |
       v
Response returned to component as if nothing happened
```

---

## Data Flow

### Registration Flow

```
Admin opens web dashboard
       |
       v
Employees page > Add Employee > fill form > POST /api/employees/
       |
       v
Backend saves to employees table

(separately on the desktop app)

Admin clicks + Register Face
       |
       v
Enter same employee_id and name
       |
       v
Look at camera
       |
       v
Haar Cascade detects face
       |
       v
LBPH trains a model from the face crop
       |
       v
Model saved as models/known_faces/emp001.yml
       |
       v
Employee saved to local SQLite
```

### Recognition Flow

```
Camera frame captured (background thread)
       |
       v
Haar Cascade detectMultiScale finds face rectangles
       |
       v
Each face is cropped, grayscaled, and resized to 200x200
       |
       v
LBPH predict() compares against every employee model
       |
       v
Best match below threshold is accepted as a recognition
       |
       v
Confidence = 1 - (distance / threshold)
       |
       v
AttendanceService checks 30 second cooldown
       |
       v
If cooldown passed: INSERT INTO attendance WHERE synced=0
       |
       v
FaceDetector draws name label on frame copy
       |
       v
CameraFeedWidget displays annotated frame at 20fps
```

### Sync Flow

```
SyncService wakes up every 60 seconds
       |
       v
SELECT * FROM attendance WHERE synced = 0
       |
       v
POST /api/attendance/bulk with X-API-Key header
       |
       v
Backend verifies API key
       |
       v
Backend inserts all records into its SQLite
       |
       v
Backend returns { "inserted": N }
       |
       v
UPDATE attendance SET synced = 1 WHERE id IN (...)
       |
       v
Status panel shows checkmark: All synced
```

---

## Security

```
JWT access tokens       Short lived (60 minutes). Signed with SECRET_KEY.
JWT refresh tokens      Long lived (7 days). Used only to get new access tokens.
bcrypt password hash    One-way hash. Plain passwords never stored.
X-API-Key               Static key shared between desktop and backend.
                        Must be changed from default in production.
Role-based access       Admin role required for create, update, delete.
                        Staff role is read-only.
Token file obfuscation  Desktop stores JWT with XOR obfuscation and chmod 600.
                        Not true encryption. Use keyring library for production.
CORS                    Backend only accepts requests from configured origins.
                        Defaults to localhost:5173 for development.
```

---

## Deployment Options

### Option 1 - All Local (Development)

Run all three parts on the same machine.

```
Terminal 1: cd backend && uvicorn main:app --reload
Terminal 2: cd web && npm run dev
Terminal 3: cd desktop && python main.py
```

### Option 2 - Docker (Backend + Web)

Backend and web run in Docker containers. Desktop still runs natively because it needs webcam access.

```
cd docker
docker compose up --build
```

Backend: http://localhost:8000

Web: http://localhost:80

### Option 3 - Production Server

Host backend and web on a cloud server. Desktop app connects to the server URL.

Change in `desktop/config/settings.py`:

```python
API_BASE_URL = "https://your-server.com"
```

Change in `web/src/services/api.js`:

```js
baseURL: "https://your-server.com"
```