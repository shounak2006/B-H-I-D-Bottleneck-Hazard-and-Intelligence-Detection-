@echo off
TITLE BHID Platform Launcher - v1.0
COLOR 0A
cls

echo ====================================================================
echo    BHID - Bottleneck Hazard and Intelligence Detection Platform v1.0
echo ====================================================================
echo.

:: 1. Auto-detect Python Virtual Environment
set "PYTHON_CMD=python"
if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
    echo [INFO] Python Virtual Environment Detected: venv\Scripts\python.exe
) else (
    echo [INFO] Using System Python Environment
)
echo.

:: 2. Pre-flight Environment and Release Verification Check
echo [STEP 1/4] Running Pre-flight Release Verification and Environment Check...
"%PYTHON_CMD%" -m bhid.release.launcher_manager check
if %ERRORLEVEL% NEQ 0 (
    COLOR 0C
    echo [ERROR] Pre-flight release verification failed. Cannot start BHID.
    pause
    exit /b 1
)
echo [OK] Environment and Release Verification Passed.
echo.

:: 3. Informational Frontend Detection Check
echo [STEP 2/4] Verifying Frontend Application...
"%PYTHON_CMD%" -m bhid.release.launcher_manager frontend_check
echo.

:: 4. Launch BHID FastAPI Dedicated Backend Service (Port 8000)
echo [STEP 3/4] Starting BHID FastAPI Backend Service on http://localhost:8000...
start "BHID_BACKEND_SERVICE" cmd /k ""%PYTHON_CMD%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

:: 5. Launch BHID React/Vite Dedicated Frontend (Port 5173)
echo [STEP 4/4] Starting BHID React/Vite Frontend Dashboard on http://localhost:5173...
if exist "%~dp0frontend\node_modules" (
    start "BHID_FRONTEND_SERVICE" cmd /k "cd /d "%~dp0frontend" && npm run dev"
) else (
    echo [INFO] First-time setup: Installing frontend npm dependencies...
    start "BHID_FRONTEND_SERVICE" cmd /k "cd /d "%~dp0frontend" && npm install && npm run dev"
)

echo.
echo ====================================================================
echo    BHID Platform Successfully Launched!
echo    - Backend API:  http://localhost:8000 (Swagger: http://localhost:8000/docs)
echo    - Frontend Dashboard: http://localhost:5173
echo    - To stop the system safely, run stop_bhid.bat
echo ====================================================================
echo.

:: Automatically open default browser
timeout /t 3 >nul
start http://localhost:5173
pause
