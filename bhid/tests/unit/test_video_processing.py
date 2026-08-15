"""
Unit tests for Video Frame Processing & Runtime Orchestrator (Phase 7B).
"""

import sys
import unittest
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.runtime.runtime_orchestrator import RuntimeOrchestrator


class TestVideoProcessing(unittest.TestCase):

    def setUp(self):
        self.orchestrator = RuntimeOrchestrator()
        self.test_video_path = Path("bhid/data/test_uploads/dummy_test.mp4")
        self.test_video_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.test_video_path, "wb") as f:
            f.write(b"dummy_mp4_bytes")

    def test_process_video_file(self):
        received_frames = []

        def callback(res):
            received_frames.append(res)

        res = self.orchestrator.process_video_file(
            video_path=str(self.test_video_path),
            telemetry_callback=callback,
            session_id="test_video_session"
        )

        self.assertEqual(res["status"], "COMPLETED")
        self.assertGreater(res["processed_frames"], 0)
        self.assertGreater(len(received_frames), 0)

    def tearDown(self):
        if self.test_video_path.exists():
            try:
                self.test_video_path.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
