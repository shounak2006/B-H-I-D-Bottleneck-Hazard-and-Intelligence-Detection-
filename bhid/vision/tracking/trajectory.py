"""
BHID Trajectory Data Structure.

Encapsulates ordered spatial position history, temporal duration,
path length computation, and velocity estimation for tracked pedestrians.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import math


@dataclass
class TrajectoryPoint:
    """
    Single spatial position sample in a trajectory.
    """
    x: float
    y: float
    timestamp: float
    frame_id: Any

    def __post_init__(self):
        self.x = float(self.x)
        self.y = float(self.y)
        self.timestamp = float(self.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "timestamp": self.timestamp,
            "frame_id": self.frame_id
        }


class Trajectory:
    """
    Ordered history of spatial positions recorded for a single tracked object.
    
    Parameters:
        max_history_points: Maximum number of historical points to retain (default: 500).
    """

    def __init__(self, max_history_points: int = 500):
        self.max_history_points = int(max_history_points)
        self.points: List[TrajectoryPoint] = []

    def add_point(
        self,
        x: float,
        y: float,
        timestamp: float,
        frame_id: Any = 0
    ) -> TrajectoryPoint:
        """Appends a new position sample to the trajectory history."""
        pt = TrajectoryPoint(x=x, y=y, timestamp=timestamp, frame_id=frame_id)
        self.points.append(pt)
        if len(self.points) > self.max_history_points:
            self.points.pop(0)
        return pt

    @property
    def start_time(self) -> Optional[float]:
        """Returns timestamp of first point, or None if trajectory is empty."""
        return self.points[0].timestamp if self.points else None

    @property
    def end_time(self) -> Optional[float]:
        """Returns timestamp of latest point, or None if trajectory is empty."""
        return self.points[-1].timestamp if self.points else None

    def duration_seconds(self) -> float:
        """Returns total temporal duration of trajectory in seconds."""
        if len(self.points) < 2:
            return 0.0
        return self.points[-1].timestamp - self.points[0].timestamp

    def get_path_length(self) -> float:
        """Computes cumulative Euclidean path length across all trajectory points."""
        if len(self.points) < 2:
            return 0.0
        length = 0.0
        for i in range(1, len(self.points)):
            p1 = self.points[i - 1]
            p2 = self.points[i]
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            length += math.sqrt(dx * dx + dy * dy)
        return length

    def get_average_velocity(self) -> Tuple[float, float]:
        """
        Estimates overall displacement velocity vector (vx, vy) in units/sec.
        Returns (0.0, 0.0) if duration is zero or trajectory has < 2 points.
        """
        dt = self.duration_seconds()
        if dt <= 0.0 or len(self.points) < 2:
            return (0.0, 0.0)
        
        p_start = self.points[0]
        p_end = self.points[-1]
        vx = (p_end.x - p_start.x) / dt
        vy = (p_end.y - p_start.y) / dt
        return (vx, vy)

    def get_recent_positions(self, n: int = 10) -> List[Tuple[float, float]]:
        """Returns list of recent (x, y) tuples up to n points."""
        recent = self.points[-n:] if len(self.points) >= n else self.points
        return [(pt.x, pt.y) for pt in recent]

    def get_recent_points(self, n_points: int = 15) -> List[TrajectoryPoint]:
        """Returns list of recent TrajectoryPoint objects up to n_points."""
        return self.points[-n_points:] if len(self.points) >= n_points else list(self.points)

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of trajectory."""
        vx, vy = self.get_average_velocity()
        return {
            "point_count": len(self.points),
            "duration_seconds": round(self.duration_seconds(), 4),
            "path_length": round(self.get_path_length(), 4),
            "velocity_x": round(vx, 4),
            "velocity_y": round(vy, 4),
            "points": [pt.to_dict() for pt in self.points]
        }
