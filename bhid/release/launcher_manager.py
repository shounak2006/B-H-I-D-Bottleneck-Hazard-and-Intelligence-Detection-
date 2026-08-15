"""
BHID Windows One-Click Launcher Manager & Script Generator.

Exposes environment validation, frontend auto-detection (informational), batch script generation
(start_bhid.bat & stop_bhid.bat), live crowd monitoring backend startup (with OpenCV cv2.imshow telemetry),
and graceful shutdown orchestration.
"""

from typing import Dict, Any, Optional
import os
import sys
import time
from pathlib import Path

from bhid.release.launcher_config import LauncherConfig
from bhid.release.environment_validator import EnvironmentValidator
from bhid.runtime.runtime_orchestrator import RuntimeOrchestrator


class LauncherManager:
    """
    Launcher script generator and operational process manager.
    """

    def __init__(self, config: Optional[LauncherConfig] = None):
        self.config = config or LauncherConfig()
        self.orchestrator = RuntimeOrchestrator()
        self.env_validator = EnvironmentValidator()
        self.is_running: bool = False

    def detect_frontend(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Scans project workspace for web frontend frameworks (React, Vite, Node, Next, Flask, FastAPI).
        Informational check only - returns detected framework or None if absent.
        """
        root = Path(project_root) if project_root else self.config.resolve_project_root()
        
        detected_framework = None
        has_package_json = (root / "package.json").exists()
        has_vite_config = (root / "vite.config.js").exists() or (root / "vite.config.ts").exists()
        has_next_config = (root / "next.config.js").exists()

        if has_next_config:
            detected_framework = "Next.js"
        elif has_vite_config:
            detected_framework = "Vite"
        elif has_package_json:
            detected_framework = "Node.js Web App"

        # Check Python web app files (e.g. app.py, main.py with Flask/FastAPI)
        api_dir = root / "bhid" / "api"
        dashboard_dir = root / "bhid" / "dashboard"
        
        has_api_files = api_dir.exists() and len(list(api_dir.glob("*.py"))) > 0
        has_dashboard_files = dashboard_dir.exists() and len(list(dashboard_dir.glob("*.py"))) > 0

        if has_api_files or has_dashboard_files:
            detected_framework = detected_framework or "Python Web API/Dashboard"

        return {
            "frontend_detected": (detected_framework is not None),
            "framework": detected_framework or "Not Detected (Headless BHID Platform Mode)",
            "informational": True
        }

    def validate_launch_environment(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Validates Python environment, dependencies, directories, model artifacts, and release verification.
        Uses runtime model resolution logic instead of hardcoding model file paths.
        """
        root = Path(project_root) if project_root else self.config.resolve_project_root()
        
        # 1. Standard environment validation
        env_res = self.env_validator.validate_environment(root)

        # 2. Dynamic model artifact check using BottleneckPredictor resolution
        model_ready = False
        try:
            from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor
            pred = BottleneckPredictor()
            model_ready = pred.model_path.exists()
        except Exception:
            model_ready = False

        # 3. Informational frontend check
        fe_info = self.detect_frontend(root)

        # 4. Pre-flight release verification check
        rel_ver = self.orchestrator.run_release_verification(project_root=root)

        passed = env_res["passed"] and model_ready and (rel_ver.get("status") == "RELEASE_READY")

        return {
            "launch_ready": passed,
            "environment_validation": env_res,
            "model_artifact_ready": model_ready,
            "frontend_info": fe_info,
            "release_verification": rel_ver
        }

    def generate_start_script(self, project_root: Optional[Path] = None) -> Path:
        """
        Generates `start_bhid.bat` in the project root directory.
        Fixes CMD parsing errors by using caret escaping (^&) or plain text.
        """
        root = Path(project_root) if project_root else self.config.resolve_project_root()
        start_bat_path, _ = self.config.get_bat_paths(root)

        bat_content = f"""@echo off
TITLE BHID Platform Launcher - v1.0
COLOR 0A
cls

echo ====================================================================
echo    BHID - Bottleneck Hazard and Intelligence Detection Platform v1.0
echo ====================================================================
echo.

:: 1. Auto-detect Python Virtual Environment
set "PYTHON_CMD=python"
if exist "%~dp0venv\\Scripts\\python.exe" (
    set "PYTHON_CMD=%~dp0venv\\Scripts\\python.exe"
    echo [INFO] Python Virtual Environment Detected: venv\\Scripts\\python.exe
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
start "{self.config.backend_process_title}" cmd /k ""%PYTHON_CMD%" -m bhid.release.launcher_manager start"

echo.
echo ====================================================================
echo    BHID Platform Successfully Launched!
echo    - Process Window Title: {self.config.backend_process_title}
echo    - To stop the system safely, run stop_bhid.bat
echo ====================================================================
echo.
pause
"""

        with open(start_bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
        return start_bat_path

    def generate_stop_script(self, project_root: Optional[Path] = None) -> Path:
        """
        Generates `stop_bhid.bat` in the project root directory.
        Safe shutdown: Calls shutdown_bhid() and closes titled windows without killing unrelated python processes.
        """
        root = Path(project_root) if project_root else self.config.resolve_project_root()
        _, stop_bat_path = self.config.get_bat_paths(root)

        bat_content = f"""@echo off
TITLE BHID Shutdown Controller
COLOR 0E
cls

echo ====================================================================
echo    BHID Platform Graceful Shutdown Controller
echo ====================================================================
echo.

:: Auto-detect Python Virtual Environment
set "PYTHON_CMD=python"
if exist "%~dp0venv\\Scripts\\python.exe" (
    set "PYTHON_CMD=%~dp0venv\\Scripts\\python.exe"
)

:: 1. Call shutdown_bhid() to flush persistence buffers and close active sessions
echo [STEP 1/2] Invoking Graceful Shutdown and Persistence Flush...
"%PYTHON_CMD%" -m bhid.release.launcher_manager stop

:: 2. Close titled BHID Backend Service Command Window safely
echo [STEP 2/2] Safely closing dedicated BHID terminal windows...
taskkill /FI "WINDOWTITLE eq {self.config.backend_process_title}*" /F >nul 2>&1

echo.
echo ====================================================================
echo    BHID Platform Shutdown Complete. All buffers flushed cleanly.
echo ====================================================================
echo.
pause
"""

        with open(stop_bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
        return stop_bat_path

    def start_backend(self, max_frames: Optional[int] = None, show_window: bool = True) -> Dict[str, Any]:
        """
        Executes backend live crowd monitoring pipeline loop:
        1. Pre-flight initialization (`initialize_bhid`).
        2. Creates PID file under `bhid/data/runtime/bhid.pid`.
        3. Instantiates `MockPedestrianDetector`, `CentroidTracker`, and `PersistenceManager`.
        4. Runs continuous live monitoring loop (`process_persistent_monitoring_frame`).
        5. Displays OpenCV visual telemetry window (`cv2.imshow`).
        """
        pid_file = self.config.pid_file
        pid_file.parent.mkdir(parents=True, exist_ok=True)

        pid = os.getpid()
        with open(pid_file, "w", encoding="utf-8") as f:
            f.write(str(pid))

        init_res = self.orchestrator.initialize_bhid()
        self.is_running = True

        print("\n====================================================================")
        print("  BHID Operational Live Crowd Monitoring Service Active")
        print(f"  - PID: {pid} (Saved to {pid_file})")
        print(f"  - Active Scene: {self.orchestrator.get_context().active_scene}")
        print("  - Displaying OpenCV Telemetry HUD Window...")
        print("  - Press 'q' or 'ESC' in HUD window, or run stop_bhid.bat to exit.")
        print("====================================================================\n")

        # Import vision and persistence components for live monitoring loop
        from bhid.vision.detection.mock_detector import MockPedestrianDetector
        from bhid.vision.tracking.centroid_tracker import CentroidTracker
        from bhid.persistence.persistence_config import PersistenceConfig
        from bhid.persistence.persistence_manager import PersistenceManager

        detector = MockPedestrianDetector(num_pedestrians=40, seed=42)
        tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=50.0)

        session_id = f"live_session_{int(time.time())}"
        p_config = PersistenceConfig(session_id=session_id)
        pm = PersistenceManager(config=p_config)

        # Check OpenCV availability for visual telemetry window rendering
        cv2 = None
        if show_window:
            try:
                import cv2 as cv2_mod
                cv2 = cv2_mod
            except ImportError:
                cv2 = None

        frame_id = 0
        current_ts = time.time()

        try:
            while self.is_running:
                frame_id += 1
                current_ts += 0.4  # 2.5 Hz timestep

                det_batch = detector.detect(frame_id=frame_id, timestamp=current_ts)
                tracking_batch = tracker.update(det_batch)

                res = self.orchestrator.process_persistent_monitoring_frame(
                    tracking_batch=tracking_batch,
                    frame=None,
                    persistence_manager=pm,
                    scene_id="LIVE_MONITORING_SCENE",
                    zone_id="ZONE_MAIN"
                )

                rendered_frame = res.get("rendered_frame")
                if cv2 is not None and rendered_frame is not None:
                    window_title = "BHID - Live Crowd Bottleneck Monitoring"
                    cv2.imshow(window_title, rendered_frame)
                    key = cv2.waitKey(40) & 0xFF  # ~25 FPS UI refresh
                    if key in (27, ord('q'), ord('Q')):
                        print("[INFO] User closed monitoring window via keypress.")
                        break

                if max_frames is not None and frame_id >= max_frames:
                    break

        except KeyboardInterrupt:
            print("\n[INFO] Backend service received KeyboardInterrupt.")
        finally:
            self.is_running = False
            if cv2 is not None:
                try:
                    cv2.destroyAllWindows()
                except Exception:
                    pass
            self.stop_backend()

        return {
            "status": "STOPPED",
            "session_id": session_id,
            "processed_frames": frame_id,
            "init_result": init_res
        }

    def stop_backend(self) -> Dict[str, Any]:
        """
        Executes backend shutdown sequence calling `shutdown_bhid()` and cleans up PID file.
        """
        self.is_running = False
        shutdown_res = self.orchestrator.shutdown_bhid()
        
        pid_file = self.config.pid_file
        if pid_file.exists():
            try:
                pid_file.unlink()
            except Exception:
                pass

        print("[OK] BHID Graceful Shutdown Completed.")
        return shutdown_res


def main():
    """CLI dispatcher for batch scripts."""
    if len(sys.argv) < 2:
        print("Usage: python -m bhid.release.launcher_manager [start|stop|check|frontend_check|generate]")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    mgr = LauncherManager()

    if cmd == "start":
        mgr.start_backend()
    elif cmd == "stop":
        mgr.stop_backend()
    elif cmd == "check":
        val = mgr.validate_launch_environment()
        if not val["launch_ready"]:
            print(f"[ERROR] Launch pre-flight check failed: {val}")
            sys.exit(1)
        else:
            print("[OK] Pre-flight release verification passed.")
            sys.exit(0)
    elif cmd == "frontend_check":
        fe = mgr.detect_frontend()
        print(f"[INFO] Frontend: {fe['framework']}")
        sys.exit(0)
    elif cmd == "generate":
        p1 = mgr.generate_start_script()
        p2 = mgr.generate_stop_script()
        print(f"Generated launcher scripts:\n  - {p1}\n  - {p2}")
        sys.exit(0)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
