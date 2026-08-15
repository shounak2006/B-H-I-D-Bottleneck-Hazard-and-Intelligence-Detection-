"""
BHID Mock Pedestrian Detector.

Deterministic synthetic detector implementation for testing and development pipelines.
"""

from typing import Dict, Any, Optional, List
import random
from bhid.vision.detection.pedestrian_detector_interface import BasePedestrianDetector
from bhid.vision.detection.detection_schema import Detection
from bhid.vision.detection.detection_batch import DetectionBatch


class MockPedestrianDetector(BasePedestrianDetector):
    """
    Synthetic detector that generates deterministic bounding box detections.
    
    Parameters:
        num_pedestrians: Default number of pedestrians to simulate per frame.
        confidence_range: (min_conf, max_conf) tuple for generated detections.
        image_width: Default simulated image width in pixels (default: 1920.0).
        image_height: Default simulated image height in pixels (default: 1080.0).
        seed: Optional random seed for reproducible synthetic generation.
    """

    def __init__(
        self,
        num_pedestrians: int = 10,
        confidence_range: tuple = (0.75, 0.98),
        image_width: float = 1920.0,
        image_height: float = 1080.0,
        seed: Optional[int] = 42
    ):
        self.num_pedestrians = int(num_pedestrians)
        self.confidence_range = confidence_range
        self.image_width = float(image_width)
        self.image_height = float(image_height)
        self.seed = seed
        self.is_initialized: bool = False
        
        if seed is not None:
            self._rng = random.Random(seed)
        else:
            self._rng = random.Random()

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initializes mock detector parameters."""
        if config:
            if "num_pedestrians" in config:
                self.num_pedestrians = int(config["num_pedestrians"])
            if "image_width" in config:
                self.image_width = float(config["image_width"])
            if "image_height" in config:
                self.image_height = float(config["image_height"])
        self.is_initialized = True

    def set_pedestrian_count(self, count: int) -> None:
        """Dynamically adjusts the simulated pedestrian count."""
        self.num_pedestrians = max(0, int(count))

    def detect(
        self,
        frame: Any = None,
        frame_id: Any = 0,
        timestamp: float = 0.0
    ) -> DetectionBatch:
        """
        Generates a synthetic DetectionBatch for the specified frame.
        """
        if not self.is_initialized:
            self.initialize()

        detections: List[Detection] = []
        min_c, max_c = self.confidence_range

        for i in range(self.num_pedestrians):
            det_id = f"mock_det_f{frame_id}_{i:03d}"
            conf = round(self._rng.uniform(min_c, max_c), 4)

            # Generate realistic bounding boxes within image boundaries
            w = self._rng.uniform(30.0, 80.0)
            h = w * self._rng.uniform(2.0, 3.5)
            x1 = self._rng.uniform(10.0, max(10.0, self.image_width - w - 10.0))
            y1 = self._rng.uniform(10.0, max(10.0, self.image_height - h - 10.0))
            x2 = min(self.image_width, x1 + w)
            y2 = min(self.image_height, y1 + h)

            det = Detection(
                detection_id=det_id,
                class_name="pedestrian",
                confidence=conf,
                bbox_x1=round(x1, 2),
                bbox_y1=round(y1, 2),
                bbox_x2=round(x2, 2),
                bbox_y2=round(y2, 2),
                frame_id=frame_id,
                timestamp=timestamp
            )
            detections.append(det)

        return DetectionBatch(
            frame_id=frame_id,
            timestamp=timestamp,
            detections=detections,
            image_width=self.image_width,
            image_height=self.image_height,
            metadata={"detector_type": "MockPedestrianDetector", "simulated_count": self.num_pedestrians}
        )

    def shutdown(self) -> None:
        """Resets initialized state."""
        self.is_initialized = False
