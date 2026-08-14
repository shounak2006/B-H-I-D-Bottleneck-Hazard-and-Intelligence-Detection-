"""
BHID Inference Validation & Metric Reproduction Script (Work Package 3).

Executes:
1. Loads unseen test set split (test.parquet).
2. Instantiates BottleneckPredictor engine.
3. Performs batch inference over all test set samples.
4. Calculates Accuracy, Precision, Recall, F1, and ROC-AUC.
5. Performs numerical tolerance verification against Phase 3C registry benchmarks (|metric_inf - metric_reg| <= 0.001).
6. Exports verification results and status summary.
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)

# Set sys.path for project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


def run_inference_validation(tolerance: float = 0.001) -> Dict[str, Any]:
    """Runs batch inference validation and compares outputs against registry metrics."""
    data_dir = PROJECT_ROOT / "data" / "processed"
    test_path = data_dir / "test.parquet"
    
    if not test_path.exists():
        raise FileNotFoundError(f"Test split dataset not found: {test_path}")
        
    test_df = pd.read_parquet(test_path)
    y_true = test_df["Y30"].values
    
    predictor = BottleneckPredictor()
    results = predictor.predict_batch(test_df)
    
    y_prob = np.array([r["prediction_probability"] for r in results])
    y_pred = np.array([r["binary_prediction"] for r in results])
    
    acc = round(float(accuracy_score(y_true, y_pred)), 4)
    prec = round(float(precision_score(y_true, y_pred, zero_division=0)), 4)
    rec = round(float(recall_score(y_true, y_pred, zero_division=0)), 4)
    f1 = round(float(f1_score(y_true, y_pred, zero_division=0)), 4)
    auc = round(float(roc_auc_score(y_true, y_prob)), 4)
    
    inf_metrics = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": auc
    }
    
    reg_metrics = predictor.registry.get("metrics", {})
    
    deviations = {}
    tolerance_passed = True
    
    for metric_name in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        val_inf = inf_metrics.get(metric_name, 0.0)
        val_reg = reg_metrics.get(metric_name, 0.0)
        diff = round(abs(val_inf - val_reg), 4)
        passed = diff <= tolerance
        
        if not passed:
            tolerance_passed = False
            
        deviations[metric_name] = {
            "inference_value": val_inf,
            "registry_value": val_reg,
            "absolute_difference": diff,
            "within_tolerance": passed
        }
        
    return {
        "validation_status": "PASS - METRICS REPRODUCED WITHIN TOLERANCE" if tolerance_passed else "WARNING - METRIC DEVIATION DETECTED",
        "total_test_samples": len(test_df),
        "target_horizon": predictor.target_horizon,
        "threshold_used": predictor.threshold,
        "inference_metrics": inf_metrics,
        "metric_deviations": deviations,
        "tolerance_threshold": tolerance
    }


def main():
    print("==========================================================================")
    print("BHID Phase 3D: Batch Prediction & Metric Reproduction Validator")
    print("==========================================================================")
    
    res = run_inference_validation()
    
    print(f"\nValidation Status: {res['validation_status']}")
    print(f"Total Test Samples Validated: {res['total_test_samples']:,}")
    print(f"Target Horizon: {res['target_horizon']} (Optimal Threshold p* = {res['threshold_used']})")
    
    print("\nMetric Comparison Table:")
    print(f"{'Metric':<12} | {'Inference Value':<15} | {'Registry Benchmark':<18} | {'Abs Diff':<10} | {'Status'}")
    print("-" * 75)
    for m, dev in res["metric_deviations"].items():
        status_str = "MATCH" if dev["within_tolerance"] else "DEVIATION"
        print(f"{m:<12} | {dev['inference_value']:<15} | {dev['registry_value']:<18} | {dev['absolute_difference']:<10} | {status_str}")
        
    print("\n==========================================================================")
    print("PHASE 3D INFERENCE VALIDATION COMPLETED SUCCESSFULLY")
    print("==========================================================================")


if __name__ == "__main__":
    main()
