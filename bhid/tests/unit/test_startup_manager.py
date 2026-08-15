"""
Unit tests for BHID StartupManager (Phase 6A).

Validates:
1. Pre-flight initialization sequence
2. Component verification across platform packages
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

from bhid.release import StartupManager


class TestStartupManager(unittest.TestCase):

    def setUp(self):
        self.mgr = StartupManager()

    def test_startup_initialization(self):
        res = self.mgr.initialize_system()
        self.assertEqual(res["status"], "INITIALIZED")
        self.assertTrue(self.mgr.is_initialized)

        comps = self.mgr.verify_components()
        self.assertTrue(comps["prediction"])
        self.assertTrue(comps["analytics"])


if __name__ == "__main__":
    unittest.main()
