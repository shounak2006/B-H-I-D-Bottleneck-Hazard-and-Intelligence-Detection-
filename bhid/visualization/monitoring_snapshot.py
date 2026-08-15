"""
BHID Monitoring Snapshot Data Model.

Dataclass encapsulating single-frame operational telemetry, visual telemetry statistics,
risk probability assessments, and active hazard event summaries.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class MonitoringSnapshot:
    """
    Single-frame operational monitoring telemetry snapshot.
    
    Attributes:
        frame_id: Frame sequence identifier.
        timestamp: Frame timestamp in seconds.
        scene_id: Active scene identifier.
        zone_id: Active spatial ROI zone identifier.
        pedestrian_count: Current count of detected pedestrians.
        density_ped_per_m2: Spatial crowd density per m^2.
        active_tracks_count: Total active tracked pedestrian objects.
        prediction_probability: Bottleneck risk probability [0.0 - 1.0].
        risk_level: Assigned risk level ('LOW', 'MODERATE', 'HIGH', 'CRITICAL').
        binary_prediction: Binary bottleneck hazard classification (0 or 1).
        active_event_count: Total active hazard events in registry.
        active_events: List of dictionary summaries for active events.
        target_horizon: Model prediction horizon (frozen at 'Y30').
    """
    frame_id: int
    timestamp: float
    scene_id: str
    zone_id: str
    pedestrian_count: int
    density_ped_per_m2: float
    active_tracks_count: int
    prediction_probability: float
    risk_level: str
    binary_prediction: int
    active_event_count: int
    active_events: List[Dict[str, Any]] = field(default_factory=list)
    target_horizon: str = "Y30"

    def __post_init__(self):
        self.frame_id = int(self.frame_id)
        self.timestamp = float(self.timestamp)
        self.scene_id = str(self.scene_id)
        self.zone_id = str(self.zone_id)
        self.pedestrian_count = int(self.pedestrian_count)
        self.density_ped_per_m2 = float(self.density_ped_per_m2)
        self.active_tracks_count = int(self.active_tracks_count)
        self.prediction_probability = float(self.prediction_probability)
        self.risk_level = str(self.risk_level).upper()
        self.binary_prediction = int(self.binary_prediction)
        self.active_event_count = int(self.active_event_count)
        self.target_horizon = str(self.target_horizon)

    def summary_string(self) -> str:
        """Returns concise operator-facing status string."""
        return (
            f"[FRAME {self.frame_id:04d} | {self.scene_id}:{self.zone_id}] "
            f"Peds={self.pedestrian_count} | Dens={self.density_ped_per_m2:.2f} ped/m2 | "
            f"Risk={self.risk_level} ({self.prediction_probability*100:.1f}%) | "
            f"ActiveEvents={self.active_event_count}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable dictionary representation."""
        return {
            "frame_id": self.frame_id,
            "timestamp": self.timestamp,
            "scene_id": self.scene_id,
            "zone_id": self.zone_id,
            "pedestrian_count": self.pedestrian_count,
            "density_ped_per_m2": round(self.density_ped_per_m2, 4),
            "active_tracks_count": self.active_tracks_count,
            "prediction_probability": round(self.prediction_probability, 4),
            "risk_level": self.risk_level,
            "binary_prediction": self.binary_prediction,
            "active_event_count": self.active_event_count,
            "active_events": list(self.active_events),
            "target_horizon": self.target_horizon,
            "summary": self.summary_string()
        }
