"""
Unit tests for BHID TrendAnalyzer (Phase 5C).

Validates:
1. Density, flow, occupancy, and risk probability time-series extractions
2. Categorical risk distribution calculations
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.reporting import TrendAnalyzer


class TestTrendAnalyzer(unittest.TestCase):

    def setUp(self):
        self.preds = [
            {"frame_id": 1, "timestamp": 1.0, "prediction_probability": 0.10, "risk_level": "LOW"},
            {"frame_id": 2, "timestamp": 2.0, "prediction_probability": 0.70, "risk_level": "HIGH"},
            {"frame_id": 3, "timestamp": 3.0, "prediction_probability": 0.90, "risk_level": "CRITICAL"}
        ]
        self.analytics = [
            {"frame_id": 1, "timestamp": 1.0, "features": {"feature_density_ped_per_m2": 0.1, "feature_inflow_rate_per_s": 5.0, "feature_outflow_rate_per_s": 0.0, "feature_net_flow_rate_per_s": 5.0, "feature_occupancy_ratio": 0.1}},
            {"frame_id": 2, "timestamp": 2.0, "features": {"feature_density_ped_per_m2": 0.5, "feature_inflow_rate_per_s": 15.0, "feature_outflow_rate_per_s": 0.0, "feature_net_flow_rate_per_s": 15.0, "feature_occupancy_ratio": 0.5}}
        ]

    def test_trend_extraction(self):
        dist = TrendAnalyzer.risk_distribution(self.preds)
        self.assertEqual(dist["LOW"], 1)
        self.assertEqual(dist["HIGH"], 1)
        self.assertEqual(dist["CRITICAL"], 1)

        d_trend = TrendAnalyzer.density_trend(self.analytics)
        self.assertEqual(len(d_trend), 2)
        self.assertEqual(d_trend[1]["density_ped_per_m2"], 0.5)

        p_trend = TrendAnalyzer.probability_trend(self.preds)
        self.assertEqual(len(p_trend), 3)
        self.assertEqual(p_trend[2]["probability"], 0.90)


if __name__ == "__main__":
    unittest.main()
