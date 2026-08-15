"""
BHID Primary Crowd Analytics Engine.

Consumes TrackingBatch inputs, maintains inter-frame state, coordinates sub-metric
calculators, and generates complete 14-feature AnalyticsSnapshots for prediction runtime.
"""

from typing import Dict, Any, Optional, Set
from bhid.vision.tracking.tracking_batch import TrackingBatch
from bhid.analytics.speed_metrics import SpeedMetricsCalculator
from bhid.analytics.flow_metrics import FlowMetricsCalculator
from bhid.analytics.density_metrics import DensityMetricsCalculator
from bhid.analytics.movement_metrics import MovementMetricsCalculator
from bhid.analytics.egress_metrics import EgressMetricsCalculator
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot


class CrowdAnalyticsEngine:
    """
    Main crowd analytics coordinator generating the frozen 14-feature runtime vector.
    
    Parameters:
        pixel_to_meter_scale: Spatial scale factor converting pixels to meters (default: 0.05).
        default_zone_area_m2: Default spatial ROI zone area in square meters (default: 100.0).
    """

    def __init__(
        self,
        pixel_to_meter_scale: float = 0.05,
        default_zone_area_m2: float = 100.0
    ):
        self.pixel_to_meter_scale = float(pixel_to_meter_scale)
        self.default_zone_area_m2 = float(default_zone_area_m2)

        self.speed_calc = SpeedMetricsCalculator(pixel_to_meter_scale=self.pixel_to_meter_scale)
        self.flow_calc = FlowMetricsCalculator()
        self.density_calc = DensityMetricsCalculator(default_zone_area_m2=self.default_zone_area_m2)
        self.movement_calc = MovementMetricsCalculator()
        self.egress_calc = EgressMetricsCalculator()

        # Inter-frame tracking state
        self._prev_track_ids: Optional[Set[Any]] = None
        self._prev_mean_speed_m_s: Optional[float] = None
        self._prev_density_ped_per_m2: Optional[float] = None
        self._prev_timestamp: Optional[float] = None

    def reset(self) -> None:
        """Resets all inter-frame state memory."""
        self._prev_track_ids = None
        self._prev_mean_speed_m_s = None
        self._prev_density_ped_per_m2 = None
        self._prev_timestamp = None

    def process_tracking_batch(
        self,
        tracking_batch: TrackingBatch,
        zone_area_m2: Optional[float] = None,
        scene_id: str = "DEFAULT_SCENE",
        zone_id: str = "ZONE_ALL"
    ) -> AnalyticsSnapshot:
        """
        Processes a TrackingBatch and computes all 14 spatiotemporal features.
        
        Args:
            tracking_batch: Input TrackingBatch object.
            zone_area_m2: Spatial zone area in m^2.
            scene_id: Active scene identifier.
            zone_id: Active zone identifier.
            
        Returns:
            AnalyticsSnapshot containing all 14 validated features.
        """
        area_m2 = float(zone_area_m2) if zone_area_m2 is not None and zone_area_m2 > 0 else self.default_zone_area_m2
        current_ts = tracking_batch.timestamp

        # Compute dt relative to previous frame
        dt_seconds = None
        if self._prev_timestamp is not None:
            dt = current_ts - self._prev_timestamp
            dt_seconds = dt if dt > 0 else 0.4
        else:
            dt_seconds = 0.4

        # 1. Density metrics
        density_res = self.density_calc.compute_density_metrics(
            tracking_batch=tracking_batch,
            zone_area_m2=area_m2,
            prev_density_ped_per_m2=self._prev_density_ped_per_m2,
            dt_seconds=dt_seconds
        )

        # 2. Speed metrics
        speed_res = self.speed_calc.compute_speed_metrics(
            tracking_batch=tracking_batch,
            prev_mean_speed_m_s=self._prev_mean_speed_m_s,
            dt_seconds=dt_seconds
        )

        # 3. Flow metrics
        flow_res = self.flow_calc.compute_flow_metrics(
            current_batch=tracking_batch,
            prev_track_ids=self._prev_track_ids,
            dt_seconds=dt_seconds
        )

        # 4. Movement metrics
        movement_res = self.movement_calc.compute_movement_metrics(
            tracking_batch=tracking_batch,
            current_mean_speed_m_s=speed_res["mean_speed_m_s"],
            prev_mean_speed_m_s=self._prev_mean_speed_m_s,
            dt_seconds=dt_seconds
        )

        # 5. Egress deficit metrics
        egress_res = self.egress_calc.compute_egress_deficit(
            inflow_rate_per_s=flow_res["inflow_rate_per_s"],
            outflow_rate_per_s=flow_res["outflow_rate_per_s"]
        )

        # Combine all 14 features
        feature_dict = {}
        feature_dict.update(density_res)
        feature_dict.update(speed_res)
        feature_dict.update(flow_res)
        feature_dict.update(movement_res)
        feature_dict.update(egress_res)

        # Create validated AnalyticsSnapshot
        snapshot = AnalyticsSnapshot(
            frame_id=tracking_batch.frame_id,
            timestamp=current_ts,
            scene_id=scene_id,
            zone_id=zone_id,
            features=feature_dict
        )

        # Update inter-frame state memory
        self._prev_track_ids = set(tracking_batch.get_track_ids())
        self._prev_mean_speed_m_s = speed_res["mean_speed_m_s"]
        self._prev_density_ped_per_m2 = density_res["density_ped_per_m2"]
        self._prev_timestamp = current_ts

        return snapshot

    def generate_feature_vector(
        self,
        tracking_batch: TrackingBatch,
        zone_area_m2: Optional[float] = None,
        scene_id: str = "DEFAULT_SCENE",
        zone_id: str = "ZONE_ALL"
    ) -> Dict[str, float]:
        """
        Processes TrackingBatch and returns exported canonical feature dictionary (feature_*).
        """
        snapshot = self.process_tracking_batch(
            tracking_batch=tracking_batch,
            zone_area_m2=zone_area_m2,
            scene_id=scene_id,
            zone_id=zone_id
        )
        return snapshot.export_feature_vector()
