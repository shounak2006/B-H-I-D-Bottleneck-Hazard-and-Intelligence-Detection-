"""
BHID Primary Playback Engine.

Coordinates historical session loading, chronological replay frame reconstruction,
event timeline synchronization, and replay summary generation.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from bhid.replay.replay_session import ReplaySession
from bhid.replay.playback_loader import PlaybackLoader
from bhid.replay.event_timeline import EventTimeline
from bhid.replay.replay_frame import ReplayFrame
from bhid.replay.timeline_controller import TimelineController
from bhid.replay.replay_metrics import ReplayMetrics


class PlaybackEngine:
    """
    Primary operational coordinator for deterministic historical playback.
    """

    def __init__(self, session_id: Optional[str] = None, storage_root: Optional[Path] = None):
        self.loader: Optional[PlaybackLoader] = None
        self.session: Optional[ReplaySession] = None
        self.event_timeline: EventTimeline = EventTimeline()
        self.timeline_controller: TimelineController = TimelineController()
        
        self.raw_predictions: List[Dict[str, Any]] = []
        self.raw_analytics: List[Dict[str, Any]] = []
        self.raw_events: List[Dict[str, Any]] = []
        self.raw_monitoring: List[Dict[str, Any]] = []
        self.replay_frames: List[ReplayFrame] = []

        if session_id:
            self.load_session(session_id, storage_root)

    def load_session(self, session_id: str, storage_root: Optional[Path] = None) -> ReplaySession:
        """Loads all persisted artifacts for a historical session and builds replay timeline."""
        self.loader = PlaybackLoader(session_id=session_id, storage_root=storage_root)
        self.session = self.loader.load_session()

        self.raw_predictions = self.loader.load_predictions()
        self.raw_analytics = self.loader.load_analytics_snapshots()
        self.raw_events = self.loader.load_events()
        self.raw_monitoring = self.loader.load_monitoring_snapshots()

        self.event_timeline.build_timeline(self.raw_events)
        self.build_replay_frames()
        self.timeline_controller = TimelineController(total_frames=len(self.replay_frames))
        return self.session

    def build_replay_frames(self) -> List[ReplayFrame]:
        """Reconstructs ReplayFrame instances chronologically matching persisted records."""
        self.replay_frames.clear()
        
        # Build mapping by frame_id / index
        num_frames = max(len(self.raw_predictions), len(self.raw_analytics), len(self.raw_monitoring))

        for idx in range(num_frames):
            pred = self.raw_predictions[idx] if idx < len(self.raw_predictions) else {}
            analytics = self.raw_analytics[idx] if idx < len(self.raw_analytics) else {}
            monitoring = self.raw_monitoring[idx] if idx < len(self.raw_monitoring) else {}

            ts = float(pred.get("timestamp", analytics.get("timestamp", monitoring.get("timestamp", 0.0))))
            fid = int(pred.get("frame_id", analytics.get("frame_id", monitoring.get("frame_id", idx))))

            # Active events at this timestamp
            active_evts = self.event_timeline.get_active_events_at(ts)

            frame = ReplayFrame(
                frame_id=fid,
                timestamp=ts,
                monitoring_snapshot=monitoring,
                active_events=active_evts,
                prediction_result=pred,
                analytics_snapshot=analytics
            )
            self.replay_frames.append(frame)

        return self.replay_frames

    def get_frame(self, frame_index: int) -> Optional[ReplayFrame]:
        """Returns reconstructed ReplayFrame at given 0-indexed position."""
        if 0 <= frame_index < len(self.replay_frames):
            return self.replay_frames[frame_index]
        return None

    def replay_all(self) -> List[ReplayFrame]:
        """Returns all reconstructed replay frames."""
        return list(self.replay_frames)

    def export_summary(self) -> Dict[str, Any]:
        """Exports statistical summary of the replayed historical session."""
        sid = self.session.session_id if self.session else "UNKNOWN"
        return ReplayMetrics.replay_summary(
            session_id=sid,
            predictions=self.raw_predictions,
            analytics=self.raw_analytics,
            events=self.raw_events
        )
