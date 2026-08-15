"""
Unit tests for BHID SessionManager & SessionMetadata (Phase 5A).

Validates:
1. Session metadata initialization
2. Frame & event count tracking
3. Session closure & duration computation
4. JSON metadata export
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

from bhid.persistence import PersistenceConfig, SessionManager


class TestSessionManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id="test_session_101")
        self.mgr = SessionManager(config=self.config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_session_lifecycle(self):
        sess = self.mgr.active_session
        self.assertIsNotNone(sess)
        self.assertEqual(sess.session_id, "test_session_101")
        self.assertTrue(sess.is_active)

        self.mgr.increment_frame_count()
        self.mgr.increment_frame_count()
        self.mgr.increment_event_count()

        self.assertEqual(sess.total_frames, 2)
        self.assertEqual(sess.total_events, 1)

        closed = self.mgr.close_session()
        self.assertFalse(closed.is_active)
        self.assertIsNotNone(closed.end_timestamp)

        meta_file = self.tmp_dir / "test_session_101" / "session_metadata.json"
        self.assertTrue(meta_file.exists())
        
        with open(meta_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["total_frames"], 2)
        self.assertEqual(data["total_events"], 1)


if __name__ == "__main__":
    unittest.main()
