# Setup Guide

---

## Requirements

Before you start, make sure you have the following installed:

- Python 3.11 (download from https://python.org/downloads)
- Node.js 18 or higher (download from https://nodejs.org)
- A webcam (built-in or USB)
- VS Code or any code editor

To check your versions:

```bash
python --version
node --version
npm --version
```

---

## Step 1 - Set Up the Backend

Open a terminal and navigate to the backend folder.

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

On Windows:

```bash
venv\Scripts\activate
```

On Mac or Linux:

```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Open `.env` and set your values:

```
SECRET_KEY=replace-this-with-a-long-random-string
DESKTOP_API_KEY=replace-this-with-any-password-you-choose
```

The `DESKTOP_API_KEY` can be anything you want. Just remember it because you will need to put the same value in the desktop settings file.

To generate a secure SECRET_KEY, run this in Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your SECRET_KEY.

Start the backend server:

```bash
uvicorn main:app --reload
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

The backend is now running. Leave this terminal open.

To verify it works, open your browser and go to:

```
http://localhost:8000/health
```

You should see:

```json
{"status": "ok", "version": "1.0.0"}
```

Also check the interactive API docs at:

```
http://localhost:8000/docs
```

---

## Step 2 - Set Up the Web Dashboard

Open a new terminal (keep the backend terminal running).

Navigate to the web folder:

```bash
cd web
```

Install dependencies:

```bash
npm install
```

Open `src/services/api.js` and make sure the baseURL points to your backend:

```js
const api = axios.create({
  baseURL: "http://localhost:8000",
  timeout: 15000,
});
```

Start the development server:

```bash
npm run dev
```

You should see:

```
  VITE v5.x.x  ready in xxx ms

  Local:   http://localhost:5173/
```

Open your browser and go to:

```
http://localhost:5173
```

You should see the FaceAttend login page.

Log in with the default credentials:

```
Username: admin
Password: admin123
```

If login works, the web dashboard is set up correctly.

---

## Step 3 - Set Up the Desktop App

Open a new terminal (keep both other terminals running).

Navigate to the desktop folder:

```bash
cd desktop
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

On Windows:

```bash
venv\Scripts\activate
```

On Mac or Linux:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

> **Important:** The project requires `opencv-contrib-python`, NOT `opencv-python`. If you accidentally installed `opencv-python`, uninstall it first:
>
> ```bash
> pip uninstall opencv-python
> pip install opencv-contrib-python
> ```

Open `config/settings.py` and update these two values to match your backend `.env`:

```python
API_BASE_URL    = "http://localhost:8000"
DESKTOP_API_KEY = "replace-this-with-any-password-you-choose"
```

The `DESKTOP_API_KEY` must be the exact same value you set in the backend `.env` file.

If you have an external webcam or multiple cameras, change this:

```python
CAMERA_INDEX = 0
```

Change 0 to 1 for a second camera, 2 for a third, and so on.

Start the desktop app:

```bash
python main.py
```

The Tkinter window should open with the camera feed.

---

## Step 4 - Register Your First Employee

This step connects all three parts of the system together.

### Add the employee in the web dashboard

1. Go to `http://localhost:5173`
2. Log in with admin / admin123
3. Click Employees in the sidebar
4. Click + Add Employee
5. Fill in the form:
   - Employee ID: `emp001` (can be any unique ID you choose)
   - Name: your name or the employee's name
   - Department: optional
   - Email: optional
6. Click Save

### Register the face on the desktop app

1. In the desktop app, click `+ Register Face`
2. Enter the same Employee ID you used in the web dashboard: `emp001`
3. Enter the same Name
4. Look directly at the camera
5. Click OK or confirm
6. You should see a success message

The face model is now saved as `models/known_faces/emp001.yml`.

---

## Step 5 - Test Face Recognition

1. In the desktop app, click `▶ Start`
2. Look at the camera
3. You should see a green bounding box around your face with your name and confidence percentage
4. The status panel on the right should show a log entry like:

```
[09:15:32]  Alice Smith   87%  ✓ Logged
```

5. If you see a red box or "Unknown", the recognition did not match. Try registering your face again under better lighting.

---

## Step 6 - Test the Sync

1. After a check-in is logged on the desktop, click `↑ Sync Now`
2. The sync badge should briefly show a number then change to `✓ All synced`
3. Go to the web dashboard at `http://localhost:5173`
4. Click Dashboard in the sidebar
5. Scroll down to Today's Records
6. Your check-in should appear in the table

If the record appears, the full system is working correctly.

---

## Running the Project Every Time

Every time you want to use the system, you need to start all three parts in separate terminals.

Terminal 1 - Backend:

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

Terminal 2 - Web dashboard:

```bash
cd web
npm run dev
```

Terminal 3 - Desktop app:

```bash
cd desktop
venv\Scripts\activate
python main.py
```

---

## Troubleshooting

### Backend will not start

Check that you activated the virtual environment and that `(venv)` appears in your terminal.

Check that you created the `.env` file from `.env.example`.

Run `pip install -r requirements.txt` again.

---

### Login says invalid username or password

Make sure the backend is running in another terminal before trying to log in.

Make sure `api.js` has `baseURL: "http://localhost:8000"`.

Try the exact credentials: username `admin`, password `admin123`.

---

### Camera does not open

Try changing `CAMERA_INDEX = 1` in `desktop/config/settings.py`.

Make sure no other application is using the webcam at the same time.

---

### Face not recognised

Make sure you registered the face with good lighting and looking directly at the camera.

Register multiple times to give the model more samples.

Try lowering `LBPH_THRESHOLD` in `settings.py` from 80 to 70 for stricter matching, or raise it to 90 for more lenient matching.

---

### Sync not working

Make sure `DESKTOP_API_KEY` in `desktop/config/settings.py` exactly matches `DESKTOP_API_KEY` in `backend/.env`. They must be identical including capitalisation.

Make sure the backend is running when you click Sync Now.

---

### ModuleNotFoundError: No module named config

You must run `python main.py` from inside the `desktop/` folder:

```bash
cd desktop
python main.py
```

Not from the parent folder.

---

### cv2.face module not found

You installed `opencv-python` instead of `opencv-contrib-python`. Fix:

```bash
pip uninstall opencv-python
pip install opencv-contrib-python
```

---

## Changing the Default Admin Password

There is no password change UI yet. To create a new admin and stop using the default:

1. Log in to the web dashboard
2. Go to Settings
3. Create a new user with role admin
4. Log out
5. Log in with your new credentials
6. Go to `http://localhost:8000/docs`
7. Use the auth/register endpoint if you need to update anything

---

## Adding More Employees

Repeat Step 4 for each new employee:

1. Add them in the web dashboard with a unique employee ID
2. Register their face on the desktop app using the same employee ID
3. They will now be recognised by the system

---

## Stopping the Project

Press `Ctrl + C` in each terminal to stop the backend and web server.

Close the desktop app window to stop it. All background threads stop automatically.

Data is saved to SQLite and will persist the next time you start the project.