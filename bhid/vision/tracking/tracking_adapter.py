"""
BHID Vision Tracking Adapter.

Converts frame-level TrackingBatch objects into trajectory observations
for runtime pipeline ingestion without computing Phase 2 engineered features.
"""

from typing import Dict, Any, Optional
import math
from bhid.vision.tracking.tracking_batch import TrackingBatch


class TrackingAdapter:
    """
    Adapter converting tracking outputs into standardized trajectory observations.
    """

    def __init__(self, pixel_to_meter_scale: float = 0.05):
        self.pixel_to_meter_scale = float(pixel_to_meter_scale)

    def adapt_batch(
        self,
        batch: TrackingBatch,
        zone_area_m2: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Transforms a TrackingBatch into a trajectory observation dictionary.
        
        Args:
            batch: Input TrackingBatch object.
            zone_area_m2: Optional spatial zone area in square meters.
            
        Returns:
            Dictionary containing track counts, velocity statistics, and trajectory summaries.
        """
        active_count = batch.active_count()
        track_ids = batch.get_track_ids()
        
        speeds_m_s = []
        path_lengths = []
        durations = []

        for track in batch.active_tracks:
            vx, vy = track.get_velocity_estimate()
            speed_px_s = math.sqrt(vx * vx + vy * vy)
            speed_m_s = speed_px_s * self.pixel_to_meter_scale
            speeds_m_s.append(speed_m_s)

            path_lengths.append(track.trajectory_history.get_path_length())
            durations.append(track.trajectory_history.duration_seconds())

        mean_speed = sum(speeds_m_s) / float(active_count) if active_count > 0 else 0.0
        mean_path_len = sum(path_lengths) / float(active_count) if active_count > 0 else 0.0
        mean_duration = sum(durations) / float(active_count) if active_count > 0 else 0.0

        return {
            "frame_id": batch.frame_id,
            "timestamp": batch.timestamp,
            "active_track_count": active_count,
            "track_ids": track_ids,
            "mean_speed_m_s": round(mean_speed, 4),
            "mean_path_length_px": round(mean_path_len, 4),
            "mean_duration_s": round(mean_duration, 4),
            "zone_area_m2": zone_area_m2,
            "bboxes": batch.get_bboxes(),
            "centroids": batch.get_centroids()
        }
