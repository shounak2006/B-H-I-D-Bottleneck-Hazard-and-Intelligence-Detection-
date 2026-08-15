"""
BHID Visualization & Visual Monitoring Package.

Provides OpenCV frame renderers, trajectory history overlays, crowd density heatmaps,
hazard alert banners, telemetry snapshots, and primary monitoring controllers.
"""

from bhid.visualization.visual_config import VisualConfig
from bhid.visualization.frame_renderer import FrameRenderer
from bhid.visualization.trajectory_renderer import TrajectoryRenderer
from bhid.visualization.heatmap_renderer import HeatmapRenderer
from bhid.visualization.event_renderer import EventRenderer
from bhid.visualization.monitoring_snapshot import MonitoringSnapshot
from bhid.visualization.monitoring_controller import MonitoringController

__all__ = [
    "VisualConfig",
    "FrameRenderer",
    "TrajectoryRenderer",
    "HeatmapRenderer",
    "EventRenderer",
    "MonitoringSnapshot",
    "MonitoringController",
]
