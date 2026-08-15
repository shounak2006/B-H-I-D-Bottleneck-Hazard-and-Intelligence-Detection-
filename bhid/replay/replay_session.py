"""
BHID Replay Session Data Model.

Dataclass representing a loaded historical operational recording session for playback.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ReplaySession:
    """
    Metadata container for a historical recording session loaded for replay.
    
    Attributes:
        session_id: Session identifier string.
        scene_id: Scene location identifier.
        zone_id: Spatial ROI zone identifier.
        start_timestamp: Time session recording began.
        end_timestamp: Time session recording completed.
        total_frames: Total indexed frame count.
        playback_manifest: Playback manifest index dictionary.
    """
    session_id: str
    scene_id: str = "UNKNOWN_SCENE"
    zone_id: str = "UNKNOWN_ZONE"
    start_timestamp: float = 0.0
    end_timestamp: Optional[float] = None
    total_frames: int = 0
    playback_manifest: Dict[str, Any] = field(default_factory=dict)

    def duration_seconds(self) -> float:
        """Returns total duration of the replayed session in seconds."""
        if self.end_timestamp is not None and self.start_timestamp > 0.0:
            return max(0.0, self.end_timestamp - self.start_timestamp)
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation."""
        return {
            "session_id": self.session_id,
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "duration_seconds": round(self.duration_seconds(), 2),
            "total_frames": self.total_frames,
            "manifest_indexed_frames": self.playback_manifest.get("total_frames_indexed", 0)
        }
