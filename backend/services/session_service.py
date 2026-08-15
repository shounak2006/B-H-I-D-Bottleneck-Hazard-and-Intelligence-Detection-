"""
BHID Session Service.
Interacts with SessionManager and PersistenceManager to query recorded sessions.
"""

from typing import List, Dict, Any, Optional
import json
import time
from pathlib import Path
from bhid.persistence.persistence_config import PersistenceConfig
from bhid.persistence.session_manager import SessionManager


class SessionService:
    """Service wrapping session directory discovery and metadata queries."""

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self.session_manager = SessionManager(config=self.config)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Lists recorded operational session directories."""
        storage_root = self.config.storage_root
        if not storage_root.exists():
            return []

        sessions = []
        for p in storage_root.iterdir():
            if p.is_dir():
                meta_file = p / "session_metadata.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        sessions.append(data)
                    except Exception:
                        sessions.append({"session_id": p.name, "created_at": time.ctime(p.stat().st_mtime)})
                else:
                    sessions.append({"session_id": p.name, "created_at": time.ctime(p.stat().st_mtime)})
        return sorted(sessions, key=lambda x: x.get("session_id", ""), reverse=True)

    def get_session_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Returns metadata for a specific session."""
        session_dir = self.config.storage_root / session_id
        meta_file = session_dir / "session_metadata.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"session_id": session_id, "status": "EXISTS"}
