"""
Unit tests for BHID Flow Metrics Calculator (Phase 4D).

Validates:
1. Inflow rate computation from track entry events
2. Outflow rate computation from track exit events
3. Net flow rate computation
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
from bhid.analytics.flow_metrics import FlowMetricsCalculator


class TestFlowMetrics(unittest.TestCase):

    def setUp(self):
        self.calc = FlowMetricsCalculator()

    def test_flow_rate_computation(self):
        # Prev frame active track IDs: {1, 2, 3}
        prev_ids = {1, 2, 3}

        # Curr frame active track IDs: {2, 3, 4, 5}
        # Inflow = {4, 5} (count = 2)
        # Outflow = {1} (count = 1)
        # dt = 0.4s
        # inflow_rate = 2 / 0.4 = 5.0 /s
        # outflow_rate = 1 / 0.4 = 2.5 /s
        # net_flow_rate = 5.0 - 2.5 = 2.5 /s

        t2 = TrackedObject(track_id=2, bbox=(0, 0, 10, 10), confidence=0.9, timestamp=10.4)
        t3 = TrackedObject(track_id=3, bbox=(0, 0, 10, 10), confidence=0.9, timestamp=10.4)
        t4 = TrackedObject(track_id=4, bbox=(0, 0, 10, 10), confidence=0.9, timestamp=10.4)
        t5 = TrackedObject(track_id=5, bbox=(0, 0, 10, 10), confidence=0.9, timestamp=10.4)

        curr_batch = TrackingBatch(frame_id=2, timestamp=10.4, active_tracks=[t2, t3, t4, t5])

        metrics = self.calc.compute_flow_metrics(
            current_batch=curr_batch,
            prev_track_ids=prev_ids,
            dt_seconds=0.4
        )

        self.assertAlmostEqual(metrics["inflow_rate_per_s"], 5.0, places=3)
        self.assertAlmostEqual(metrics["outflow_rate_per_s"], 2.5, places=3)
        self.assertAlmostEqual(metrics["net_flow_rate_per_s"], 2.5, places=3)

    def test_first_frame_no_prev_reference(self):
        t1 = TrackedObject(track_id=1, bbox=(0, 0, 10, 10), confidence=0.9, timestamp=10.0)
        curr_batch = TrackingBatch(frame_id=1, timestamp=10.0, active_tracks=[t1])

        metrics = self.calc.compute_flow_metrics(current_batch=curr_batch, prev_track_ids=None)
        self.assertEqual(metrics["inflow_rate_per_s"], 0.0)
        self.assertEqual(metrics["outflow_rate_per_s"], 0.0)
        self.assertEqual(metrics["net_flow_rate_per_s"], 0.0)


if __name__ == "__main__":
    unittest.main()
