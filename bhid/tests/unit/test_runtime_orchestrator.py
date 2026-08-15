"""
Unit tests for BHID Runtime Orchestrator (Phase 4A).

Validates:
1. Orchestrator initialization with Phase 3D Bottleneck Predictor
2. Single snapshot processing & runtime request payload generation
3. Prediction result generation & risk level classification
4. Pipeline context state updates (active scene/zone, timestamp, bottleneck risk state)
5. Synthetic stream execution
6. Invalid feature schema & prediction error handling
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.runtime.runtime_orchestrator import RuntimeOrchestrator
from bhid.runtime.pipeline_context import PipelineContext
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.runtime.exceptions import FeatureValidationError
from bhid.runtime.feature_schema import FROZEN_FEATURE_NAMES
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestRuntimeOrchestrator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()
        cls.sample_low_risk = {
            "feature_pedestrian_count": 50.0,
            "feature_density_ped_per_m2": 0.2,
            "feature_occupancy_ratio": 0.05,
            "feature_mean_speed_m_s": 1.20,
            "feature_velocity_variance": 0.05,
            "feature_acceleration_m_s2": 0.01,
            "feature_directional_entropy": 0.20,
            "feature_inflow_rate_per_s": 0.5,
            "feature_outflow_rate_per_s": 0.5,
            "feature_net_flow_rate_per_s": 0.0,
            "feature_egress_deficit_ratio": 0.0,
            "feature_trajectory_convergence": 0.10,
            "feature_temporal_density_change": 0.01,
            "feature_temporal_speed_change": 0.00
        }
        cls.sample_high_risk = {
            "feature_pedestrian_count": 450.0,
            "feature_density_ped_per_m2": 2.5,
            "feature_occupancy_ratio": 0.75,
            "feature_mean_speed_m_s": 0.25,
            "feature_velocity_variance": 0.08,
            "feature_acceleration_m_s2": -0.02,
            "feature_directional_entropy": 0.95,
            "feature_inflow_rate_per_s": 3.0,
            "feature_outflow_rate_per_s": 0.5,
            "feature_net_flow_rate_per_s": 2.5,
            "feature_egress_deficit_ratio": 0.83,
            "feature_trajectory_convergence": 0.85,
            "feature_temporal_density_change": 0.90,
            "feature_temporal_speed_change": -0.50
        }

    def setUp(self):
        self.context = PipelineContext(active_scene="TEST_SCENE", active_zone="ZONE_A")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

    def test_initialization(self):
        self.assertIsNotNone(self.orchestrator.predictor)
        self.assertEqual(self.orchestrator.context.active_scene, "TEST_SCENE")
        self.assertEqual(self.orchestrator.feature_buffer.size, 0)

    def test_process_snapshot_low_risk(self):
        res = self.orchestrator.process_snapshot(
            features=self.sample_low_risk,
            timestamp=1000.0,
            scene_id="SCENE_01",
            zone_id="GATE_A"
        )

        self.assertIsInstance(res, RuntimePredictionResult)
        self.assertEqual(res.scene_id, "SCENE_01")
        self.assertEqual(res.zone_id, "GATE_A")
        self.assertEqual(res.timestamp, 1000.0)
        self.assertIn("prediction_probability", res.to_dict())
        self.assertEqual(res.target_horizon, "Y30")
        self.assertEqual(res.threshold_used, 0.60)

        # Context updates
        ctx_dict = self.orchestrator.context.to_dict()
        self.assertEqual(ctx_dict["active_scene"], "SCENE_01")
        self.assertEqual(ctx_dict["active_zone"], "GATE_A")
        self.assertEqual(ctx_dict["buffer_size"], 1)
        self.assertEqual(ctx_dict["runtime_metadata"]["total_predictions"], 1)

    def test_process_snapshot_high_risk(self):
        res = self.orchestrator.process_snapshot(
            features=self.sample_high_risk,
            timestamp=1005.0,
            scene_id="SCENE_CROWD",
            zone_id="ZONE_BTL"
        )

        self.assertIsInstance(res, RuntimePredictionResult)
        self.assertGreaterEqual(res.prediction_probability, 0.0)
        self.assertIn(res.risk_level, ["LOW", "MODERATE", "HIGH", "CRITICAL"])
        
        ctx = self.orchestrator.get_context()
        self.assertIn(ctx.bottleneck_state, ["LOW", "MODERATE", "HIGH", "CRITICAL"])

    def test_process_synthetic_stream(self):
        stream = [self.sample_low_risk] * 10
        results = self.orchestrator.process_synthetic_stream(
            sample_stream=stream,
            scene_id="SYNTH_01",
            zone_id="ZONE_01",
            start_timestamp=100.0,
            time_step=0.4
        )

        self.assertEqual(len(results), 10)
        self.assertEqual(self.orchestrator.feature_buffer.size, 10)
        self.assertEqual(self.orchestrator.context.runtime_metadata["total_predictions"], 10)
        self.assertAlmostEqual(results[-1].timestamp, 103.6, places=5)

    def test_schema_validation_failure(self):
        invalid_sample = {"feature_pedestrian_count": 10.0}
        with self.assertRaises(FeatureValidationError):
            self.orchestrator.process_snapshot(features=invalid_sample, timestamp=100.0)


if __name__ == "__main__":
    unittest.main()
