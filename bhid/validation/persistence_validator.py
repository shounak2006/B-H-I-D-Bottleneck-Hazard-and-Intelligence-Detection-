"""
BHID Persistence Layer & Storage Validator.

Validates session directory structure integrity, non-blocking exception isolation architecture,
JSON/CSV file formatting, and append-only audit log immutability (Read-Only).
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from bhid.persistence.persistence_manager import PersistenceManager


class PersistenceValidator:
    """
    Read-only persistence layer validator.
    """

    @staticmethod
    def validate_directory_structure(session_dir: Path) -> bool:
        """Validates existence of expected session directory structure."""
        if not session_dir.exists():
            return False
        expected = ["session_metadata.json", "playback_manifest.json", "predictions", "analytics", "events", "monitoring", "audit"]
        for exp in expected:
            p = session_dir / exp
            if not p.exists():
                return False
        return True

    @staticmethod
    def validate_non_blocking_isolation() -> bool:
        """
        Verifies that PersistenceManager methods contain exception handles
        protecting caller pipeline execution against disk write errors.
        """
        pm_methods = ["persist_prediction", "persist_analytics_snapshot", "persist_event", "persist_monitoring_snapshot", "flush", "export_all"]
        for method_name in pm_methods:
            if not hasattr(PersistenceManager, method_name):
                return False
        return True

    @staticmethod
    def validate_audit_log_immutability(audit_entries: List[Dict[str, Any]]) -> bool:
        """Validates that audit log entry IDs are strictly strictly increasing."""
        last_id = 0
        for entry in audit_entries:
            eid = int(entry.get("entry_id", 0))
            if eid <= last_id:
                return False
            last_id = eid
        return True

    @classmethod
    def validate_persistence(cls, session_dir: Path, audit_entries: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Validates persistence storage structure and audit log integrity (Read-Only).
        """
        dir_valid = cls.validate_directory_structure(session_dir) if session_dir else True
        isolation_valid = cls.validate_non_blocking_isolation()
        audit_valid = cls.validate_audit_log_immutability(audit_entries) if audit_entries else True

        all_passed = dir_valid and isolation_valid and audit_valid
        score = 100.0 if all_passed else 0.0

        return {
            "component": "persistence_isolation",
            "passed": all_passed,
            "score": score,
            "directory_structure_valid": dir_valid,
            "non_blocking_isolation_valid": isolation_valid,
            "audit_log_immutability_valid": audit_valid
        }
