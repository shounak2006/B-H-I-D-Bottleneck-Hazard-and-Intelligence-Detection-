"""
BHID Speed & Kinematic Metrics Calculator.

Computes mean speed, velocity variance, and frame-over-frame acceleration.
"""

from typing import List, Dict, Any, Tuple, Optional
import math
from bhid.vision.tracking.tracking_batch import TrackingBatch


class SpeedMetricsCalculator:
    """
    Calculates speed and acceleration metrics for a TrackingBatch.
    
    Parameters:
        pixel_to_meter_scale: Spatial scaling factor converting pixels/sec to meters/sec (default: 0.05).
    """

    def __init__(self, pixel_to_meter_scale: float = 0.05):
        self.pixel_to_meter_scale = float(pixel_to_meter_scale)

    def compute_speed_metrics(
        self,
        tracking_batch: TrackingBatch,
        prev_mean_speed_m_s: Optional[float] = None,
        dt_seconds: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Computes mean_speed_m_s, velocity_variance, and acceleration_m_s2.
        
        Args:
            tracking_batch: Input TrackingBatch.
            prev_mean_speed_m_s: Mean speed from previous frame (if available).
            dt_seconds: Time delta between current and previous frame in seconds.
            
        Returns:
            Dictionary containing computed speed metrics.
        """
        tracks = tracking_batch.active_tracks
        count = len(tracks)

        if count == 0:
            return {
                "mean_speed_m_s": 0.0,
                "velocity_variance": 0.0,
                "acceleration_m_s2": 0.0
            }

        speeds_m_s = []
        for t in tracks:
            vx, vy = t.get_velocity_estimate()
            speed_px = math.sqrt(vx * vx + vy * vy)
            speed_m = speed_px * self.pixel_to_meter_scale
            speeds_m_s.append(speed_m)

        mean_speed = sum(speeds_m_s) / float(count)
        
        # Velocity variance across active track speeds
        variance = sum((s - mean_speed) ** 2 for s in speeds_m_s) / float(count) if count > 0 else 0.0

        # Acceleration (rate of change of mean speed over dt)
        acceleration = 0.0
        if prev_mean_speed_m_s is not None and dt_seconds is not None and dt_seconds > 0:
            acceleration = (mean_speed - prev_mean_speed_m_s) / dt_seconds

        return {
            "mean_speed_m_s": round(mean_speed, 4),
            "velocity_variance": round(variance, 4),
            "acceleration_m_s2": round(acceleration, 4)
        }
