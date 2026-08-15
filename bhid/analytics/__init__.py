"""
BHID Crowd Analytics Package.

Transforms vision tracking data into the frozen 14 spatiotemporal feature vectors
required by the production bottleneck prediction engine.
"""

from bhid.analytics.speed_metrics import SpeedMetricsCalculator
from bhid.analytics.flow_metrics import FlowMetricsCalculator
from bhid.analytics.density_metrics import DensityMetricsCalculator
from bhid.analytics.movement_metrics import MovementMetricsCalculator
from bhid.analytics.egress_metrics import EgressMetricsCalculator
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot
from bhid.analytics.crowd_analytics_engine import CrowdAnalyticsEngine

__all__ = [
    "SpeedMetricsCalculator",
    "FlowMetricsCalculator",
    "DensityMetricsCalculator",
    "MovementMetricsCalculator",
    "EgressMetricsCalculator",
    "AnalyticsSnapshot",
    "CrowdAnalyticsEngine",
]
