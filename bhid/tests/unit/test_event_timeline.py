"""
Unit tests for BHID EventTimeline (Phase 5B).

Validates:
1. Event timeline building & indexing
2. Timestamp active event queries
3. Event transition chronological indexing
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

from bhid.replay import EventTimeline


class TestEventTimeline(unittest.TestCase):

    def setUp(self):
        self.raw_events = [{
            "event_id": "EVT_1",
            "scene_id": "S1",
            "zone_id": "Z1",
            "start_timestamp": 10.0,
            "last_updated_timestamp": 20.0,
            "resolved_timestamp": 25.0,
            "risk_level": "CRITICAL",
            "prediction_history": [
                {"timestamp": 10.0, "risk_level": "HIGH", "status": "ACTIVE"},
                {"timestamp": 15.0, "risk_level": "CRITICAL", "status": "ESCALATED"},
                {"timestamp": 25.0, "risk_level": "LOW", "status": "RESOLVED"}
            ]
        }]
        self.timeline = EventTimeline(events=self.raw_events)

    def test_active_event_queries(self):
        # Time 5.0 -> Not active
        self.assertEqual(len(self.timeline.get_active_events_at(5.0)), 0)

        # Time 15.0 -> Active
        active = self.timeline.get_active_events_at(15.0)
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0]["event_id"], "EVT_1")

        # Time 30.0 -> Resolved, not active
        self.assertEqual(len(self.timeline.get_active_events_at(30.0)), 0)

    def test_transitions(self):
        transitions = self.timeline.get_event_transitions()
        self.assertEqual(len(transitions), 3)
        self.assertEqual(transitions[0]["status"], "ACTIVE")
        self.assertEqual(transitions[1]["status"], "ESCALATED")


if __name__ == "__main__":
    unittest.main()
