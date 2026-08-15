"""
BHID Multi-Format Report Generator Engine.

Exports SessionReport and comparative benchmarking analytics into JSON, CSV, and Markdown formats.
"""

from typing import Dict, Any, List, Optional
import json
import csv
from pathlib import Path
from bhid.reporting.report_config import ReportConfig
from bhid.reporting.session_report import SessionReport


class ReportGenerator:
    """
    Multi-format report export engine.
    
    Parameters:
        config: Optional ReportConfig instance.
    """

    def __init__(self, config: Optional[ReportConfig] = None):
        self.config = config or ReportConfig()
        self.config.initialize_directories()

    def export_json(self, session_report: SessionReport, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports session report dictionary to JSON file."""
        try:
            if not self.config.export_json_enabled:
                return None
            out_file = file_path or self.config.generate_report_path(session_report.session_id, "json")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(session_report.to_dict(), f, indent=2)
            return out_file
        except Exception:
            return None

    def export_csv(self, session_report: SessionReport, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports session report KPIs to CSV file."""
        try:
            if not self.config.export_csv_enabled:
                return None
            out_file = file_path or self.config.generate_report_path(session_report.session_id, "csv")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            kpis = dict(session_report.kpi_summary)
            kpis["session_id"] = session_report.session_id
            kpis["scene_id"] = session_report.scene_id
            kpis["zone_id"] = session_report.zone_id

            headers = list(kpis.keys())
            with open(out_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerow(kpis)
            return out_file
        except Exception:
            return None

    def export_markdown(self, session_report: SessionReport, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports session report to formatted Markdown document."""
        try:
            if not self.config.export_markdown_enabled:
                return None
            out_file = file_path or self.config.generate_report_path(session_report.session_id, "md")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            md_content = session_report.to_markdown()
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            return out_file
        except Exception:
            return None

    def generate_comparative_markdown(
        self,
        comparative_data: Dict[str, Any],
        file_path: Optional[Path] = None
    ) -> Optional[Path]:
        """Exports comparative cross-session analysis report to Markdown file."""
        try:
            if not self.config.export_markdown_enabled:
                return None
            out_file = file_path or (self.config.report_output_directory / "report_comparative_summary.md")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            md = []
            md.append("# BHID Cross-Session Comparative Analytics Report\n")
            md.append(f"**Total Sessions Benchmarked**: `{comparative_data.get('total_sessions_analyzed', 0)}`\n")
            md.append("---\n")

            dens = comparative_data.get("density_comparison", [])
            if dens:
                md.append("## Crowd Density Rankings across Sessions\n")
                md.append("| Rank | Session ID | Scene ID | Zone ID | Peak Density (ped/m²) | Avg Density | Peak Peds |")
                md.append("|---|---|---|---|---|---|---|")
                for idx, r in enumerate(dens, 1):
                    md.append(f"| {idx} | `{r['session_id']}` | `{r['scene_id']}` | `{r['zone_id']}` | `{r['peak_density_ped_per_m2']:.2f}` | `{r['average_density_ped_per_m2']:.2f}` | `{r['peak_pedestrian_count']}` |")
                md.append("\n")

            with open(out_file, "w", encoding="utf-8") as f:
                f.write("\n".join(md))
            return out_file
        except Exception:
            return None
