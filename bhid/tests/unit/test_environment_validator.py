"""
Unit tests for BHID EnvironmentValidator (Phase 6A).

Validates:
1. Python version compatibility checking
2. Dependency package availability checking
3. Filesystem directory structure and write permission checking
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

from bhid.release import EnvironmentValidator


class TestEnvironmentValidator(unittest.TestCase):

    def setUp(self):
        self.validator = EnvironmentValidator()

    def test_python_version_validation(self):
        res = self.validator.validate_python_version()
        self.assertTrue(res["passed"])
        self.assertIn("major_minor", res)

    def test_dependency_validation(self):
        res = self.validator.validate_dependencies()
        self.assertIn("packages", res)
        self.assertTrue(res["packages"]["numpy"]["available"])

    def test_filesystem_validation(self):
        res = self.validator.validate_filesystem()
        self.assertTrue(res["model_registry_found"])
        self.assertTrue(res["write_permissions_ok"])


if __name__ == "__main__":
    unittest.main()
