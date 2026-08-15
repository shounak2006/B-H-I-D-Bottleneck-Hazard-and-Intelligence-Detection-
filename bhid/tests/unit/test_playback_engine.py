"""
Unit tests for BHID PlaybackEngine (Phase 5B).

Validates:
1. PlaybackEngine initialization and disk loading
2. Historical ReplayFrame reconstruction
3. Summary export generation
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
from bhid.replay import PlaybackEngine, ReplayFrame


class TestPlaybackEngine(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.session_id = "test_pe_sess"
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id=self.session_id)
        self.pm = PersistenceManager(config=self.config)

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

        self.engine = PlaybackEngine(session_id=self.session_id, storage_root=self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_playback_reconstruction(self):
        frames = self.engine.replay_all()
        self.assertEqual(len(frames), 1)
        
        f1 = self.engine.get_frame(0)
        self.assertIsInstance(f1, ReplayFrame)
        self.assertEqual(f1.prediction_result["risk_level"], "CRITICAL")

        summary = self.engine.export_summary()
        self.assertEqual(summary["session_id"], self.session_id)
        self.assertEqual(summary["max_prediction_probability"], 0.92)


if __name__ == "__main__":
    unittest.main()
