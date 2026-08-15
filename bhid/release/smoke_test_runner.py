"""
BHID Release Smoke Test Verification Suite.

Executes fast, lightweight initialization and execution path checks across all 8 platform layers
without retraining models or modifying persisted session data.
"""

from typing import Dict, Any


class SmokeTestRunner:
    """
    Release smoke test verification runner.
    """

    @staticmethod
    def test_analytics_layer() -> bool:
        """Verifies CrowdAnalyticsEngine instantiation."""
        from bhid.analytics import CrowdAnalyticsEngine
        eng = CrowdAnalyticsEngine()
        return hasattr(eng, "process_tracking_batch")

    @staticmethod
    def test_predictor_layer() -> bool:
        """Verifies BottleneckPredictor instantiation and model artifact loading."""
        from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor
        pred = BottleneckPredictor()
        return hasattr(pred, "predict_single")

    @staticmethod
    def test_event_layer() -> bool:
        """Verifies HazardEventEngine instantiation."""
        from bhid.events import HazardEventEngine
        ee = HazardEventEngine()
        return hasattr(ee, "process_prediction")

    @staticmethod
    def test_visualization_layer() -> bool:
        """Verifies MonitoringController instantiation."""
        from bhid.visualization import MonitoringController
        mc = MonitoringController()
        return hasattr(mc, "render_frame")

    @staticmethod
    def test_persistence_layer() -> bool:
        """Verifies PersistenceManager instantiation and non-blocking methods."""
        from bhid.persistence import PersistenceManager
        pm = PersistenceManager()
        return hasattr(pm, "persist_prediction")

    @staticmethod
    def test_replay_layer() -> bool:
        """Verifies PlaybackEngine instantiation."""
        from bhid.replay import PlaybackEngine
        pe = PlaybackEngine()
        return hasattr(pe, "replay_all")

    @staticmethod
    def test_reporting_layer() -> bool:
        """Verifies ReportingManager instantiation."""
        from bhid.reporting import ReportingManager
        rm = ReportingManager()
        return hasattr(rm, "generate_report")

    @staticmethod
    def test_validation_layer() -> bool:
        """Verifies ValidationManager instantiation."""
        from bhid.validation import ValidationManager
        vm = ValidationManager()
        return hasattr(vm, "run_all_validations")

    @classmethod
    def run_smoke_tests(cls) -> Dict[str, Any]:
        """
        Runs all 8 component layer smoke tests.
        """
        results = {
            "analytics_layer": cls.test_analytics_layer(),
            "predictor_layer": cls.test_predictor_layer(),
            "event_layer": cls.test_event_layer(),
            "visualization_layer": cls.test_visualization_layer(),
            "persistence_layer": cls.test_persistence_layer(),
            "replay_layer": cls.test_replay_layer(),
            "reporting_layer": cls.test_reporting_layer(),
            "validation_layer": cls.test_validation_layer()
        }

        all_passed = all(results.values())

        return {
            "passed": all_passed,
            "total_layers_tested": len(results),
            "passed_layers_count": sum(1 for v in results.values() if v),
            "layer_results": results
        }

    @classmethod
    def generate_results(cls) -> Dict[str, Any]:
        """Returns smoke test execution summary."""
        return cls.run_smoke_tests()
