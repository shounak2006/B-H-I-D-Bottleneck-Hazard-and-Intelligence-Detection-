"""
BHID Runtime Prediction Request Schema.

Encapsulates prediction input payload passed to the Phase 3D Bottleneck Predictor.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Union
import pandas as pd
from bhid.runtime.feature_schema import validate_feature_dict, FROZEN_FEATURE_NAMES
from bhid.runtime.exceptions import FeatureValidationError


@dataclass
class RuntimePredictionRequest:
    """
    Input payload for runtime bottleneck prediction.
    
    Attributes:
        scene_id: Scene/video stream identifier.
        zone_id: Spatial ROI zone identifier.
        timestamp: Time of feature observation.
        features: Dictionary containing all 14 frozen spatiotemporal feature values.
    """
    scene_id: str
    zone_id: str
    timestamp: float
    features: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        self.scene_id = str(self.scene_id)
        self.zone_id = str(self.zone_id)
        self.timestamp = float(self.timestamp)
        if self.features:
            self.features = validate_feature_dict(self.features)

    def validate(self) -> Dict[str, float]:
        """Validates feature schema and returns normalized features dictionary."""
        self.features = validate_feature_dict(self.features)
        return self.features

    def to_model_dict(self) -> Dict[str, Any]:
        """
        Converts request to dictionary format required by Phase 3D BottleneckPredictor.predict_single().
        Includes sample_id constructed from scene, zone, and timestamp.
        """
        validated_feat = self.validate()
        sample_id = f"{self.scene_id}_{self.zone_id}_{int(self.timestamp)}"
        payload = dict(validated_feat)
        payload["sample_id"] = sample_id
        return payload

    def to_dataframe(self) -> pd.DataFrame:
        """Converts request to a single-row pandas DataFrame for batch/model inference."""
        model_dict = self.to_model_dict()
        return pd.DataFrame([model_dict])

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of the request."""
        return {
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "timestamp": self.timestamp,
            "features": dict(self.features)
        }
