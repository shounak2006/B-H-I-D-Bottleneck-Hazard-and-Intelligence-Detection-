"""
BHID Events Router.
Exposes hazard event endpoints.
"""

from fastapi import APIRouter, HTTPException
from backend.services.event_service import EventService

router = APIRouter(prefix="/api/events", tags=["Events"])
event_service = EventService()


@router.get("")
def get_all_events():
    """Returns event history list."""
    return {"events": event_service.get_event_history()}


@router.get("/active")
def get_active_events():
    """Returns currently active hazard events."""
    return {"active_events": event_service.get_active_events()}


@router.get("/{event_id}")
def get_event_by_id(event_id: str):
    """Returns specific hazard event by ID."""
    evt = event_service.get_event_by_id(event_id)
    if evt is None:
        raise HTTPException(status_code=404, detail=f"Hazard event '{event_id}' not found.")
    return evt
