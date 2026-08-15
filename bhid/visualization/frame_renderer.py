"""
BHID OpenCV Frame Renderer Utilities.

Provides drawing functions for detections, active tracks, trajectory trails, spatial ROI zones,
pedestrian density telemetry, and bottleneck risk indicator badges.
"""

from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
from bhid.visualization.visual_config import VisualConfig
from bhid.vision.detection.detection_batch import DetectionBatch
from bhid.vision.tracking.tracking_batch import TrackingBatch


class FrameRenderer:
    """
    OpenCV frame rendering utilities.
    
    Parameters:
        config: Optional VisualConfig instance.
    """

    def __init__(self, config: Optional[VisualConfig] = None):
        self.config = config or VisualConfig()

    def create_blank_frame(
        self,
        width: int = 1920,
        height: int = 1080,
        color: Tuple[int, int, int] = (20, 20, 20)
    ) -> np.ndarray:
        """Generates a blank BGR image frame of specified size."""
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = color
        return frame

    def draw_detections(
        self,
        frame: np.ndarray,
        detection_batch: DetectionBatch
    ) -> np.ndarray:
        """
        Draws raw detection bounding boxes on frame.
        """
        out_frame = frame.copy()
        color = (180, 180, 180)  # Light Gray for raw detections

        for det in detection_batch.detections:
            x1, y1, x2, y2 = map(int, det.bbox)
            cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 1)
            label = f"Det {det.confidence:.2f}"
            cv2.putText(
                out_frame, label, (x1, max(15, y1 - 4)),
                self.config.font_face, 0.4, color, 1, cv2.LINE_AA
            )

        return out_frame

    def draw_tracks(
        self,
        frame: np.ndarray,
        tracking_batch: TrackingBatch
    ) -> np.ndarray:
        """
        Draws active track bounding boxes and track IDs.
        """
        out_frame = frame.copy()
        color = self.config.track_color

        for track in tracking_batch.active_tracks:
            x1, y1, x2, y2 = map(int, track.bbox)
            cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, self.config.line_thickness)
            
            # Centroid point
            cx, cy = map(int, track.centroid)
            cv2.circle(out_frame, (cx, cy), 3, (0, 255, 255), -1)

            label = f"ID #{track.track_id}"
            cv2.putText(
                out_frame, label, (x1, max(18, y1 - 5)),
                self.config.font_face, self.config.font_scale, color, 1, cv2.LINE_AA
            )

        return out_frame

    def draw_trajectories(
        self,
        frame: np.ndarray,
        tracking_batch: TrackingBatch,
        trail_length: Optional[int] = None
    ) -> np.ndarray:
        """
        Renders historical motion trails for active tracks.
        """
        out_frame = frame.copy()
        max_len = trail_length if trail_length is not None else self.config.trail_length

        for track in tracking_batch.active_tracks:
            points = track.trajectory.get_recent_points(n_points=max_len)
            if len(points) < 2:
                continue

            for i in range(1, len(points)):
                pt1 = (int(points[i - 1].x), int(points[i - 1].y))
                pt2 = (int(points[i].x), int(points[i].y))
                
                # Fading trail opacity / thickness
                thickness = max(1, int(self.config.line_thickness * (i / float(len(points)))))
                cv2.line(out_frame, pt1, pt2, self.config.trajectory_color, thickness, cv2.LINE_AA)

        return out_frame

    def draw_zone_boundaries(
        self,
        frame: np.ndarray,
        zone_id: str,
        bbox_polygon: Optional[List[Tuple[int, int]]] = None
    ) -> np.ndarray:
        """
        Draws spatial ROI zone boundaries.
        """
        out_frame = frame.copy()
        color = (255, 255, 255)  # White zone boundary

        if bbox_polygon and len(bbox_polygon) >= 3:
            pts = np.array(bbox_polygon, np.int32).reshape((-1, 1, 2))
            cv2.polylines(out_frame, [pts], isClosed=True, color=color, thickness=2)
            lbl_pt = bbox_polygon[0]
            cv2.putText(
                out_frame, f"ZONE: {zone_id}", (lbl_pt[0] + 5, lbl_pt[1] + 20),
                self.config.font_face, 0.6, color, 2, cv2.LINE_AA
            )
        else:
            # Default zone boundary header panel
            cv2.rectangle(out_frame, (10, 10), (320, 45), (40, 40, 40), -1)
            cv2.putText(
                out_frame, f"ZONE ROI: {zone_id}", (15, 33),
                self.config.font_face, 0.6, (0, 255, 255), 2, cv2.LINE_AA
            )

        return out_frame

    def draw_density_annotations(
        self,
        frame: np.ndarray,
        pedestrian_count: int,
        density_ped_per_m2: float
    ) -> np.ndarray:
        """
        Draws pedestrian count and spatial density HUD panel.
        """
        out_frame = frame.copy()
        h, w = out_frame.shape[:2]
        
        # Telemetry panel bottom left
        panel_x1, panel_y1 = 15, h - 75
        panel_x2, panel_y2 = 320, h - 15

        cv2.rectangle(out_frame, (panel_x1, panel_y1), (panel_x2, panel_y2), self.config.panel_bg_color, -1)
        cv2.rectangle(out_frame, (panel_x1, panel_y1), (panel_x2, panel_y2), (100, 100, 100), 1)

        txt1 = f"PEDESTRIANS: {pedestrian_count}"
        txt2 = f"DENSITY: {density_ped_per_m2:.2f} ped/m2"

        cv2.putText(out_frame, txt1, (panel_x1 + 10, panel_y1 + 25), self.config.font_face, 0.55, self.config.text_color, 1, cv2.LINE_AA)
        cv2.putText(out_frame, txt2, (panel_x1 + 10, panel_y1 + 50), self.config.font_face, 0.55, (0, 220, 255), 1, cv2.LINE_AA)

        return out_frame

    def draw_risk_indicator(
        self,
        frame: np.ndarray,
        risk_level: str,
        probability: float,
        target_horizon: str = "Y30"
    ) -> np.ndarray:
        """
        Draws top-right bottleneck hazard risk indicator badge.
        """
        out_frame = frame.copy()
        w = out_frame.shape[1]
        
        color = self.config.get_risk_color(risk_level)

        # Risk indicator badge top right
        panel_x1, panel_y1 = w - 340, 15
        panel_x2, panel_y2 = w - 15, 80

        cv2.rectangle(out_frame, (panel_x1, panel_y1), (panel_x2, panel_y2), (20, 20, 20), -1)
        cv2.rectangle(out_frame, (panel_x1, panel_y1), (panel_x2, panel_y2), color, 2)

        txt_risk = f"RISK: {risk_level.upper()}"
        txt_prob = f"PROB ({target_horizon}): {probability * 100.0:.1f}%"

        cv2.putText(out_frame, txt_risk, (panel_x1 + 15, panel_y1 + 30), self.config.font_face, 0.7, color, 2, cv2.LINE_AA)
        cv2.putText(out_frame, txt_prob, (panel_x1 + 15, panel_y1 + 55), self.config.font_face, 0.55, self.config.text_color, 1, cv2.LINE_AA)

        return out_frame
