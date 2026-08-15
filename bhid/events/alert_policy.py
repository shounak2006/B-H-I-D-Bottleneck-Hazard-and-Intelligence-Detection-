"""
BHID Alert Decision Policy.

Encapsulates event trigger, escalation, and resolution policy rules based strictly
on Phase 3D RuntimePredictionResult outputs.
"""

from typing import Dict, Any, Optional
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.events.hazard_event import HazardEvent


class AlertPolicy:
    """
    Central operational decision rules for hazard alert lifecycle.
    
    Parameters:
        safe_resolution_threshold: Number of consecutive safe predictions required to resolve an active event (default: 3).
        escalation_prob_delta: Probability increase step triggering escalation (default: 0.15).
    """

    def __init__(
        self,
        safe_resolution_threshold: int = 3,
        escalation_prob_delta: float = 0.15
    ):
        self.safe_resolution_threshold = int(safe_resolution_threshold)
        self.escalation_prob_delta = float(escalation_prob_delta)

    def should_create_event(self, result: RuntimePredictionResult) -> bool:
        """
        Determines whether a new HazardEvent should be created for a prediction.
        Triggers when binary_prediction == 1 or risk level is HIGH / CRITICAL.
        """
        return bool(
            result.binary_prediction == 1 or
            result.risk_level in ["HIGH", "CRITICAL"] or
            result.prediction_probability >= result.threshold_used
        )

    def should_escalate_event(
        self,
        event: HazardEvent,
        result: RuntimePredictionResult
    ) -> bool:
        """
        Determines whether an existing active HazardEvent should be escalated.
        Triggers if risk level transitions to CRITICAL or probability increases significantly.
        """
        if event.status == "RESOLVED":
            return False

        # Escalation condition 1: Transition to CRITICAL risk from non-CRITICAL
        if result.risk_level == "CRITICAL" and event.risk_level != "CRITICAL":
            return True

        # Escalation condition 2: Probability jump > escalation_prob_delta above current event probability
        if result.prediction_probability >= (event.prediction_probability + self.escalation_prob_delta):
            return True

        return False

    def should_resolve_event(
        self,
        event: HazardEvent,
        consecutive_safe_count: int
    ) -> bool:
        """
        Determines whether an active HazardEvent should be resolved.
        Requires a sustained sequence of consecutive safe predictions (consecutive_safe_count >= safe_resolution_threshold).
        Prevents single-frame LOW predictions from prematurely resolving active critical hazards.
        """
        if event.status == "RESOLVED":
            return False

        return consecutive_safe_count >= self.safe_resolution_threshold
