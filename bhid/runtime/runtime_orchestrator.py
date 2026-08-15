"""
BHID Runtime Orchestrator.

Main runtime coordinator orchestrating crowd feature streams, rolling window buffers,
prediction engine execution, state context management, and risk assessment events.
"""

import time
from typing import Dict, Any, List, Optional
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor
from bhid.runtime.pipeline_context import PipelineContext
from bhid.runtime.feature_window_manager import FeatureWindowManager
from bhid.runtime.runtime_prediction_request import RuntimePredictionRequest
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.runtime.exceptions import PredictionError, FeatureValidationError


class RuntimeOrchestrator:
    """
    Main orchestrator connecting feature input streams to Phase 3D prediction engine.
    
    Parameters:
        predictor: Optional BottleneckPredictor instance. If None, initializes default predictor.
        context: Optional PipelineContext instance. If None, initializes default context.
    """

    def __init__(
        self,
        predictor: Optional[BottleneckPredictor] = None,
        context: Optional[PipelineContext] = None
    ):
        if predictor is None:
            self.predictor = BottleneckPredictor()
        else:
            self.predictor = predictor

        if context is None:
            self.context = PipelineContext()
        else:
            self.context = context

    @property
    def feature_buffer(self) -> FeatureWindowManager:
        """Returns the rolling feature window manager from current context."""
        return self.context.feature_buffer

    def process_snapshot(
        self,
        features: Dict[str, Any],
        timestamp: Optional[float] = None,
        scene_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RuntimePredictionResult:
        """
        Ingests a single crowd feature snapshot, updates rolling window buffer,
        runs Phase 3D prediction inference, updates pipeline context, and returns prediction result.
        
        Args:
            features: Dictionary containing feature values.
            timestamp: Time of observation (defaults to current system time if None).
            scene_id: Scene identifier (defaults to context active scene if None).
            zone_id: Zone identifier (defaults to context active zone if None).
            metadata: Optional metadata dictionary.
            
        Returns:
            RuntimePredictionResult encapsulating bottleneck risk assessment.
            
        Raises:
            FeatureValidationError: If features fail schema validation.
            PredictionError: If inference engine fails execution.
        """
        ts = time.time() if timestamp is None else float(timestamp)
        s_id = self.context.active_scene if scene_id is None else str(scene_id)
        z_id = self.context.active_zone if zone_id is None else str(zone_id)

        # 1. Update location context and timestamp
        self.context.set_active_location(s_id, z_id)
        self.context.update_timestamp(ts)
        self.context.increment_frame_count()

        # 2. Add sample to pure rolling feature window buffer
        sample_record = self.feature_buffer.add_sample(
            features=features,
            timestamp=ts,
            metadata=metadata,
            validate=True
        )

        # 3. Create prediction request payload using validated 14 features
        req = RuntimePredictionRequest(
            scene_id=s_id,
            zone_id=z_id,
            timestamp=ts,
            features=sample_record.features
        )

        # 4. Invoke Phase 3D Bottleneck Predictor
        try:
            inference_output = self.predictor.predict_single(req.to_model_dict())
        except Exception as e:
            if isinstance(e, FeatureValidationError):
                raise
            raise PredictionError(f"Prediction engine failed for scene {s_id}, zone {z_id}: {str(e)}") from e

        # 5. Format output as structured RuntimePredictionResult
        result = RuntimePredictionResult.from_inference_output(
            inference_dict=inference_output,
            scene_id=s_id,
            zone_id=z_id,
            timestamp=ts
        )

        # 6. Record prediction in runtime state context
        self.context.record_prediction(result.to_dict())

        return result

    def process_synthetic_stream(
        self,
        sample_stream: List[Dict[str, Any]],
        scene_id: str = "SYNTH_SCENE",
        zone_id: str = "SYNTH_ZONE",
        start_timestamp: float = 1000.0,
        time_step: float = 0.4
    ) -> List[RuntimePredictionResult]:
        """
        Helper method to process a sequence of synthetic feature snapshots at 2.5Hz.
        
        Args:
            sample_stream: List of feature dictionaries.
            scene_id: Target scene ID.
            zone_id: Target zone ID.
            start_timestamp: Base starting timestamp.
            time_step: Time increment between samples in seconds (0.4s = 2.5Hz).
            
        Returns:
            List of RuntimePredictionResult objects for each snapshot in sequence.
        """
        results: List[RuntimePredictionResult] = []
        current_ts = float(start_timestamp)

        for i, feat_dict in enumerate(sample_stream):
            res = self.process_snapshot(
                features=feat_dict,
                timestamp=current_ts,
                scene_id=scene_id,
                zone_id=zone_id,
                metadata={"sequence_index": i}
            )
            results.append(res)
            current_ts += time_step

        return results

    def get_context(self) -> PipelineContext:
        """Returns the active runtime pipeline context."""
        return self.context
