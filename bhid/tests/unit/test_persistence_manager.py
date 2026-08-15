"""
Unit tests for BHID PersistenceManager (Phase 5A).

Validates:
1. Coordinated storage of predictions, analytics snapshots, hazard events, and monitoring snapshots
2. Unified file export & session flushing
3. Non-blocking error handling when file write operations fail
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot
from bhid.events.hazard_event import HazardEvent
from bhid.visualization.monitoring_snapshot import MonitoringSnapshot
from bhid.persistence import PersistenceConfig, PersistenceManager


class TestPersistenceManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id="test_pm_sess")
        self.pm = PersistenceManager(config=self.config)

        self.pred = RuntimePredictionResult(
            prediction_probability=0.88, binary_prediction=1, risk_level="CRITICAL",
            threshold_used=0.60, target_horizon="Y30", timestamp=10.0, scene_id="S1", zone_id="Z1"
        )
        sample_features = {
            "feature_pedestrian_count": 15.0, "feature_density_ped_per_m2": 0.15, "feature_occupancy_ratio": 0.15,
            "feature_mean_speed_m_s": 1.1, "feature_velocity_variance": 0.01, "feature_acceleration_m_s2": 0.0,
            "feature_directional_entropy": 0.5, "feature_inflow_rate_per_s": 0.0, "feature_outflow_rate_per_s": 0.0,
            "feature_net_flow_rate_per_s": 0.0, "feature_egress_deficit_ratio": 0.0, "feature_trajectory_convergence": 0.5,
            "feature_temporal_density_change": 0.0, "feature_temporal_speed_change": 0.0
        }
        self.analytics = AnalyticsSnapshot(frame_id=1, timestamp=10.0, scene_id="S1", zone_id="Z1", features=sample_features)
        self.event = HazardEvent("E1", "S1", "Z1", 10.0, 10.0, 0.88, "CRITICAL", "ACTIVE")
        self.mon_snap = MonitoringSnapshot(1, 10.0, "S1", "Z1", 15, 0.15, 15, 0.88, "CRITICAL", 1, 1, [])

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_coordinated_persistence_and_flush(self):
        self.assertTrue(self.pm.persist_prediction(self.pred))
        self.assertTrue(self.pm.persist_analytics_snapshot(self.analytics))
        self.assertTrue(self.pm.persist_event(self.event))
        self.assertTrue(self.pm.persist_monitoring_snapshot(self.mon_snap))

        exports = self.pm.flush()
        self.assertIsNotNone(exports.get("predictions_json"))
        self.assertTrue(exports["predictions_json"].exists())
        self.assertTrue(exports["analytics_json"].exists())
        self.assertTrue(exports["events_json"].exists())
        self.assertTrue(exports["monitoring_json"].exists())

    def test_non_blocking_error_isolation(self):
        """Verify that export errors are logged to AuditLog non-blockingly without stopping caller."""
        from unittest.mock import patch

        # Mock export_json in prediction_store to raise PermissionError
        with patch.object(self.pm.prediction_store, "export_json", side_effect=PermissionError("Permission denied")):
            exports = self.pm.export_all()
            self.assertIsInstance(exports, dict)

        # Verify AuditLog logged the error non-blockingly
        audit_entries = self.pm.audit_log.get_entries()
        has_error = any("ERROR" in e["action_type"] for e in audit_entries)
        self.assertTrue(has_error, "Export failures must be non-blocking and logged to AuditLog")


if __name__ == "__main__":
    unittest.main()
