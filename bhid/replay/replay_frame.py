"""
BHID Replay Frame Container.

Dataclass encapsulating reconstructed historical state for a single replayed frame.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class ReplayFrame:
    """
    Reconstructed state container for a single historical frame.
    
    Attributes:
        frame_id: Frame sequence number.
        timestamp: Historical observation timestamp.
        monitoring_snapshot: Reconstructed monitoring telemetry snapshot dict.
        active_events: List of hazard events active at timestamp.
        prediction_result: Historical prediction result dict.
        analytics_snapshot: Historical 14-feature analytics snapshot dict.
    """
    frame_id: int
    timestamp: float
    monitoring_snapshot: Dict[str, Any] = field(default_factory=dict)
    active_events: List[Dict[str, Any]] = field(default_factory=list)
    prediction_result: Dict[str, Any] = field(default_factory=dict)
    analytics_snapshot: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation."""
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "monitoring_snapshot": dict(self.monitoring_snapshot),
            "active_events": list(self.active_events),
            "prediction_result": dict(self.prediction_result),
            "analytics_snapshot": dict(self.analytics_snapshot)
        }
