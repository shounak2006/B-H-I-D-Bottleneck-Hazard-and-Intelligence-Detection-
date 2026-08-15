"""
Unit tests for BHID Speed Metrics Calculator (Phase 4D).

Validates:
1. Mean speed calculation from TrackedObject velocities
2. Velocity variance computation
3. Frame-over-frame acceleration calculation
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.vision.tracking.tracked_object import TrackedObject
from bhid.vision.tracking.tracking_batch import TrackingBatch
from bhid.analytics.speed_metrics import SpeedMetricsCalculator


class TestSpeedMetrics(unittest.TestCase):

    def setUp(self):
        self.calc = SpeedMetricsCalculator(pixel_to_meter_scale=0.05)

        # Track 1: moving at (10, 0) px/s -> speed = 10 * 0.05 = 0.5 m/s
        self.t1 = TrackedObject(track_id=1, bbox=(0, 0, 10, 10), confidence=0.9, timestamp=10.0)
        self.t1.update(bbox=(4, 0, 14, 10), confidence=0.9, timestamp=10.4)  # dx=4 in 0.4s -> 10 px/s

        # Track 2: moving at (20, 0) px/s -> speed = 20 * 0.05 = 1.0 m/s
        self.t2 = TrackedObject(track_id=2, bbox=(0, 0, 10, 10), confidence=0.9, timestamp=10.0)
        self.t2.update(bbox=(8, 0, 18, 10), confidence=0.9, timestamp=10.4)  # dx=8 in 0.4s -> 20 px/s

        self.batch = TrackingBatch(frame_id=2, timestamp=10.4, active_tracks=[self.t1, self.t2])

    def test_speed_and_variance_computation(self):
        metrics = self.calc.compute_speed_metrics(self.batch)
        self.assertIn("mean_speed_m_s", metrics)
        self.assertIn("velocity_variance", metrics)
        self.assertIn("acceleration_m_s2", metrics)

        # Mean speed = (0.5 + 1.0) / 2 = 0.75 m/s
        self.assertAlmostEqual(metrics["mean_speed_m_s"], 0.75, places=3)
        # Variance = ((0.5 - 0.75)^2 + (1.0 - 0.75)^2) / 2 = (0.0625 + 0.0625)/2 = 0.0625
        self.assertAlmostEqual(metrics["velocity_variance"], 0.0625, places=3)

    def test_acceleration_computation(self):
        # Prev mean speed = 0.35 m/s, current mean speed = 0.75 m/s, dt = 0.4s
        # accel = (0.75 - 0.35) / 0.4 = 1.0 m/s^2
        metrics = self.calc.compute_speed_metrics(
            tracking_batch=self.batch,
            prev_mean_speed_m_s=0.35,
            dt_seconds=0.4
        )
        self.assertAlmostEqual(metrics["acceleration_m_s2"], 1.0, places=3)

    def test_empty_batch(self):
        empty_batch = TrackingBatch(frame_id=0, timestamp=0.0)
        metrics = self.calc.compute_speed_metrics(empty_batch)
        self.assertEqual(metrics["mean_speed_m_s"], 0.0)
        self.assertEqual(metrics["velocity_variance"], 0.0)
        self.assertEqual(metrics["acceleration_m_s2"], 0.0)


if __name__ == "__main__":
    unittest.main()
