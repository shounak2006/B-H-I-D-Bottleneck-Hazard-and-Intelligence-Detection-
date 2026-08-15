"""
BHID Operational Readiness System Evaluator.

Computes weighted operational readiness score (0.0 - 100.0%) and system health status
(PASSED, WARNING, FAILED) based on explicit component weights.

Readiness Score Formula:
    Score = sum(w_c * S_c) for all validation components c
    where:
        w_schema = 0.15
        w_prediction = 0.20
        w_event = 0.20
        w_persistence = 0.15
        w_replay = 0.15
        w_reporting = 0.15
"""

from typing import Dict, Any, Tuple, Optional
from bhid.validation.validation_config import ValidationConfig


class SystemEvaluator:
    """
    Operational readiness scoring engine and system health evaluator.
    """

    @classmethod
    def compute_readiness_score(
        cls,
        results: Dict[str, Dict[str, Any]],
        config: Optional[ValidationConfig] = None
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Computes weighted composite operational readiness score and overall health status.
        
        Returns:
            Tuple of (readiness_score_pct, health_status, score_breakdown_dict)
        """
        cfg = config or ValidationConfig()
        weights = cfg.component_weights

        total_weighted_score = 0.0
        total_weight = 0.0
        breakdown = {}
        all_passed = True

        for comp_key, weight in weights.items():
            comp_res = results.get(comp_key, {})
            score = float(comp_res.get("score", 0.0))
            passed = bool(comp_res.get("passed", False))

            if not passed:
                all_passed = False

            weighted_contrib = weight * score
            total_weighted_score += weighted_contrib
            total_weight += weight

            breakdown[comp_key] = {
                "weight": weight,
                "score": score,
                "passed": passed,
                "weighted_contribution": round(weighted_contrib, 2)
            }

        final_score = round(total_weighted_score, 2)

        # Health status determination
        if final_score >= cfg.readiness_pass_threshold and all_passed:
            status = "PASSED"
        elif final_score >= 80.0:
            status = "WARNING"
        else:
            status = "FAILED"

        return final_score, status, breakdown

    @classmethod
    def evaluate_system(
        cls,
        results: Dict[str, Dict[str, Any]],
        config: Optional[ValidationConfig] = None
    ) -> Dict[str, Any]:
        """
        Generates complete system evaluation report dictionary.
        """
        score, status, breakdown = cls.compute_readiness_score(results, config)
        cfg = config or ValidationConfig()

        return {
            "overall_status": status,
            "readiness_score_pct": score,
            "pass_threshold_pct": cfg.readiness_pass_threshold,
            "ready_for_release": (status == "PASSED"),
            "component_breakdown": breakdown,
            "validation_components_count": len(breakdown)
        }
