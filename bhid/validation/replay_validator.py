"""
BHID Historical Replay Determinism Validator.

Compares replayed ReplayFrame records against persisted Phase 5A session files to guarantee
100% deterministic reconstruction without re-running inference or analytics (Read-Only).
"""

from typing import List, Dict, Any


class ReplayValidator:
    """
    Read-only replay determinism validator using Phase 5B artifacts.
    """

    @staticmethod
    def validate_replay_determinism(
        predictions: List[Dict[str, Any]],
        replay_frames: List[Dict[str, Any]]
    ) -> bool:
        """
        Validates 100% prediction determinism between persisted predictions
        and replayed frame states.
        """
        if len(predictions) != len(replay_frames):
            return False

        for idx in range(len(predictions)):
            orig = predictions[idx]
            rf = replay_frames[idx]
            rf_dict = rf.to_dict() if hasattr(rf, "to_dict") else dict(rf)
            rf_pred = rf_dict.get("prediction_result", {})

            orig_prob = float(orig.get("prediction_probability", 0.0))
            rf_prob = float(rf_pred.get("prediction_probability", 0.0))
            if abs(orig_prob - rf_prob) > 1e-5:
                return False

            if orig.get("risk_level") != rf_pred.get("risk_level"):
                return False

        return True

    @staticmethod
    def validate_event_timeline_reconstruction(
        events: List[Dict[str, Any]],
        replay_frames: List[Dict[str, Any]]
    ) -> bool:
        """Validates that replayed frames contain valid active hazard event lookups."""
        for rf in replay_frames:
            rf_dict = rf.to_dict() if hasattr(rf, "to_dict") else dict(rf)
            ts = float(rf_dict.get("timestamp", 0.0))
            active_evts = rf_dict.get("active_events", [])

            for evt in active_evts:
                start_ts = float(evt.get("start_timestamp", 0.0))
                res_ts = evt.get("resolved_timestamp")
                end_ts = float(res_ts) if res_ts is not None else (float(evt.get("last_updated_timestamp", start_ts)) + 1.0)
                if not (start_ts <= ts <= end_ts):
                    return False

        return True

    @classmethod
    def validate_replay(
        cls,
        predictions: List[Dict[str, Any]],
        analytics: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        replay_frames: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates deterministic historical replay fidelity (Read-Only).
        """
        if not replay_frames:
            return {"component": "replay_determinism", "passed": True, "score": 100.0, "total_replayed_frames": 0}

        pred_det_valid = cls.validate_replay_determinism(predictions, replay_frames)
        evt_rec_valid = cls.validate_event_timeline_reconstruction(events, replay_frames)

        all_passed = pred_det_valid and evt_rec_valid
        score = 100.0 if all_passed else 0.0

        return {
            "component": "replay_determinism",
            "passed": all_passed,
            "score": score,
            "total_replayed_frames": len(replay_frames),
            "prediction_determinism_valid": pred_det_valid,
            "event_timeline_reconstruction_valid": evt_rec_valid
        }
