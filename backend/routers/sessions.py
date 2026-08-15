"""
BHID Sessions Router.
Exposes recorded operational session metadata endpoints.
"""

from fastapi import APIRouter, HTTPException
from backend.services.session_service import SessionService

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])
session_service = SessionService()


@router.get("")
def list_sessions():
    """Returns list of recorded operational sessions."""
    return {"sessions": session_service.list_sessions()}


@router.get("/{session_id}")
def get_session(session_id: str):
    """Returns metadata for a specific session."""
    meta = session_service.get_session_metadata(session_id)
    if meta is None:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return meta
