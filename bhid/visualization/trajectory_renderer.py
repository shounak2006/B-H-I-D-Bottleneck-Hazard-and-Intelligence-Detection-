"""
BHID Trajectory Renderer Utilities.

Provides trajectory history trail rendering and velocity vector arrow drawing on image frames.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
import cv2
import numpy as np
from bhid.visualization.visual_config import VisualConfig
from bhid.vision.tracking.tracking_batch import TrackingBatch


class TrajectoryRenderer:
    """
    Trajectory and motion vector renderer.
    
    Parameters:
        config: Optional VisualConfig instance.
    """

    def __init__(self, config: Optional[VisualConfig] = None):
        self.config = config or VisualConfig()

    def render_track_history(
        self,
        frame: np.ndarray,
        tracking_batch: TrackingBatch,
        trail_length: Optional[int] = None
    ) -> np.ndarray:
        """
        Renders colored historical motion paths for all active tracks.
        """
        out_frame = frame.copy()
        max_len = trail_length if trail_length is not None else self.config.trail_length

        for track in tracking_batch.active_tracks:
            pts = track.trajectory.get_recent_points(n_points=max_len)
            if len(pts) < 2:
                continue

            for i in range(1, len(pts)):
                p1 = (int(pts[i - 1].x), int(pts[i - 1].y))
                p2 = (int(pts[i].x), int(pts[i].y))
                cv2.line(out_frame, p1, p2, self.config.trajectory_color, 2, cv2.LINE_AA)

        return out_frame

    def render_velocity_vectors(
        self,
        frame: np.ndarray,
        tracking_batch: TrackingBatch,
        arrow_scale: float = 1.5
    ) -> np.ndarray:
        """
        Renders velocity direction arrows from track centroids.
        """
        out_frame = frame.copy()
        color = self.config.velocity_vector_color

        for track in tracking_batch.active_tracks:
            vx, vy = track.velocity
            speed = math.hypot(vx, vy)
            if speed < 1.0:
                continue

            cx, cy = map(int, track.centroid)
            end_x = int(cx + vx * arrow_scale)
            end_y = int(cy + vy * arrow_scale)

            cv2.arrowedLine(
                out_frame, (cx, cy), (end_x, end_y),
                color, 2, cv2.LINE_AA, tipLength=0.3
            )

        return out_frame

    def render_motion_paths(
        self,
        frame: np.ndarray,
        tracking_batch: TrackingBatch
    ) -> np.ndarray:
        """
        Renders composite motion visualization (trails + velocity arrows).
        """
        out_frame = self.render_track_history(frame, tracking_batch)
        out_frame = self.render_velocity_vectors(out_frame, tracking_batch)
        return out_frame
