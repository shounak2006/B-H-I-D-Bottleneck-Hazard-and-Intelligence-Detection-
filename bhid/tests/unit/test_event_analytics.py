"""
Unit tests for BHID EventAnalytics (Phase 5C).

Validates:
1. Hazard event intelligence & duration statistics
2. Escalation count aggregations
3. Spatial zone risk rankings
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

from bhid.reporting import EventAnalytics


class TestEventAnalytics(unittest.TestCase):

    def setUp(self):
        self.events = [
            {"event_id": "E1", "scene_id": "S1", "zone_id": "ZONE_CRITICAL", "risk_level": "CRITICAL", "prediction_probability": 0.95, "escalation_count": 2, "duration_seconds": 20.0, "status": "ACTIVE"},
            {"event_id": "E2", "scene_id": "S1", "zone_id": "ZONE_SAFE", "risk_level": "HIGH", "prediction_probability": 0.70, "escalation_count": 0, "duration_seconds": 10.0, "status": "RESOLVED"}
        ]

    def test_event_analysis(self):
        stats = EventAnalytics.event_statistics(self.events)
        self.assertEqual(stats["total_events"], 2)
        self.assertEqual(stats["active_events"], 1)

        dur = EventAnalytics.event_duration_analysis(self.events)
        self.assertEqual(dur["max_duration_seconds"], 20.0)
        self.assertEqual(dur["average_duration_seconds"], 15.0)

        rankings = EventAnalytics.zone_risk_ranking(self.events)
        self.assertEqual(rankings[0]["zone_id"], "ZONE_CRITICAL")
        self.assertEqual(rankings[0]["critical_count"], 1)


if __name__ == "__main__":
    unittest.main()
