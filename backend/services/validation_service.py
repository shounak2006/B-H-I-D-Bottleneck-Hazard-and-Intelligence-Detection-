"""
BHID Validation Service.
Interacts with ValidationManager to execute read-only system readiness audits.
"""

from typing import Dict, Any, Optional
from bhid.validation.validation_manager import ValidationManager


class ValidationService:
    """Service wrapping ValidationManager operations."""

    def __init__(self, validation_manager: Optional[ValidationManager] = None):
        self.validation_manager = validation_manager or ValidationManager()

    def run_validation(self, session_id: str = "default_session", storage_root: Optional[Any] = None) -> Dict[str, Any]:
        """Runs read-only system validation audit."""
        eval_res = self.validation_manager.run_all_validations(session_id=session_id, storage_root=storage_root)
        exports = self.validation_manager.export_validation_report(eval_res)

        return {
            "evaluation": eval_res,
            "exported_files": {k: str(v) for k, v in exports.items() if v is not None}
        }
