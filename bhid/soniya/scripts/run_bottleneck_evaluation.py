import csv
import sys
from pathlib import Path

# Project root ko Python path mein add karo
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from bhid.dataset.preparation.label_evaluator import (
    
    BottleneckLabelRule,
    BottleneckLabelEvaluator,
)


# --------------------------------------------------
# Input / Output
# --------------------------------------------------

FEATURE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "output"
    / "bhid_features.csv"
)

OUTPUT_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "output"
    / "bottleneck_evaluation.csv"
)


# --------------------------------------------------
# Load real feature sequence
# --------------------------------------------------

feature_sequence = []

with open(FEATURE_FILE, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        feature_sequence.append({
            "frame_index": int(row["frame_index"]),
            "density_ped_per_m2": float(
                row.get("density_ped_per_m2", 0)
            ),
            "mean_speed_m_s": float(
                row.get("mean_speed_m_s", 0)
            ),

            # Existing feature extractor calls this
            # egress_deficit_ratio.
            # Label evaluator expects flow_drop_ratio.
            "flow_drop_ratio": float(
                row.get("egress_deficit_ratio", 0)
            ),
        })


print("=" * 55)
print("BHID REAL VIDEO BOTTLENECK EVALUATION")
print("=" * 55)

print(f"Feature file: {FEATURE_FILE}")
print(f"Frames loaded: {len(feature_sequence)}")


# --------------------------------------------------
# Candidate rules
# --------------------------------------------------

rules = [

    BottleneckLabelRule(
        rule_name="Rule_Conservative_LOS_F",
        density_thresh=3.0,
        speed_thresh=0.3,
        flow_drop_thresh=0.5,
        sustain_sec=5.0,
    ),

    BottleneckLabelRule(
        rule_name="Rule_Moderate_FlowBreakdown",
        density_thresh=2.5,
        speed_thresh=0.4,
        flow_drop_thresh=0.4,
        sustain_sec=4.0,
    ),

    BottleneckLabelRule(
        rule_name="Rule_Sensitive_EarlyWarning",
        density_thresh=2.0,
        speed_thresh=0.5,
        flow_drop_thresh=0.3,
        sustain_sec=3.0,
    ),
]


# --------------------------------------------------
# Evaluate
# --------------------------------------------------

results = []

for rule in rules:

    evaluator = BottleneckLabelEvaluator(
        rule=rule,
        frame_step_sec=1 / 30
    )

    result = evaluator.evaluate_sequence(feature_sequence)

    results.append(result)

    print()
    print(f"Rule: {result['rule_name']}")
    print(f"Events detected: {result['event_count']}")
    print(
        f"Average event duration: "
        f"{result['avg_event_duration_sec']} sec"
    )
    print(
        f"Positive frames: "
        f"{result['positive_bottleneck_frames']}/"
        f"{result['total_frames_evaluated']}"
    )
    print(
        f"Positive event ratio: "
        f"{result['positive_event_ratio'] * 100:.2f}%"
    )
    print(
        f"Class imbalance: "
        f"{result['class_imbalance_ratio']}"
    )


# --------------------------------------------------
# Save results
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

fieldnames = [
    "rule_name",
    "density_thresh",
    "speed_thresh",
    "flow_drop_thresh",
    "sustain_sec",
    "total_frames_evaluated",
    "positive_bottleneck_frames",
    "event_count",
    "avg_event_duration_sec",
    "positive_event_ratio",
    "class_imbalance_ratio",
    "spatial_validity_notes",
]

with open(OUTPUT_FILE, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(results)


print()
print("=" * 55)
print(f"Evaluation report saved:")
print(OUTPUT_FILE)
print("=" * 55)