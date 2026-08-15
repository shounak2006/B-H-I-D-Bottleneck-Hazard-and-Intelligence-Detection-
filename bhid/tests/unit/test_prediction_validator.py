"""
Unit tests for BHID PredictionValidator (Phase 5D).

Validates:
1. Prediction probability bounds [0.0, 1.0]
2. Decision threshold enforcement (0.60)
3. 4-tier risk level mapping
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

from bhid.validation import PredictionValidator


class TestPredictionValidator(unittest.TestCase):

    def test_valid_predictions(self):
        preds = [
            {"prediction_probability": 0.10, "binary_prediction": 0, "risk_level": "LOW"},
            {"prediction_probability": 0.40, "binary_prediction": 0, "risk_level": "MODERATE"},
            {"prediction_probability": 0.70, "binary_prediction": 1, "risk_level": "HIGH"},
            {"prediction_probability": 0.90, "binary_prediction": 1, "risk_level": "CRITICAL"}
        ]
        res = PredictionValidator.validate_predictions(preds)
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 100.0)

    def test_invalid_threshold_enforcement(self):
        invalid_preds = [
            {"prediction_probability": 0.70, "binary_prediction": 0, "risk_level": "HIGH"} # Should be 1
        ]
        res = PredictionValidator.validate_predictions(invalid_preds)
        self.assertFalse(res["passed"])


if __name__ == "__main__":
    unittest.main()
