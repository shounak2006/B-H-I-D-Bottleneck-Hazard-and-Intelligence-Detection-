"""
BHID Comparative Cross-Session Analytics Engine.

Provides multi-session benchmarking, comparative risk profiling, peak crowd density rankings,
and operational performance comparisons across historical recording sessions.
"""

from typing import List, Dict, Any, Optional
from bhid.reporting.session_report import SessionReport


class ComparativeAnalysis:
    """
    Cross-session comparative analytics engine.
    """

    @staticmethod
    def compare_density(reports: List[SessionReport]) -> List[Dict[str, Any]]:
        """Compares peak and average crowd densities across sessions."""
        res = []
        for r in reports:
            kpis = r.kpi_summary
            res.append({
                "session_id": r.session_id,
                "scene_id": r.scene_id,
                "zone_id": r.zone_id,
                "peak_density_ped_per_m2": kpis.get("peak_density_ped_per_m2", 0.0),
                "average_density_ped_per_m2": kpis.get("average_density_ped_per_m2", 0.0),
                "peak_pedestrian_count": kpis.get("peak_pedestrian_count", 0)
            })
        res.sort(key=lambda x: x["peak_density_ped_per_m2"], reverse=True)
        return res

    @staticmethod
    def compare_event_frequency(reports: List[SessionReport]) -> List[Dict[str, Any]]:
        """Compares total hazard event counts and resolution rates across sessions."""
        res = []
        for r in reports:
            kpis = r.kpi_summary
            res.append({
                "session_id": r.session_id,
                "total_hazard_events": kpis.get("total_hazard_events", 0),
                "resolved_hazard_events": kpis.get("resolved_hazard_events", 0),
                "resolution_rate_pct": kpis.get("resolution_rate_pct", 100.0),
                "total_escalations": kpis.get("total_escalations", 0)
            })
        res.sort(key=lambda x: x["total_hazard_events"], reverse=True)
        return res

    @staticmethod
    def compare_risk_profiles(reports: List[SessionReport]) -> List[Dict[str, Any]]:
        """Compares peak bottleneck risk probabilities across sessions."""
        res = []
        for r in reports:
            kpis = r.kpi_summary
            res.append({
                "session_id": r.session_id,
                "scene_id": r.scene_id,
                "peak_prediction_probability": kpis.get("peak_prediction_probability", 0.0),
                "average_prediction_probability": kpis.get("average_prediction_probability", 0.0)
            })
        res.sort(key=lambda x: x["peak_prediction_probability"], reverse=True)
        return res

    @classmethod
    def identify_peak_sessions(cls, reports: List[SessionReport]) -> Dict[str, Any]:
        """Identifies session with highest density and session with highest event count."""
        if not reports:
            return {}

        density_comp = cls.compare_density(reports)
        event_comp = cls.compare_event_frequency(reports)
        risk_comp = cls.compare_risk_profiles(reports)

        return {
            "highest_density_session": density_comp[0] if density_comp else None,
            "highest_event_session": event_comp[0] if event_comp else None,
            "highest_risk_session": risk_comp[0] if risk_comp else None
        }

    @classmethod
    def compare_sessions(cls, reports: List[SessionReport]) -> Dict[str, Any]:
        """Generates complete comparative benchmarking analysis dictionary."""
        return {
            "total_sessions_analyzed": len(reports),
            "density_comparison": cls.compare_density(reports),
            "event_frequency_comparison": cls.compare_event_frequency(reports),
            "risk_profile_comparison": cls.compare_risk_profiles(reports),
            "peaks_summary": cls.identify_peak_sessions(reports)
        }
