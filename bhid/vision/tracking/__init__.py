"""
BHID Vision Tracking Package.

Provides trajectory models, tracked object state containers, tracker interfaces,
baseline centroid tracking, and tracking-to-observation adapters.
"""

from bhid.vision.tracking.trajectory import TrajectoryPoint, Trajectory
from bhid.vision.tracking.tracked_object import TrackedObject
from bhid.vision.tracking.tracker_interface import BasePedestrianTracker
from bhid.vision.tracking.centroid_tracker import CentroidTracker
from bhid.vision.tracking.tracking_batch import TrackingBatch
from bhid.vision.tracking.tracking_adapter import TrackingAdapter

__all__ = [
    "TrajectoryPoint",
    "Trajectory",
    "TrackedObject",
    "BasePedestrianTracker",
    "CentroidTracker",
    "TrackingBatch",
    "TrackingAdapter",
]
