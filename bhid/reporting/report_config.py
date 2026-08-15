"""
BHID Operational Reporting Configuration.

Defines report output paths, multi-format export toggles (JSON, CSV, Markdown),
timestamp formatting strings, and output directory resolution helpers.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import time


@dataclass
class ReportConfig:
    """
    Central reporting configuration.
    
    Attributes:
        report_output_directory: Directory path where generated reports are saved.
        export_json_enabled: Whether JSON report exports are enabled.
        export_csv_enabled: Whether CSV report exports are enabled.
        export_markdown_enabled: Whether Markdown report exports are enabled.
        report_timestamp_format: Timestamp formatting string.
        default_reporting_window: Reporting window descriptor ('ALL', 'LAST_HOUR', etc.).
    """
    report_output_directory: Path = field(default_factory=lambda: Path("bhid/reports"))
    export_json_enabled: bool = True
    export_csv_enabled: bool = True
    export_markdown_enabled: bool = True
    report_timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    default_reporting_window: str = "ALL"

    def __post_init__(self):
        if isinstance(self.report_output_directory, str):
            self.report_output_directory = Path(self.report_output_directory)

    def initialize_directories(self) -> bool:
        """Creates report output directory if missing."""
        try:
            self.report_output_directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def generate_report_path(self, session_id: str, extension: str = "md") -> Path:
        """Generates full output file path for a session report."""
        ext = extension.lstrip(".")
        filename = f"report_{session_id}.{ext}"
        return self.report_output_directory / filename
