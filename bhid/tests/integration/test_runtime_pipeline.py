"""
End-to-End Integration Test for BHID Runtime Pipeline (Phase 4A).

Validates complete data flow:
Synthetic Feature Stream
      ↓
Window Manager (Pure Rolling Buffer 10s @ 2.5Hz)
      ↓
Prediction Request Payload (14 Frozen Features)
      ↓
Bottleneck Predictor (LightGBM/XGBoost Inference Engine)
      ↓
Prediction Result (Probability, Binary, Risk Level, Horizon Y30)
      ↓
Pipeline Context State Update
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

from bhid.runtime import (
    RuntimeOrchestrator,
    PipelineContext,
    FeatureWindowManager,
    RuntimePredictionRequest,
    RuntimePredictionResult,
    FeatureValidationError,
    FROZEN_FEATURE_NAMES,
)
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestRuntimePipelineIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.context = PipelineContext(active_scene="MADRAS_SCENE_01", active_zone="GATE_4")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

    def generate_synthetic_stream(self, num_samples: int = 30):
        """
        Generates a sequence of 30 synthetic feature snapshots at 2.5Hz (0.4s step).
        Simulates transition from normal crowd flow to bottleneck hazard.
        """
        stream = []
        for i in range(num_samples):
            progress = i / float(num_samples)  # 0.0 to 1.0
            
            # Linearly transition features from low risk to high risk
            feat = {
                "feature_pedestrian_count": 50.0 + (400.0 * progress),
                "feature_density_ped_per_m2": 0.2 + (2.3 * progress),
                "feature_occupancy_ratio": 0.05 + (0.70 * progress),
                "feature_mean_speed_m_s": max(0.1, 1.2 - (1.0 * progress)),
                "feature_velocity_variance": 0.05 + (0.05 * progress),
                "feature_acceleration_m_s2": -0.01 * progress,
                "feature_directional_entropy": 0.20 + (0.75 * progress),
                "feature_inflow_rate_per_s": 0.5 + (2.5 * progress),
                "feature_outflow_rate_per_s": max(0.2, 0.8 - (0.3 * progress)),
                "feature_net_flow_rate_per_s": (0.5 + (2.5 * progress)) - max(0.2, 0.8 - (0.3 * progress)),
                "feature_egress_deficit_ratio": 0.0 + (0.80 * progress),
                "feature_trajectory_convergence": 0.10 + (0.75 * progress),
                "feature_temporal_density_change": 0.01 + (0.85 * progress),
                "feature_temporal_speed_change": -0.45 * progress
            }
            stream.append(feat)
        return stream

    def test_full_pipeline_execution(self):
        stream = self.generate_synthetic_stream(num_samples=30)
        start_ts = 1000.0
        time_step = 0.4  # 2.5Hz update rate

        results = self.orchestrator.process_synthetic_stream(
            sample_stream=stream,
            scene_id="MADRAS_SCENE_01",
            zone_id="GATE_4",
            start_timestamp=start_ts,
            time_step=time_step
        )

        # 1. Verify stream length and result objects
        self.assertEqual(len(results), 30)
        for res in results:
            self.assertIsInstance(res, RuntimePredictionResult)
            self.assertEqual(res.scene_id, "MADRAS_SCENE_01")
            self.assertEqual(res.zone_id, "GATE_4")
            self.assertEqual(res.target_horizon, "Y30")
            self.assertEqual(res.threshold_used, 0.60)
            self.assertIn(res.risk_level, ["LOW", "MODERATE", "HIGH", "CRITICAL"])
            self.assertIn(res.binary_prediction, [0, 1])
            self.assertGreaterEqual(res.prediction_probability, 0.0)
            self.assertLessEqual(res.prediction_probability, 1.0)

        # 2. Verify pure rolling window manager state
        # 30 samples at 0.4s interval span 11.6 seconds (1000.0 to 1011.6)
        # Capacity is 25, window duration is 10.0s
        buffer = self.orchestrator.feature_buffer
        self.assertEqual(buffer.capacity, 25)
        # Samples older than (1011.6 - 10.0 = 1001.6) should be purged
        self.assertLessEqual(buffer.size, 25)
        samples = buffer.get_window_samples()
        self.assertGreaterEqual(samples[0].timestamp, 1001.6)

        # 3. Verify risk progression over time
        initial_prob = results[0].prediction_probability
        final_prob = results[-1].prediction_probability
        self.assertGreater(final_prob, initial_prob, "Risk probability should increase as density escalates")

        # 4. Verify context state tracking
        context_dict = self.orchestrator.context.to_dict()
        self.assertEqual(context_dict["active_scene"], "MADRAS_SCENE_01")
        self.assertEqual(context_dict["active_zone"], "GATE_4")
        self.assertEqual(context_dict["runtime_metadata"]["total_predictions"], 30)
        self.assertEqual(context_dict["runtime_metadata"]["processed_frames"], 30)
        self.assertIsNotNone(context_dict["latest_prediction"])

    def test_pipeline_error_recovery_and_isolation(self):
        """Verify that invalid feature snapshots fail gracefully without corrupting pipeline context."""
        # Process valid sample
        valid_sample = {feat: 0.5 for feat in FROZEN_FEATURE_NAMES}
        res1 = self.orchestrator.process_snapshot(valid_sample, timestamp=100.0)
        self.assertIsNotNone(res1)
        self.assertEqual(self.orchestrator.context.runtime_metadata["total_predictions"], 1)

        # Inject invalid sample
        invalid_sample = valid_sample.copy()
        del invalid_sample["feature_pedestrian_count"]
        with self.assertRaises(FeatureValidationError):
            self.orchestrator.process_snapshot(invalid_sample, timestamp=100.4)

        # Context frame count incremented, but prediction count stayed at 1
        self.assertEqual(self.orchestrator.context.runtime_metadata["total_predictions"], 1)

        # Resume valid sample stream
        res2 = self.orchestrator.process_snapshot(valid_sample, timestamp=100.8)
        self.assertIsNotNone(res2)
        self.assertEqual(self.orchestrator.context.runtime_metadata["total_predictions"], 2)


if __name__ == "__main__":
    unittest.main()
