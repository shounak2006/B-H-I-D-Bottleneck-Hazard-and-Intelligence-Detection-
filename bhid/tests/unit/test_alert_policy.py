"""
Unit tests for BHID AlertPolicy (Phase 4E).

Validates:
1. Event creation policy rules
2. Event escalation policy rules
3. Sustained safe prediction resolution policy rules
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
from bhid.events.hazard_event import HazardEvent
from bhid.events.alert_policy import AlertPolicy


class TestAlertPolicy(unittest.TestCase):

    def setUp(self):
        self.policy = AlertPolicy(safe_resolution_threshold=3, escalation_prob_delta=0.15)

    def test_should_create_event(self):
        res_safe = RuntimePredictionResult(
            prediction_probability=0.20,
            binary_prediction=0,
            risk_level="LOW",
            threshold_used=0.60,
            target_horizon="Y30",
            timestamp=100.0,
            scene_id="S1",
            zone_id="Z1"
        )
        self.assertFalse(self.policy.should_create_event(res_safe))

        res_hazard = RuntimePredictionResult(
            prediction_probability=0.75,
            binary_prediction=1,
            risk_level="HIGH",
            threshold_used=0.60,
            target_horizon="Y30",
            timestamp=100.0,
            scene_id="S1",
            zone_id="Z1"
        )
        self.assertTrue(self.policy.should_create_event(res_hazard))

    def test_should_escalate_event(self):
        evt = HazardEvent(
            event_id="E1",
            scene_id="S1",
            zone_id="Z1",
            start_timestamp=100.0,
            last_updated_timestamp=100.0,
            prediction_probability=0.65,
            risk_level="HIGH"
        )

        res_critical = RuntimePredictionResult(
            prediction_probability=0.92,
            binary_prediction=1,
            risk_level="CRITICAL",
            threshold_used=0.60,
            target_horizon="Y30",
            timestamp=104.0,
            scene_id="S1",
            zone_id="Z1"
        )
        self.assertTrue(self.policy.should_escalate_event(evt, res_critical))

    def test_should_resolve_event_requires_sustained_safe_count(self):
        evt = HazardEvent("E1", "S1", "Z1", 100.0, 100.0, 0.75, "HIGH")

        # 1 safe prediction: count = 1 -> should NOT resolve
        self.assertFalse(self.policy.should_resolve_event(evt, consecutive_safe_count=1))
        # 2 safe predictions: count = 2 -> should NOT resolve
        self.assertFalse(self.policy.should_resolve_event(evt, consecutive_safe_count=2))
        # 3 safe predictions: count = 3 -> SHOULD resolve
        self.assertTrue(self.policy.should_resolve_event(evt, consecutive_safe_count=3))


if __name__ == "__main__":
    unittest.main()
