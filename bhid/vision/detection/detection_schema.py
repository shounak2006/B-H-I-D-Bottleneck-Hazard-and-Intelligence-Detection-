"""
BHID Vision Detection Schema.

Defines the canonical single-object detection schema for vision pipelines.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional


class DetectionValidationError(ValueError):
    """Raised when detection object validation fails."""
    pass


@dataclass
class Detection:
    """
    Canonical bounding box detection record for a single object.
    
    Attributes:
        detection_id: Unique detection identifier string.
        class_name: Target class label (default: 'pedestrian').
        confidence: Detection confidence probability in [0.0, 1.0].
        bbox_x1: Top-left bounding box X coordinate in pixels or normalized [0, 1].
        bbox_y1: Top-left bounding box Y coordinate in pixels or normalized [0, 1].
        bbox_x2: Bottom-right bounding box X coordinate in pixels or normalized [0, 1].
        bbox_y2: Bottom-right bounding box Y coordinate in pixels or normalized [0, 1].
        frame_id: Frame sequence number or identifier.
        timestamp: Time of observation.
    """
    detection_id: str
    confidence: float
    bbox_x1: float
    bbox_y1: float
    bbox_x2: float
    bbox_y2: float
    frame_id: Any = 0
    timestamp: float = 0.0
    class_name: str = "pedestrian"

    def __post_init__(self):
        self.detection_id = str(self.detection_id)
        self.class_name = str(self.class_name).lower()
        self.confidence = float(self.confidence)
        self.bbox_x1 = float(self.bbox_x1)
        self.bbox_y1 = float(self.bbox_y1)
        self.bbox_x2 = float(self.bbox_x2)
        self.bbox_y2 = float(self.bbox_y2)
        self.timestamp = float(self.timestamp)
        self.validate()

    def validate(self) -> bool:
        """Validates bounding box geometry and confidence values."""
        if not (0.0 <= self.confidence <= 1.0):
            raise DetectionValidationError(f"Confidence score out of bounds [0, 1]: {self.confidence}")
        if self.bbox_x1 > self.bbox_x2:
            raise DetectionValidationError(f"Invalid bbox X coordinates: x1 ({self.bbox_x1}) > x2 ({self.bbox_x2})")
        if self.bbox_y1 > self.bbox_y2:
            raise DetectionValidationError(f"Invalid bbox Y coordinates: y1 ({self.bbox_y1}) > y2 ({self.bbox_y2})")
        return True

    @property
    def width(self) -> float:
        """Returns bounding box width."""
        return max(0.0, self.bbox_x2 - self.bbox_x1)

    @property
    def height(self) -> float:
        """Returns bounding box height."""
        return max(0.0, self.bbox_y2 - self.bbox_y1)

    @property
    def area(self) -> float:
        """Returns bounding box area."""
        return self.width * self.height

    @property
    def center(self) -> Tuple[float, float]:
        """Returns (center_x, center_y) of bounding box."""
        return (
            (self.bbox_x1 + self.bbox_x2) / 2.0,
            (self.bbox_y1 + self.bbox_y2) / 2.0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns dictionary representation of detection."""
        return {
            "detection_id": self.detection_id,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "bbox_x1": self.bbox_x1,
            "bbox_y1": self.bbox_y1,
            "bbox_x2": self.bbox_x2,
            "bbox_y2": self.bbox_y2,
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "area": self.area,
            "center": self.center
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Detection":
        """Creates Detection instance from dictionary."""
        return cls(
            detection_id=d.get("detection_id", "det_unk"),
            class_name=d.get("class_name", "pedestrian"),
            confidence=d.get("confidence", 1.0),
            bbox_x1=d.get("bbox_x1", 0.0),
            bbox_y1=d.get("bbox_y1", 0.0),
            bbox_x2=d.get("bbox_x2", 0.0),
            bbox_y2=d.get("bbox_y2", 0.0),
            frame_id=d.get("frame_id", 0),
            timestamp=d.get("timestamp", 0.0)
        )
