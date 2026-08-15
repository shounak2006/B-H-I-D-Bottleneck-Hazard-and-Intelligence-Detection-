"""
Unit tests for BHID ValidationManager (Phase 5D).

Validates:
1. Complete read-only system validation execution
2. System readiness scoring (PASSED / FAILED)
3. Validation report file exports (JSON, Markdown)
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
from bhid.validation import ValidationConfig, ValidationManager


class TestValidationManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.session_id = "test_val_sess_001"
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

        self.v_config = ValidationConfig(validation_output_directory=self.tmp_dir / "reports" / "validation")
        self.vm = ValidationManager(config=self.v_config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_run_all_validations(self):
        eval_res = self.vm.run_all_validations(session_id=self.session_id, storage_root=self.tmp_dir)
        self.assertEqual(eval_res["overall_status"], "PASSED")
        self.assertEqual(eval_res["readiness_score_pct"], 100.0)

        outputs = self.vm.export_validation_report(eval_res)
        self.assertTrue(outputs["json"].exists())
        self.assertTrue(outputs["markdown"].exists())


if __name__ == "__main__":
    unittest.main()
