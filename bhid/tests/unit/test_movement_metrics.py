"""
Unit tests for BHID Movement Metrics Calculator (Phase 4D).

Validates:
1. Directional entropy computation across 8 angular bins
2. Trajectory convergence calculation
3. Temporal speed change calculation
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
from bhid.analytics.movement_metrics import MovementMetricsCalculator


class TestMovementMetrics(unittest.TestCase):

    def setUp(self):
        self.calc = MovementMetricsCalculator()

    def test_directional_entropy_uniform_direction(self):
        # 4 tracks moving in exact same direction (vx=10, vy=0)
        tracks = []
        for i in range(4):
            t = TrackedObject(track_id=i+1, bbox=(i*10, 0, i*10+10, 10), confidence=0.9, timestamp=10.0)
            t.update(bbox=(i*10+4, 0, i*10+14, 10), confidence=0.9, timestamp=10.4)
            tracks.append(t)

        batch = TrackingBatch(frame_id=2, timestamp=10.4, active_tracks=tracks)
        metrics = self.calc.compute_movement_metrics(batch, current_mean_speed_m_s=0.5)

        self.assertIn("directional_entropy", metrics)
        self.assertIn("trajectory_convergence", metrics)
        self.assertIn("temporal_speed_change", metrics)

        # All in same bin -> p=1.0 -> entropy = 0.0
        self.assertEqual(metrics["directional_entropy"], 0.0)
        # All vectors aligned -> convergence = 1.0
        self.assertAlmostEqual(metrics["trajectory_convergence"], 1.0, places=3)

    def test_temporal_speed_change(self):
        t1 = TrackedObject(track_id=1, bbox=(0, 0, 10, 10), confidence=0.9, timestamp=10.0)
        batch = TrackingBatch(frame_id=1, timestamp=10.0, active_tracks=[t1])

        # Current mean speed = 1.2 m/s, prev mean speed = 0.8 m/s, dt = 0.4s
        # change = (1.2 - 0.8) / 0.4 = 1.0 m/s^2
        metrics = self.calc.compute_movement_metrics(
            tracking_batch=batch,
            current_mean_speed_m_s=1.2,
            prev_mean_speed_m_s=0.8,
            dt_seconds=0.4
        )
        self.assertAlmostEqual(metrics["temporal_speed_change"], 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
