"""
BHID Prediction Integrity & Determinism Validator.

Validates persisted prediction probability bounds, decision threshold enforcement (0.60),
and risk level mapping without re-running model inference (Read-Only).
"""

from typing import List, Dict, Any


class PredictionValidator:
    """
    Read-only prediction validator operating on persisted session records.
    """

    @staticmethod
    def validate_probability_range(predictions: List[Dict[str, Any]]) -> bool:
        """Validates that all prediction probabilities fall within [0.0, 1.0]."""
        for p in predictions:
            prob = float(p.get("prediction_probability", -1.0))
            if not (0.0 <= prob <= 1.0):
                return False
        return True

    @staticmethod
    def validate_threshold_enforcement(predictions: List[Dict[str, Any]]) -> bool:
        """
        Validates binary classification decision rule:
        binary_prediction == 1 if and only if prediction_probability >= 0.60.
        """
        for p in predictions:
            prob = float(p.get("prediction_probability", 0.0))
            bin_pred = int(p.get("binary_prediction", 0))
            expected_bin = 1 if prob >= 0.60 else 0
            if bin_pred != expected_bin:
                return False
        return True

    @staticmethod
    def validate_risk_level_mapping(predictions: List[Dict[str, Any]]) -> bool:
        """
        Validates 4-tier risk level mapping rule:
        - LOW: probability < 0.30
        - MODERATE: 0.30 <= probability < 0.60
        - HIGH: 0.60 <= probability < 0.85
        - CRITICAL: probability >= 0.85
        """
        for p in predictions:
            prob = float(p.get("prediction_probability", 0.0))
            risk = str(p.get("risk_level", "")).upper()

            if prob < 0.30:
                expected_risk = "LOW"
            elif prob < 0.60:
                expected_risk = "MODERATE"
            elif prob < 0.85:
                expected_risk = "HIGH"
            else:
                expected_risk = "CRITICAL"

            if risk != expected_risk:
                return False
        return True

    @classmethod
    def validate_predictions(cls, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates all prediction records in a session (Read-Only, No Re-Inference).
        """
        if not predictions:
            return {"component": "prediction_integrity", "passed": True, "score": 100.0, "total_predictions": 0}

        prob_valid = cls.validate_probability_range(predictions)
        thresh_valid = cls.validate_threshold_enforcement(predictions)
        risk_valid = cls.validate_risk_level_mapping(predictions)

        all_passed = prob_valid and thresh_valid and risk_valid
        score = 100.0 if all_passed else 0.0

        return {
            "component": "prediction_integrity",
            "passed": all_passed,
            "score": score,
            "total_predictions": len(predictions),
            "probability_range_valid": prob_valid,
            "threshold_enforcement_valid": thresh_valid,
            "risk_level_mapping_valid": risk_valid
        }
