"""
Unit tests for BHID ReplayMetrics Engine (Phase 5B).

Validates:
1. Replay statistical telemetry calculations
2. Summary report dict generation
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

from bhid.replay import ReplayMetrics


class TestReplayMetrics(unittest.TestCase):

    def test_replay_metrics_computations(self):
        preds = [
            {"prediction_probability": 0.20},
            {"prediction_probability": 0.88},
            {"prediction_probability": 0.50}
        ]
        analytics = [
            {"features": {"feature_pedestrian_count": 10, "feature_density_ped_per_m2": 0.10}},
            {"features": {"feature_pedestrian_count": 50, "feature_density_ped_per_m2": 0.50}}
        ]
        events = [
            {"event_id": "E1", "status": "RESOLVED"},
            {"event_id": "E2", "status": "ACTIVE"}
        ]

        self.assertEqual(ReplayMetrics.max_probability(preds), 0.88)
        self.assertEqual(ReplayMetrics.peak_pedestrian_count(analytics), 50)
        self.assertEqual(ReplayMetrics.peak_density(analytics), 0.50)
        self.assertEqual(ReplayMetrics.total_events(events), 2)
        self.assertEqual(ReplayMetrics.resolved_events(events), 1)

        summary = ReplayMetrics.replay_summary("SESS_001", preds, analytics, events)
        self.assertEqual(summary["session_id"], "SESS_001")
        self.assertEqual(summary["total_frames_analyzed"], 3)


if __name__ == "__main__":
    unittest.main()
