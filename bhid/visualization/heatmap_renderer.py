"""
BHID Crowd Density Heatmap Renderer.

Generates accumulated spatial density heatmaps and overlays colormapped heatmaps on video frames.
"""

from typing import Dict, Any, Optional, Tuple
import cv2
import numpy as np
from bhid.visualization.visual_config import VisualConfig
from bhid.vision.tracking.tracking_batch import TrackingBatch


class HeatmapRenderer:
    """
    Crowd density heatmap rendering engine using Gaussian density accumulation.
    
    Parameters:
        config: Optional VisualConfig instance.
    """

    def __init__(self, config: Optional[VisualConfig] = None):
        self.config = config or VisualConfig()

    def generate_density_heatmap(
        self,
        tracking_batch: TrackingBatch,
        image_width: int = 1920,
        image_height: int = 1080,
        sigma: float = 35.0
    ) -> np.ndarray:
        """
        Generates a 3-channel BGR heatmap image from track centroid accumulation.
        
        Args:
            tracking_batch: TrackingBatch containing active tracks.
            image_width: Target image width.
            image_height: Target image height.
            sigma: Gaussian blur kernel radius in pixels.
            
        Returns:
            3-channel BGR heatmap image array.
        """
        density_map = np.zeros((image_height, image_width), dtype=np.float32)

        for track in tracking_batch.active_tracks:
            cx, cy = map(int, track.centroid)
            if 0 <= cx < image_width and 0 <= cy < image_height:
                density_map[cy, cx] += 1.0

        if len(tracking_batch.active_tracks) > 0:
            ksize = int(sigma * 3) | 1  # ensure odd kernel size
            density_map = cv2.GaussianBlur(density_map, (ksize, ksize), sigma)
            
            # Normalize to [0, 255]
            max_val = np.max(density_map)
            if max_val > 0:
                density_norm = np.uint8((density_map / max_val) * 255.0)
            else:
                density_norm = np.zeros((image_height, image_width), dtype=np.uint8)
        else:
            density_norm = np.zeros((image_height, image_width), dtype=np.uint8)

        # Apply OpenCV colormap
        color_heatmap = cv2.applyColorMap(density_norm, self.config.heatmap_colormap)
        return color_heatmap

    def overlay_heatmap(
        self,
        frame: np.ndarray,
        tracking_batch: TrackingBatch,
        alpha: Optional[float] = None
    ) -> np.ndarray:
        """
        Blends crowd density heatmap over input image frame.
        
        Args:
            frame: Input BGR image frame.
            tracking_batch: TrackingBatch containing active tracks.
            alpha: Alpha blending ratio [0.0 - 1.0].
            
        Returns:
            Blended BGR image frame.
        """
        h, w = frame.shape[:2]
        blend_alpha = alpha if alpha is not None else self.config.heatmap_alpha
        
        heatmap = self.generate_density_heatmap(tracking_batch, image_width=w, image_height=h)

        if len(tracking_batch.active_tracks) == 0:
            return frame.copy()

        blended = cv2.addWeighted(frame, 1.0 - blend_alpha, heatmap, blend_alpha, 0)
        return blended
