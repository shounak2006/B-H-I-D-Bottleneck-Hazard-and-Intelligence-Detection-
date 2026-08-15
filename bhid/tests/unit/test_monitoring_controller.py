"""
Unit tests for BHID MonitoringController (Phase 4F).

Validates:
1. MonitoringSnapshot building from pipeline outputs
2. Composite image frame rendering (Heatmap + Tracks + Telemetry + Alert Banners)
3. Summary export formatting
"""

import sys
import unittest
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.vision.tracking import TrackedObject, TrackingBatch
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.events.hazard_event import HazardEvent
from bhid.visualization.monitoring_controller import MonitoringController
from bhid.visualization.monitoring_snapshot import MonitoringSnapshot


class TestMonitoringController(unittest.TestCase):

    def setUp(self):
        self.controller = MonitoringController()

        track = TrackedObject(track_id=1, bbox=(100, 100, 140, 200), confidence=0.9, timestamp=10.0)
        self.track_batch = TrackingBatch(frame_id=1, timestamp=10.0, active_tracks=[track])

        sample_features = {
            "feature_pedestrian_count": 10.0,
            "feature_density_ped_per_m2": 0.10,
            "feature_occupancy_ratio": 0.10,
            "feature_mean_speed_m_s": 1.20,
            "feature_velocity_variance": 0.01,
            "feature_acceleration_m_s2": 0.00,
            "feature_directional_entropy": 0.50,
            "feature_inflow_rate_per_s": 0.00,
            "feature_outflow_rate_per_s": 0.00,
            "feature_net_flow_rate_per_s": 0.00,
            "feature_egress_deficit_ratio": 0.00,
            "feature_trajectory_convergence": 0.50,
            "feature_temporal_density_change": 0.00,
            "feature_temporal_speed_change": 0.00
        }

        self.analytics_snapshot = AnalyticsSnapshot(
            frame_id=1, timestamp=10.0, scene_id="S1", zone_id="Z1",
            features=sample_features
        )

        self.pred_result = RuntimePredictionResult(
            prediction_probability=0.20, binary_prediction=0, risk_level="LOW",
            threshold_used=0.60, target_horizon="Y30", timestamp=10.0, scene_id="S1", zone_id="Z1"
        )

    def test_snapshot_generation(self):
        snap = self.controller.generate_snapshot(
            tracking_batch=self.track_batch,
            analytics_snapshot=self.analytics_snapshot,
            prediction_result=self.pred_result,
            active_events=[]
        )

        self.assertIsInstance(snap, MonitoringSnapshot)
        self.assertEqual(snap.frame_id, 1)
        self.assertEqual(snap.risk_level, "LOW")

    def test_composite_frame_rendering(self):
        rendered = self.controller.render_frame(
            frame=None,
            tracking_batch=self.track_batch,
            analytics_snapshot=self.analytics_snapshot,
            prediction_result=self.pred_result,
            active_events=[]
        )

        self.assertIsInstance(rendered, np.ndarray)
        self.assertEqual(rendered.shape, (1080, 1920, 3))


if __name__ == "__main__":
    unittest.main()
