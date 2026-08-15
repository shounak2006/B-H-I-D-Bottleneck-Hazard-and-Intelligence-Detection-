"""
BHID Monitoring Router.
Exposes live crowd monitoring lifecycle control endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])
monitoring_service = MonitoringService()


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
