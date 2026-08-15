"""
Unit tests for BHID EventStore (Phase 5A).

Validates:
1. HazardEvent ingestion and state update overwrite
2. Event retrieval
3. JSON file export
4. CSV file export
"""

import sys
import unittest
import tempfile
import shutil
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.events.hazard_event import HazardEvent
from bhid.persistence import PersistenceConfig, EventStore


class TestEventStore(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id="test_event_sess")
        self.store = EventStore(config=self.config)

        self.event = HazardEvent(
            event_id="EVT_001",
            scene_id="SCENE_1",
            zone_id="ZONE_A",
            start_timestamp=100.0,
            last_updated_timestamp=105.0,
            prediction_probability=0.88,
            risk_level="CRITICAL",
            status="ACTIVE"
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_store_and_update(self):
        self.store.store_event(self.event)
        self.assertEqual(len(self.store.get_events()), 1)

        # Update event status
        self.event.escalate(probability=0.95, risk_level="CRITICAL", timestamp=106.0)
        self.store.update_event(self.event)
        self.assertEqual(len(self.store.get_events()), 1)
        self.assertEqual(self.store.get_events()[0]["status"], "ESCALATED")

        json_file = self.store.export_json()
        self.assertTrue(json_file.exists())

        csv_file = self.store.export_csv()
        self.assertTrue(csv_file.exists())


if __name__ == "__main__":
    unittest.main()
