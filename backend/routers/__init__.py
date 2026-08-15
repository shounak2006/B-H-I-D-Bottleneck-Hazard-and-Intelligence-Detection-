"""
BHID FastAPI Routers.
"""

from backend.routers.health import router as health_router
from backend.routers.monitoring import router as monitoring_router
from backend.routers.events import router as events_router
from backend.routers.sessions import router as sessions_router
from backend.routers.replay import router as replay_router
from backend.routers.reports import router as reports_router
from backend.routers.validation import router as validation_router

__all__ = [
    "health_router",
    "monitoring_router",
    "events_router",
    "sessions_router",
    "replay_router",
    "reports_router",
    "validation_router",
]
