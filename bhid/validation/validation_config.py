"""
BHID Operational Validation Configuration.

Defines validation output paths, tolerance parameters, component evaluation weights,
and output directory resolution helpers.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ValidationConfig:
    """
    Central validation configuration.
    
    Attributes:
        validation_output_directory: Directory path for exported validation reports.
        export_json_enabled: Whether validation_report.json export is enabled.
        export_markdown_enabled: Whether validation_report.md export is enabled.
        readiness_pass_threshold: Minimum composite score percentage required for PASSED status (default: 95.0%).
        probability_tolerance: Numerical tolerance for prediction probability checks (0.0).
        feature_tolerance: Numerical tolerance for 14-feature vector checks (0.0).
        component_weights: Explicit weights for operational readiness score computation (Sum = 1.0).
    """
    validation_output_directory: Path = field(default_factory=lambda: Path("bhid/reports/validation"))
    export_json_enabled: bool = True
    export_markdown_enabled: bool = True
    readiness_pass_threshold: float = 95.0
    probability_tolerance: float = 0.0
    feature_tolerance: float = 0.0
    component_weights: Dict[str, float] = field(default_factory=lambda: {
        "schema_consistency": 0.15,
        "prediction_integrity": 0.20,
        "event_lifecycle": 0.20,
        "persistence_isolation": 0.15,
        "replay_determinism": 0.15,
        "reporting_accuracy": 0.15
    })

    def __post_init__(self):
        if isinstance(self.validation_output_directory, str):
            self.validation_output_directory = Path(self.validation_output_directory)

    def initialize_directories(self) -> bool:
        """Creates validation output directory if missing."""
        try:
            self.validation_output_directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def generate_validation_path(self, filename: str) -> Path:
        """Generates full output file path for validation reports."""
        return self.validation_output_directory / filename
