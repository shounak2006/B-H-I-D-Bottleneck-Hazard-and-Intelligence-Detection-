"""
BHID Persistence Configuration.

Defines storage roots, session directory structures, export flags, and directory resolution helpers.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import time


@dataclass
class PersistenceConfig:
    """
    Central persistence configuration dataclass.
    
    Attributes:
        storage_root: Root directory for session persistence.
        session_id: Active session identifier string.
        json_export_enabled: Whether JSON file exports are enabled.
        csv_export_enabled: Whether CSV file exports are enabled.
        max_session_retention_days: Retention limit for historical session archives.
    """
    storage_root: Path = field(default_factory=lambda: Path("bhid/data/sessions"))
    session_id: Optional[str] = None
    json_export_enabled: bool = True
    csv_export_enabled: bool = True
    max_session_retention_days: int = 30

    def __post_init__(self):
        if isinstance(self.storage_root, str):
            self.storage_root = Path(self.storage_root)
        if self.session_id is None:
            self.session_id = f"session_{int(time.time())}"

    def get_session_dir(self) -> Path:
        """Returns session directory path for active session."""
        return self.storage_root / str(self.session_id)

    def get_predictions_dir(self) -> Path:
        """Returns predictions export directory."""
        return self.get_session_dir() / "predictions"

    def get_analytics_dir(self) -> Path:
        """Returns analytics snapshots export directory."""
        return self.get_session_dir() / "analytics"

    def get_events_dir(self) -> Path:
        """Returns hazard events export directory."""
        return self.get_session_dir() / "events"

    def get_monitoring_dir(self) -> Path:
        """Returns monitoring snapshots export directory."""
        return self.get_session_dir() / "monitoring"

    def get_audit_dir(self) -> Path:
        """Returns audit logs export directory."""
        return self.get_session_dir() / "audit"

    def ensure_directories(self) -> bool:
        """Creates session folder hierarchy if missing."""
        try:
            self.get_session_dir().mkdir(parents=True, exist_ok=True)
            self.get_predictions_dir().mkdir(parents=True, exist_ok=True)
            self.get_analytics_dir().mkdir(parents=True, exist_ok=True)
            self.get_events_dir().mkdir(parents=True, exist_ok=True)
            self.get_monitoring_dir().mkdir(parents=True, exist_ok=True)
            self.get_audit_dir().mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
