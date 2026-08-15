"""
Unit tests for BHID HazardEventEngine (Phase 4E).

Validates:
1. Operational event engine orchestration
2. Active event and event history tracking
3. Summary metrics generation
4. System reset capability
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

from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.events.event_engine import HazardEventEngine


class TestEventEngine(unittest.TestCase):

    def setUp(self):
        self.engine = HazardEventEngine()

        self.res_high = RuntimePredictionResult(
            prediction_probability=0.75, binary_prediction=1, risk_level="HIGH",
            threshold_used=0.60, target_horizon="Y30", timestamp=100.0, scene_id="SCENE_1", zone_id="ZONE_A"
        )
        self.res_safe = RuntimePredictionResult(
            prediction_probability=0.20, binary_prediction=0, risk_level="LOW",
            threshold_used=0.60, target_horizon="Y30", timestamp=104.0, scene_id="SCENE_1", zone_id="ZONE_A"
        )

    def test_process_prediction(self):
        evt = self.engine.process_prediction(self.res_high)
        self.assertIsNotNone(evt)
        self.assertEqual(len(self.engine.get_active_events()), 1)

        summary = self.engine.generate_summary()
        self.assertEqual(summary["active_event_count"], 1)
        self.assertIn("history_statistics", summary)

    def test_reset(self):
        self.engine.process_prediction(self.res_high)
        self.assertEqual(len(self.engine.get_active_events()), 1)

        self.engine.reset()
        self.assertEqual(len(self.engine.get_active_events()), 0)
        self.assertEqual(len(self.engine.get_event_history()), 0)


if __name__ == "__main__":
    unittest.main()
