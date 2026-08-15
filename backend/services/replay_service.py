"""
BHID Replay Service.
Interacts with PlaybackEngine and TimelineController to control historical session replay.
"""

from typing import Dict, Any, Optional
from bhid.replay.playback_engine import PlaybackEngine
from bhid.replay.timeline_controller import TimelineController


class ReplayService:
    """Service wrapping PlaybackEngine and TimelineController."""

    def __init__(self):
        self.playback_engine: Optional[PlaybackEngine] = None
        self.timeline_controller: Optional[TimelineController] = None
        self.active_session_id: Optional[str] = None

    def load_session(self, session_id: str, storage_root: Optional[Any] = None) -> Dict[str, Any]:
        """Loads session artifacts for historical replay."""
        self.active_session_id = session_id
        self.playback_engine = PlaybackEngine(session_id=session_id, storage_root=storage_root)
        self.timeline_controller = TimelineController(playback_engine=self.playback_engine)
        
        frames = self.playback_engine.build_replay_frames()
        summary = self.playback_engine.export_summary()

        return {
            "session_id": session_id,
            "total_frames": len(frames),
            "summary": summary
        }

    def play(self) -> Dict[str, Any]:
        """Starts playback."""
        if self.timeline_controller:
            self.timeline_controller.play()
            return {"status": "PLAYING", "current_frame_id": self.timeline_controller.current_frame_id}
        return {"status": "NO_SESSION_LOADED"}

    def pause(self) -> Dict[str, Any]:
        """Pauses playback."""
        if self.timeline_controller:
            self.timeline_controller.pause()
            return {"status": "PAUSED", "current_frame_id": self.timeline_controller.current_frame_id}
        return {"status": "NO_SESSION_LOADED"}

    def get_frame(self, frame_index: int = 0) -> Optional[Dict[str, Any]]:
        """Returns replayed frame dictionary by index."""
        if self.playback_engine:
            frames = self.playback_engine.build_replay_frames()
            if 0 <= frame_index < len(frames):
                return frames[frame_index].to_dict()
        return None
