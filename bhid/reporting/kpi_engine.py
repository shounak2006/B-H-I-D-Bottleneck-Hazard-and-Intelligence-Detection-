"""
BHID Operational Key Performance Indicator (KPI) Computation Engine.

Computes quantitative performance metrics, density peaks, average crowd metrics,
risk probability stats, and hazard event resolution rates from persisted operational data.
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class KPIEngine:
    """
    Operational KPI computation and export engine.
    """

    @staticmethod
    def compute_kpis(
        predictions: List[Dict[str, Any]],
        analytics: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Computes comprehensive operational KPIs for a recording session.
        """
        # 1. Predictions metrics
        probs = [float(p.get("prediction_probability", 0.0)) for p in predictions]
        peak_prob = max(probs) if probs else 0.0
        avg_prob = (sum(probs) / len(probs)) if probs else 0.0

        # 2. Analytics metrics
        ped_counts = []
        densities = []
        for a in analytics:
            feat = a.get("features", {})
            cnt = feat.get("feature_pedestrian_count", a.get("pedestrian_count", 0))
            den = feat.get("feature_density_ped_per_m2", a.get("density_ped_per_m2", 0.0))
            ped_counts.append(int(cnt))
            densities.append(float(den))

        peak_peds = max(ped_counts) if ped_counts else 0
        avg_peds = (sum(ped_counts) / float(len(ped_counts))) if ped_counts else 0.0
        peak_dens = max(densities) if densities else 0.0
        avg_dens = (sum(densities) / float(len(densities))) if densities else 0.0

        # 3. Hazard events metrics
        tot_events = len(events)
        res_events = sum(1 for e in events if e.get("status") == "RESOLVED")
        esc_counts = sum(int(e.get("escalation_count", 0)) for e in events)

        durations = [float(e.get("duration_seconds", 0.0)) for e in events]
        avg_duration = (sum(durations) / float(len(durations))) if durations else 0.0

        return {
            "peak_density_ped_per_m2": round(peak_dens, 4),
            "average_density_ped_per_m2": round(avg_dens, 4),
            "peak_pedestrian_count": peak_peds,
            "average_pedestrian_count": round(avg_peds, 2),
            "peak_prediction_probability": round(peak_prob, 4),
            "average_prediction_probability": round(avg_prob, 4),
            "total_hazard_events": tot_events,
            "resolved_hazard_events": res_events,
            "resolution_rate_pct": round((res_events / tot_events * 100.0), 2) if tot_events > 0 else 100.0,
            "total_escalations": esc_counts,
            "average_event_duration_seconds": round(avg_duration, 2)
        }

    @staticmethod
    def export_kpis(kpis: Dict[str, Any], file_path: Path) -> Optional[Path]:
        """Exports computed KPIs dictionary to JSON file."""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(kpis, f, indent=2)
            return file_path
        except Exception:
            return None
