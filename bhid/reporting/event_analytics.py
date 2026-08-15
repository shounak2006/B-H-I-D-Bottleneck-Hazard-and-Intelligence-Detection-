"""
BHID Hazard Event Intelligence & Analytics Engine.

Analyzes operational hazard event severity breakdowns, escalation frequencies,
duration statistics, resolution rates, and spatial zone risk rankings.
"""

from typing import List, Dict, Any


class EventAnalytics:
    """
    Hazard event intelligence and spatial risk ranking analyzer.
    """

    @staticmethod
    def event_statistics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Computes general hazard event statistics."""
        tot = len(events)
        active = sum(1 for e in events if e.get("status") in ["ACTIVE", "ESCALATED"])
        resolved = sum(1 for e in events if e.get("status") == "RESOLVED")
        
        risk_counts = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
        for e in events:
            r = str(e.get("risk_level", "LOW")).upper()
            risk_counts[r] = risk_counts.get(r, 0) + 1

        return {
            "total_events": tot,
            "active_events": active,
            "resolved_events": resolved,
            "risk_level_breakdown": risk_counts
        }

    @staticmethod
    def escalation_statistics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Computes escalation count metrics across events."""
        esc_counts = [int(e.get("escalation_count", 0)) for e in events]
        tot_esc = sum(esc_counts)
        max_esc = max(esc_counts) if esc_counts else 0
        avg_esc = (tot_esc / float(len(esc_counts))) if esc_counts else 0.0

        return {
            "total_escalations": tot_esc,
            "max_escalations_single_event": max_esc,
            "average_escalations_per_event": round(avg_esc, 2)
        }

    @staticmethod
    def event_duration_analysis(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Computes min, max, and average hazard event durations in seconds."""
        if not events:
            return {"min_duration_seconds": 0.0, "max_duration_seconds": 0.0, "average_duration_seconds": 0.0}

        durations = [float(e.get("duration_seconds", 0.0)) for e in events]
        return {
            "min_duration_seconds": round(min(durations), 2),
            "max_duration_seconds": round(max(durations), 2),
            "average_duration_seconds": round(sum(durations) / float(len(durations)), 2)
        }

    @staticmethod
    def zone_risk_ranking(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ranks spatial ROI zones by total event frequency and maximum probability."""
        zone_map: Dict[str, Dict[str, Any]] = {}
        
        for e in events:
            z_id = str(e.get("zone_id", "UNKNOWN_ZONE"))
            prob = float(e.get("prediction_probability", 0.0))

            if z_id not in zone_map:
                zone_map[z_id] = {
                    "zone_id": z_id,
                    "scene_id": str(e.get("scene_id", "UNKNOWN")),
                    "event_count": 0,
                    "max_probability": 0.0,
                    "critical_count": 0
                }

            entry = zone_map[z_id]
            entry["event_count"] += 1
            entry["max_probability"] = max(entry["max_probability"], prob)
            if e.get("risk_level") == "CRITICAL":
                entry["critical_count"] += 1

        rankings = list(zone_map.values())
        # Sort by critical_count desc, event_count desc, max_probability desc
        rankings.sort(key=lambda x: (x["critical_count"], x["event_count"], x["max_probability"]), reverse=True)
        return rankings

    @classmethod
    def analyze_events(cls, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Computes complete hazard event intelligence package."""
        return {
            "summary": cls.event_statistics(events),
            "escalations": cls.escalation_statistics(events),
            "durations": cls.event_duration_analysis(events),
            "zone_rankings": cls.zone_risk_ranking(events)
        }
