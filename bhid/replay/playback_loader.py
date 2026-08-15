"""
BHID Playback Artifact Loader.

Loads persisted Phase 5A session files (session metadata, predictions, analytics snapshots,
hazard events, monitoring snapshots, and playback manifests) from disk storage.
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from bhid.replay.replay_session import ReplaySession


class PlaybackLoader:
    """
    Disk loader for Phase 5A historical operational recording artifacts.
    """

    def __init__(self, session_id: str, storage_root: Optional[Path] = None):
        self.session_id = str(session_id)
        self.storage_root = Path(storage_root) if storage_root is not None else Path("bhid/data/sessions")
        self.session_dir = self.storage_root / self.session_id

    def load_session_metadata(self) -> Dict[str, Any]:
        """Loads session_metadata.json dictionary."""
        file_path = self.session_dir / "session_metadata.json"
        if not file_path.exists():
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_manifest(self) -> Dict[str, Any]:
        """Loads playback_manifest.json dictionary."""
        file_path = self.session_dir / "playback_manifest.json"
        if not file_path.exists():
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_predictions(self) -> List[Dict[str, Any]]:
        """Loads predictions.json list."""
        file_path = self.session_dir / "predictions" / "predictions.json"
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_analytics_snapshots(self) -> List[Dict[str, Any]]:
        """Loads analytics_snapshots.json list."""
        file_path = self.session_dir / "analytics" / "analytics_snapshots.json"
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_events(self) -> List[Dict[str, Any]]:
        """Loads hazard_events.json list."""
        file_path = self.session_dir / "events" / "hazard_events.json"
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_monitoring_snapshots(self) -> List[Dict[str, Any]]:
        """Loads monitoring_snapshots.json list."""
        file_path = self.session_dir / "monitoring" / "monitoring_snapshots.json"
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_session(self) -> ReplaySession:
        """Constructs a ReplaySession dataclass instance from disk files."""
        meta = self.load_session_metadata()
        manifest = self.load_manifest()

        return ReplaySession(
            session_id=self.session_id,
            scene_id=meta.get("scene_id", "UNKNOWN_SCENE"),
            zone_id=meta.get("zone_id", "UNKNOWN_ZONE"),
            start_timestamp=float(meta.get("start_timestamp", 0.0)),
            end_timestamp=meta.get("end_timestamp"),
            total_frames=int(meta.get("total_frames", len(manifest.get("frame_timeline", [])))),
            playback_manifest=manifest
        )
