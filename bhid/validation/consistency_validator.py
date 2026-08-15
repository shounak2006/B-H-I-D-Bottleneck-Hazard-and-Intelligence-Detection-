"""
BHID Cross-Phase Schema Consistency Validator.

Verifies strict schema compatibility across Detection, Tracking, Analytics, Prediction,
Hazard Event, and Persistence interfaces without mutating any stored data (Read-Only).
"""

from typing import Dict, Any, List


class ConsistencyValidator:
    """
    Read-only schema consistency validator across all BHID pipeline stages.
    """

    FROZEN_14_FEATURES = [
        "feature_pedestrian_count",
        "feature_density_ped_per_m2",
        "feature_occupancy_ratio",
        "feature_mean_speed_m_s",
        "feature_velocity_variance",
        "feature_acceleration_m_s2",
        "feature_directional_entropy",
        "feature_inflow_rate_per_s",
        "feature_outflow_rate_per_s",
        "feature_net_flow_rate_per_s",
        "feature_egress_deficit_ratio",
        "feature_trajectory_convergence",
        "feature_temporal_density_change",
        "feature_temporal_speed_change"
    ]

    @classmethod
    def validate_analytics_schema(cls, analytics_record: Dict[str, Any]) -> bool:
        """Validates that an analytics record contains all 14 frozen spatiotemporal features."""
        features = analytics_record.get("features", {})
        for feat in cls.FROZEN_14_FEATURES:
            if feat not in features:
                return False
        return True

    @staticmethod
    def validate_prediction_schema(prediction_record: Dict[str, Any]) -> bool:
        """Validates prediction result record fields, horizon (Y30), and threshold (0.60)."""
        required = ["prediction_probability", "binary_prediction", "risk_level", "threshold_used", "target_horizon"]
        for req in required:
            if req not in prediction_record:
                return False
        if str(prediction_record.get("target_horizon")) != "Y30":
            return False
        if float(prediction_record.get("threshold_used", 0.0)) != 0.60:
            return False
        return True

    @staticmethod
    def validate_event_schema(event_record: Dict[str, Any]) -> bool:
        """Validates hazard event record schema."""
        required = ["event_id", "scene_id", "zone_id", "start_timestamp", "status", "risk_level", "prediction_probability"]
        for req in required:
            if req not in event_record:
                return False
        if event_record.get("status") not in ["ACTIVE", "ESCALATED", "RESOLVED"]:
            return False
        return True

    @classmethod
    def validate_pipeline_schemas(
        cls,
        predictions: List[Dict[str, Any]],
        analytics: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates all pipeline record schemas across a session (Read-Only).
        """
        ana_valid = all(cls.validate_analytics_schema(a) for a in analytics) if analytics else True
        pred_valid = all(cls.validate_prediction_schema(p) for p in predictions) if predictions else True
        evt_valid = all(cls.validate_event_schema(e) for e in events) if events else True

        all_passed = ana_valid and pred_valid and evt_valid
        score = 100.0 if all_passed else 0.0

        return {
            "component": "schema_consistency",
            "passed": all_passed,
            "score": score,
            "analytics_schema_valid": ana_valid,
            "prediction_schema_valid": pred_valid,
            "event_schema_valid": evt_valid,
            "frozen_features_count": len(cls.FROZEN_14_FEATURES)
        }
