"""
BHID Single Source of Truth for Runtime Feature Definitions.

Encapsulates all 14 frozen spatiotemporal features approved in Phase 1-3D.
Provides validation, normalization, and bounds-checking utilities.
"""

from typing import Dict, Any, List
import math
from bhid.runtime.exceptions import FeatureValidationError

# Canonical 14 model feature names as defined in model_registry.json & predict_bottleneck.py
FROZEN_FEATURE_NAMES: List[str] = [
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

# Mapping of short / plain feature names to canonical model feature names
SHORT_TO_CANONICAL_MAP: Dict[str, str] = {
    "pedestrian_count": "feature_pedestrian_count",
    "density_ped_per_m2": "feature_density_ped_per_m2",
    "occupancy_ratio": "feature_occupancy_ratio",
    "mean_speed_m_s": "feature_mean_speed_m_s",
    "velocity_variance": "feature_velocity_variance",
    "acceleration_m_s2": "feature_acceleration_m_s2",
    "directional_entropy": "feature_directional_entropy",
    "inflow_rate_per_s": "feature_inflow_rate_per_s",
    "outflow_rate_per_s": "feature_outflow_rate_per_s",
    "net_flow_rate_per_s": "feature_net_flow_rate_per_s",
    "egress_deficit_ratio": "feature_egress_deficit_ratio",
    "trajectory_convergence": "feature_trajectory_convergence",
    "temporal_density_change": "feature_temporal_density_change",
    "temporal_speed_change": "feature_temporal_speed_change",
}

# Reverse mapping: canonical -> short
CANONICAL_TO_SHORT_MAP: Dict[str, str] = {v: k for k, v in SHORT_TO_CANONICAL_MAP.items()}


def normalize_feature_name(name: str) -> str:
    """Maps a short feature name or canonical feature name to the canonical model feature name."""
    if name in FROZEN_FEATURE_NAMES:
        return name
    if name in SHORT_TO_CANONICAL_MAP:
        return SHORT_TO_CANONICAL_MAP[name]
    if f"feature_{name}" in FROZEN_FEATURE_NAMES:
        return f"feature_{name}"
    return name


def normalize_feature_dict(raw_features: Dict[str, Any]) -> Dict[str, float]:
    """
    Normalizes feature dictionary keys to canonical model feature names
    and converts numeric values to float.
    """
    normalized: Dict[str, float] = {}
    for key, value in raw_features.items():
        norm_key = normalize_feature_name(key)
        if norm_key in FROZEN_FEATURE_NAMES:
            try:
                normalized[norm_key] = float(value)
            except (ValueError, TypeError) as e:
                raise FeatureValidationError(f"Invalid non-numeric value for feature '{key}': {value}") from e
    return normalized


def validate_feature_dict(feature_dict: Dict[str, Any]) -> Dict[str, float]:
    """
    Validates that input dictionary contains all 14 frozen features with non-null,
    valid finite numeric values. Returns normalized feature dict.
    
    Raises:
        FeatureValidationError if missing required features, contains NaN/Inf, or invalid type.
    """
    if not isinstance(feature_dict, dict):
        raise FeatureValidationError(f"Expected feature dictionary, got {type(feature_dict).__name__}")

    normalized = normalize_feature_dict(feature_dict)
    
    missing = [feat for feat in FROZEN_FEATURE_NAMES if feat not in normalized]
    if missing:
        raise FeatureValidationError(f"Missing required features ({len(missing)}/14): {missing}")

    for feat in FROZEN_FEATURE_NAMES:
        val = normalized[feat]
        if math.isnan(val) or math.isinf(val):
            raise FeatureValidationError(f"Feature '{feat}' contains invalid value: {val}")

    return normalized
