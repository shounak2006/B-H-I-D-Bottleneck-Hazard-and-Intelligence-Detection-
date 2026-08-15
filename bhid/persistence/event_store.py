"""
BHID Event Store.

Persists HazardEvent lifecycle records into JSON files and CSV tables.
"""

from typing import List, Dict, Any, Optional
import json
import csv
from pathlib import Path
from bhid.persistence.persistence_config import PersistenceConfig
from bhid.events.hazard_event import HazardEvent


class EventStore:
    """
    Storage engine for operational HazardEvent records.
    """

    def __init__(self, config: Optional[PersistenceConfig] = None):
        self.config = config or PersistenceConfig()
        self._events: Dict[str, Dict[str, Any]] = {}

    def store_event(self, event: HazardEvent) -> bool:
        """Stores or updates a HazardEvent record."""
        try:
            d = event.to_dict() if hasattr(event, "to_dict") else dict(event)
            eid = str(d.get("event_id"))
            self._events[eid] = d
            return True
        except Exception:
            return False

    def update_event(self, event: HazardEvent) -> bool:
        """Alias for store_event."""
        return self.store_event(event)

    def get_events(self) -> List[Dict[str, Any]]:
        """Returns deep copies of all stored event records."""
        return [dict(e) for e in self._events.values()]

    def export_json(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports hazard events to JSON file."""
        try:
            if not self.config.json_export_enabled:
                return None
            out_file = file_path or (self.config.get_events_dir() / "hazard_events.json")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            records = list(self._events.values())
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)
            return out_file
        except Exception:
            return None

    def export_csv(self, file_path: Optional[Path] = None) -> Optional[Path]:
        """Exports hazard events to CSV file."""
        try:
            if not self.config.csv_export_enabled or not self._events:
                return None
            out_file = file_path or (self.config.get_events_dir() / "hazard_events.csv")
            out_file.parent.mkdir(parents=True, exist_ok=True)

            records = list(self._events.values())
            # Prepare CSV rows, serializing prediction_history to string length
            rows = []
            for r in records:
                row = dict(r)
                if "prediction_history" in row:
                    row["prediction_history_length"] = len(row.pop("prediction_history"))
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
        self._events.clear()
