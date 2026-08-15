"""
BHID Movement & Directional Entropy Metrics Calculator.

Computes 8-bin directional entropy, trajectory convergence, and temporal speed change.
"""

from typing import Dict, Any, Optional, List
import math
from bhid.vision.tracking.tracking_batch import TrackingBatch


class MovementMetricsCalculator:
    """
    Calculates motion pattern metrics for active pedestrian trajectories.
    """

    def compute_movement_metrics(
        self,
        tracking_batch: TrackingBatch,
        current_mean_speed_m_s: float = 0.0,
        prev_mean_speed_m_s: Optional[float] = None,
        dt_seconds: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Computes directional_entropy (8-bin), trajectory_convergence, and temporal_speed_change.
        
        Args:
            tracking_batch: Input TrackingBatch.
            current_mean_speed_m_s: Precomputed mean speed for current frame.
            prev_mean_speed_m_s: Precomputed mean speed from previous frame.
            dt_seconds: Time delta between frames in seconds.
            
        Returns:
            Dictionary containing computed movement metrics.
        """
        tracks = tracking_batch.active_tracks
        count = len(tracks)

        if count == 0:
            return {
                "directional_entropy": 0.0,
                "trajectory_convergence": 0.0,
                "temporal_speed_change": 0.0
            }

        angles: List[float] = []
        vx_list: List[float] = []
        vy_list: List[float] = []
        speeds: List[float] = []

        for t in tracks:
            vx, vy = t.get_velocity_estimate()
            speed = math.sqrt(vx * vx + vy * vy)
            speeds.append(speed)
            vx_list.append(vx)
            vy_list.append(vy)
            angle = math.atan2(vy, vx)
            angles.append(angle)

        # 1. Directional Entropy using 8 uniform angular bins across [-pi, pi]
        bins = [0] * 8
        for angle in angles:
            # Map [-pi, pi] to [0, 8)
            bin_idx = int(((angle + math.pi) / (2.0 * math.pi)) * 8) % 8
            bins[bin_idx] += 1

        directional_entropy = 0.0
        for b_count in bins:
            if b_count > 0:
                p = b_count / float(count)
                directional_entropy -= p * math.log2(p)

        # 2. Trajectory Convergence: ratio of mean velocity vector magnitude to mean scalar speed
        convergence = 0.0
        mean_scalar_speed = sum(speeds) / float(count) if count > 0 else 0.0
        if count > 1 and mean_scalar_speed > 1e-5:
            mean_vx = sum(vx_list) / float(count)
            mean_vy = sum(vy_list) / float(count)
            mean_vector_mag = math.sqrt(mean_vx * mean_vx + mean_vy * mean_vy)
            convergence = min(1.0, mean_vector_mag / (mean_scalar_speed + 1e-5))

        # 3. Temporal Speed Change
        temp_speed_change = 0.0
        if prev_mean_speed_m_s is not None and dt_seconds is not None and dt_seconds > 0:
            temp_speed_change = (current_mean_speed_m_s - prev_mean_speed_m_s) / dt_seconds

        return {
            "directional_entropy": round(directional_entropy, 4),
            "trajectory_convergence": round(convergence, 4),
            "temporal_speed_change": round(temp_speed_change, 4)
        }
