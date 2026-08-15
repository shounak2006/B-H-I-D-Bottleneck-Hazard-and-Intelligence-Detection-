"""
BHID Pedestrian Detector Interface.

Abstract base contract for all vision detector implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from bhid.vision.detection.detection_batch import DetectionBatch


class BasePedestrianDetector(ABC):
    """
    Abstract interface defining detector lifecycle and detection contract.
    """

    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes detector model weights, device context, and parameters.
        
        Args:
            config: Optional configuration dictionary.
        """
        pass

    @abstractmethod
    def detect(
        self,
        frame: Any,
        frame_id: Any = 0,
        timestamp: float = 0.0
    ) -> DetectionBatch:
        """
        Executes pedestrian detection on an input image frame.
        
        Args:
            frame: Input image array, tensor, or frame matrix.
            frame_id: Frame sequence identifier.
            timestamp: Frame observation timestamp.
            
        Returns:
            DetectionBatch containing detected objects.
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Releases GPU memory, model contexts, and device resources.
        """
        pass
