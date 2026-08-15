"""
BHID Replay Analytics Metrics Engine.

Computes statistical telemetry aggregations across replayed historical sessions (peak density,
peak pedestrian count, maximum risk probability, total/resolved hazard events).
"""

from typing import List, Dict, Any


class ReplayMetrics:
    """
    Statistical metric calculator for historical replayed sessions.
    """

    @staticmethod
    def total_events(events: List[Dict[str, Any]]) -> int:
        """Returns total hazard event count."""
        return len(events)

    @staticmethod
    def resolved_events(events: List[Dict[str, Any]]) -> int:
        """Returns total resolved hazard event count."""
        return sum(1 for e in events if e.get("status") == "RESOLVED")

    @staticmethod
    def max_probability(predictions: List[Dict[str, Any]]) -> float:
        """Returns maximum bottleneck hazard prediction probability observed."""
        if not predictions:
            return 0.0
        return max(float(p.get("prediction_probability", 0.0)) for p in predictions)

    @staticmethod
    def average_density(analytics: List[Dict[str, Any]]) -> float:
        """Returns average spatial crowd density per m^2."""
        if not analytics:
            return 0.0
        densities = []
        for a in analytics:
            features = a.get("features", {})
            d = features.get("feature_density_ped_per_m2", a.get("density_ped_per_m2", 0.0))
            densities.append(float(d))
        return sum(densities) / float(len(densities)) if densities else 0.0

    @staticmethod
    def peak_density(analytics: List[Dict[str, Any]]) -> float:
        """Returns peak spatial crowd density per m^2 observed."""
        if not analytics:
            return 0.0
        densities = []
        for a in analytics:
            features = a.get("features", {})
            d = features.get("feature_density_ped_per_m2", a.get("density_ped_per_m2", 0.0))
            densities.append(float(d))
        return max(densities) if densities else 0.0

    @staticmethod
    def peak_pedestrian_count(analytics: List[Dict[str, Any]]) -> int:
        """Returns peak detected pedestrian count observed."""
        if not analytics:
            return 0
        counts = []
        for a in analytics:
            features = a.get("features", {})
            c = features.get("feature_pedestrian_count", a.get("pedestrian_count", 0))
            counts.append(int(c))
        return max(counts) if counts else 0

    @classmethod
    def replay_summary(
        cls,
        session_id: str,
        predictions: List[Dict[str, Any]],
        analytics: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Computes comprehensive statistical replay summary dictionary."""
        return {
            "session_id": str(session_id),
            "total_frames_analyzed": len(predictions),
            "total_events": cls.total_events(events),
            "resolved_events": cls.resolved_events(events),
            "max_prediction_probability": round(cls.max_probability(predictions), 4),
            "average_density_ped_per_m2": round(cls.average_density(analytics), 4),
            "peak_density_ped_per_m2": round(cls.peak_density(analytics), 4),
            "peak_pedestrian_count": cls.peak_pedestrian_count(analytics)
        }
