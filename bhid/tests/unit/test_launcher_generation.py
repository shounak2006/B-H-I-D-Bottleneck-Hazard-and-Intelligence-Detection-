"""
Unit tests for BHID Batch Script Generation (Phase 6A/6B Launcher).

Validates:
1. start_bhid.bat file generation and syntax structure
2. stop_bhid.bat file generation and graceful shutdown commands
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


class TestLauncherGeneration(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = LauncherConfig(
            start_bat_filename="start_test.bat",
            stop_bat_filename="stop_test.bat"
        )
        self.mgr = LauncherManager(config=self.config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_generate_start_script(self):
        p_start = self.mgr.generate_start_script(project_root=self.tmp_dir)
        self.assertTrue(p_start.exists())
        
        with open(p_start, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertIn("@echo off", content)
        self.assertIn("TITLE BHID Platform Launcher", content)
        self.assertIn("launcher_manager check", content)
        self.assertIn("BHID_BACKEND_SERVICE", content)

    def test_generate_stop_script(self):
        p_stop = self.mgr.generate_stop_script(project_root=self.tmp_dir)
        self.assertTrue(p_stop.exists())

        with open(p_stop, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("@echo off", content)
        self.assertIn("launcher_manager stop", content)
        self.assertIn("taskkill", content)
        self.assertIn("BHID_BACKEND_SERVICE", content)


if __name__ == "__main__":
    unittest.main()
