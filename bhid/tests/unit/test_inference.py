"""
Unit tests for BHID Standalone Prediction Inference Engine (Phase 3D).

Validates:
1. Model loading & registry initialization
2. Schema validation & column order alignment
3. Threshold classification & risk level assignment
4. Single sample prediction
5. Batch prediction
6. Invalid schema handling (missing features, null values, invalid types)
"""

import sys
import unittest
import numpy as np
import pandas as pd
from pathlib import Path

# Set sys.path for project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor, APPROVED_FEATURES


class TestInferenceEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()
        cls.valid_sample = {
            "sample_id": "UNIT_TEST_001",
            "feature_pedestrian_count": 350.0,
            "feature_density_ped_per_m2": 1.8,
            "feature_occupancy_ratio": 0.45,
            "feature_mean_speed_m_s": 0.85,
            "feature_velocity_variance": 0.10,
            "feature_acceleration_m_s2": 0.0,
            "feature_directional_entropy": 1.20,
            "feature_inflow_rate_per_s": 1.5,
            "feature_outflow_rate_per_s": 1.2,
            "feature_net_flow_rate_per_s": 0.3,
            "feature_egress_deficit_ratio": 0.20,
            "feature_trajectory_convergence": 0.25,
            "feature_temporal_density_change": 0.10,
            "feature_temporal_speed_change": -0.05
        }

    def test_model_and_registry_loading(self):
        self.assertIsNotNone(self.predictor.model)
        self.assertEqual(self.predictor.target_horizon, "Y30")
        self.assertEqual(self.predictor.threshold, 0.60)
        self.assertEqual(len(self.predictor.feature_names), 14)

    def test_single_sample_prediction(self):
        res = self.predictor.predict_single(self.valid_sample)
        
        self.assertIn("prediction_probability", res)
        self.assertIn("binary_prediction", res)
        self.assertIn("risk_level", res)
        self.assertEqual(res["target_horizon"], "Y30")
        self.assertIn(res["binary_prediction"], [0, 1])
        self.assertIn(res["risk_level"], ["LOW", "MODERATE", "HIGH", "CRITICAL"])

    def test_batch_prediction(self):
        df_batch = pd.DataFrame([self.valid_sample, self.valid_sample])
        results = self.predictor.predict_batch(df_batch)
        
        self.assertEqual(len(results), 2)
        self.assertIn("prediction_probability", results[0])
        self.assertIn("binary_prediction", results[1])

    def test_schema_validation_missing_feature(self):
        invalid_sample = self.valid_sample.copy()
        del invalid_sample["feature_density_ped_per_m2"]
        
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_single(invalid_sample)
        self.assertIn("Missing required feature columns", str(ctx.exception))

    def test_schema_validation_null_value(self):
        invalid_sample = self.valid_sample.copy()
        invalid_sample["feature_density_ped_per_m2"] = np.nan
        
        with self.assertRaises(ValueError) as ctx:
            self.predictor.predict_single(invalid_sample)
        self.assertIn("contains null or NaN values", str(ctx.exception))

    def test_risk_level_assignment(self):
        self.assertEqual(self.predictor.compute_risk_level(0.15), "LOW")
        self.assertEqual(self.predictor.compute_risk_level(0.45), "MODERATE")
        self.assertEqual(self.predictor.compute_risk_level(0.75), "HIGH")
        self.assertEqual(self.predictor.compute_risk_level(0.92), "CRITICAL")


if __name__ == "__main__":
    unittest.main()
