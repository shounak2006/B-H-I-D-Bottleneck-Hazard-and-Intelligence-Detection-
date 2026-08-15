"""
BHID Data Persistence & Historical Storage Package.

Provides session managers, prediction stores, 14-feature analytics stores, hazard event stores,
monitoring telemetry stores, append-only audit logs, historical playback manifests, and unified persistence managers.
"""

from bhid.persistence.persistence_config import PersistenceConfig
from bhid.persistence.session_manager import SessionMetadata, SessionManager
from bhid.persistence.prediction_store import PredictionStore
from bhid.persistence.analytics_store import AnalyticsStore
from bhid.persistence.event_store import EventStore
from bhid.persistence.monitoring_store import MonitoringStore
from bhid.persistence.audit_log import AuditEntry, AuditLog
from bhid.persistence.playback_manifest import PlaybackManifest
from bhid.persistence.persistence_manager import PersistenceManager

__all__ = [
    "PersistenceConfig",
    "SessionMetadata",
    "SessionManager",
    "PredictionStore",
    "AnalyticsStore",
    "EventStore",
    "MonitoringStore",
    "AuditEntry",
    "AuditLog",
    "PlaybackManifest",
    "PersistenceManager",
]
