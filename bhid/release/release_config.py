"""
BHID Operational Release Configuration & Version Metadata.

Defines platform release version string, system identifiers, supported Python versions,
minimum dependency specifications, and release artifact export directory resolution helpers.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import json


@dataclass
class ReleaseConfig:
    """
    Central release configuration.
    
    Attributes:
        system_name: Platform title string.
        version: Platform release semantic version string (1.0.0).
        release_type: Release classification tag (STABLE_RELEASE).
        build_timestamp: Epoch timestamp release was compiled.
        release_output_directory: Directory path for exported release artifacts.
        supported_python_versions: List of supported Python major.minor version strings.
        minimum_requirements: Core dependency minimum version requirements.
    """
    system_name: str = "BHID - Bottleneck Hazard & Intelligence Detection"
    version: str = "1.0.0"
    release_type: str = "STABLE_RELEASE"
    build_timestamp: float = field(default_factory=lambda: time.time())
    release_output_directory: Path = field(default_factory=lambda: Path("bhid/reports/release"))
    supported_python_versions: List[str] = field(default_factory=lambda: ["3.9", "3.10", "3.11", "3.12"])
    minimum_requirements: Dict[str, str] = field(default_factory=lambda: {
        "numpy": "1.20.0",
        "pandas": "1.3.0",
        "opencv-python": "4.5.0",
        "lightgbm": "3.2.0",
        "xgboost": "1.4.0",
        "scikit-learn": "0.24.0",
        "scipy": "1.7.0"
    })

    def __post_init__(self):
        if isinstance(self.release_output_directory, str):
            self.release_output_directory = Path(self.release_output_directory)

    def initialize_directories(self) -> bool:
        """Creates release output directory if missing."""
        try:
            self.release_output_directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def generate_build_metadata(self) -> Dict[str, Any]:
        """Generates release build metadata dictionary."""
        return {
            "system_name": self.system_name,
            "version": self.version,
            "release_type": self.release_type,
            "build_timestamp": self.build_timestamp,
            "build_date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.build_timestamp)),
            "supported_python_versions": list(self.supported_python_versions),
            "minimum_requirements": dict(self.minimum_requirements)
        }

    def export_release_info(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports build metadata dictionary to JSON file."""
        try:
            self.initialize_directories()
            out_file = file_path or (self.release_output_directory / "release_info.json")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(self.generate_build_metadata(), f, indent=2)
            return out_file
        except Exception:
            return None
