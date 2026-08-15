"""
BHID Health Router.
Provides platform status, version, and health endpoints.
"""

from fastapi import APIRouter
from bhid.release.release_config import ReleaseConfig

router = APIRouter(prefix="/api", tags=["Health"])

_config = ReleaseConfig()


@router.get("/health")
def get_health():
    """Returns platform health status."""
    return {"status": "HEALTHY", "system": _config.system_name, "version": _config.version}


@router.get("/version")
def get_version():
    """Returns release build version metadata."""
    return _config.generate_build_metadata()


@router.get("/status")
def get_status():
    """Returns operational platform status."""
    return {
        "status": "OPERATIONAL",
        "release_type": _config.release_type,
        "supported_python_versions": _config.supported_python_versions
    }
