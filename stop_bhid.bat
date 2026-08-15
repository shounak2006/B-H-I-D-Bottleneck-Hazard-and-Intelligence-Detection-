@echo off
TITLE BHID Shutdown Controller
COLOR 0E
cls

echo ====================================================================
echo    BHID Platform Graceful Shutdown Controller
echo ====================================================================
echo.

:: Auto-detect Python Virtual Environment
set "PYTHON_CMD=python"
if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
)

:: 1. Call shutdown_bhid() to flush persistence buffers and close active sessions
echo [STEP 1/2] Invoking Graceful Shutdown & Persistence Flush...
"%PYTHON_CMD%" -m bhid.release.launcher_manager stop

:: 2. Close titled BHID Backend Service Command Window safely
echo [STEP 2/2] Safely closing dedicated BHID terminal windows...
taskkill /FI "WINDOWTITLE eq BHID_BACKEND_SERVICE*" /F >nul 2>&1

echo.
echo ====================================================================
echo    BHID Platform Shutdown Complete. All buffers flushed cleanly.
echo ====================================================================
echo.
pause
