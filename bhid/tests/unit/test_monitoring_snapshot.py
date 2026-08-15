"""
Unit tests for BHID MonitoringSnapshot Model (Phase 4F).

Validates:
1. MonitoringSnapshot field initialization & type enforcement
2. Dictionary export formatting
3. Operator-facing summary string format
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

from bhid.visualization.monitoring_snapshot import MonitoringSnapshot


class TestMonitoringSnapshot(unittest.TestCase):

    def test_snapshot_creation_and_formatting(self):
        snap = MonitoringSnapshot(
            frame_id=42,
            timestamp=104.2,
            scene_id="SCENE_GATE_01",
            zone_id="MAIN_ENTRANCE",
            pedestrian_count=75,
            density_ped_per_m2=1.5,
            active_tracks_count=75,
            prediction_probability=0.88,
            risk_level="CRITICAL",
            binary_prediction=1,
            active_event_count=1,
            active_events=[{"event_id": "E1", "status": "ACTIVE"}]
        )

        self.assertEqual(snap.frame_id, 42)
        self.assertEqual(snap.risk_level, "CRITICAL")
        self.assertEqual(snap.target_horizon, "Y30")

        summary = snap.summary_string()
        self.assertIn("FRAME 0042", summary)
        self.assertIn("Peds=75", summary)
        self.assertIn("CRITICAL (88.0%)", summary)

        d = snap.to_dict()
        self.assertEqual(d["frame_id"], 42)
        self.assertEqual(d["pedestrian_count"], 75)
        self.assertEqual(d["active_event_count"], 1)
        self.assertIn("summary", d)


if __name__ == "__main__":
    unittest.main()
