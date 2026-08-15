"""
Unit tests for TelemetryManager (Phase 7B).
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

from backend.services.telemetry_manager import TelemetryManager


class TestTelemetryManager(unittest.TestCase):

    def setUp(self):
        self.mgr = TelemetryManager()

    def test_manager_initialization(self):
        self.assertEqual(len(self.mgr.active_connections), 0)

    def test_broadcast_safely_handles_empty_connections(self):
        payload = {"density": 2.5, "probability": 0.65}
        try:
            self.mgr.broadcast(payload)
            success = True
        except Exception:
            success = False

        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
