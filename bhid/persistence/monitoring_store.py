"""
BHID Monitoring Telemetry Store.

Persists MonitoringSnapshot visual telemetry records into JSON files and CSV tables.
"""

from typing import List, Dict, Any, Optional
import json
import csv
from pathlib import Path
from bhid.persistence.persistence_config import PersistenceConfig
from bhid.visualization.monitoring_snapshot import MonitoringSnapshot


class MonitoringStore:
    """
    Storage engine for single-frame operational MonitoringSnapshot visual telemetry.
    """

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self._records: List[Dict[str, Any]] = []

    def store_snapshot(self, snapshot: MonitoringSnapshot) -> bool:
        """Ingests a MonitoringSnapshot record into the store."""
        try:
            d = snapshot.to_dict() if hasattr(snapshot, "to_dict") else dict(snapshot)
            self._records.append(d)
            return True
        except Exception:
            return False

    def get_snapshots(self) -> List[Dict[str, Any]]:
        """Returns deep copies of all stored monitoring snapshots."""
        return [dict(r) for r in self._records]

    def export_json(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports monitoring snapshots to JSON file."""
        try:
            if not self.config.json_export_enabled:
                return None
            out_file = file_path or (self.config.get_monitoring_dir() / "monitoring_snapshots.json")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(self._records, f, indent=2)
            return out_file
        except Exception:
            return None

    def export_csv(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports monitoring snapshots to CSV file."""
        try:
            if not self.config.csv_export_enabled or not self._records:
                return None
            out_file = file_path or (self.config.get_monitoring_dir() / "monitoring_snapshots.csv")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            rows = []
            for r in self._records:
                row = dict(r)
                if "active_events" in row:
                    row["active_events_count"] = len(row.pop("active_events"))
                rows.append(row)

            headers = list(rows[0].keys())
            with open(out_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for r in rows:
                    writer.writerow(r)
            return out_file
        except Exception:
            return None

    def clear(self) -> None:
        """Clears in-memory buffer."""
        self._records.clear()
