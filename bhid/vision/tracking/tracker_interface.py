"""
BHID Pedestrian Tracker Interface.

Abstract base contract for multi-object tracking implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from bhid.vision.detection.detection_batch import DetectionBatch


class BasePedestrianTracker(ABC):
    """
    Abstract interface defining pedestrian multi-object tracker lifecycle and updates.
    """

    @abstractmethod
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes tracker parameters, distance thresholds, and internal counters.
        
        Args:
            config: Optional configuration dictionary.
        """
        pass

    @abstractmethod
    def update(self, detection_batch: DetectionBatch) -> Any:
        """
        Updates tracking state with frame-level DetectionBatch and returns a TrackingBatch.
        
        Args:
            detection_batch: Input DetectionBatch from vision detector.
            
        Returns:
            TrackingBatch object containing active tracks for the frame.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Resets active tracks and resets internal state."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleans up resources and resets tracker state."""
        pass
