"""
Unit tests for Video File Upload & Storage (Phase 7B).
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

from backend.services.video_analysis_service import VideoAnalysisService


class TestVideoUpload(unittest.TestCase):

    def setUp(self):
        self.service = VideoAnalysisService(upload_dir=Path("bhid/data/test_uploads"))

    def test_upload_video(self):
        fake_content = b"header_fake_video_stream_bytes"
        job = self.service.upload_video(file_name="sample_crowd.mp4", file_bytes=fake_content)

        self.assertIn("session_id", job)
        self.assertEqual(job["status"], "UPLOADED")
        self.assertTrue(Path(job["file_path"]).exists())

    def tearDown(self):
        test_dir = Path("bhid/data/test_uploads")
        if test_dir.exists():
            for p in test_dir.iterdir():
                try:
                    p.unlink()
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
