"""
BHID Primary Release Packaging Manager.

Coordinates pre-flight environment checks, component smoke testing, release manifest building,
and release artifact exports in a dedicated release directory (`bhid/reports/release`).
"""

from typing import Dict, Any, Optional
import time
from pathlib import Path

from bhid.release.release_config import ReleaseConfig
from bhid.release.environment_validator import EnvironmentValidator
from bhid.release.startup_manager import StartupManager
from bhid.release.smoke_test_runner import SmokeTestRunner
from bhid.release.release_manifest import ReleaseManifest


class PackagingManager:
    """
    Primary release packaging and release readiness coordinator.
    """

    def __init__(self, config: Optional[ReleaseConfig] = None):
        self.config = config or ReleaseConfig()
        self.config.initialize_directories()
        self.env_validator = EnvironmentValidator(config=self.config)
        self.manifest_builder = ReleaseManifest(config=self.config)

    def run_release_checks(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """Runs pre-release environment validation and component smoke tests."""
        env_res = self.env_validator.validate_environment(project_root)
        smoke_res = SmokeTestRunner.run_smoke_tests()

        ready = env_res["passed"] and smoke_res["passed"]

        return {
            "release_ready": ready,
            "environment_validation": env_res,
            "smoke_tests": smoke_res
        }

    def export_release_artifacts(self, project_root: Optional[Path] = None) -> Dict[str, Optional[Path]]:
        """
        Exports `release_info.json` and `release_manifest.json` into dedicated release directory.
        """
        out_dir = self.config.release_output_directory
        out_dir.mkdir(parents=True, exist_ok=True)

        info_path = self.config.export_release_info(out_dir / "release_info.json")
        manifest_path = self.manifest_builder.export_manifest(output_dir=out_dir, project_root=project_root)

        return {
            "release_info_json": info_path,
            "release_manifest_json": manifest_path
        }

    def generate_release_bundle(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Builds full release summary bundle.
        """
        checks = self.run_release_checks(project_root)
        manifest = self.manifest_builder.generate_manifest(project_root)
        artifacts = self.export_release_artifacts(project_root)

        return {
            "status": "RELEASE_READY" if checks["release_ready"] else "RELEASE_BLOCKED",
            "release_info": self.config.generate_build_metadata(),
            "pre_release_checks": checks,
            "manifest_summary": {
                "modules_count": manifest["inventory"]["source_modules_count"],
                "test_suites_count": manifest["inventory"]["test_suites_count"],
                "docs_count": manifest["inventory"]["documentation_files_count"]
            },
            "exported_artifacts": {k: str(v) for k, v in artifacts.items() if v is not None}
        }

    def build_release(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """Alias for generate_release_bundle."""
        return self.generate_release_bundle(project_root)
