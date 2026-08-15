"""
Unit tests for BHID CrowdAnalyticsEngine (Phase 4D).

Validates:
1. Generation of all 14 frozen spatiotemporal features
2. Exact key alignment with model schema (feature_*)
3. AnalyticsSnapshot validation & vector export
4. Inter-frame state retention & reset behavior
"""

import sys
import math
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.vision.tracking.tracked_object import TrackedObject
from bhid.vision.tracking.tracking_batch import TrackingBatch
from bhid.analytics.crowd_analytics_engine import CrowdAnalyticsEngine
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot
from bhid.runtime.feature_schema import FROZEN_FEATURE_NAMES


class TestAnalyticsEngine(unittest.TestCase):

    def setUp(self):
        self.engine = CrowdAnalyticsEngine(pixel_to_meter_scale=0.05, default_zone_area_m2=100.0)

        self.t1 = TrackedObject(track_id=1, bbox=(0, 0, 10, 20), confidence=0.9, timestamp=10.0)
        self.t2 = TrackedObject(track_id=2, bbox=(50, 50, 70, 90), confidence=0.8, timestamp=10.0)
        self.t1.update(bbox=(4, 0, 14, 20), confidence=0.9, timestamp=10.4)
        self.t2.update(bbox=(54, 50, 74, 90), confidence=0.8, timestamp=10.4)

        self.batch1 = TrackingBatch(frame_id=1, timestamp=10.0, active_tracks=[self.t1])
        self.batch2 = TrackingBatch(frame_id=2, timestamp=10.4, active_tracks=[self.t1, self.t2])

    def test_complete_14_feature_generation(self):
        snapshot = self.engine.process_tracking_batch(
            tracking_batch=self.batch2,
            zone_area_m2=100.0,
            scene_id="TEST_SCENE",
            zone_id="TEST_ZONE"
        )

        self.assertIsInstance(snapshot, AnalyticsSnapshot)
        feat_vec = snapshot.export_feature_vector()

        self.assertEqual(len(feat_vec), 14)
        for feat in FROZEN_FEATURE_NAMES:
            self.assertIn(feat, feat_vec, f"Missing frozen feature key: {feat}")
            val = feat_vec[feat]
            self.assertIsInstance(val, float)
            self.assertFalse(math.isnan(val))
            self.assertFalse(math.isinf(val))

    def test_inter_frame_state_and_reset(self):
        # Process frame 1
        s1 = self.engine.process_tracking_batch(self.batch1, zone_area_m2=100.0)
        v1 = s1.export_feature_vector()

        # Process frame 2 (t2 joined -> inflow detected)
        s2 = self.engine.process_tracking_batch(self.batch2, zone_area_m2=100.0)
        v2 = s2.export_feature_vector()

        self.assertGreater(v2["feature_inflow_rate_per_s"], 0.0)

        # Reset engine
        self.engine.reset()
        self.assertIsNone(self.engine._prev_track_ids)

        # Process frame 2 again after reset -> inflow reset to 0
        s3 = self.engine.process_tracking_batch(self.batch2, zone_area_m2=100.0)
        v3 = s3.export_feature_vector()
        self.assertEqual(v3["feature_inflow_rate_per_s"], 0.0)


if __name__ == "__main__":
    import math
    unittest.main()
