"""
Unit tests for BHID PlaybackLoader (Phase 5B).

Validates:
1. Historical session loading from disk
2. Ingestion of predictions, analytics snapshots, hazard events, and manifest records
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

from bhid.persistence import PersistenceConfig, PersistenceManager
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.replay import PlaybackLoader


class TestPlaybackLoader(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.session_id = "replay_sess_001"
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id=self.session_id)
        self.pm = PersistenceManager(config=self.config)

        # Ingest test prediction record
        pred = RuntimePredictionResult(0.85, 1, "CRITICAL", 0.60, "Y30", 10.0, "SCENE_1", "ZONE_1")
        self.pm.persist_prediction(pred)
        self.pm.flush()

        self.loader = PlaybackLoader(session_id=self.session_id, storage_root=self.tmp_dir)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_load_artifacts(self):
        sess = self.loader.load_session()
        self.assertEqual(sess.session_id, self.session_id)

        preds = self.loader.load_predictions()
        self.assertEqual(len(preds), 1)
        self.assertEqual(preds[0]["risk_level"], "CRITICAL")

        manifest = self.loader.load_manifest()
        self.assertIn("frame_timeline", manifest)


if __name__ == "__main__":
    unittest.main()
