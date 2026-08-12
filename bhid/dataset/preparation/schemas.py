"""
Standardized Data Schemas for BHID Dataset Preparation and Data Adapters.
Preserves original dataset provenance, timestamps, IDs, bounding boxes, and velocity vectors.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Timestamp:
    frame_index: int
    timestamp_seconds: float
    time_step_delta: float = 0.04  # Default 25 FPS step

@dataclass
class Detection:
    bbox_xywh: List[float]  # [x_min, y_min, width, height]
    confidence: float
    class_id: int = 0  # Default 0 = Person
    class_name: str = "person"

@dataclass
class Frame:
    camera_id: str
    timestamp: Timestamp
    frame_width: int
    frame_height: int
    detections: List[Detection] = field(default_factory=list)
    dataset_provenance: str = "unknown"

@dataclass
class Track:
    track_id: int
    frame_index: int
    timestamp_seconds: float
    bbox_xywh: List[float]
    confidence: float
    velocity_xy: Optional[List[float]] = None  # [vx, vy] in m/s or px/s
    world_pos_xy: Optional[List[float]] = None  # [x, y] metric ground position if available
    class_name: str = "person"

@dataclass
class Trajectory:
    track_id: int
    dataset_provenance: str
    camera_id: str
    states: List[Track] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        if not self.states:
            return 0.0
        return self.states[-1].timestamp_seconds - self.states[0].timestamp_seconds

@dataclass
class Zone:
    zone_id: str
    polygon_vertices: List[List[float]]  # List of [x, y] coordinates
    area_m2: float
    description: str = ""
