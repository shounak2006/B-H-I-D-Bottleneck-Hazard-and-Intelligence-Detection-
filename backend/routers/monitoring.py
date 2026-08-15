"""
BHID Monitoring Router.
Exposes live crowd monitoring lifecycle control endpoints and video upload analysis endpoints.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services.monitoring_service import MonitoringService
from backend.services.video_analysis_service import VideoAnalysisService

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])
monitoring_service = MonitoringService()
video_analysis_service = VideoAnalysisService()


class StartMonitoringRequest(BaseModel):
    scene_id: Optional[str] = "LIVE_SCENE"
    zone_id: Optional[str] = "ZONE_MAIN"


@router.post("/start")
def start_monitoring(req: Optional[StartMonitoringRequest] = None):
    """Starts live monitoring session."""
    s_id = req.scene_id if req and req.scene_id else "LIVE_SCENE"
    z_id = req.zone_id if req and req.zone_id else "ZONE_MAIN"
    return monitoring_service.start_monitoring(scene_id=s_id, zone_id=z_id)


@router.post("/stop")
def stop_monitoring():
    """Stops active monitoring session."""
    return monitoring_service.stop_monitoring()


@router.get("/state")
def get_monitoring_state():
    """Returns current monitoring runtime state."""
    return monitoring_service.get_state()


@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Uploads a video file (.mp4, .avi, .mov, .mkv) for BHID analysis."""
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    
    filename = file.filename or "uploaded_video.mp4"
    res = video_analysis_service.upload_video(file_name=filename, file_bytes=contents)
    return res


@router.post("/analyze/{session_id}")
def start_video_analysis(session_id: str):
    """Launches video analysis for target uploaded session."""
    res = video_analysis_service.start_analysis(session_id)
    if res.get("status") == "ERROR":
        raise HTTPException(status_code=404, detail=res.get("message"))
    return res


@router.get("/progress/{session_id}")
def get_video_analysis_progress(session_id: str):
    """Returns video processing status and completion percentage."""
    res = video_analysis_service.get_status(session_id)
    if res.get("status") == "NOT_FOUND":
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return res
