"""
Integration test for BHID System Packaging & Release Readiness Pipeline (Phase 1 - Phase 6A).

Validates end-to-end platform release lifecycle:
Runtime Orchestrator Initialization (initialize_bhid)
      ↓
Pre-Flight Environment Validation & Smoke Testing
      ↓
System Execution & Historical Session Validation
      ↓
Release Bundle Generation & Manifest Export (run_release_verification)
      ↓
Graceful System Shutdown (shutdown_bhid)
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

from bhid.runtime import RuntimeOrchestrator, PipelineContext
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestReleasePipelineIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.context = PipelineContext(active_scene="RELEASE_STATION", active_zone="PLATFORM_1")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_release_lifecycle(self):
        # 1. Initialize BHID platform
        init_res = self.orchestrator.initialize_bhid()
        self.assertEqual(init_res["status"], "INITIALIZED")

        # 2. Run release verification bundle
        rel_out = self.orchestrator.run_release_verification()
        self.assertEqual(rel_out["status"], "RELEASE_READY")
        self.assertIn("exported_artifacts", rel_out)

        # 3. Shutdown BHID platform cleanly
        shut_res = self.orchestrator.shutdown_bhid()
        self.assertEqual(shut_res["status"], "SHUTDOWN_COMPLETE")


if __name__ == "__main__":
    unittest.main()
