"""
BHID Visualization Configuration.

Defines color maps, font styles, rendering line weights, and overlay parameters
for OpenCV-based visual monitoring.
"""

from dataclasses import dataclass, field
from typing import Dict, Tuple, Any
import cv2


@dataclass
class VisualConfig:
    """
    Central visual styling configuration.
    
    Attributes:
        risk_colors: Mapping of risk levels ('LOW', 'MODERATE', 'HIGH', 'CRITICAL') to OpenCV BGR tuples.
        track_color: BGR tuple for track bounding boxes and IDs.
        trajectory_color: BGR tuple for trajectory history trails.
        velocity_vector_color: BGR tuple for velocity direction arrows.
        text_color: BGR tuple for text labels.
        panel_bg_color: BGR tuple for telemetry panel background overlays.
        trail_length: Max historical trajectory points to render per track.
        line_thickness: Line thickness in pixels.
        font_face: OpenCV font type.
        font_scale: OpenCV font scale multiplier.
        heatmap_alpha: Alpha blending opacity for density heatmap overlays [0.0 - 1.0].
        heatmap_colormap: OpenCV colormap constant.
    """
    risk_colors: Dict[str, Tuple[int, int, int]] = field(default_factory=lambda: {
        "LOW": (0, 200, 0),        # Green
        "MODERATE": (0, 215, 255),  # Yellow
        "HIGH": (0, 140, 255),      # Orange
        "CRITICAL": (0, 0, 255)     # Red
    })
    track_color: Tuple[int, int, int] = (255, 180, 0)       # Cyan/Blue
    trajectory_color: Tuple[int, int, int] = (255, 255, 0) # Cyan
    velocity_vector_color: Tuple[int, int, int] = (0, 255, 255) # Yellow
    text_color: Tuple[int, int, int] = (255, 255, 255)       # White
    panel_bg_color: Tuple[int, int, int] = (30, 30, 30)      # Dark Gray
    
    trail_length: int = 15
    line_thickness: int = 2
    font_face: int = cv2.FONT_HERSHEY_SIMPLEX
    font_scale: float = 0.55
    heatmap_alpha: float = 0.4
    heatmap_colormap: int = cv2.COLORMAP_JET

    def get_risk_color(self, risk_level: str) -> Tuple[int, int, int]:
        """Returns BGR color tuple corresponding to the risk level."""
        return self.risk_colors.get(str(risk_level).upper(), (200, 200, 200))
