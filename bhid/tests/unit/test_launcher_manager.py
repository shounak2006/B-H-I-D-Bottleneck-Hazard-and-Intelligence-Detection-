"""
Unit tests for BHID LauncherManager (Windows One-Click Launcher).

Validates:
1. Informational frontend auto-detection
2. Dynamic environment launch readiness validation
3. Backend process startup & PID file management under bhid/data/runtime/
4. Graceful backend process shutdown
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

from bhid.release import LauncherConfig, LauncherManager


class TestLauncherManager(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = LauncherConfig(pid_file=self.tmp_dir / "data" / "runtime" / "bhid.pid")
        self.mgr = LauncherManager(config=self.config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_detect_frontend(self):
        res = self.mgr.detect_frontend()
        self.assertIn("frontend_detected", res)
        self.assertIn("framework", res)
        self.assertTrue(res["informational"])

    def test_validate_launch_environment(self):
        res = self.mgr.validate_launch_environment()
        self.assertIn("launch_ready", res)
        self.assertTrue(res["launch_ready"])
        self.assertTrue(res["model_artifact_ready"])

    def test_start_and_stop_backend(self):
        start_res = self.mgr.start_backend()
        self.assertEqual(start_res["status"], "RUNNING")
        self.assertTrue(self.config.pid_file.exists())

        stop_res = self.mgr.stop_backend()
        self.assertEqual(stop_res["status"], "SHUTDOWN_COMPLETE")
        self.assertFalse(self.config.pid_file.exists())


if __name__ == "__main__":
    unittest.main()
