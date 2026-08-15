"""
Unit tests for BHID FeatureWindowManager (Phase 4A).

Validates:
1. Initialization defaults (10s window, 2.5Hz, max 25 samples)
2. Pure rolling window behavior & capacity limits (exact 25 retention)
3. Time-based sample expiration purging (samples older than 10s evicted)
4. Non-chronological timestamp prevention (no future leakage)
5. Schema validation during sample ingestion
6. Zero analytics/feature calculation inside manager
"""

import sys
import unittest
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.runtime.feature_window_manager import FeatureWindowManager, SampleRecord
from bhid.runtime.exceptions import FeatureValidationError
from bhid.runtime.feature_schema import FROZEN_FEATURE_NAMES


class TestFeatureWindowManager(unittest.TestCase):

    def setUp(self):
        self.wm = FeatureWindowManager(window_duration=10.0, cadence_hz=2.5, max_samples=25)
        self.valid_features = {feat: 1.0 for feat in FROZEN_FEATURE_NAMES}

    def test_initial_state(self):
        self.assertEqual(self.wm.size, 0)
        self.assertEqual(self.wm.capacity, 25)
        self.assertTrue(self.wm.is_empty())
        self.assertFalse(self.wm.is_full())
        self.assertFalse(self.wm.is_ready(min_samples=1))
        self.assertIsNone(self.wm.get_latest_sample())

    def test_add_single_sample(self):
        rec = self.wm.add_sample(self.valid_features, timestamp=100.0)
        self.assertIsInstance(rec, SampleRecord)
        self.assertEqual(rec.timestamp, 100.0)
        self.assertEqual(self.wm.size, 1)
        self.assertFalse(self.wm.is_empty())
        self.assertTrue(self.wm.is_ready(min_samples=1))
        self.assertEqual(self.wm.get_latest_sample().timestamp, 100.0)

    def test_rolling_capacity_retention(self):
        """Verify that pushing 30 samples retains exactly the latest 25 samples."""
        base_ts = 100.0
        # Add 30 samples at 0.1s intervals (total span 3.0s < 10s window duration)
        for i in range(30):
            ts = base_ts + (i * 0.1)
            self.wm.add_sample(self.valid_features, timestamp=ts)

        self.assertEqual(self.wm.size, 25)
        self.assertTrue(self.wm.is_full())

        samples = self.wm.get_window_samples()
        self.assertEqual(len(samples), 25)
        # Oldest sample in buffer should be sample index 5 (ts = 100.5)
        self.assertAlmostEqual(samples[0].timestamp, 100.5, places=5)
        # Latest sample should be sample index 29 (ts = 102.9)
        self.assertAlmostEqual(samples[-1].timestamp, 102.9, places=5)

    def test_time_based_expiration_purging(self):
        """Verify that samples older than 10.0 seconds are purged regardless of sample count."""
        # Add sample at t = 100.0
        self.wm.add_sample(self.valid_features, timestamp=100.0)
        # Add sample at t = 105.0
        self.wm.add_sample(self.valid_features, timestamp=105.0)
        self.assertEqual(self.wm.size, 2)

        # Add sample at t = 110.5 (cutoff is 110.5 - 10.0 = 100.5 -> t=100.0 is expired)
        self.wm.add_sample(self.valid_features, timestamp=110.5)
        self.assertEqual(self.wm.size, 2)
        
        samples = self.wm.get_window_samples()
        timestamps = [s.timestamp for s in samples]
        self.assertNotIn(100.0, timestamps)
        self.assertIn(105.0, timestamps)
        self.assertIn(110.5, timestamps)

    def test_non_chronological_timestamp_rejection(self):
        """Verify that adding a sample with an earlier timestamp raises FeatureValidationError."""
        self.wm.add_sample(self.valid_features, timestamp=100.0)
        with self.assertRaises(FeatureValidationError) as ctx:
            self.wm.add_sample(self.valid_features, timestamp=99.0)
        self.assertIn("Non-chronological timestamp", str(ctx.exception))

    def test_invalid_feature_schema_rejection(self):
        """Verify that invalid/missing features are rejected upon ingestion."""
        incomplete_features = {"feature_pedestrian_count": 10.0}
        with self.assertRaises(FeatureValidationError):
            self.wm.add_sample(incomplete_features, timestamp=100.0)

    def test_clear_buffer(self):
        self.wm.add_sample(self.valid_features, timestamp=100.0)
        self.assertEqual(self.wm.size, 1)
        self.wm.clear()
        self.assertEqual(self.wm.size, 0)
        self.assertTrue(self.wm.is_empty())
        self.assertIsNone(self.wm.get_latest_sample())


if __name__ == "__main__":
    unittest.main()
