"""
Unit tests for BHID PersistenceValidator (Phase 5D).

Validates:
1. Persistence directory structure verification
2. Non-blocking exception isolation method checks
3. Audit log append immutability
"""

import sys
import unittest
import tempfile
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.validation import PersistenceValidator


class TestPersistenceValidator(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.session_dir = self.tmp_dir / "sess_001"
        self.session_dir.mkdir()
        for sub in ["session_metadata.json", "playback_manifest.json", "predictions", "analytics", "events", "monitoring", "audit"]:
            p = self.session_dir / sub
            if "." in sub:
                p.touch()
            else:
                p.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_persistence_validation(self):
        audit_entries = [{"entry_id": 1}, {"entry_id": 2}]
        res = PersistenceValidator.validate_persistence(self.session_dir, audit_entries)
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 100.0)


if __name__ == "__main__":
    unittest.main()
