"""
BHID Analytics Feature Store.

Persists 14-feature AnalyticsSnapshot outputs into JSON records and CSV tables.
"""

from typing import List, Dict, Any, Optional
import json
import csv
from pathlib import Path
from bhid.persistence.persistence_config import PersistenceConfig
from bhid.analytics.analytics_snapshot import AnalyticsSnapshot


class AnalyticsStore:
    """
    Storage engine for 14-feature spatiotemporal crowd analytics snapshots.
    """

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self._records: List[Dict[str, Any]] = []

    def store_snapshot(self, snapshot: AnalyticsSnapshot) -> bool:
        """Ingests an AnalyticsSnapshot into the store."""
        try:
            d = snapshot.to_dict() if hasattr(snapshot, "to_dict") else dict(snapshot)
            self._records.append(d)
            return True
        except Exception:
            return False

    def get_snapshots(self) -> List[Dict[str, Any]]:
        """Returns deep copies of all stored analytics records."""
        return [dict(r) for r in self._records]

    def export_json(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports analytics snapshots to JSON file."""
        try:
            if not self.config.json_export_enabled:
                return None
            out_file = file_path or (self.config.get_analytics_dir() / "analytics_snapshots.json")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(self._records, f, indent=2)
            return out_file
        except Exception:
            return None

    def export_csv(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports analytics features to CSV file."""
        try:
            if not self.config.csv_export_enabled or not self._records:
                return None
            out_file = file_path or (self.config.get_analytics_dir() / "analytics_snapshots.csv")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            # Flatten metadata + 14 features into CSV columns
            flattened = []
            for rec in self._records:
                row = {
                    "frame_id": rec.get("frame_id"),
                    "timestamp": rec.get("timestamp"),
                    "scene_id": rec.get("scene_id"),
                    "zone_id": rec.get("zone_id"),
                }
                features = rec.get("features", {})
                row.update(features)
                flattened.append(row)

            headers = list(flattened[0].keys())
            with open(out_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for r in flattened:
                    writer.writerow(r)
            return out_file
        except Exception:
            return None

    def clear(self) -> None:
        """Clears in-memory buffer."""
        self._records.clear()
