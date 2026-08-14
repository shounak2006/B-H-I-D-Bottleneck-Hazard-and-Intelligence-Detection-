"""
BHID Standalone Prediction Inference Engine (Work Package 1).

Class: BottleneckPredictor

Capabilities:
1. Loads optimized model artifact (lightgbm_optimized.joblib or xgboost_optimized.joblib).
2. Loads model registry metadata (model_registry.json).
3. Validates 14-feature input schema.
4. Accepts pandas DataFrame, dictionary, or single sample dict.
5. Returns JSON-serializable structured predictions:
   - prediction_probability
   - binary_prediction
   - threshold_used
   - target_horizon ("Y30")
   - risk_level ("LOW", "MODERATE", "HIGH", "CRITICAL")
"""

import sys
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Union

# Set sys.path for project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

APPROVED_FEATURES = [
    "feature_pedestrian_count",
    "feature_density_ped_per_m2",
    "feature_occupancy_ratio",
    "feature_mean_speed_m_s",
    "feature_velocity_variance",
    "feature_acceleration_m_s2",
    "feature_directional_entropy",
    "feature_inflow_rate_per_s",
    "feature_outflow_rate_per_s",
    "feature_net_flow_rate_per_s",
    "feature_egress_deficit_ratio",
    "feature_trajectory_convergence",
    "feature_temporal_density_change",
    "feature_temporal_speed_change"
]


class BottleneckPredictor:
    """Standalone production prediction inference engine for BHID."""

    def __init__(self, model_path: Union[str, Path] = None, registry_path: Union[str, Path] = None):
        self.project_root = PROJECT_ROOT
        
        # Default paths if not specified
        if registry_path is None:
            registry_path = self.project_root / "models" / "model_registry.json"
        self.registry_path = Path(registry_path)
        
        # Load registry metadata
        if not self.registry_path.exists():
            raise FileNotFoundError(f"Model registry file not found: {self.registry_path}")
        with open(self.registry_path, "r") as f:
            self.registry = json.load(f)
            
        self.threshold = float(self.registry.get("threshold", 0.60))
        self.target_horizon = str(self.registry.get("target_horizon", "Y30"))
        self.feature_names = self.registry.get("approved_features", APPROVED_FEATURES)
        
        # Load model artifact
        if model_path is None:
            rel_m_path = self.registry.get("model_path", "models/lightgbm_optimized.joblib")
            if rel_m_path.startswith("bhid/"):
                rel_m_path = rel_m_path[5:]
            model_path = self.project_root / rel_m_path
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Optimized model artifact not found: {self.model_path}")
            
        self.model = joblib.load(self.model_path)

    def validate_schema(self, input_data: Union[Dict[str, Any], pd.DataFrame]) -> pd.DataFrame:
        """Validates that input features contain all 14 approved columns with non-null numeric values."""
        if isinstance(input_data, dict):
            df = pd.DataFrame([input_data])
        elif isinstance(input_data, pd.DataFrame):
            df = input_data.copy()
        else:
            raise ValueError(f"Unsupported input type: {type(input_data)}. Expected dict or pandas DataFrame.")
            
        missing_cols = [c for c in self.feature_names if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required feature columns: {missing_cols}")
            
        # Extract features in correct column order
        df_feat = df[self.feature_names]
        
        if df_feat.isnull().any().any():
            raise ValueError("Input feature matrix contains null or NaN values.")
            
        return df_feat

    def compute_risk_level(self, prob: float) -> str:
        """Classifies prediction probability into human-understandable risk levels."""
        if prob < 0.30:
            return "LOW"
        elif prob < self.threshold:
            return "MODERATE"
        elif prob < 0.85:
            return "HIGH"
        else:
            return "CRITICAL"

    def predict_single(self, sample_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Runs prediction on a single feature dictionary and returns a JSON-serializable output."""
        df_feat = self.validate_schema(sample_dict)
        probs = self.model.predict_proba(df_feat.values)[:, 1]
        prob = float(probs[0])
        binary_pred = int(prob >= self.threshold)
        risk = self.compute_risk_level(prob)
        
        return {
            "prediction_probability": round(prob, 4),
            "binary_prediction": binary_pred,
            "threshold_used": self.threshold,
            "target_horizon": self.target_horizon,
            "risk_level": risk,
            "sample_id": sample_dict.get("sample_id", "BHID_UNKNOWN")
        }

    def predict_batch(self, df_input: pd.DataFrame) -> List[Dict[str, Any]]:
        """Runs batch predictions over a DataFrame of feature vectors."""
        df_feat = self.validate_schema(df_input)
        probs = self.model.predict_proba(df_feat.values)[:, 1]
        
        results = []
        for i in range(len(df_input)):
            prob = float(probs[i])
            binary_pred = int(prob >= self.threshold)
            risk = self.compute_risk_level(prob)
            
            sample_id = str(df_input["sample_id"].iloc[i]) if "sample_id" in df_input.columns else f"SAMPLE_{i:05d}"
            
            results.append({
                "sample_id": sample_id,
                "prediction_probability": round(prob, 4),
                "binary_prediction": binary_pred,
                "threshold_used": self.threshold,
                "target_horizon": self.target_horizon,
                "risk_level": risk
            })
            
        return results


def main():
    print("--- Testing BHID Bottleneck Predictor Engine ---")
    predictor = BottleneckPredictor()
    
    # Generate dummy sample
    dummy_sample = {
        "sample_id": "TEST_SAMPLE_001",
        "feature_pedestrian_count": 450.0,
        "feature_density_ped_per_m2": 2.2,
        "feature_occupancy_ratio": 0.55,
        "feature_mean_speed_m_s": 0.35,
        "feature_velocity_variance": 0.08,
        "feature_acceleration_m_s2": -0.01,
        "feature_directional_entropy": 0.95,
        "feature_inflow_rate_per_s": 2.8,
        "feature_outflow_rate_per_s": 0.7,
        "feature_net_flow_rate_per_s": 2.1,
        "feature_egress_deficit_ratio": 0.75,
        "feature_trajectory_convergence": 0.82,
        "feature_temporal_density_change": 0.85,
        "feature_temporal_speed_change": -0.45
    }
    
    result = predictor.predict_single(dummy_sample)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
