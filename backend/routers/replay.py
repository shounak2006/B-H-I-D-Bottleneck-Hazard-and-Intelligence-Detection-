"""
BHID Replay Router.
Exposes historical session playback control endpoints.
"""

from fastapi import APIRouter
from backend.services.replay_service import ReplayService

router = APIRouter(prefix="/api/replay", tags=["Replay"])
replay_service = ReplayService()


@router.get("/{session_id}")
def load_replay_session(session_id: str):
    """Loads historical session artifacts for replay."""
    return replay_service.load_session(session_id)


@router.post("/{session_id}/play")
def play_replay(session_id: str):
    """Starts playback for loaded session."""
    return replay_service.play()


@router.post("/{session_id}/pause")
def pause_replay(session_id: str):
    """Pauses playback for loaded session."""
    return replay_service.pause()
