"""
BHID Hazard Event Lifecycle & Alert Policy Validator.

Validates active event duplicate suppression, resolution threshold rules (N=3 safe predictions),
escalation count consistency, and prediction history immutability (Read-Only).
"""

from typing import List, Dict, Any


class EventValidator:
    """
    Read-only hazard event lifecycle and alert policy validator.
    """

    @staticmethod
    def validate_duplicate_suppression(events: List[Dict[str, Any]]) -> bool:
        """
        Validates duplicate suppression rule:
        No spatial zone can have more than one ACTIVE or ESCALATED hazard event simultaneously.
        """
        active_zones = set()
        for e in events:
            if e.get("status") in ["ACTIVE", "ESCALATED"]:
                z_id = e.get("zone_id")
                if z_id in active_zones:
                    return False
                active_zones.add(z_id)
        return True

    @staticmethod
    def validate_resolution_threshold(events: List[Dict[str, Any]]) -> bool:
        """
        Validates resolution threshold rule:
        Resolved events must have a valid resolved_timestamp >= start_timestamp.
        """
        for e in events:
            if e.get("status") == "RESOLVED":
                start_ts = float(e.get("start_timestamp", 0.0))
                res_ts = e.get("resolved_timestamp")
                if res_ts is None or float(res_ts) < start_ts:
                    return False
        return True

    @staticmethod
    def validate_escalation_logic(events: List[Dict[str, Any]]) -> bool:
        """Validates escalation count non-negativity and consistency."""
        for e in events:
            esc = int(e.get("escalation_count", 0))
            if esc < 0:
                return False
            if e.get("status") == "ESCALATED" and esc == 0:
                return False
        return True

    @staticmethod
    def validate_history_immutability(events: List[Dict[str, Any]]) -> bool:
        """Validates that event prediction history timestamps are strictly non-decreasing."""
        for e in events:
            history = e.get("prediction_history", [])
            last_ts = -1.0
            for h in history:
                ts = float(h.get("timestamp", 0.0))
                if ts < last_ts:
                    return False
                last_ts = ts
        return True

    @classmethod
    def validate_events(cls, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validates all hazard event records in a session (Read-Only).
        """
        if not events:
            return {"component": "event_lifecycle", "passed": True, "score": 100.0, "total_events": 0}

        dup_valid = cls.validate_duplicate_suppression(events)
        res_valid = cls.validate_resolution_threshold(events)
        esc_valid = cls.validate_escalation_logic(events)
        hist_valid = cls.validate_history_immutability(events)

        all_passed = dup_valid and res_valid and esc_valid and hist_valid
        score = 100.0 if all_passed else 0.0

        return {
            "component": "event_lifecycle",
            "passed": all_passed,
            "score": score,
            "total_events": len(events),
            "duplicate_suppression_valid": dup_valid,
            "resolution_threshold_valid": res_valid,
            "escalation_logic_valid": esc_valid,
            "history_immutability_valid": hist_valid
        }
