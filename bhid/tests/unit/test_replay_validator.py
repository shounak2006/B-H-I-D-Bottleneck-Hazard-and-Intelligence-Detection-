"""
Unit tests for BHID ReplayValidator (Phase 5D).

Validates:
1. Historical replay prediction determinism
2. Event timeline reconstruction timestamp validity
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

from bhid.validation import ReplayValidator


class TestReplayValidator(unittest.TestCase):

    def test_replay_validation(self):
        preds = [{"prediction_probability": 0.85, "risk_level": "CRITICAL"}]
        replay_frames = [{
            "timestamp": 10.0,
            "prediction_result": {"prediction_probability": 0.85, "risk_level": "CRITICAL"},
            "active_events": []
        }]

        res = ReplayValidator.validate_replay(preds, [], [], replay_frames)
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 100.0)


if __name__ == "__main__":
    unittest.main()
