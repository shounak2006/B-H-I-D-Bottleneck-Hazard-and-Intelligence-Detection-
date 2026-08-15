"""
BHID Reporting Service.
Interacts with ReportingManager to generate and export operational reports.
"""

from typing import Dict, Any, Optional
from bhid.reporting.reporting_manager import ReportingManager


class ReportingService:
    """Service wrapping ReportingManager operations."""

    def __init__(self, reporting_manager: Optional[ReportingManager] = None):
        self.reporting_manager = reporting_manager or ReportingManager()

    def generate_report(self, session_id: str, storage_root: Optional[Any] = None) -> Dict[str, Any]:
        """Generates operational report for session."""
        session_report = self.reporting_manager.generate_report(session_id=session_id, storage_root=storage_root, export=True)
        exports = self.reporting_manager.export_all(session_report)

        return {
            "session_id": session_id,
            "session_report": session_report.to_dict(),
            "markdown": session_report.to_markdown(),
            "exported_files": {k: str(v) for k, v in exports.items() if v is not None}
        }
