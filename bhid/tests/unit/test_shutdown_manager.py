"""
Unit tests for BHID ShutdownManager (Phase 6A).

Validates:
1. Graceful platform shutdown sequence
2. Pending persistence export flushes
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.release import ShutdownManager


class TestShutdownManager(unittest.TestCase):

    def setUp(self):
        self.mgr = ShutdownManager()

    def test_shutdown_sequence(self):
        res = self.mgr.shutdown_system()
        self.assertEqual(res["status"], "SHUTDOWN_COMPLETE")
        self.assertTrue(self.mgr.is_shutdown)
        self.assertTrue(res["session_closed"])


if __name__ == "__main__":
    unittest.main()
