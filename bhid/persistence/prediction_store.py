"""
BHID Prediction Store.

Persists RuntimePredictionResult outputs into in-memory buffers, JSON records, and CSV tables.
"""

from typing import List, Dict, Any, Optional
import json
import csv
from pathlib import Path
from bhid.persistence.persistence_config import PersistenceConfig
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult


class PredictionStore:
    """
    In-memory and file storage engine for runtime bottleneck risk predictions.
    """

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self._records: List[Dict[str, Any]] = []

    def store_prediction(self, pred_result: RuntimePredictionResult) -> bool:
        """
        Ingests a RuntimePredictionResult into the store.
        """
        try:
            d = pred_result.to_dict() if hasattr(pred_result, "to_dict") else dict(pred_result)
            self._records.append(d)
            return True
        except Exception:
            return False

    def get_predictions(self) -> List[Dict[str, Any]]:
        """Returns deep copies of all stored prediction records."""
        return [dict(r) for r in self._records]

    def export_json(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports prediction records to JSON file."""
        try:
            if not self.config.json_export_enabled:
                return None
            out_file = file_path or (self.config.get_predictions_dir() / "predictions.json")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(self._records, f, indent=2)
            return out_file
        except Exception:
            return None

    def export_csv(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports prediction records to CSV file."""
        try:
            if not self.config.csv_export_enabled or not self._records:
                return None
            out_file = file_path or (self.config.get_predictions_dir() / "predictions.csv")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            headers = list(self._records[0].keys())
            with open(out_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for rec in self._records:
                    writer.writerow(rec)
            return out_file
        except Exception:
            return None

    def clear(self) -> None:
        """Clears in-memory buffer."""
        self._records.clear()
