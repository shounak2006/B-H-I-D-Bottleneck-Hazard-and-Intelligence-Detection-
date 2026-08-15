"""
Integration test for BHID Historical Playback Pipeline (Phase 4A - Phase 5B).

Validates end-to-end replay execution:
Phase 5A Recording Session
      ↓
Persisted Disk Artifacts (JSON / CSV Files)
      ↓
Playback Loader (Disk Artifact Ingestion)
      ↓
Event Timeline (Historical Event Reconstruction)
      ↓
Playback Engine (Chronological Frame Reconstruction)
      ↓
Monitoring Controller (Visual Replay Frame Rendering)
"""

import sys
import unittest
import tempfile
import shutil
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.vision.detection import MockPedestrianDetector
from bhid.vision.tracking import CentroidTracker
from bhid.analytics import CrowdAnalyticsEngine
from bhid.events import HazardEventEngine
from bhid.visualization import MonitoringController
from bhid.persistence import PersistenceConfig, PersistenceManager
from bhid.replay import PlaybackEngine
from bhid.runtime import RuntimeOrchestrator, PipelineContext
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestReplayPipelineIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.session_id = "integration_replay_sess_001"
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id=self.session_id)
        self.persistence_manager = PersistenceManager(config=self.config)

        self.detector = MockPedestrianDetector(num_pedestrians=2, seed=555)
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=150.0)
        self.analytics_engine = CrowdAnalyticsEngine(pixel_to_meter_scale=0.05, default_zone_area_m2=100.0)
        self.event_engine = HazardEventEngine()
        self.monitoring_controller = MonitoringController()

        self.context = PipelineContext(active_scene="TERMINAL_GATE_09", active_zone="BOARDING_ZONE")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_replay_pipeline_execution(self):
        scene_id = "TERMINAL_GATE_09"
        zone_id = "BOARDING_ZONE"
        start_ts = 4000.0
        time_step = 0.4

        # 1. Record 10 persistent frames in Phase 5A
        for f in range(10):
            ts = start_ts + f * time_step
            self.detector.set_pedestrian_count(10 + f * 15)
            det_batch = self.detector.detect(frame_id=f, timestamp=ts)
            track_batch = self.tracker.update(det_batch)

            self.orchestrator.process_persistent_monitoring_frame(
                tracking_batch=track_batch,
                frame=None,
                persistence_manager=self.persistence_manager,
                monitoring_controller=self.monitoring_controller,
                event_engine=self.event_engine,
                analytics_engine=self.analytics_engine,
                zone_area_m2=100.0,
                scene_id=scene_id,
                zone_id=zone_id
            )

        self.persistence_manager.flush()

        # 2. Replay historical session deterministically in Phase 5B
        replay_out = self.orchestrator.replay_historical_session(
            session_id=self.session_id,
            storage_root=self.tmp_dir,
            monitoring_controller=self.monitoring_controller
        )

        self.assertEqual(replay_out["session_id"], self.session_id)
        self.assertEqual(replay_out["total_frames"], 10)

        # Verify summary metrics
        summary = replay_out["replay_summary"]
        self.assertEqual(summary["total_frames_analyzed"], 10)
        self.assertGreater(summary["peak_pedestrian_count"], 0)

        # Verify rendered replay images
        replayed_frames = replay_out["replayed_frames"]
        self.assertEqual(len(replayed_frames), 10)

        first_rf = replayed_frames[0]
        self.assertIn("replay_frame", first_rf)
        self.assertIn("rendered_image", first_rf)

        rendered_img = first_rf["rendered_image"]
        self.assertIsInstance(rendered_img, np.ndarray)
        self.assertEqual(rendered_img.shape, (1080, 1920, 3))


if __name__ == "__main__":
    unittest.main()
