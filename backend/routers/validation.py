"""
BHID Validation Router.
Exposes read-only system validation & readiness assessment endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.validation_service import ValidationService

router = APIRouter(prefix="/api/validation", tags=["Validation"])
validation_service = ValidationService()


class RunValidationRequest(BaseModel):
    session_id: Optional[str] = "default_session"


@router.get("")
def get_validation_info():
    """Returns validation capability info."""
    return {"status": "READONLY_VALIDATOR_READY"}


@router.post("/run")
def run_validation(req: Optional[RunValidationRequest] = None):
    """Executes read-only system readiness audit."""
    sess_id = req.session_id if req and req.session_id else "default_session"
    return validation_service.run_validation(session_id=sess_id)
