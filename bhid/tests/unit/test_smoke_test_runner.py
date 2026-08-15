"""
Unit tests for BHID SmokeTestRunner (Phase 6A).

Validates:
1. Automated smoke testing across all 8 platform layers
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

from bhid.release import SmokeTestRunner


class TestSmokeTestRunner(unittest.TestCase):

    def test_smoke_test_execution(self):
        res = SmokeTestRunner.run_smoke_tests()
        self.assertTrue(res["passed"])
        self.assertEqual(res["total_layers_tested"], 8)
        self.assertEqual(res["passed_layers_count"], 8)


if __name__ == "__main__":
    unittest.main()
