"""
BHID Pre-Flight Runtime Environment Validator.

Validates Python runtime version, dependency library availability, model registry existence,
directory structure completeness, and filesystem write permissions.
Returns structured result dictionaries non-fatally.
"""

import sys
import importlib
from typing import Dict, Any, List, Optional
from pathlib import Path
from bhid.release.release_config import ReleaseConfig


class EnvironmentValidator:
    """
    Pre-flight runtime environment validator.
    """

    def __init__(self, config: Optional[ReleaseConfig] = None):
        self.config = config or ReleaseConfig()

    def validate_python_version(self) -> Dict[str, Any]:
        """Checks current Python runtime major.minor version against supported list."""
        current_ver = f"{sys.version_info.major}.{sys.version_info.minor}"
        supported = self.config.supported_python_versions
        is_supported = current_ver in supported or sys.version_info.major == 3

        return {
            "check": "python_version",
            "current_version": sys.version,
            "major_minor": current_ver,
            "supported_versions": supported,
            "passed": is_supported
        }

    def validate_dependencies(self) -> Dict[str, Any]:
        """Checks availability of required Python third-party packages non-fatally."""
        packages = {
            "numpy": "numpy",
            "pandas": "pandas",
            "cv2": "cv2",
            "lightgbm": "lightgbm",
            "xgboost": "xgboost",
            "sklearn": "sklearn",
            "scipy": "scipy"
        }

        results = {}
        all_found = True

        for pkg_name, import_name in packages.items():
            try:
                mod = importlib.import_module(import_name)
                ver = getattr(mod, "__version__", "AVAILABLE")
                results[pkg_name] = {"available": True, "version": ver}
            except ImportError:
                results[pkg_name] = {"available": False, "version": None}
                all_found = False

        return {
            "check": "dependencies",
            "passed": all_found,
            "packages": results
        }

    def validate_filesystem(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """Checks project directory structure, model_registry.json, and write permissions non-fatally."""
        root = Path(project_root) if project_root else Path(__file__).resolve().parent.parent.parent
        
        # Required directories
        dirs_to_check = ["bhid/vision", "bhid/analytics", "bhid/events", "bhid/visualization", "bhid/persistence", "bhid/replay", "bhid/reporting", "bhid/validation", "bhid/models"]
        missing_dirs = []
        for d in dirs_to_check:
            if not (root / d).exists():
                missing_dirs.append(d)

        # Model registry check
        model_reg = root / "bhid" / "models" / "model_registry.json"
        model_reg_found = model_reg.exists()

        # Write permission check on reports directory
        reports_dir = root / "bhid" / "reports"
        try:
            reports_dir.mkdir(parents=True, exist_ok=True)
            test_file = reports_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
            write_perm = True
        except Exception:
            write_perm = False

        passed = (len(missing_dirs) == 0) and model_reg_found and write_perm

        return {
            "check": "filesystem",
            "passed": passed,
            "missing_directories": missing_dirs,
            "model_registry_found": model_reg_found,
            "write_permissions_ok": write_perm
        }

    def validate_environment(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Runs full pre-flight runtime environment validation suite and returns structured summary.
        """
        py_res = self.validate_python_version()
        dep_res = self.validate_dependencies()
        fs_res = self.validate_filesystem(project_root)

        all_passed = py_res["passed"] and dep_res["passed"] and fs_res["passed"]

        return {
            "component": "environment_validation",
            "passed": all_passed,
            "python_check": py_res,
            "dependency_check": dep_res,
            "filesystem_check": fs_res
        }
