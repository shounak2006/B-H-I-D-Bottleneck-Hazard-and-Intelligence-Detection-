"""
BHID Tracked Object Model.

Encapsulates a single tracked pedestrian instance across consecutive video frames.
"""

from typing import Dict, Any, Tuple, Optional
from bhid.vision.tracking.trajectory import Trajectory


class TrackedObject:
    """
    State container for a tracked pedestrian.
    
    Attributes:
        track_id: Unique track identifier.
        current_bbox: Latest bounding box tuple (x1, y1, x2, y2).
        confidence: Latest detection confidence score.
        first_seen_timestamp: Time of initial track creation.
        last_seen_timestamp: Time of most recent track update.
        age_frames: Total number of frames since track creation.
        missed_frames: Consecutive frames missed since last detection match.
        trajectory_history: Trajectory instance tracking position history.
    """

    def __init__(
        self,
        track_id: Any,
        bbox: Tuple[float, float, float, float],
        confidence: float,
        timestamp: float,
        frame_id: Any = 0
    ):
        self.track_id = track_id
        self.current_bbox = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        self.confidence = float(confidence)
        self.first_seen_timestamp = float(timestamp)
        self.last_seen_timestamp = float(timestamp)
        self.age_frames: int = 1
        self.missed_frames: int = 0
        
        self.trajectory_history = Trajectory()
        center_x, center_y = self.get_center()
        self.trajectory_history.add_point(x=center_x, y=center_y, timestamp=timestamp, frame_id=frame_id)

    def get_center(self) -> Tuple[float, float]:
        """Returns current center coordinates (x, y) of bounding box."""
        x1, y1, x2, y2 = self.current_bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def update(
        self,
        bbox: Tuple[float, float, float, float],
        confidence: float,
        timestamp: float,
        frame_id: Any = 0
    ) -> None:
        """
        Updates track state with a newly matched detection.
        Resets missed_frames counter and appends new point to trajectory history.
        """
        self.current_bbox = (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        self.confidence = float(confidence)
        self.last_seen_timestamp = float(timestamp)
        self.age_frames += 1
        self.missed_frames = 0
        
        center_x, center_y = self.get_center()
        self.trajectory_history.add_point(x=center_x, y=center_y, timestamp=timestamp, frame_id=frame_id)

    def mark_missed(self) -> None:
        """Increments age_frames and missed_frames when no matching detection is found."""
        self.age_frames += 1
        self.missed_frames += 1

    def get_velocity_estimate(self) -> Tuple[float, float]:
        """Estimates current velocity (vx, vy) from trajectory history."""
        return self.trajectory_history.get_average_velocity()

    @property
    def bbox(self) -> Tuple[float, float, float, float]:
        """Property alias for current_bbox."""
        return self.current_bbox

    @property
    def centroid(self) -> Tuple[float, float]:
        """Property alias for get_center()."""
        return self.get_center()

    @property
    def trajectory(self) -> Trajectory:
        """Property alias for trajectory_history."""
        return self.trajectory_history

    @property
    def velocity(self) -> Tuple[float, float]:
        """Property alias for get_velocity_estimate()."""
        return self.get_velocity_estimate()

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of tracked object."""
        vx, vy = self.get_velocity_estimate()
        return {
            "track_id": self.track_id,
            "current_bbox": list(self.current_bbox),
            "confidence": self.confidence,
            "center": list(self.get_center()),
            "first_seen_timestamp": self.first_seen_timestamp,
            "last_seen_timestamp": self.last_seen_timestamp,
            "age_frames": self.age_frames,
            "missed_frames": self.missed_frames,
            "velocity": [round(vx, 4), round(vy, 4)],
            "trajectory_points": len(self.trajectory_history.points)
        }

