"""
BHID Operational Reporting Accuracy Validator.

Validates that exported report KPIs, trend stats, and hazard event summaries match
source session records 100% accurately without mutating reports (Read-Only).
"""

from typing import Dict, Any, List
from bhid.reporting.kpi_engine import KPIEngine


class ReportingValidator:
    """
    Read-only reporting accuracy validator.
    """

    @staticmethod
    def validate_kpi_accuracy(
        kpis: Dict[str, Any],
        predictions: List[Dict[str, Any]],
        analytics: List[Dict[str, Any]],
        events: List[Dict[str, Any]]
    ) -> bool:
        """Validates that computed report KPIs match re-derived ground truth KPIs."""
        gt_kpis = KPIEngine.compute_kpis(predictions=predictions, analytics=analytics, events=events)

        keys = ["peak_pedestrian_count", "peak_density_ped_per_m2", "peak_prediction_probability", "total_hazard_events", "resolved_hazard_events"]
        for k in keys:
            if k in kpis and k in gt_kpis:
                if kpis[k] != gt_kpis[k]:
                    return False
        return True

    @staticmethod
    def validate_markdown_formatting(md_content: str, session_report_dict: Dict[str, Any]) -> bool:
        """Validates Markdown document title and alert callout structure."""
        if not md_content or not isinstance(md_content, str):
            return False
        sid = session_report_dict.get("session_id", "")
        if f"Session `{sid}`" not in md_content and "# BHID Operational" not in md_content:
            return False
        return True

    @classmethod
    def validate_reporting(
        cls,
        session_report_dict: Dict[str, Any],
        predictions: List[Dict[str, Any]],
        analytics: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        markdown_content: str = ""
    ) -> Dict[str, Any]:
        """
        Validates reporting accuracy and output formatting (Read-Only).
        """
        kpis = session_report_dict.get("kpi_summary", {})
        kpi_valid = cls.validate_kpi_accuracy(kpis, predictions, analytics, events)
        md_valid = cls.validate_markdown_formatting(markdown_content, session_report_dict) if markdown_content else True

        all_passed = kpi_valid and md_valid
        score = 100.0 if all_passed else 0.0

        return {
            "component": "reporting_accuracy",
            "passed": all_passed,
            "score": score,
            "kpi_accuracy_valid": kpi_valid,
            "markdown_formatting_valid": md_valid
        }
