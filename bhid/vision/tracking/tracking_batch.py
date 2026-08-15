"""
BHID Tracking Batch Container.

Encapsulates active pedestrian tracks for a single video frame.
"""

from typing import List, Dict, Any, Tuple, Optional
from bhid.vision.tracking.tracked_object import TrackedObject


class TrackingBatch:
    """
    Container representing active pedestrian tracks for a frame.
    
    Attributes:
        frame_id: Frame sequence number or identifier.
        timestamp: Observation timestamp.
        active_tracks: List of active TrackedObject instances.
        metadata: Optional dictionary of frame metadata.
    """

    def __init__(
        self,
        frame_id: Any,
        timestamp: float,
        active_tracks: Optional[List[TrackedObject]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        image_width: float = 1920.0,
        image_height: float = 1080.0
    ):
        self.frame_id = frame_id
        self.timestamp = float(timestamp)
        self.active_tracks: List[TrackedObject] = active_tracks if active_tracks is not None else []
        self.metadata: Dict[str, Any] = metadata or {}
        self.image_width = float(image_width) if image_width is not None else 1920.0
        self.image_height = float(image_height) if image_height is not None else 1080.0

    def active_count(self) -> int:
        """Returns count of active pedestrian tracks in the batch."""
        return len(self.active_tracks)

    def get_track_ids(self) -> List[Any]:
        """Returns list of active track IDs."""
        return [t.track_id for t in self.active_tracks]

    def get_bboxes(self) -> List[Tuple[float, float, float, float]]:
        """Returns list of current bounding box tuples for active tracks."""
        return [t.current_bbox for t in self.active_tracks]

    def get_centroids(self) -> List[Tuple[float, float]]:
        """Returns list of current center (x, y) tuples for active tracks."""
        return [t.get_center() for t in self.active_tracks]

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of tracking batch."""
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "active_count": self.active_count(),
            "track_ids": self.get_track_ids(),
            "active_tracks": [t.to_dict() for t in self.active_tracks],
            "metadata": dict(self.metadata)
        }
