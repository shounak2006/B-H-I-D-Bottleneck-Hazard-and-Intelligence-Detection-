"""
BHID Spatial & Temporal Density Metrics Calculator.

Computes pedestrian count, spatial density, area occupancy ratio, and temporal density change.
"""

from typing import Dict, Any, Optional
from bhid.vision.tracking.tracking_batch import TrackingBatch


class DensityMetricsCalculator:
    """
    Calculates spatial and temporal crowd density metrics for a TrackingBatch.
    
    Parameters:
        default_zone_area_m2: Default spatial ROI zone area in square meters (default: 100.0 m^2).
    """

    def __init__(self, default_zone_area_m2: float = 100.0):
        self.default_zone_area_m2 = float(default_zone_area_m2)

    def compute_density_metrics(
        self,
        tracking_batch: TrackingBatch,
        zone_area_m2: Optional[float] = None,
        prev_density_ped_per_m2: Optional[float] = None,
        dt_seconds: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Computes pedestrian_count, density_ped_per_m2, occupancy_ratio, and temporal_density_change.
        
        Args:
            tracking_batch: Input TrackingBatch.
            zone_area_m2: Spatial zone area in square meters.
            prev_density_ped_per_m2: Spatial density from previous frame.
            dt_seconds: Time delta between frames in seconds.
            
        Returns:
            Dictionary containing computed density metrics.
        """
        area_m2 = float(zone_area_m2) if zone_area_m2 is not None and zone_area_m2 > 0 else self.default_zone_area_m2
        ped_count = tracking_batch.active_count()
        
        # Spatial density in pedestrians / m^2
        density = ped_count / area_m2 if area_m2 > 0 else 0.0

        # Area occupancy ratio relative to zone area
        total_bbox_area = sum(
            (t.current_bbox[2] - t.current_bbox[0]) * (t.current_bbox[3] - t.current_bbox[1])
            for t in tracking_batch.active_tracks
        )
        # Scaled area conversion factor (assuming pixels or normalized bounding boxes)
        occupancy = min(1.0, total_bbox_area / (area_m2 * 1000.0))

        # Temporal density change over dt
        temp_density_change = 0.0
        if prev_density_ped_per_m2 is not None and dt_seconds is not None and dt_seconds > 0:
            temp_density_change = (density - prev_density_ped_per_m2) / dt_seconds

        return {
            "pedestrian_count": float(ped_count),
            "density_ped_per_m2": round(density, 4),
            "occupancy_ratio": round(occupancy, 4),
            "temporal_density_change": round(temp_density_change, 4)
        }
