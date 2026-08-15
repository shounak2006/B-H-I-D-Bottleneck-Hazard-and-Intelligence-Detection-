"""
Unit tests for BHID ReportingValidator (Phase 5D).

Validates:
1. Report KPI accuracy verification against source session data
2. Markdown report formatting structure
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

from bhid.validation import ReportingValidator


class TestReportingValidator(unittest.TestCase):

    def test_reporting_validation(self):
        preds = [{"prediction_probability": 0.85}]
        analytics = [{"features": {"feature_pedestrian_count": 20, "feature_density_ped_per_m2": 0.2}}]
        events = []

        report_dict = {
            "session_id": "S1",
            "kpi_summary": {
                "peak_pedestrian_count": 20,
                "peak_density_ped_per_m2": 0.2,
                "peak_prediction_probability": 0.85,
                "total_hazard_events": 0,
                "resolved_hazard_events": 0
            }
        }
        md_text = "# BHID Operational Intelligence Report - Session `S1`"

        res = ReportingValidator.validate_reporting(report_dict, preds, analytics, events, md_text)
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 100.0)


if __name__ == "__main__":
    unittest.main()
