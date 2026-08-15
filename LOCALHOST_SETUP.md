# BHID v1.0 - Localhost Web Platform Setup Guide

This guide details how to install, launch, and operate the **Bottleneck Hazard and Intelligence Detection (BHID)** v1.0 full-stack localhost web application (FastAPI backend + React/Vite/TailwindCSS frontend).

---

## 1. Prerequisites

- **Python**: Python `3.9`, `3.10`, `3.11`, or `3.12` (64-bit).
- **Node.js**: Node.js `v18.0.0+` (includes `npm`).
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS.

---

## 2. Quick Start (One-Click Launch)

### Launching the Full-Stack Localhost Web Application
Double-click `start_bhid.bat` in the project root directory or run from Windows Command Prompt:

```cmd
.\start_bhid.bat
```

What `start_bhid.bat` does automatically:
1. **Runs Pre-flight Release Verification**: Validates Python environment and model registry artifacts.
2. **Launches FastAPI Dedicated Backend**: Starts `uvicorn backend.main:app --host 127.0.0.1 --port 8000` on `http://localhost:8000`.
3. **Launches React/Vite Frontend**: Starts `npm run dev` in `frontend/` on `http://localhost:5173`.
4. **Opens Default Browser**: Automatically navigates your browser to `http://localhost:5173`.

---

### Stopping the Localhost Web Application
Double-click `stop_bhid.bat` in the project root directory or run:

```cmd
.\stop_bhid.bat
```

What `stop_bhid.bat` does automatically:
1. Invokes `shutdown_bhid()` to flush all persistence buffers and close active sessions cleanly.
2. Terminates dedicated backend and frontend command windows (`BHID_BACKEND_SERVICE` and `BHID_FRONTEND_SERVICE`).

---

## 3. Manual Component Launching

### Launching Backend Independently

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Interactive API Swagger Docs**: `http://localhost:8000/docs`
- **ReDoc Specification**: `http://localhost:8000/redoc`
- **WebSocket Telemetry Stream**: `ws://localhost:8000/ws/telemetry`

### Launching Frontend Independently

```bash
cd frontend
npm install
npm run dev
```

- **Frontend Dashboard**: `http://localhost:5173`
