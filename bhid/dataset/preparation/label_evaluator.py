"""
Candidate Bottleneck Label Evaluator for BHID (Audit Refined - Milestone 2.9).
Evaluates candidate bottleneck ground-truth rules against temporal feature sequences
using rigorous boundary-crossing flow drop metrics without model training.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class BottleneckLabelRule:
    rule_name: str
    density_thresh: float    # p/m2
    speed_thresh: float      # m/s
    flow_drop_thresh: float  # R_flow ratio = 1 - Q_out/Q_in [0.0, 1.0]
    sustain_sec: float       # duration in seconds

class BottleneckLabelEvaluator:
    """Evaluates empirical label rules against temporal crowd sequence distributions."""

    def __init__(self, rule: BottleneckLabelRule, frame_step_sec: float = 0.4):
        self.rule = rule
        self.frame_step_sec = frame_step_sec
        self.sustain_frames = int(round(rule.sustain_sec / frame_step_sec))

    def evaluate_sequence(self, feature_sequence: List[Dict[str, float]]) -> Dict[str, Any]:
        """Applies rule over temporal feature sequence and measures event frequency."""
        total_frames = len(feature_sequence)
        raw_hits = []
        
        for feat in feature_sequence:
            density = feat.get("density_ped_per_m2", 0.0)
            speed = feat.get("mean_speed_m_s", 99.0)
            flow_drop = feat.get("flow_drop_ratio", 0.0)
            
            is_hit = (density >= self.rule.density_thresh and 
                      speed <= self.rule.speed_thresh and 
                      flow_drop >= self.rule.flow_drop_thresh)
            raw_hits.append(is_hit)
            
        # Apply temporal sustainment constraint and identify discrete events
        sustained_hits = [False] * total_frames
        event_durations = []
        current_event_len = 0
        count = 0
        
        for i in range(total_frames):
            if raw_hits[i]:
                count += 1
            else:
                if count >= self.sustain_frames:
                    event_durations.append(count * self.frame_step_sec)
                count = 0
                
            if count >= self.sustain_frames:
                for j in range(i - self.sustain_frames + 1, i + 1):
                    sustained_hits[j] = True
                    
        if count >= self.sustain_frames:
            event_durations.append(count * self.frame_step_sec)
            
        positive_frames = sum(sustained_hits)
        pos_ratio = positive_frames / max(total_frames, 1)
        event_count = len(event_durations)
        avg_event_duration = sum(event_durations)/max(event_count, 1) if event_count > 0 else 0.0
        
        return {
            "rule_name": self.rule.rule_name,
            "density_thresh": self.rule.density_thresh,
            "speed_thresh": self.rule.speed_thresh,
            "flow_drop_thresh": self.rule.flow_drop_thresh,
            "sustain_sec": self.rule.sustain_sec,
            "total_frames_evaluated": total_frames,
            "positive_bottleneck_frames": positive_frames,
            "event_count": event_count,
            "avg_event_duration_sec": round(avg_event_duration, 2),
            "positive_event_ratio": round(pos_ratio, 4),
            "class_imbalance_ratio": f"{round((1-pos_ratio)/max(pos_ratio, 1e-4), 1)} : 1",
            "spatial_validity_notes": "Valid flow breakdown (Inflow > Outflow + Low Speed)" if pos_ratio > 0 else "Zero events detected"
        }

def main():
    candidate_rules = [
        BottleneckLabelRule(rule_name="Rule_Conservative_LOS_F", density_thresh=3.0, speed_thresh=0.3, flow_drop_thresh=0.5, sustain_sec=5.0),
        BottleneckLabelRule(rule_name="Rule_Moderate_FlowBreakdown", density_thresh=2.5, speed_thresh=0.4, flow_drop_thresh=0.4, sustain_sec=4.0),
        BottleneckLabelRule(rule_name="Rule_Sensitive_EarlyWarning", density_thresh=2.0, speed_thresh=0.5, flow_drop_thresh=0.3, sustain_sec=3.0)
    ]
    
    # Generate 100 synthetic sequence frames simulating a bottleneck event mid-sequence
    seq = []
    for i in range(100):
        if 40 <= i <= 75:  # Bottleneck episode: High density, low speed, high flow drop ratio
            seq.append({"density_ped_per_m2": 2.8, "mean_speed_m_s": 0.35, "flow_drop_ratio": 0.55})
        else:
            seq.append({"density_ped_per_m2": 1.2, "mean_speed_m_s": 1.1, "flow_drop_ratio": 0.0})
            
    print("--- Audit Refined Label Evaluator Benchmark ---")
    for r in candidate_rules:
        evaluator = BottleneckLabelEvaluator(r)
        res = evaluator.evaluate_sequence(seq)
        print(f"\nRule: {res['rule_name']}")
        print(f"  Events Detected: {res['event_count']} (Avg Duration: {res['avg_event_duration_sec']}s)")
        print(f"  Pos Ratio: {res['positive_event_ratio']*100}% ({res['positive_bottleneck_frames']}/{res['total_frames_evaluated']} frames)")
        print(f"  Class Imbalance: {res['class_imbalance_ratio']}")
        print(f"  Parameters: rho >= {res['density_thresh']} p/m2, v <= {res['speed_thresh']} m/s, R_flow >= {res['flow_drop_thresh']}, tau >= {res['sustain_sec']}s")

if __name__ == "__main__":
    main()
