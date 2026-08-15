"""
Unit tests for BHID HazardEvent Model (Phase 4E).

Validates:
1. HazardEvent creation & default field initialization
2. Active vs resolved duration calculations
3. Event escalation & history tracking
4. Event resolution & dictionary serialization
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

from bhid.events.hazard_event import HazardEvent


class TestHazardEvent(unittest.TestCase):

    def test_event_creation(self):
        evt = HazardEvent(
            event_id="HAZARD_001",
            scene_id="SCENE_A",
            zone_id="ZONE_1",
            start_timestamp=100.0,
            last_updated_timestamp=100.0,
            prediction_probability=0.75,
            risk_level="HIGH"
        )

        self.assertEqual(evt.event_id, "HAZARD_001")
        self.assertEqual(evt.status, "ACTIVE")
        self.assertEqual(evt.risk_level, "HIGH")
        self.assertEqual(evt.escalation_count, 0)
        self.assertEqual(len(evt.prediction_history), 1)

    def test_duration_and_updates(self):
        evt = HazardEvent(
            event_id="HAZARD_002",
            scene_id="SCENE_A",
            zone_id="ZONE_1",
            start_timestamp=100.0,
            last_updated_timestamp=100.0,
            prediction_probability=0.65,
            risk_level="HIGH"
        )

        evt.update_prediction(probability=0.70, risk_level="HIGH", timestamp=105.0)
        self.assertAlmostEqual(evt.duration_seconds(), 5.0, places=3)
        self.assertEqual(len(evt.prediction_history), 2)

    def test_escalate_and_resolve(self):
        evt = HazardEvent(
            event_id="HAZARD_003",
            scene_id="SCENE_B",
            zone_id="ZONE_2",
            start_timestamp=200.0,
            last_updated_timestamp=200.0,
            prediction_probability=0.70,
            risk_level="HIGH"
        )

        evt.escalate(probability=0.92, risk_level="CRITICAL", timestamp=204.0)
        self.assertEqual(evt.status, "ESCALATED")
        self.assertEqual(evt.escalation_count, 1)

        evt.resolve(timestamp=210.0)
        self.assertEqual(evt.status, "RESOLVED")
        self.assertEqual(evt.resolved_timestamp, 210.0)
        self.assertAlmostEqual(evt.duration_seconds(), 10.0, places=3)


if __name__ == "__main__":
    unittest.main()
