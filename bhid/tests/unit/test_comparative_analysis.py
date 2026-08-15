"""
Unit tests for BHID ComparativeAnalysis (Phase 5C).

Validates:
1. Multi-session density & event frequency comparisons
2. Peak operational session identification
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

from bhid.reporting import SessionReport, ComparativeAnalysis


class TestComparativeAnalysis(unittest.TestCase):

    def setUp(self):
        r1 = SessionReport(
            session_id="SESS_A", scene_id="S1", zone_id="Z1",
            kpi_summary={"peak_density_ped_per_m2": 0.40, "total_hazard_events": 1, "peak_prediction_probability": 0.70}
        )
        r2 = SessionReport(
            session_id="SESS_B", scene_id="S1", zone_id="Z2",
            kpi_summary={"peak_density_ped_per_m2": 0.85, "total_hazard_events": 5, "peak_prediction_probability": 0.95}
        )
        self.reports = [r1, r2]

    def test_comparative_analysis(self):
        comp = ComparativeAnalysis.compare_sessions(self.reports)
        self.assertEqual(comp["total_sessions_analyzed"], 2)

        dens_comp = comp["density_comparison"]
        self.assertEqual(dens_comp[0]["session_id"], "SESS_B")
        self.assertEqual(dens_comp[0]["peak_density_ped_per_m2"], 0.85)

        peaks = comp["peaks_summary"]
        self.assertEqual(peaks["highest_density_session"]["session_id"], "SESS_B")
        self.assertEqual(peaks["highest_event_session"]["session_id"], "SESS_B")


if __name__ == "__main__":
    unittest.main()
