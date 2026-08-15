"""
BHID Historical Trend Analytics Engine.

Computes chronological time-series trends (density, flow rates, occupancy, risk probability)
and categorical risk level distributions across operational sessions.
"""

from typing import List, Dict, Any


class TrendAnalyzer:
    """
    Chronological trend analytics engine for session telemetry.
    """

    @staticmethod
    def density_trend(analytics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts chronological crowd density time-series."""
        trend = []
        for a in analytics:
            feat = a.get("features", {})
            ts = float(a.get("timestamp", 0.0))
            fid = a.get("frame_id", 0)
            den = float(feat.get("feature_density_ped_per_m2", a.get("density_ped_per_m2", 0.0)))
            trend.append({"frame_id": fid, "timestamp": ts, "density_ped_per_m2": round(den, 4)})
        return trend

    @staticmethod
    def flow_trend(analytics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts chronological inflow, outflow, and net flow rate time-series."""
        trend = []
        for a in analytics:
            feat = a.get("features", {})
            ts = float(a.get("timestamp", 0.0))
            fid = a.get("frame_id", 0)
            inflow = float(feat.get("feature_inflow_rate_per_s", 0.0))
            outflow = float(feat.get("feature_outflow_rate_per_s", 0.0))
            netflow = float(feat.get("feature_net_flow_rate_per_s", 0.0))
            trend.append({
                "frame_id": fid,
                "timestamp": ts,
                "inflow_rate": round(inflow, 2),
                "outflow_rate": round(outflow, 2),
                "net_flow_rate": round(netflow, 2)
            })
        return trend

    @staticmethod
    def occupancy_trend(analytics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts chronological spatial occupancy ratio time-series."""
        trend = []
        for a in analytics:
            feat = a.get("features", {})
            ts = float(a.get("timestamp", 0.0))
            fid = a.get("frame_id", 0)
            occ = float(feat.get("feature_occupancy_ratio", 0.0))
            trend.append({"frame_id": fid, "timestamp": ts, "occupancy_ratio": round(occ, 4)})
        return trend

    @staticmethod
    def probability_trend(predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts chronological bottleneck hazard probability time-series."""
        trend = []
        for p in predictions:
            ts = float(p.get("timestamp", 0.0))
            fid = p.get("frame_id", 0)
            prob = float(p.get("prediction_probability", 0.0))
            risk = str(p.get("risk_level", "LOW"))
            trend.append({"frame_id": fid, "timestamp": ts, "probability": round(prob, 4), "risk_level": risk})
        return trend

    @staticmethod
    def risk_distribution(predictions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Computes categorical frequency distribution of assigned risk levels."""
        dist = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
        for p in predictions:
            risk = str(p.get("risk_level", "LOW")).upper()
            if risk in dist:
                dist[risk] += 1
            else:
                dist[risk] = 1
        return dist

    @classmethod
    def analyze_trends(
        cls,
        predictions: List[Dict[str, Any]],
        analytics: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Computes complete trend analytics package dictionary."""
        return {
            "risk_distribution": cls.risk_distribution(predictions),
            "density_samples_count": len(analytics),
            "prediction_samples_count": len(predictions),
            "density_trend": cls.density_trend(analytics),
            "probability_trend": cls.probability_trend(predictions),
            "flow_trend": cls.flow_trend(analytics),
            "occupancy_trend": cls.occupancy_trend(analytics)
        }
