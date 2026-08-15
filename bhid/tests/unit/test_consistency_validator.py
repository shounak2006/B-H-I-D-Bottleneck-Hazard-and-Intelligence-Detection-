"""
Unit tests for BHID ConsistencyValidator (Phase 5D).

Validates:
1. Schema consistency verification across Analytics, Predictions, and Events (Read-Only)
2. 14 frozen feature vector verification
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

from bhid.validation import ConsistencyValidator


class TestConsistencyValidator(unittest.TestCase):

    def setUp(self):
        sample_features = {f: 0.1 for f in ConsistencyValidator.FROZEN_14_FEATURES}
        self.analytics = [{"features": sample_features}]
        self.predictions = [{
            "prediction_probability": 0.80, "binary_prediction": 1, "risk_level": "HIGH",
            "threshold_used": 0.60, "target_horizon": "Y30"
        }]
        self.events = [{
            "event_id": "E1", "scene_id": "S1", "zone_id": "Z1", "start_timestamp": 10.0,
            "status": "ACTIVE", "risk_level": "HIGH", "prediction_probability": 0.80
        }]

    def test_schema_validations(self):
        res = ConsistencyValidator.validate_pipeline_schemas(self.predictions, self.analytics, self.events)
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 100.0)


if __name__ == "__main__":
    unittest.main()
