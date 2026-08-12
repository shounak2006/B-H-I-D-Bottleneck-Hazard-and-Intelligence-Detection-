"""
Candidate Temporal Prediction Dataset Builder for BHID (Milestone 2.8).
Constructs sliding window feature sequence arrays (T_obs = 10s -> T_pred in {10s, 20s, 30s})
and packages sequence tensors without performing ML model training.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from dataclasses import dataclass, field
from typing import List, Dict, Any
from bhid.analytics.feature_extractor import CandidateFeatureExtractor
from bhid.dataset.preparation.schemas import Zone, Track

@dataclass
class TemporalWindowSample:
    """A single temporal sequence sample for predictive hazard modeling."""
    scene_id: str
    zone_id: str
    timestamp_sec: float
    dataset_source: str
    observation_features_sequence: List[Dict[str, float]]  # Length L = T_obs / dt (e.g. 25 frames @ 0.4s)
    prediction_horizons: List[int]  # [10, 20, 30] seconds
    future_state_placeholders: Dict[str, Any] = field(default_factory=dict)

class PredictionDatasetBuilder:
    """Constructs temporal prediction sequence datasets from trajectory streams."""

    def __init__(self, t_obs_sec: float = 10.0, step_sec: float = 0.4, horizons_sec: List[int] = None):
        self.t_obs_sec = t_obs_sec
        self.step_sec = step_sec
        self.horizons_sec = horizons_sec or [10, 20, 30]
        self.seq_len = int(round(t_obs_sec / step_sec))  # 25 steps for 10s window at 0.4s step

    def build_sample(self, scene_id: str, zone: Zone, feature_history: List[Dict[str, float]], current_ts: float) -> TemporalWindowSample:
        """Packages historical feature sequence into a standardized TemporalWindowSample."""
        if len(feature_history) < self.seq_len:
            # Pad window if trajectory starts mid-sequence
            pad = [feature_history[0]] * (self.seq_len - len(feature_history)) if feature_history else []
            obs_seq = pad + feature_history
        else:
            obs_seq = feature_history[-self.seq_len:]
            
        future_placeholders = {f"future_density_{h}s": None for h in self.horizons_sec}
        future_placeholders.update({f"candidate_label_{h}s": None for h in self.horizons_sec})
        
        return TemporalWindowSample(
            scene_id=scene_id,
            zone_id=zone.zone_id,
            timestamp_sec=current_ts,
            dataset_source="MADRAS-Candidate",
            observation_features_sequence=obs_seq,
            prediction_horizons=self.horizons_sec,
            future_state_placeholders=future_placeholders
        )

def main():
    z = Zone(zone_id="Zone_B1", polygon_vertices=[[0,0],[20,0],[20,20],[0,20]], area_m2=400.0)
    builder = PredictionDatasetBuilder()
    
    # Generate synthetic 25-step feature sequence
    dummy_history = []
    for step in range(25):
        dummy_history.append({
            "pedestrian_count": float(10 + step % 3),
            "density_ped_per_m2": round((10 + step % 3)/400.0, 3),
            "mean_speed_m_s": 1.2 - step*0.01,
            "directional_entropy": 1.2
        })
        
    sample = builder.build_sample(scene_id="Lyon_Square_1", zone=z, feature_history=dummy_history, current_ts=10.0)
    
    print("--- Candidate Prediction Dataset Sample Constructed ---")
    print(f"  Scene ID: {sample.scene_id}")
    print(f"  Zone ID: {sample.zone_id}")
    print(f"  Observation Window Steps: {len(sample.observation_features_sequence)} steps (10.0 seconds)")
    print(f"  Prediction Horizons: {sample.prediction_horizons} seconds")
    print(f"  Future State Placeholders: {list(sample.future_state_placeholders.keys())}")

if __name__ == "__main__":
    main()
