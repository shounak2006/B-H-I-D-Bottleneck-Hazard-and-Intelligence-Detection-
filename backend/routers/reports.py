"""
BHID Reports Router.
Exposes operational reporting endpoints.
"""

from fastapi import APIRouter
from backend.services.reporting_service import ReportingService
from backend.services.session_service import SessionService

router = APIRouter(prefix="/api/reports", tags=["Reports"])
reporting_service = ReportingService()
session_service = SessionService()


@router.get("")
def list_reports():
    """Lists sessions available for report generation."""
    return {"available_sessions": session_service.list_sessions()}


@router.get("/{session_id}")
def generate_report(session_id: str):
    """Generates structured operational report for target session."""
    return reporting_service.generate_report(session_id=session_id)
