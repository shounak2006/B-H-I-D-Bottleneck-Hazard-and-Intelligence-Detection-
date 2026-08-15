"""
Unit tests for BHID PredictionStore (Phase 5A).

Validates:
1. Prediction record ingestion
2. JSON file export
3. CSV file export
"""

import sys
import unittest
import tempfile
import shutil
import json
import csv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.persistence import PersistenceConfig, PredictionStore


class TestPredictionStore(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id="test_pred_sess")
        self.store = PredictionStore(config=self.config)

        self.pred = RuntimePredictionResult(
            prediction_probability=0.85,
            binary_prediction=1,
            risk_level="CRITICAL",
            threshold_used=0.60,
            target_horizon="Y30",
            timestamp=105.0,
            scene_id="SCENE_A",
            zone_id="ZONE_1"
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_store_and_export(self):
        ok = self.store.store_prediction(self.pred)
        self.assertTrue(ok)
        records = self.store.get_predictions()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["risk_level"], "CRITICAL")

        # Export JSON
        json_file = self.store.export_json()
        self.assertIsNotNone(json_file)
        self.assertTrue(json_file.exists())
        with open(json_file, "r", encoding="utf-8") as f:
            j_data = json.load(f)
        self.assertEqual(len(j_data), 1)

        # Export CSV
        csv_file = self.store.export_csv()
        self.assertIsNotNone(csv_file)
        self.assertTrue(csv_file.exists())
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["risk_level"], "CRITICAL")


if __name__ == "__main__":
    unittest.main()
