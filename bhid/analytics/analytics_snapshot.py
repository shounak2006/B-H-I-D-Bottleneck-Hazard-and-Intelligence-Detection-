"""
BHID Analytics Snapshot Data Structure.

Dataclass container holding all 14 spatiotemporal crowd analytics features for a frame.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from bhid.runtime.feature_schema import validate_feature_dict, FROZEN_FEATURE_NAMES, SHORT_TO_CANONICAL_MAP
from bhid.runtime.exceptions import FeatureValidationError


@dataclass
class AnalyticsSnapshot:
    """
    Container for 14-feature crowd analytics snapshot for a single frame.
    
    Attributes:
        frame_id: Frame sequence identifier.
        timestamp: Time of observation.
        scene_id: Active scene identifier.
        zone_id: Active zone/ROI identifier.
        features: Dictionary of the 14 spatiotemporal feature values.
    """
    frame_id: Any
    timestamp: float
    scene_id: str = "DEFAULT_SCENE"
    zone_id: str = "ZONE_ALL"
    features: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        self.timestamp = float(self.timestamp)
        self.scene_id = str(self.scene_id)
        self.zone_id = str(self.zone_id)
        if self.features:
            self.validate()

    def validate(self) -> Dict[str, float]:
        """
        Validates feature schema completeness and correctness.
        Returns normalized feature dict with canonical model feature names (feature_*).
        """
        if not self.features:
            raise FeatureValidationError("AnalyticsSnapshot features dictionary is empty.")
        validated = validate_feature_dict(self.features)
        return validated

    def export_feature_vector(self) -> Dict[str, float]:
        """
        Exports feature dictionary formatted with canonical feature_* model column names
        matching Phase 3D BottleneckPredictor schema.
        """
        return self.validate()

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of snapshot."""
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "features": self.export_feature_vector()
        }
