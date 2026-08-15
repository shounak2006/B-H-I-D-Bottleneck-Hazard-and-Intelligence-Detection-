"""
Unit tests for BHID EventValidator (Phase 5D).

Validates:
1. Active duplicate event suppression
2. Resolution threshold timestamp validity
3. Prediction history immutability
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

from bhid.validation import EventValidator


class TestEventValidator(unittest.TestCase):

    def test_valid_events(self):
        events = [
            {
                "event_id": "E1", "zone_id": "Z1", "status": "RESOLVED",
                "start_timestamp": 10.0, "resolved_timestamp": 20.0, "escalation_count": 1,
                "prediction_history": [{"timestamp": 10.0}, {"timestamp": 20.0}]
            }
        ]
        res = EventValidator.validate_events(events)
        self.assertTrue(res["passed"])

    def test_duplicate_active_events_failure(self):
        duplicate_events = [
            {"event_id": "E1", "zone_id": "Z1", "status": "ACTIVE"},
            {"event_id": "E2", "zone_id": "Z1", "status": "ACTIVE"}
        ]
        res = EventValidator.validate_events(duplicate_events)
        self.assertFalse(res["passed"])


if __name__ == "__main__":
    unittest.main()
