"""
BHID Video Analysis Service.

Coordinates uploaded video file storage, OpenCV frame extraction, background orchestrator processing,
and progress tracking.
"""

from typing import Dict, Any, Optional
import os
import time
import threading
from pathlib import Path
from bhid.runtime.runtime_orchestrator import RuntimeOrchestrator
from bhid.persistence.persistence_config import PersistenceConfig
from bhid.persistence.persistence_manager import PersistenceManager
from backend.services.telemetry_manager import telemetry_manager


class VideoAnalysisService:
    """Service handling video uploads and background BHID video processing."""

    def __init__(self, upload_dir: Optional[Path] = None):
        self.orchestrator = RuntimeOrchestrator()
        self.upload_dir = upload_dir or Path("bhid/data/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self.latest_metrics: Dict[str, Any] = {}

    def upload_video(self, file_name: str, file_bytes: bytes) -> Dict[str, Any]:
        """Saves uploaded video file and initializes job record."""
        session_id = f"session_video_{int(time.time())}"
        safe_filename = f"{session_id}_{Path(file_name).name}"
        target_path = self.upload_dir / safe_filename

        with open(target_path, "wb") as f:
            f.write(file_bytes)

        # Inspect video parameters via OpenCV if available
        total_frames = 100
        fps = 25.0
        try:
            import cv2
            cap = cv2.VideoCapture(str(target_path))
            if cap.isOpened():
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 100
                fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
                cap.release()
        except Exception:
            pass

        job_info = {
            "session_id": session_id,
            "filename": safe_filename,
            "original_filename": file_name,
            "file_path": str(target_path),
            "status": "UPLOADED",
            "frames_processed": 0,
            "total_frames": total_frames,
            "fps": fps,
            "progress": 0.0,
            "start_time": None,
            "end_time": None
        }

        self.active_jobs[session_id] = job_info
        return job_info

    def start_analysis(self, session_id: str) -> Dict[str, Any]:
        """Launches video analysis in a background worker thread."""
        if session_id not in self.active_jobs:
            return {"status": "ERROR", "message": f"Session '{session_id}' not found."}

        job = self.active_jobs[session_id]
        if job["status"] == "PROCESSING":
            return {"status": "ALREADY_PROCESSING", "session_id": session_id}

        job["status"] = "PROCESSING"
        job["start_time"] = time.time()

        thread = threading.Thread(
            target=self._run_video_processing_thread,
            args=(session_id,),
            daemon=True
        )
        thread.start()

        return {"status": "STARTED", "session_id": session_id}

    def _run_video_processing_thread(self, session_id: str):
        """Worker thread processing video frames through BHID orchestrator."""
        job = self.active_jobs.get(session_id)
        if not job:
            return

        video_path = job["file_path"]
        p_config = PersistenceConfig(session_id=session_id)
        pm = PersistenceManager(config=p_config)

        def telemetry_callback(frame_res: Dict[str, Any]):
            job["frames_processed"] = frame_res.get("frame_id", job["frames_processed"] + 1)
            total = job["total_frames"] or 1
            job["progress"] = min(100.0, round((job["frames_processed"] / total) * 100.0, 1))

            pred = frame_res.get("prediction_result", {})
            snapshot = frame_res.get("monitoring_snapshot", {})

            telemetry_payload = {
                "session_id": session_id,
                "timestamp": snapshot.get("timestamp", time.time()),
                "frame_id": job["frames_processed"],
                "total_frames": job["total_frames"],
                "progress_pct": job["progress"],
                "pedestrian_count": snapshot.get("pedestrian_count", 0),
                "density_ped_per_m2": snapshot.get("density_ped_per_m2", 0.0),
                "prediction_probability": pred.get("prediction_probability", 0.0),
                "risk_level": pred.get("risk_level", "LOW"),
                "binary_prediction": pred.get("binary_prediction", 0),
                "active_events_count": snapshot.get("active_event_count", 0),
                "active_events": snapshot.get("active_events", [])
            }

            self.latest_metrics = telemetry_payload
            telemetry_manager.broadcast(telemetry_payload)

        try:
            self.orchestrator.process_video_file(
                video_path=video_path,
                telemetry_callback=telemetry_callback,
                session_id=session_id
            )
            job["status"] = "COMPLETED"
        except Exception as e:
            job["status"] = "FAILED"
            job["error"] = str(e)
        finally:
            job["end_time"] = time.time()
            self.orchestrator.shutdown_bhid(persistence_manager=pm)

    def stop_analysis(self, session_id: str) -> Dict[str, Any]:
        """Stops active video analysis job."""
        job = self.active_jobs.get(session_id)
        if job:
            job["status"] = "STOPPED"
            return {"status": "STOPPED", "session_id": session_id}
        return {"status": "ERROR", "message": "Session not found."}

    def get_status(self, session_id: str) -> Dict[str, Any]:
        """Returns processing status and progress for a session."""
        return self.active_jobs.get(session_id, {"status": "NOT_FOUND"})

    def get_current_metrics(self) -> Dict[str, Any]:
        """Returns latest broadcast telemetry metrics."""
        return self.latest_metrics
