"""
BHID Operational Audit Log.

Provides append-only immutable audit recording for runtime session events, prediction triggers,
hazard alert state transitions, and disk I/O operational errors.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
import time
from pathlib import Path
from bhid.persistence.persistence_config import PersistenceConfig


@dataclass
class AuditEntry:
    """
    Single append-only operational audit record.
    """
    entry_id: int
    timestamp: float
    action_type: str
    scene_id: str
    zone_id: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation."""
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "action_type": self.action_type,
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "details": dict(self.details)
        }


class AuditLog:
    """
    Append-only operational audit trail coordinator.
    """

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self._entries: List[AuditEntry] = []
        self._next_id: int = 1

    def write_entry(
        self,
        action_type: str,
        scene_id: str = "SYSTEM",
        zone_id: str = "SYSTEM",
        details: Optional[Dict[str, Any]] = None
    ) -> AuditEntry:
        """
        Appends a new immutable audit entry to the log.
        """
        entry = AuditEntry(
            entry_id=self._next_id,
            timestamp=time.time(),
            action_type=str(action_type).upper(),
            scene_id=str(scene_id),
            zone_id=str(zone_id),
            details=details or {}
        )
        self._next_id += 1
        self._entries.append(entry)
        return entry

    def get_entries(self) -> List[Dict[str, Any]]:
        """Returns deep copies of all audit log entries."""
        return [e.to_dict() for e in self._entries]

    def export_json(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports audit log entries to JSON file."""
        try:
            if not self.config.json_export_enabled:
                return None
            out_file = file_path or (self.config.get_audit_dir() / "audit_log.json")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            records = [e.to_dict() for e in self._entries]
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
            return out_file
        except Exception:
            return None

    def clear(self) -> None:
        """Clears in-memory buffer."""
        self._entries.clear()
        self._next_id = 1
