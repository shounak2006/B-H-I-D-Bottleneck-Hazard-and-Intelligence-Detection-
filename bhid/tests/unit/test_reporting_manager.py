"""
Unit tests for BHID ReportingManager (Phase 5C).

Validates:
1. Unified session report generation from Phase 5A disk artifacts
2. Multi-format file exports (JSON, CSV, Markdown)
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

from bhid.persistence import PersistenceConfig, PersistenceManager
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot
from bhid.reporting import ReportConfig, ReportingManager, SessionReport


class TestReportingManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.session_id = "test_report_sess_001"
        self.p_config = PersistenceConfig(storage_root=self.tmp_dir, session_id=self.session_id)
        self.pm = PersistenceManager(config=self.p_config)

        # Ingest test prediction and analytics snapshot
        pred = RuntimePredictionResult(0.92, 1, "CRITICAL", 0.60, "Y30", 10.0, "SCENE_1", "ZONE_1")
        sample_features = {
            "feature_pedestrian_count": 40.0, "feature_density_ped_per_m2": 0.40, "feature_occupancy_ratio": 0.40,
            "feature_mean_speed_m_s": 0.3, "feature_velocity_variance": 0.01, "feature_acceleration_m_s2": 0.0,
            "feature_directional_entropy": 0.5, "feature_inflow_rate_per_s": 0.0, "feature_outflow_rate_per_s": 0.0,
            "feature_net_flow_rate_per_s": 0.0, "feature_egress_deficit_ratio": 0.0, "feature_trajectory_convergence": 0.5,
            "feature_temporal_density_change": 0.0, "feature_temporal_speed_change": 0.0
        }
        snap = AnalyticsSnapshot(frame_id=1, timestamp=10.0, scene_id="SCENE_1", zone_id="ZONE_1", features=sample_features)
        
        self.pm.persist_prediction(pred)
        self.pm.persist_analytics_snapshot(snap)
        self.pm.flush()

        self.r_config = ReportConfig(report_output_directory=self.tmp_dir / "reports")
        self.rm = ReportingManager(config=self.r_config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_generate_session_report(self):
        report = self.rm.generate_report(session_id=self.session_id, storage_root=self.tmp_dir)
        self.assertIsInstance(report, SessionReport)
        self.assertEqual(report.session_id, self.session_id)

        exports = self.rm.export_all(report)
        self.assertTrue(exports["json"].exists())
        self.assertTrue(exports["csv"].exists())
        self.assertTrue(exports["markdown"].exists())

        md_content = report.to_markdown()
        self.assertIn("# BHID Operational Intelligence Report", md_content)
        self.assertIn("CRITICAL HAZARD OBSERVED", md_content)


if __name__ == "__main__":
    unittest.main()
