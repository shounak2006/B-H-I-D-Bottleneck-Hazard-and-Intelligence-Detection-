"""
BHID Hazard Event Data Model.

Encapsulates an operational bottleneck hazard event record.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class HazardEvent:
    """
    Operational bottleneck hazard event record.
    
    Attributes:
        event_id: Unique event identifier string.
        scene_id: Scene/video stream identifier.
        zone_id: Spatial ROI zone identifier.
        start_timestamp: Time of initial event trigger.
        last_updated_timestamp: Time of latest prediction update.
        resolved_timestamp: Time of event resolution (None if active).
        prediction_probability: Latest bottleneck prediction probability.
        risk_level: Latest risk level ('LOW', 'MODERATE', 'HIGH', 'CRITICAL').
        target_horizon: Prediction time horizon (frozen at 'Y30').
        status: Event status ('ACTIVE', 'ESCALATED', 'RESOLVED').
        escalation_count: Total times event risk level was escalated.
        prediction_history: Chronological list of predictions received during event lifetime.
    """
    event_id: str
    scene_id: str
    zone_id: str
    start_timestamp: float
    last_updated_timestamp: float
    prediction_probability: float
    risk_level: str
    target_horizon: str = "Y30"
    status: str = "ACTIVE"
    resolved_timestamp: Optional[float] = None
    escalation_count: int = 0
    prediction_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        self.event_id = str(self.event_id)
        self.scene_id = str(self.scene_id)
        self.zone_id = str(self.zone_id)
        self.start_timestamp = float(self.start_timestamp)
        self.last_updated_timestamp = float(self.last_updated_timestamp)
        self.prediction_probability = float(self.prediction_probability)
        self.risk_level = str(self.risk_level).upper()
        self.target_horizon = str(self.target_horizon)
        self.status = str(self.status).upper()
        
        if not self.prediction_history:
            self.prediction_history = [{
                "timestamp": self.start_timestamp,
                "prediction_probability": self.prediction_probability,
                "risk_level": self.risk_level,
                "status": self.status
            }]

    def duration_seconds(self) -> float:
        """Returns active or resolved duration of event in seconds."""
        end_ts = self.resolved_timestamp if self.resolved_timestamp is not None else self.last_updated_timestamp
        return max(0.0, end_ts - self.start_timestamp)

    def update_prediction(
        self,
        probability: float,
        risk_level: str,
        timestamp: float
    ) -> None:
        """Appends prediction record and updates timestamp."""
        self.prediction_probability = float(probability)
        self.risk_level = str(risk_level).upper()
        self.last_updated_timestamp = float(timestamp)
        self.prediction_history.append({
            "timestamp": self.last_updated_timestamp,
            "prediction_probability": self.prediction_probability,
            "risk_level": self.risk_level,
            "status": self.status
        })

    def escalate(
        self,
        probability: float,
        risk_level: str,
        timestamp: float
    ) -> None:
        """Escalates event risk status."""
        self.status = "ESCALATED"
        self.escalation_count += 1
        self.update_prediction(probability=probability, risk_level=risk_level, timestamp=timestamp)

    def resolve(self, timestamp: float) -> None:
        """Marks event as RESOLVED."""
        self.status = "RESOLVED"
        self.resolved_timestamp = float(timestamp)
        self.last_updated_timestamp = float(timestamp)
        self.prediction_history.append({
            "timestamp": self.last_updated_timestamp,
            "prediction_probability": self.prediction_probability,
            "risk_level": self.risk_level,
            "status": "RESOLVED"
        })

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation of hazard event."""
        return {
            "event_id": self.event_id,
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "start_timestamp": self.start_timestamp,
            "last_updated_timestamp": self.last_updated_timestamp,
            "resolved_timestamp": self.resolved_timestamp,
            "duration_seconds": round(self.duration_seconds(), 4),
            "prediction_probability": self.prediction_probability,
            "risk_level": self.risk_level,
            "target_horizon": self.target_horizon,
            "status": self.status,
            "escalation_count": self.escalation_count,
            "history_count": len(self.prediction_history),
            "prediction_history": list(self.prediction_history)
        }
