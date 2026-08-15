"""
Unit tests for BHID Density Metrics Calculator (Phase 4D).

Validates:
1. Pedestrian count extraction
2. Spatial density calculation per m^2
3. Occupancy ratio computation
4. Temporal density change calculation
"""

import sys
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
from bhid.analytics.density_metrics import DensityMetricsCalculator


class TestDensityMetrics(unittest.TestCase):

    def setUp(self):
        self.calc = DensityMetricsCalculator(default_zone_area_m2=100.0)

        t1 = TrackedObject(track_id=1, bbox=(0, 0, 10, 20), confidence=0.9, timestamp=10.0)
        t2 = TrackedObject(track_id=2, bbox=(20, 20, 40, 60), confidence=0.8, timestamp=10.0)
        self.batch = TrackingBatch(frame_id=1, timestamp=10.0, active_tracks=[t1, t2])

    def test_density_computation(self):
        metrics = self.calc.compute_density_metrics(self.batch, zone_area_m2=100.0)

        self.assertEqual(metrics["pedestrian_count"], 2.0)
        # density = 2 / 100 = 0.02 ped/m^2
        self.assertAlmostEqual(metrics["density_ped_per_m2"], 0.02, places=3)
        self.assertGreaterEqual(metrics["occupancy_ratio"], 0.0)
        self.assertLessEqual(metrics["occupancy_ratio"], 1.0)

    def test_temporal_density_change(self):
        # Prev density = 0.01 ped/m^2, current density = 0.02 ped/m^2, dt = 0.4s
        # change = (0.02 - 0.01) / 0.4 = 0.025
        metrics = self.calc.compute_density_metrics(
            tracking_batch=self.batch,
            zone_area_m2=100.0,
            prev_density_ped_per_m2=0.01,
            dt_seconds=0.4
        )
        self.assertAlmostEqual(metrics["temporal_density_change"], 0.025, places=3)


if __name__ == "__main__":
    unittest.main()
