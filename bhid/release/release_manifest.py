"""
BHID Release Manifest Builder & System Inventory Generator.

Auto-discovers platform Python modules, unit/integration test suites, and Markdown
documentation specifications to build `release_manifest.json`.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from bhid.release.release_config import ReleaseConfig


class ReleaseManifest:
    """
    Release manifest builder using dynamic filesystem auto-discovery.
    """

    def __init__(self, config: Optional[ReleaseConfig] = None):
        self.config = config or ReleaseConfig()

    @staticmethod
    def discover_modules(project_root: Optional[Path] = None) -> List[str]:
        """Auto-discovers Python `.py` source files in the bhid package."""
        root = Path(project_root) if project_root else Path(__file__).resolve().parent.parent.parent
        bhid_dir = root / "bhid"
        if not bhid_dir.exists():
            return []
        
        modules = []
        for p in bhid_dir.rglob("*.py"):
            if "tests" not in p.parts:
                rel = p.relative_to(root)
                modules.append(str(rel).replace("\\", "/"))
        return sorted(modules)

    @staticmethod
    def discover_tests(project_root: Optional[Path] = None) -> List[str]:
        """Auto-discovers Python test files under bhid/tests."""
        root = Path(project_root) if project_root else Path(__file__).resolve().parent.parent.parent
        tests_dir = root / "bhid" / "tests"
        if not tests_dir.exists():
            return []

        tests = []
        for p in tests_dir.rglob("test_*.py"):
            rel = p.relative_to(root)
            tests.append(str(rel).replace("\\", "/"))
        return sorted(tests)

    @staticmethod
    def discover_docs(project_root: Optional[Path] = None) -> List[str]:
        """Auto-discovers Markdown documentation files under bhid/docs."""
        root = Path(project_root) if project_root else Path(__file__).resolve().parent.parent.parent
        docs = []

        # Check bhid/docs
        docs_dir = root / "bhid" / "docs"
        if docs_dir.exists():
            for p in docs_dir.rglob("*.md"):
                rel = p.relative_to(root)
                docs.append(str(rel).replace("\\", "/"))

        # Check root level guides
        for guide in ["INSTALLATION.md", "OPERATOR_GUIDE.md", "README.md"]:
            if (root / guide).exists():
                docs.append(guide)

        return sorted(docs)

    def generate_manifest(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Generates complete release manifest inventory dictionary.
        """
        build_meta = self.config.generate_build_metadata()
        modules = self.discover_modules(project_root)
        tests = self.discover_tests(project_root)
        docs = self.discover_docs(project_root)

        return {
            "release_info": build_meta,
            "system_capabilities": [
                "Vision Pedestrian Detection (Mock & Adapters)",
                "Centroid Multi-Object Association & Trajectory Generation",
                "14 Spatiotemporal Feature Extraction Engine",
                "10s @ 2.5Hz Feature Window Manager",
                "LightGBM & XGBoost Optimization Engine (Y30 Horizon, Threshold 0.60)",
                "Hazard Event Engine (Active Registry, Escalation, Resolution)",
                "OpenCV Visualization & Monitoring Telemetry Layer",
                "Non-Blocking Data Persistence & Audit Storage Layer (Phase 5A)",
                "Deterministic Historical Playback & Replay Engine (Phase 5B)",
                "Operational Reporting & Comparative Analytics Layer (Phase 5C)",
                "Read-Only Operational Validation & System Readiness Evaluator (Phase 5D)",
                "Pre-Flight Environment Validation & Release Packaging (Phase 6A)"
            ],
            "inventory": {
                "source_modules_count": len(modules),
                "source_modules": modules,
                "test_suites_count": len(tests),
                "test_suites": tests,
                "documentation_files_count": len(docs),
                "documentation_files": docs
            }
        }

    def export_manifest(self, output_dir: Optional[Path] = None, project_root: Optional[Path] = None) -> Optional[Path]:
        """Exports `release_manifest.json` to specified output directory."""
        try:
            target_dir = Path(output_dir) if output_dir else self.config.release_output_directory
            target_dir.mkdir(parents=True, exist_ok=True)
            manifest_file = target_dir / "release_manifest.json"

            data = self.generate_manifest(project_root)
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return manifest_file
        except Exception:
            return None
