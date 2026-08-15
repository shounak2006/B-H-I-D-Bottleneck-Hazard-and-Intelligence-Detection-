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

    def process_detection_batch(
        self,
        detection_batch: Any,
        zone_area_m2: Optional[float] = None,
        scene_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        confidence_threshold: float = 0.50,
        adapter: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Ingests a frame-level DetectionBatch via DetectionAdapter, updates runtime context
        and location tracking, and returns detection observation statistics.
        
        Args:
            detection_batch: DetectionBatch object containing frame detections.
            zone_area_m2: Optional spatial zone area in square meters.
            scene_id: Optional scene identifier override.
            zone_id: Optional zone identifier override.
            confidence_threshold: Minimum detection confidence score.
            adapter: Optional DetectionAdapter instance.
            
        Returns:
            Dictionary containing adapted frame-level detection statistics.
        """
        from bhid.vision.detection.detection_adapter import DetectionAdapter

        if adapter is None:
            adapter = DetectionAdapter()

        s_id = self.context.active_scene if scene_id is None else str(scene_id)
        z_id = self.context.active_zone if zone_id is None else str(zone_id)

        self.context.set_active_location(s_id, z_id)
        self.context.update_timestamp(detection_batch.timestamp)
        self.context.increment_frame_count()

        observation = adapter.adapt_batch(
            batch=detection_batch,
            zone_area_m2=zone_area_m2,
            confidence_threshold=confidence_threshold
        )

        return observation

    def process_tracking_batch(
        self,
        tracking_batch: Any,
        zone_area_m2: Optional[float] = None,
        scene_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        adapter: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Ingests a frame-level TrackingBatch via TrackingAdapter, updates runtime context
        and location tracking, and returns trajectory observation statistics.
        
        Args:
            tracking_batch: TrackingBatch object containing active tracks.
            zone_area_m2: Optional spatial zone area in square meters.
            scene_id: Optional scene identifier override.
            zone_id: Optional zone identifier override.
            adapter: Optional TrackingAdapter instance.
            
        Returns:
            Dictionary containing adapted trajectory observation statistics.
        """
        from bhid.vision.tracking.tracking_adapter import TrackingAdapter

        if adapter is None:
            adapter = TrackingAdapter()

        s_id = self.context.active_scene if scene_id is None else str(scene_id)
        z_id = self.context.active_zone if zone_id is None else str(zone_id)

        self.context.set_active_location(s_id, z_id)
        self.context.update_timestamp(tracking_batch.timestamp)
        self.context.increment_frame_count()

        observation = adapter.adapt_batch(
            batch=tracking_batch,
            zone_area_m2=zone_area_m2
        )

        return observation

    def process_tracking_batch_with_analytics(
        self,
        tracking_batch: Any,
        analytics_engine: Optional[Any] = None,
        zone_area_m2: float = 100.0,
        scene_id: Optional[str] = None,
        zone_id: Optional[str] = None
    ) -> RuntimePredictionResult:
        """
        Ingests a TrackingBatch, runs CrowdAnalyticsEngine to compute the 14 spatiotemporal features,
        updates FeatureWindowManager, executes Phase 3D BottleneckPredictor, updates PipelineContext,
        and returns RuntimePredictionResult.
        
        Args:
            tracking_batch: Input TrackingBatch object.
            analytics_engine: Optional CrowdAnalyticsEngine instance.
            zone_area_m2: Spatial zone area in m^2.
            scene_id: Optional scene ID override.
            zone_id: Optional zone ID override.
            
        Returns:
            RuntimePredictionResult encapsulating bottleneck risk assessment.
        """
        from bhid.analytics.crowd_analytics_engine import CrowdAnalyticsEngine

        if analytics_engine is None:
            if not hasattr(self, "_analytics_engine"):
                self._analytics_engine = CrowdAnalyticsEngine(default_zone_area_m2=zone_area_m2)
            analytics_engine = self._analytics_engine

        s_id = self.context.active_scene if scene_id is None else str(scene_id)
        z_id = self.context.active_zone if zone_id is None else str(zone_id)

        # 1. Process TrackingBatch through CrowdAnalyticsEngine to generate 14-feature snapshot
        snapshot = analytics_engine.process_tracking_batch(
            tracking_batch=tracking_batch,
            zone_area_m2=zone_area_m2,
            scene_id=s_id,
            zone_id=z_id
        )

        # 2. Extract canonical 14 feature dictionary
        features = snapshot.export_feature_vector()

        # 3. Process 14-feature snapshot through orchestrator pipeline
        result = self.process_snapshot(
            features=features,
            timestamp=tracking_batch.timestamp,
            scene_id=s_id,
            zone_id=z_id,
            metadata={"frame_id": tracking_batch.frame_id, "analytics_processed": True}
        )

        return result

    def process_prediction_event(
        self,
        tracking_batch: Any,
        event_engine: Optional[Any] = None,
        analytics_engine: Optional[Any] = None,
        zone_area_m2: float = 100.0,
        scene_id: Optional[str] = None,
        zone_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete end-to-end BHID operational intelligence pipeline:
        TrackingBatch -> CrowdAnalyticsEngine -> FeatureWindowManager -> BottleneckPredictor -> RuntimePredictionResult -> HazardEventEngine -> HazardEvent.
        
        Args:
            tracking_batch: Input TrackingBatch object.
            event_engine: Optional HazardEventEngine instance.
            analytics_engine: Optional CrowdAnalyticsEngine instance.
            zone_area_m2: Spatial zone area in m^2.
            scene_id: Optional scene ID override.
            zone_id: Optional zone ID override.
            
        Returns:
            Dictionary containing prediction result and affected HazardEvent (if any).
        """
        from bhid.events.event_engine import HazardEventEngine

        if event_engine is None:
            if not hasattr(self, "_event_engine"):
                self._event_engine = HazardEventEngine()
            event_engine = self._event_engine

        # 1. Execute analytics & prediction engine pipeline
        pred_result = self.process_tracking_batch_with_analytics(
            tracking_batch=tracking_batch,
            analytics_engine=analytics_engine,
            zone_area_m2=zone_area_m2,
            scene_id=scene_id,
            zone_id=zone_id
        )

        # 2. Ingest RuntimePredictionResult into HazardEventEngine
        hazard_event = event_engine.process_prediction(pred_result)

        return {
            "prediction_result": pred_result.to_dict(),
            "hazard_event": hazard_event.to_dict() if hazard_event is not None else None,
            "active_event_count": len(event_engine.get_active_events()),
            "pipeline_context": self.context.to_dict()
        }

    def process_monitoring_frame(
        self,
        tracking_batch: Any,
        frame: Optional[Any] = None,
        event_engine: Optional[Any] = None,
        analytics_engine: Optional[Any] = None,
        monitoring_controller: Optional[Any] = None,
        zone_area_m2: float = 100.0,
        scene_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        draw_heatmap: bool = True,
        draw_trajectories: bool = True
    ) -> Dict[str, Any]:
        """
        Executes end-to-end BHID visual monitoring pipeline:
        TrackingBatch -> Analytics -> Prediction -> Event Engine -> Monitoring Snapshot -> Visual Overlay Frame.
        
        Args:
            tracking_batch: Input TrackingBatch object.
            frame: Optional input OpenCV BGR image array.
            event_engine: Optional HazardEventEngine instance.
            analytics_engine: Optional CrowdAnalyticsEngine instance.
            monitoring_controller: Optional MonitoringController instance.
            zone_area_m2: Spatial zone area in m^2.
            scene_id: Optional scene ID override.
            zone_id: Optional zone ID override.
            draw_heatmap: Whether to overlay density heatmap.
            draw_trajectories: Whether to render trajectory motion trails.
            
        Returns:
            Dictionary containing prediction_result, monitoring_snapshot, rendered_frame, active_events.
        """
        from bhid.events.event_engine import HazardEventEngine
        from bhid.analytics.crowd_analytics_engine import CrowdAnalyticsEngine
        from bhid.visualization.monitoring_controller import MonitoringController

        if event_engine is None:
            if not hasattr(self, "_event_engine"):
                self._event_engine = HazardEventEngine()
            event_engine = self._event_engine

        if analytics_engine is None:
            if not hasattr(self, "_analytics_engine"):
                self._analytics_engine = CrowdAnalyticsEngine(default_zone_area_m2=zone_area_m2)
            analytics_engine = self._analytics_engine

        if monitoring_controller is None:
            if not hasattr(self, "_monitoring_controller"):
                self._monitoring_controller = MonitoringController()
            monitoring_controller = self._monitoring_controller

        s_id = self.context.active_scene if scene_id is None else str(scene_id)
        z_id = self.context.active_zone if zone_id is None else str(zone_id)

        # 1. Compute analytics snapshot
        analytics_snapshot = analytics_engine.process_tracking_batch(
            tracking_batch=tracking_batch,
            zone_area_m2=zone_area_m2,
            scene_id=s_id,
            zone_id=z_id
        )

        # 2. Run prediction pipeline
        features = analytics_snapshot.export_feature_vector()
        pred_result = self.process_snapshot(
            features=features,
            timestamp=tracking_batch.timestamp,
            scene_id=s_id,
            zone_id=z_id,
            metadata={"frame_id": tracking_batch.frame_id}
        )

        # 3. Process prediction in event engine
        hazard_event = event_engine.process_prediction(pred_result)
        active_events = event_engine.get_active_events()

        # 4. Generate monitoring snapshot
        monitoring_snapshot = monitoring_controller.generate_snapshot(
            tracking_batch=tracking_batch,
            analytics_snapshot=analytics_snapshot,
            prediction_result=pred_result,
            active_events=active_events
        )

        # 5. Render annotated OpenCV visual frame
        rendered_frame = monitoring_controller.render_frame(
            frame=frame,
            tracking_batch=tracking_batch,
            analytics_snapshot=analytics_snapshot,
            prediction_result=pred_result,
            active_events=active_events,
            draw_heatmap=draw_heatmap,
            draw_trajectories=draw_trajectories
        )

        return {
            "prediction_result": pred_result.to_dict(),
            "hazard_event": hazard_event.to_dict() if hazard_event is not None else None,
            "monitoring_snapshot": monitoring_snapshot.to_dict(),
            "rendered_frame": rendered_frame,
            "active_event_count": len(active_events)
        }

    def process_persistent_monitoring_frame(
        self,
        tracking_batch: Any,
        frame: Optional[Any] = None,
        persistence_manager: Optional[Any] = None,
        monitoring_controller: Optional[Any] = None,
        event_engine: Optional[Any] = None,
        analytics_engine: Optional[Any] = None,
        zone_area_m2: float = 100.0,
        scene_id: Optional[str] = None,
        zone_id: Optional[str] = None,
        draw_heatmap: bool = True,
        draw_trajectories: bool = True
    ) -> Dict[str, Any]:
        """
        Executes complete end-to-end BHID operational pipeline with non-blocking persistence:
        TrackingBatch -> Analytics -> Prediction -> Event Engine -> Monitoring Snapshot -> Visualization -> Persistence Manager.
        
        Args:
            tracking_batch: Input TrackingBatch object.
            frame: Optional input OpenCV BGR image array.
            persistence_manager: Optional PersistenceManager instance.
            monitoring_controller: Optional MonitoringController instance.
            event_engine: Optional HazardEventEngine instance.
            analytics_engine: Optional CrowdAnalyticsEngine instance.
            zone_area_m2: Spatial zone area in m^2.
            scene_id: Optional scene ID override.
            zone_id: Optional zone ID override.
            draw_heatmap: Whether to overlay density heatmap.
            draw_trajectories: Whether to render trajectory motion trails.
            
        Returns:
            Dictionary containing prediction_result, monitoring_snapshot, rendered_frame, active_events, persistence_active.
        """
        from bhid.events.event_engine import HazardEventEngine
        from bhid.analytics.crowd_analytics_engine import CrowdAnalyticsEngine
        from bhid.visualization.monitoring_controller import MonitoringController
        from bhid.persistence.persistence_manager import PersistenceManager

        if event_engine is None:
            if not hasattr(self, "_event_engine"):
                self._event_engine = HazardEventEngine()
            event_engine = self._event_engine

        if analytics_engine is None:
            if not hasattr(self, "_analytics_engine"):
                self._analytics_engine = CrowdAnalyticsEngine(default_zone_area_m2=zone_area_m2)
            analytics_engine = self._analytics_engine

        if monitoring_controller is None:
            if not hasattr(self, "_monitoring_controller"):
                self._monitoring_controller = MonitoringController()
            monitoring_controller = self._monitoring_controller

        if persistence_manager is None:
            if not hasattr(self, "_persistence_manager"):
                self._persistence_manager = PersistenceManager()
            persistence_manager = self._persistence_manager

        s_id = self.context.active_scene if scene_id is None else str(scene_id)
        z_id = self.context.active_zone if zone_id is None else str(zone_id)

        # 1. Compute analytics snapshot
        analytics_snapshot = analytics_engine.process_tracking_batch(
            tracking_batch=tracking_batch,
            zone_area_m2=zone_area_m2,
            scene_id=s_id,
            zone_id=z_id
        )

        # 2. Run prediction pipeline
        features = analytics_snapshot.export_feature_vector()
        pred_result = self.process_snapshot(
            features=features,
            timestamp=tracking_batch.timestamp,
            scene_id=s_id,
            zone_id=z_id,
            metadata={"frame_id": tracking_batch.frame_id}
        )
        setattr(pred_result, "frame_id", tracking_batch.frame_id)

        # 3. Process prediction in event engine
        hazard_event = event_engine.process_prediction(pred_result)
        active_events = event_engine.get_active_events()

        # 4. Generate monitoring snapshot
        monitoring_snapshot = monitoring_controller.generate_snapshot(
            tracking_batch=tracking_batch,
            analytics_snapshot=analytics_snapshot,
            prediction_result=pred_result,
            active_events=active_events
        )

        # 5. Render annotated OpenCV visual frame
        rendered_frame = monitoring_controller.render_frame(
            frame=frame,
            tracking_batch=tracking_batch,
            analytics_snapshot=analytics_snapshot,
            prediction_result=pred_result,
            active_events=active_events,
            draw_heatmap=draw_heatmap,
            draw_trajectories=draw_trajectories
        )

        # 6. Non-blocking persistence ingestion
        persistence_manager.persist_prediction(pred_result)
        persistence_manager.persist_analytics_snapshot(analytics_snapshot)
        if hazard_event is not None:
            persistence_manager.persist_event(hazard_event)
        persistence_manager.persist_monitoring_snapshot(monitoring_snapshot)

        return {
            "prediction_result": pred_result.to_dict(),
            "hazard_event": hazard_event.to_dict() if hazard_event is not None else None,
            "monitoring_snapshot": monitoring_snapshot.to_dict(),
            "rendered_frame": rendered_frame,
            "active_event_count": len(active_events),
            "persistence_active": True
        }

    def get_context(self) -> PipelineContext:
        """Returns the active runtime pipeline context."""
        return self.context






