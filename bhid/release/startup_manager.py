"""
BHID Operational System Startup Manager.

Orchestrates pre-flight environment checks, platform component initialization,
configuration loading, and startup health reporting.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import time
from bhid.release.release_config import ReleaseConfig
from bhid.release.environment_validator import EnvironmentValidator


class StartupManager:
    """
    System startup orchestrator.
    """

    def __init__(self, config: Optional[ReleaseConfig] = None):
        self.config = config or ReleaseConfig()
        self.env_validator = EnvironmentValidator(config=self.config)
        self.is_initialized: bool = False
        self.startup_timestamp: float = 0.0

    def verify_components(self) -> Dict[str, bool]:
        """Verifies imports of core BHID platform packages."""
        components = {}
        
        comps = [
            ("vision", "bhid.vision"),
            ("analytics", "bhid.analytics"),
            ("prediction", "bhid.prediction"),
            ("events", "bhid.events"),
            ("visualization", "bhid.visualization"),
            ("persistence", "bhid.persistence"),
            ("replay", "bhid.replay"),
            ("reporting", "bhid.reporting"),
            ("validation", "bhid.validation")
        ]

        import importlib
        for name, mod_path in comps:
            try:
                importlib.import_module(mod_path)
                components[name] = True
            except ImportError:
                components[name] = False

        return components

    def load_configuration(self) -> Dict[str, Any]:
        """Loads release configuration build metadata."""
        return self.config.generate_build_metadata()

    def initialize_system(self, project_root: Optional[Path] = None) -> Dict[str, Any]:
        """
        Executes complete pre-flight startup initialization sequence.
        """
        self.startup_timestamp = time.time()
        
        env_res = self.env_validator.validate_environment(project_root=project_root)
        comp_res = self.verify_components()
        config_data = self.load_configuration()

        comp_passed = all(comp_res.values())
        self.is_initialized = env_res["passed"] and comp_passed

        return {
            "status": "INITIALIZED" if self.is_initialized else "STARTUP_FAILED",
            "startup_timestamp": self.startup_timestamp,
            "environment_validation": env_res,
            "component_verification": comp_res,
            "platform_config": config_data
        }

    def startup_summary(self) -> Dict[str, Any]:
        """Returns startup status summary."""
        return {
            "initialized": self.is_initialized,
            "startup_timestamp": self.startup_timestamp,
            "version": self.config.version
        }
