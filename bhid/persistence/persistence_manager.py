"""
BHID Primary Persistence Manager & Coordinator.

Coordinates session lifecycle tracking, prediction storage, 14-feature analytics recording,
hazard event auditing, monitoring telemetry buffering, and non-blocking file exports.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from bhid.persistence.persistence_config import PersistenceConfig
from bhid.persistence.session_manager import SessionManager
from bhid.persistence.prediction_store import PredictionStore
from bhid.persistence.analytics_store import AnalyticsStore
from bhid.persistence.event_store import EventStore
from bhid.persistence.monitoring_store import MonitoringStore
from bhid.persistence.audit_log import AuditLog
from bhid.persistence.playback_manifest import PlaybackManifest
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot
from bhid.events.hazard_event import HazardEvent
from bhid.visualization.monitoring_snapshot import MonitoringSnapshot

logger = logging.getLogger("bhid.persistence")


class PersistenceManager:
    """
    Primary operational persistence coordinator.
    
    Enforces non-blocking execution isolation: Disk write exceptions are caught,
    logged as audit entries, and swallowed to protect the main prediction pipeline.
    """

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self.session_manager = SessionManager(config=self.config)
        self.prediction_store = PredictionStore(config=self.config)
        self.analytics_store = AnalyticsStore(config=self.config)
        self.event_store = EventStore(config=self.config)
        self.monitoring_store = MonitoringStore(config=self.config)
        self.audit_log = AuditLog(config=self.config)
        self.playback_manifest = PlaybackManifest(config=self.config)

        self.audit_log.write_entry(
            action_type="SESSION_START",
            scene_id=self.session_manager.active_session.scene_id if self.session_manager.active_session else "SYS",
            zone_id=self.session_manager.active_session.zone_id if self.session_manager.active_session else "SYS",
            details={"session_id": self.config.session_id}
        )

    def persist_prediction(self, pred_result: RuntimePredictionResult) -> bool:
        """
        Safely ingests a RuntimePredictionResult into PredictionStore and PlaybackManifest.
        Non-blocking: Swallows exceptions on failure.
        """
        try:
            self.prediction_store.store_prediction(pred_result)
            self.session_manager.increment_frame_count()

            self.playback_manifest.add_frame_index(
                frame_id=getattr(pred_result, "frame_id", 0),
                timestamp=pred_result.timestamp,
                prediction_prob=pred_result.prediction_probability,
                risk_level=pred_result.risk_level
            )
            return True
        except Exception as e:
            self._log_error("PERSIST_PREDICTION_ERROR", str(e))
            return False

    def persist_analytics_snapshot(self, snapshot: AnalyticsSnapshot) -> bool:
        """
        Safely ingests an AnalyticsSnapshot into AnalyticsStore.
        Non-blocking: Swallows exceptions on failure.
        """
        try:
            return self.analytics_store.store_snapshot(snapshot)
        except Exception as e:
            self._log_error("PERSIST_ANALYTICS_ERROR", str(e))
            return False

    def persist_event(self, event: HazardEvent) -> bool:
        """
        Safely ingests a HazardEvent into EventStore and writes AuditLog event.
        Non-blocking: Swallows exceptions on failure.
        """
        try:
            stored = self.event_store.store_event(event)
            self.session_manager.increment_event_count()

            action = f"EVENT_{event.status.upper()}"
            self.audit_log.write_entry(
                action_type=action,
                scene_id=event.scene_id,
                zone_id=event.zone_id,
                details={"event_id": event.event_id, "risk_level": event.risk_level, "prob": event.prediction_probability}
            )
            return stored
        except Exception as e:
            self._log_error("PERSIST_EVENT_ERROR", str(e))
            return False

    def persist_monitoring_snapshot(self, snapshot: MonitoringSnapshot) -> bool:
        """
        Safely ingests a MonitoringSnapshot into MonitoringStore.
        Non-blocking: Swallows exceptions on failure.
        """
        try:
            return self.monitoring_store.store_snapshot(snapshot)
        except Exception as e:
            self._log_error("PERSIST_MONITORING_ERROR", str(e))
            return False

    def export_all(self) -> Dict[str, Optional[Path]]:
        """
        Flushes and exports JSON & CSV files for all stores.
        Non-blocking: Errors are logged to AuditLog without raising.
        """
        exports: Dict[str, Optional[Path]] = {}
        try:
            exports["metadata"] = self.session_manager.export_session_metadata()
            exports["predictions_json"] = self.prediction_store.export_json()
            exports["predictions_csv"] = self.prediction_store.export_csv()
            exports["analytics_json"] = self.analytics_store.export_json()
            exports["analytics_csv"] = self.analytics_store.export_csv()
            exports["events_json"] = self.event_store.export_json()
            exports["events_csv"] = self.event_store.export_csv()
            exports["monitoring_json"] = self.monitoring_store.export_json()
            exports["monitoring_csv"] = self.monitoring_store.export_csv()
            exports["manifest_json"] = self.playback_manifest.export_manifest(self.session_manager.active_session)
            exports["audit_json"] = self.audit_log.export_json()
            
            self.audit_log.write_entry(
                action_type="FLUSH_COMPLETED",
                details={"exported_files": [str(p) for p in exports.values() if p is not None]}
            )
        except Exception as e:
            self._log_error("EXPORT_ERROR", str(e))

        return exports

    def flush(self) -> Dict[str, Optional[Path]]:
        """Alias for export_all."""
        return self.export_all()

    def close(self) -> SessionManager:
        """Closes session and performs final export."""
        try:
            self.session_manager.close_session()
            self.export_all()
        except Exception as e:
            self._log_error("CLOSE_SESSION_ERROR", str(e))
        return self.session_manager

    def reset(self) -> None:
        """Clears all store buffers and resets session."""
        self.prediction_store.clear()
        self.analytics_store.clear()
        self.event_store.clear()
        self.monitoring_store.clear()
        self.audit_log.clear()
        self.playback_manifest.clear()

    def _log_error(self, action_type: str, error_msg: str) -> None:
        """Internal helper to write error audit entries non-blockingly."""
        try:
            logger.error(f"BHID Persistence Exception [{action_type}]: {error_msg}")
            self.audit_log.write_entry(
                action_type=action_type,
                details={"error": error_msg}
            )
        except Exception:
            pass
