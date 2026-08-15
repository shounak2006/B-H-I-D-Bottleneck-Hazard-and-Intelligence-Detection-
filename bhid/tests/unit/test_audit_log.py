"""
Unit tests for BHID AuditLog (Phase 5A).

Validates:
1. Append-only audit entry writing & auto-increment IDs
2. Entry retrieval
3. JSON export integrity
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

from bhid.persistence import PersistenceConfig, AuditLog


class TestAuditLog(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id="test_audit_sess")
        self.log = AuditLog(config=self.config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_audit_entries(self):
        e1 = self.log.write_entry(action_type="SESSION_START", scene_id="SCENE_1", zone_id="ZONE_1")
        e2 = self.log.write_entry(action_type="EVENT_CREATED", scene_id="SCENE_1", zone_id="ZONE_1", details={"event_id": "EVT_1"})

        self.assertEqual(e1.entry_id, 1)
        self.assertEqual(e2.entry_id, 2)

        entries = self.log.get_entries()
        self.assertEqual(len(entries), 2)

        json_file = self.log.export_json()
        self.assertTrue(json_file.exists())
        with open(json_file, "r", encoding="utf-8") as f:
            records = json.load(f)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["action_type"], "SESSION_START")


if __name__ == "__main__":
    unittest.main()
