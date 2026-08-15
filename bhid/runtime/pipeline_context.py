"""
BHID Centralized Runtime State Container.

Tracks active scene/zone context, rolling feature window buffer,
latest prediction results, bottleneck risk state, and runtime execution metadata.
"""

from typing import Dict, Any, List, Optional
import time
from bhid.runtime.feature_window_manager import FeatureWindowManager


class PipelineContext:
    """
    Centralized runtime state container for BHID pipeline execution.
    
    Parameters:
        active_scene: Identifier for active scene/video stream (default: "DEFAULT_SCENE").
        active_zone: Identifier for target spatial zone/ROI (default: "ZONE_ALL").
        feature_buffer: Optional existing FeatureWindowManager instance.
        runtime_metadata: Optional initial metadata dictionary.
    """

    def __init__(
        self,
        active_scene: str = "DEFAULT_SCENE",
        active_zone: str = "ZONE_ALL",
        feature_buffer: Optional[FeatureWindowManager] = None,
        runtime_metadata: Optional[Dict[str, Any]] = None
    ):
        self.active_scene = str(active_scene)
        self.active_zone = str(active_zone)
        self.current_timestamp: float = time.time()
        self.feature_buffer = feature_buffer or FeatureWindowManager()
        
        self.prediction_results: List[Dict[str, Any]] = []
        self.latest_prediction: Optional[Dict[str, Any]] = None
        self.bottleneck_state: str = "LOW"
        self.is_bottleneck_active: bool = False
        
        self.runtime_metadata: Dict[str, Any] = runtime_metadata or {
            "processed_frames": 0,
            "total_predictions": 0,
            "created_at": self.current_timestamp
        }

    def update_timestamp(self, ts: float) -> None:
        """Updates current runtime timestamp."""
        self.current_timestamp = float(ts)

    def set_active_location(self, scene_id: str, zone_id: str) -> None:
        """Updates active scene and zone identifiers."""
        self.active_scene = str(scene_id)
        self.active_zone = str(zone_id)

    def record_prediction(self, prediction_result_dict: Dict[str, Any]) -> None:
        """Records a new prediction result and updates current bottleneck risk state."""
        self.latest_prediction = dict(prediction_result_dict)
        self.prediction_results.append(dict(prediction_result_dict))
        
        # Keep only latest 100 predictions in context history
        if len(self.prediction_results) > 100:
            self.prediction_results.pop(0)

        risk_level = prediction_result_dict.get("risk_level", "LOW")
        binary_pred = prediction_result_dict.get("binary_prediction", 0)

        self.bottleneck_state = risk_level
        self.is_bottleneck_active = bool(binary_pred == 1)
        
        self.runtime_metadata["total_predictions"] = self.runtime_metadata.get("total_predictions", 0) + 1

    def increment_frame_count(self) -> None:
        """Increments processed frames counter."""
        self.runtime_metadata["processed_frames"] = self.runtime_metadata.get("processed_frames", 0) + 1

    def to_dict(self) -> Dict[str, Any]:
        """Serializes current runtime context to dictionary format."""
        return {
            "active_scene": self.active_scene,
            "active_zone": self.active_zone,
            "current_timestamp": self.current_timestamp,
            "buffer_size": self.feature_buffer.size,
            "bottleneck_state": self.bottleneck_state,
            "is_bottleneck_active": self.is_bottleneck_active,
            "latest_prediction": self.latest_prediction,
            "runtime_metadata": dict(self.runtime_metadata)
        }

    def reset(self) -> None:
        """Resets buffer, prediction history, and counters."""
        self.feature_buffer.clear()
        self.prediction_results.clear()
        self.latest_prediction = None
        self.bottleneck_state = "LOW"
        self.is_bottleneck_active = False
        self.runtime_metadata["processed_frames"] = 0
        self.runtime_metadata["total_predictions"] = 0
