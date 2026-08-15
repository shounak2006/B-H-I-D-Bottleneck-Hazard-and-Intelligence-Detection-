"""
BHID Primary Visualization & Monitoring Controller.

Coordinates frame rendering, track trajectory overlays, density heatmap generation,
hazard alert banners, and operational monitoring telemetry snapshots.
"""

from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
from bhid.visualization.visual_config import VisualConfig
from bhid.visualization.frame_renderer import FrameRenderer
from bhid.visualization.trajectory_renderer import TrajectoryRenderer
from bhid.visualization.heatmap_renderer import HeatmapRenderer
from bhid.visualization.event_renderer import EventRenderer
from bhid.visualization.monitoring_snapshot import MonitoringSnapshot
from bhid.vision.tracking.tracking_batch import TrackingBatch
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.events.hazard_event import HazardEvent


class MonitoringController:
    """
    Primary visualization coordinator orchestrating renderers and visual overlays.
    
    Parameters:
        config: Optional VisualConfig instance.
    """

    def __init__(self, config: Optional[VisualConfig] = None):
        self.config = config or VisualConfig()
        self.frame_renderer = FrameRenderer(config=self.config)
        self.trajectory_renderer = TrajectoryRenderer(config=self.config)
        self.heatmap_renderer = HeatmapRenderer(config=self.config)
        self.event_renderer = EventRenderer(config=self.config)

    def generate_snapshot(
        self,
        tracking_batch: TrackingBatch,
        analytics_snapshot: AnalyticsSnapshot,
        prediction_result: RuntimePredictionResult,
        active_events: List[HazardEvent]
    ) -> MonitoringSnapshot:
        """
        Builds a structured MonitoringSnapshot from pipeline layer outputs.
        """
        event_dicts = [e.to_dict() for e in active_events]
        vec = analytics_snapshot.export_feature_vector() if analytics_snapshot else {}
        ped_count = int(vec.get("feature_pedestrian_count", 0))
        density = float(vec.get("feature_density_ped_per_m2", 0.0))

        return MonitoringSnapshot(
            frame_id=tracking_batch.frame_id,
            timestamp=tracking_batch.timestamp,
            scene_id=prediction_result.scene_id,
            zone_id=prediction_result.zone_id,
            pedestrian_count=ped_count,
            density_ped_per_m2=density,
            active_tracks_count=len(tracking_batch.active_tracks),
            prediction_probability=float(prediction_result.prediction_probability),
            risk_level=str(prediction_result.risk_level),
            binary_prediction=int(prediction_result.binary_prediction),
            active_event_count=len(active_events),
            active_events=event_dicts,
            target_horizon=str(prediction_result.target_horizon)
        )

    def render_frame(
        self,
        frame: Optional[np.ndarray],
        tracking_batch: TrackingBatch,
        analytics_snapshot: AnalyticsSnapshot,
        prediction_result: RuntimePredictionResult,
        active_events: List[HazardEvent],
        draw_heatmap: bool = True,
        draw_trajectories: bool = True
    ) -> np.ndarray:
        """
        Renders complete composite visual monitoring frame with tracks, trajectories, heatmaps, HUDs, and alert banners.
        
        Args:
            frame: Optional input OpenCV image array (if None, blank canvas is created).
            tracking_batch: Active tracking batch.
            analytics_snapshot: 14-feature crowd analytics snapshot.
            prediction_result: Bottleneck risk prediction result.
            active_events: List of currently active hazard events.
            draw_heatmap: Whether to blend density heatmap overlay.
            draw_trajectories: Whether to render trajectory motion trails and velocity vectors.
            
        Returns:
            Annotated 3-channel OpenCV BGR image array.
        """
        if frame is None:
            # Create default canvas matching tracking batch image size or 1920x1080
            w = int(tracking_batch.image_width) if tracking_batch.image_width > 0 else 1920
            h = int(tracking_batch.image_height) if tracking_batch.image_height > 0 else 1080
            canvas = self.frame_renderer.create_blank_frame(width=w, height=h)
        else:
            canvas = frame.copy()

        # 1. Blend density heatmap overlay
        if draw_heatmap:
            canvas = self.heatmap_renderer.overlay_heatmap(canvas, tracking_batch)

        # 2. Render trajectory history trails and velocity vectors
        if draw_trajectories:
            canvas = self.trajectory_renderer.render_motion_paths(canvas, tracking_batch)

        # 3. Draw active track bounding boxes and IDs
        canvas = self.frame_renderer.draw_tracks(canvas, tracking_batch)

        # 4. Draw spatial ROI zone boundary tag
        canvas = self.frame_renderer.draw_zone_boundaries(canvas, prediction_result.zone_id)

        # 5. Draw crowd density HUD panel
        vec = analytics_snapshot.export_feature_vector() if analytics_snapshot else {}
        ped_count = int(vec.get("feature_pedestrian_count", 0))
        density = float(vec.get("feature_density_ped_per_m2", 0.0))

        canvas = self.frame_renderer.draw_density_annotations(
            canvas,
            pedestrian_count=ped_count,
            density_ped_per_m2=density
        )

        # 6. Draw bottleneck risk indicator badge
        canvas = self.frame_renderer.draw_risk_indicator(
            canvas,
            risk_level=prediction_result.risk_level,
            probability=prediction_result.prediction_probability,
            target_horizon=prediction_result.target_horizon
        )

        # 7. Draw active hazard event alert banners
        if active_events:
            canvas = self.event_renderer.draw_active_events(canvas, active_events)
            # Draw critical warning banner across screen if critical hazard exists
            for evt in active_events:
                if evt.risk_level == "CRITICAL":
                    canvas = self.event_renderer.draw_alert_annotations(canvas, evt)
                    break

        return canvas

    def export_summary(self, snapshot: MonitoringSnapshot) -> Dict[str, Any]:
        """Exports JSON-serializable summary of monitoring snapshot."""
        return snapshot.to_dict()

    def render_replay_frame(
        self,
        replay_frame: Any,
        frame: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Renders an annotated visual frame from a historical ReplayFrame instance.
        Reuses Phase 4F rendering utilities without duplicating logic.
        """
        r_dict = replay_frame.to_dict() if hasattr(replay_frame, "to_dict") else dict(replay_frame)
        pred = r_dict.get("prediction_result", {})
        analytics = r_dict.get("analytics_snapshot", {})

        if frame is None:
            canvas = self.frame_renderer.create_blank_frame(width=1920, height=1080)
        else:
            canvas = frame.copy()

        features = analytics.get("features", {})
        ped_count = int(features.get("feature_pedestrian_count", analytics.get("pedestrian_count", 0)))
        density = float(features.get("feature_density_ped_per_m2", analytics.get("density_ped_per_m2", 0.0)))
        
        risk_level = str(pred.get("risk_level", "LOW"))
        prob = float(pred.get("prediction_probability", 0.0))
        horizon = str(pred.get("target_horizon", "Y30"))
        zone_id = str(pred.get("zone_id", "REPLAY_ZONE"))

        canvas = self.frame_renderer.draw_zone_boundaries(canvas, zone_id)
        canvas = self.frame_renderer.draw_density_annotations(canvas, pedestrian_count=ped_count, density_ped_per_m2=density)
        canvas = self.frame_renderer.draw_risk_indicator(canvas, risk_level=risk_level, probability=prob, target_horizon=horizon)

        # REPLAY mode visual banner
        cv2.rectangle(canvas, (canvas.shape[1] - 180, canvas.shape[0] - 40), (canvas.shape[1] - 10, canvas.shape[0] - 10), (0, 0, 150), -1)
        cv2.putText(canvas, "[REPLAY MODE]", (canvas.shape[1] - 170, canvas.shape[0] - 18), self.config.font_face, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        return canvas

    def render_replay_timeline(self, replay_frame: Any) -> Dict[str, Any]:
        """
        Returns JSON-serializable timeline annotation dictionary for a replayed frame.
        """
        r_dict = replay_frame.to_dict() if hasattr(replay_frame, "to_dict") else dict(replay_frame)
        return {
            "mode": "HISTORICAL_REPLAY",
            "frame_id": r_dict.get("frame_id"),
            "timestamp": r_dict.get("timestamp"),
            "active_event_count": len(r_dict.get("active_events", [])),
            "prediction": r_dict.get("prediction_result")
        }

