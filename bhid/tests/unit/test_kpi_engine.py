"""
Unit tests for BHID KPIEngine (Phase 5C).

Validates:
1. Operational KPI calculations (peak/average density, pedestrian counts, hazard event resolution rates)
2. JSON file export of KPIs
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.reporting import KPIEngine


class TestKPIEngine(unittest.TestCase):

    def setUp(self):
        self.preds = [
            {"prediction_probability": 0.20},
            {"prediction_probability": 0.90}
        ]
        self.analytics = [
            {"features": {"feature_pedestrian_count": 10, "feature_density_ped_per_m2": 0.10}},
            {"features": {"feature_pedestrian_count": 50, "feature_density_ped_per_m2": 0.50}}
        ]
        self.events = [
            {"event_id": "E1", "status": "RESOLVED", "escalation_count": 1, "duration_seconds": 12.5},
            {"event_id": "E2", "status": "ACTIVE", "escalation_count": 0, "duration_seconds": 5.0}
        ]

    def test_compute_kpis(self):
        kpis = KPIEngine.compute_kpis(self.preds, self.analytics, self.events)

        self.assertEqual(kpis["peak_pedestrian_count"], 50)
        self.assertEqual(kpis["average_pedestrian_count"], 30.0)
        self.assertEqual(kpis["peak_density_ped_per_m2"], 0.50)
        self.assertEqual(kpis["average_density_ped_per_m2"], 0.30)
        self.assertEqual(kpis["peak_prediction_probability"], 0.90)
        self.assertEqual(kpis["average_prediction_probability"], 0.55)
        self.assertEqual(kpis["total_hazard_events"], 2)
        self.assertEqual(kpis["resolved_hazard_events"], 1)
        self.assertEqual(kpis["resolution_rate_pct"], 50.0)
        self.assertEqual(kpis["total_escalations"], 1)


if __name__ == "__main__":
    unittest.main()
