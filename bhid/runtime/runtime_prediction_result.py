"""
BHID Runtime Prediction Result Schema.

Encapsulates prediction output payload from Phase 3D Bottleneck Predictor.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class RuntimePredictionResult:
    """
    Structured output schema for runtime bottleneck risk assessment.
    
    Attributes:
        prediction_probability: Floating point prediction probability [0.0, 1.0].
        binary_prediction: Binary decision classification (0 = No Bottleneck, 1 = Bottleneck).
        risk_level: Categorical risk level ('LOW', 'MODERATE', 'HIGH', 'CRITICAL').
        threshold_used: Decision boundary probability threshold (frozen at 0.60).
        target_horizon: Prediction time horizon (frozen at 'Y30').
        timestamp: Time of observation / prediction.
        scene_id: Scene/video stream identifier.
        zone_id: Spatial ROI zone identifier.
        sample_id: Unique sample identifier string.
    """
    prediction_probability: float
    binary_prediction: int
    risk_level: str
    threshold_used: float
    target_horizon: str
    timestamp: float
    scene_id: str
    zone_id: str
    sample_id: Optional[str] = None

    def __post_init__(self):
        self.prediction_probability = float(self.prediction_probability)
        self.binary_prediction = int(self.binary_prediction)
        self.risk_level = str(self.risk_level).upper()
        self.threshold_used = float(self.threshold_used)
        self.target_horizon = str(self.target_horizon)
        self.timestamp = float(self.timestamp)
        self.scene_id = str(self.scene_id)
        self.zone_id = str(self.zone_id)
        if self.sample_id is None:
            self.sample_id = f"{self.scene_id}_{self.zone_id}_{int(self.timestamp)}"

    @classmethod
    def from_inference_output(
        cls,
        inference_dict: Dict[str, Any],
        scene_id: str,
        zone_id: str,
        timestamp: float
    ) -> "RuntimePredictionResult":
        """
        Factory method constructing RuntimePredictionResult from Phase 3D BottleneckPredictor output.
        """
        return cls(
            prediction_probability=inference_dict.get("prediction_probability", 0.0),
            binary_prediction=inference_dict.get("binary_prediction", 0),
            risk_level=inference_dict.get("risk_level", "LOW"),
            threshold_used=inference_dict.get("threshold_used", 0.60),
            target_horizon=inference_dict.get("target_horizon", "Y30"),
            timestamp=timestamp,
            scene_id=scene_id,
            zone_id=zone_id,
            sample_id=inference_dict.get("sample_id")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of prediction result."""
        return {
            "prediction_probability": self.prediction_probability,
            "binary_prediction": self.binary_prediction,
            "risk_level": self.risk_level,
            "threshold_used": self.threshold_used,
            "target_horizon": self.target_horizon,
            "timestamp": self.timestamp,
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "sample_id": self.sample_id
        }
