"""
Unit tests for BHID PackagingManager (Phase 6A).

Validates:
1. Release bundle generation & pre-release checks
2. Artifact exports to dedicated release directory
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

from bhid.release import ReleaseConfig, PackagingManager


class TestPackagingManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = ReleaseConfig(release_output_directory=self.tmp_dir / "reports" / "release")
        self.mgr = PackagingManager(config=self.config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_build_release(self):
        bundle = self.mgr.build_release()
        self.assertEqual(bundle["status"], "RELEASE_READY")
        self.assertTrue(bundle["pre_release_checks"]["release_ready"])

        exported = bundle["exported_artifacts"]
        self.assertTrue(Path(exported["release_info_json"]).exists())
        self.assertTrue(Path(exported["release_manifest_json"]).exists())


if __name__ == "__main__":
    unittest.main()
