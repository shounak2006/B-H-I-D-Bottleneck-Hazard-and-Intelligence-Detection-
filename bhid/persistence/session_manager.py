"""
BHID Session Manager & Metadata Container.

Manages runtime operational session lifecycles, session frame counters,
active spatial ROI targets, and session summary exports.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json
import time
from pathlib import Path
from bhid.persistence.persistence_config import PersistenceConfig


@dataclass
class SessionMetadata:
    """
    Metadata container for a single BHID operational recording session.
    """
    session_id: str
    start_timestamp: float
    end_timestamp: Optional[float] = None
    scene_id: str = "UNKNOWN_SCENE"
    zone_id: str = "UNKNOWN_ZONE"
    total_frames: int = 0
    total_predictions: int = 0
    total_events: int = 0
    is_active: bool = True

    def duration_seconds(self) -> float:
        """Returns active or completed session duration in seconds."""
        end = self.end_timestamp if self.end_timestamp is not None else time.time()
        return max(0.0, end - self.start_timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation."""
        return {
            "session_id": self.session_id,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "duration_seconds": round(self.duration_seconds(), 2),
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "total_frames": self.total_frames,
            "total_predictions": self.total_predictions,
            "total_events": self.total_events,
            "is_active": self.is_active
        }


class SessionManager:
    """
    Session lifecycle manager coordinating active session state and exports.
    """

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self.active_session: Optional[SessionMetadata] = None
        self.create_session(
            session_id=self.config.session_id,
            scene_id="DEFAULT_SCENE",
            zone_id="DEFAULT_ZONE"
        )

    def create_session(
        self,
        session_id: Optional[str] = None,
        scene_id: str = "DEFAULT_SCENE",
        zone_id: str = "DEFAULT_ZONE"
    ) -> SessionMetadata:
        """Creates a new active operational session."""
        sid = session_id if session_id is not None else f"session_{int(time.time())}"
        self.config.session_id = sid
        self.config.ensure_directories()

        self.active_session = SessionMetadata(
            session_id=sid,
            start_timestamp=time.time(),
            scene_id=str(scene_id),
            zone_id=str(zone_id)
        )
        self.export_session_metadata()
        return self.active_session

    def increment_frame_count(self) -> None:
        """Increments processed frame and prediction counter."""
        if self.active_session and self.active_session.is_active:
            self.active_session.total_frames += 1
            self.active_session.total_predictions += 1

    def increment_event_count(self) -> None:
        """Increments created hazard event counter."""
        if self.active_session and self.active_session.is_active:
            self.active_session.total_events += 1

    def close_session(self) -> SessionMetadata:
        """Closes active session and writes final metadata summary."""
        if self.active_session and self.active_session.is_active:
            self.active_session.end_timestamp = time.time()
            self.active_session.is_active = False
            self.export_session_metadata()
        return self.active_session  # type: ignore

    def export_session_metadata(self) -> Optional[Path]:
        """Writes session_metadata.json to session directory."""
        if not self.active_session:
            return None
        try:
            self.config.ensure_directories()
            out_file = self.config.get_session_dir() / "session_metadata.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(self.active_session.to_dict(), f, indent=2)
            return out_file
        except Exception:
            return None
