"""
Unit tests for BHID Prediction Dataset Generator (Phase 3A).
Verifies sliding window creation, 14-feature column structure,
active-event masking, and temporal data leakage prevention rules.
"""

import sys
import unittest
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.scripts.generate_prediction_dataset import (
    PredictionDatasetGenerator,
    audit_data_leakage,
    get_approved_14_feature_names,
    create_event_aware_splits
)

class TestDatasetGenerator(unittest.TestCase):

    def test_feature_columns_count_and_names(self):
        feat_cols = get_approved_14_feature_names()
        self.assertEqual(len(feat_cols), 14)
        self.assertIn("feature_density_ped_per_m2", feat_cols)
        self.assertIn("feature_egress_deficit_ratio", feat_cols)

    def test_dataset_generation_and_leakage(self):
        generator = PredictionDatasetGenerator()
        df, audit_counts = generator.build_full_dataset()
        
        self.assertGreater(len(df), 1000)
        self.assertIn("Y10", df.columns)
        self.assertIn("Y20", df.columns)
        self.assertIn("Y30", df.columns)
        
        # Verify no NaN values
        self.assertEqual(df[get_approved_14_feature_names()].isnull().sum().sum(), 0)
        
        # Audit leakage
        leakage_report = audit_data_leakage(df)
        self.assertFalse(leakage_report["leakage_detected"])
        self.assertTrue(leakage_report["horizon_ monotonicity_passed"])

    def test_event_aware_splits(self):
        generator = PredictionDatasetGenerator()
        df, _ = generator.build_full_dataset()
        train_df, val_df, test_df, split_stats = create_event_aware_splits(df)
        
        self.assertEqual(len(train_df) + len(val_df) + len(test_df), len(df))
        self.assertEqual(split_stats["train_events"], 7)
        self.assertEqual(split_stats["val_events"], 4)
        self.assertEqual(split_stats["test_events"], 3)

if __name__ == "__main__":
    unittest.main()
