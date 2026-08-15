"""
BHID Historical Playback Manifest Index Builder.

Indexes frame sequences, timestamps, prediction probabilities, risk levels, and hazard events
to enable offline replay engines to reconstruct session chronologies.
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from bhid.persistence.persistence_config import PersistenceConfig
from bhid.persistence.session_manager import SessionMetadata


class PlaybackManifest:
    """
    Historical playback index builder and parser.
    """

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self._frame_indices: List[Dict[str, Any]] = []

    def add_frame_index(
        self,
        frame_id: int,
        timestamp: float,
        prediction_prob: float,
        risk_level: str,
        hazard_event_id: Optional[str] = None
    ) -> None:
        """Appends a frame index entry to the playback manifest."""
        self._frame_indices.append({
            "frame_id": int(frame_id),
            "timestamp": float(timestamp),
            "prediction_probability": round(float(prediction_prob), 4),
            "risk_level": str(risk_level),
            "hazard_event_id": hazard_event_id
        })

    def build_manifest(self, session_metadata: Optional[SessionMetadata] = None) -> Dict[str, Any]:
        """Generates complete playback manifest index dictionary."""
        sess_dict = session_metadata.to_dict() if session_metadata else {}
        return {
            "session": sess_dict,
            "total_frames_indexed": len(self._frame_indices),
            "frame_timeline": list(self._frame_indices)
        }

    def export_manifest(
        self,
        session_metadata: Optional[SessionMetadata] = None,
        file_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Exports playback manifest to JSON file."""
        try:
            if not self.config.json_export_enabled:
                return None
            out_file = file_path or (self.config.get_session_dir() / "playback_manifest.json")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            manifest = self.build_manifest(session_metadata)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            return out_file
        except Exception:
            return None

    @classmethod
    def load_manifest(cls, file_path: Path) -> Dict[str, Any]:
        """Parses a playback manifest JSON file from disk."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def clear(self) -> None:
        """Clears in-memory frame timeline index."""
        self._frame_indices.clear()
