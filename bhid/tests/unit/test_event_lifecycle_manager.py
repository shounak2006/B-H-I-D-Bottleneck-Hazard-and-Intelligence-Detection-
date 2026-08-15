"""
Unit tests for BHID EventLifecycleManager (Phase 4E).

Validates:
1. Event state transitions (NEW -> ACTIVE -> ESCALATED -> RESOLVED)
2. Duplicate event suppression for same spatial zone
3. Sustained safe condition resolution requirement (threshold = 3)
4. Immutable history archival upon event resolution
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
from bhid.events.event_lifecycle_manager import EventLifecycleManager
from bhid.events.alert_policy import AlertPolicy


class TestEventLifecycleManager(unittest.TestCase):

    def setUp(self):
        policy = AlertPolicy(safe_resolution_threshold=3, escalation_prob_delta=0.15)
        self.mgr = EventLifecycleManager(alert_policy=policy)

        self.res_high = RuntimePredictionResult(
            prediction_probability=0.70, binary_prediction=1, risk_level="HIGH",
            threshold_used=0.60, target_horizon="Y30", timestamp=100.0, scene_id="S1", zone_id="Z1"
        )
        self.res_critical = RuntimePredictionResult(
            prediction_probability=0.92, binary_prediction=1, risk_level="CRITICAL",
            threshold_used=0.60, target_horizon="Y30", timestamp=104.0, scene_id="S1", zone_id="Z1"
        )
        self.res_safe = RuntimePredictionResult(
            prediction_probability=0.20, binary_prediction=0, risk_level="LOW",
            threshold_used=0.60, target_horizon="Y30", timestamp=108.0, scene_id="S1", zone_id="Z1"
        )

    def test_new_event_creation_and_duplicate_suppression(self):
        # 1. Process HIGH prediction -> Creates NEW active event
        e1 = self.mgr.process_prediction(self.res_high)
        self.assertIsNotNone(e1)
        self.assertEqual(e1.status, "ACTIVE")
        self.assertEqual(len(self.mgr.registry.get_active_events()), 1)

        # 2. Process another HIGH prediction for same zone -> Suppresses duplicate creation, updates active event
        res_high_2 = RuntimePredictionResult(
            prediction_probability=0.72, binary_prediction=1, risk_level="HIGH",
            threshold_used=0.60, target_horizon="Y30", timestamp=102.0, scene_id="S1", zone_id="Z1"
        )
        e2 = self.mgr.process_prediction(res_high_2)
        self.assertEqual(e2.event_id, e1.event_id)
        self.assertEqual(len(self.mgr.registry.get_active_events()), 1)

    def test_event_escalation(self):
        self.mgr.process_prediction(self.res_high)
        
        # Process CRITICAL prediction -> Escalates active event
        e_esc = self.mgr.process_prediction(self.res_critical)
        self.assertEqual(e_esc.status, "ESCALATED")
        self.assertEqual(e_esc.escalation_count, 1)

    def test_sustained_safe_resolution(self):
        # Create event
        self.mgr.process_prediction(self.res_high)
        self.assertEqual(len(self.mgr.registry.get_active_events()), 1)

        # 1st LOW prediction -> safe count = 1 -> STILL ACTIVE
        e_safe1 = self.mgr.process_prediction(self.res_safe)
        self.assertEqual(e_safe1.status, "ACTIVE")
        self.assertEqual(len(self.mgr.registry.get_active_events()), 1)

        # 2nd LOW prediction -> safe count = 2 -> STILL ACTIVE
        res_safe_2 = RuntimePredictionResult(
            prediction_probability=0.18, binary_prediction=0, risk_level="LOW",
            threshold_used=0.60, target_horizon="Y30", timestamp=112.0, scene_id="S1", zone_id="Z1"
        )
        e_safe2 = self.mgr.process_prediction(res_safe_2)
        self.assertEqual(e_safe2.status, "ACTIVE")
        self.assertEqual(len(self.mgr.registry.get_active_events()), 1)

        # 3rd LOW prediction -> safe count = 3 -> RESOLVES event and archives to history
        res_safe_3 = RuntimePredictionResult(
            prediction_probability=0.15, binary_prediction=0, risk_level="LOW",
            threshold_used=0.60, target_horizon="Y30", timestamp=116.0, scene_id="S1", zone_id="Z1"
        )
        e_resolved = self.mgr.process_prediction(res_safe_3)
        self.assertEqual(e_resolved.status, "RESOLVED")
        self.assertEqual(len(self.mgr.registry.get_active_events()), 0)
        self.assertEqual(len(self.mgr.history.get_all_events()), 1)


if __name__ == "__main__":
    unittest.main()
