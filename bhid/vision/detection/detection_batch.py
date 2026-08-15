"""
BHID Detection Batch Container.

Encapsulates frame-level detection outputs with filtering and summary capabilities.
"""

from typing import List, Dict, Any, Optional, Tuple
import math
from bhid.vision.detection.detection_schema import Detection


class DetectionBatch:
    """
    Frame-level container for object detections.
    
    Attributes:
        frame_id: Frame sequence number or identifier.
        timestamp: Observation timestamp.
        detections: List of Detection objects.
        image_width: Optional image width in pixels.
        image_height: Optional image height in pixels.
        metadata: Optional dictionary of frame metadata.
    """

    def __init__(
        self,
        frame_id: Any,
        timestamp: float,
        detections: Optional[List[Detection]] = None,
        image_width: Optional[float] = None,
        image_height: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.frame_id = frame_id
        self.timestamp = float(timestamp)
        self.detections: List[Detection] = detections if detections is not None else []
        self.image_width = float(image_width) if image_width is not None else None
        self.image_height = float(image_height) if image_height is not None else None
        self.metadata: Dict[str, Any] = metadata or {}

    def add_detection(self, detection: Detection) -> None:
        """Appends a Detection object to the batch."""
        if not isinstance(detection, Detection):
            raise TypeError(f"Expected Detection instance, got {type(detection).__name__}")
        self.detections.append(detection)

    def pedestrian_count(self, confidence_threshold: float = 0.0) -> int:
        """Returns count of pedestrian detections meeting minimum confidence threshold."""
        return sum(
            1 for d in self.detections
            if d.class_name == "pedestrian" and d.confidence >= confidence_threshold
        )

    def confidence_summary(self) -> Dict[str, float]:
        """Returns statistical summary of detection confidence scores."""
        if not self.detections:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "std": 0.0, "count": 0}

        confidences = [d.confidence for d in self.detections]
        n = len(confidences)
        mean_conf = sum(confidences) / float(n)
        min_conf = min(confidences)
        max_conf = max(confidences)
        
        variance = sum((c - mean_conf) ** 2 for c in confidences) / float(n) if n > 1 else 0.0
        std_conf = math.sqrt(variance)

        return {
            "mean": round(mean_conf, 4),
            "min": round(min_conf, 4),
            "max": round(max_conf, 4),
            "std": round(std_conf, 4),
            "count": n
        }

    def filter_by_class(self, class_name: str = "pedestrian") -> List[Detection]:
        """Returns list of detections matching specified class label."""
        target_cls = class_name.lower()
        return [d for d in self.detections if d.class_name == target_cls]

    def filter_by_confidence(self, min_confidence: float = 0.50) -> "DetectionBatch":
        """Returns a new DetectionBatch containing only detections >= min_confidence."""
        filtered_dets = [d for d in self.detections if d.confidence >= min_confidence]
        return DetectionBatch(
            frame_id=self.frame_id,
            timestamp=self.timestamp,
            detections=filtered_dets,
            image_width=self.image_width,
            image_height=self.image_height,
            metadata=dict(self.metadata)
        )

    def get_bboxes(self) -> List[Tuple[float, float, float, float]]:
        """Returns list of (x1, y1, x2, y2) tuples for all detections in batch."""
        return [(d.bbox_x1, d.bbox_y1, d.bbox_x2, d.bbox_y2) for d in self.detections]

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of batch."""
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "count": len(self.detections),
            "pedestrian_count": self.pedestrian_count(),
            "confidence_summary": self.confidence_summary(),
            "image_width": self.image_width,
            "image_height": self.image_height,
            "detections": [d.to_dict() for d in self.detections],
            "metadata": dict(self.metadata)
        }
