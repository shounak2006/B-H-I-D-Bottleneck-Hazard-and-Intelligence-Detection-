"""
BHID Vision Detection Package.

Provides detection schemas, frame-level batch containers, detector interfaces,
mock detectors, and detection-to-observation adapters.
"""

from bhid.vision.detection.detection_schema import Detection, DetectionValidationError
from bhid.vision.detection.detection_batch import DetectionBatch
from bhid.vision.detection.pedestrian_detector_interface import BasePedestrianDetector
from bhid.vision.detection.mock_detector import MockPedestrianDetector
from bhid.vision.detection.detection_adapter import DetectionAdapter

__all__ = [
    "Detection",
    "DetectionValidationError",
    "DetectionBatch",
    "BasePedestrianDetector",
    "MockPedestrianDetector",
    "DetectionAdapter",
]
