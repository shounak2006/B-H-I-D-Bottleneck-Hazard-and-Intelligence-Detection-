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
echo [STEP 1/3] Running Pre-flight Release Verification and Environment Check...
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
echo [STEP 2/3] Checking Optional Web Frontend...
"%PYTHON_CMD%" -m bhid.release.launcher_manager frontend_check
echo.

:: 4. Launch BHID Backend Live Monitoring Service in a Dedicated Terminal
echo [STEP 3/3] Starting BHID Live Crowd Monitoring Pipeline in a Dedicated Window...
start "BHID_BACKEND_SERVICE" cmd /k ""%PYTHON_CMD%" -m bhid.release.launcher_manager start"

echo.
echo ====================================================================
echo    BHID Platform Successfully Launched!
echo    - Process Window Title: BHID_BACKEND_SERVICE
echo    - To stop the system safely, run stop_bhid.bat
echo ====================================================================
echo.
pause
