"""
Integration test for BHID End-to-End Persistence Pipeline (Phase 4A - Phase 5A).

Validates complete persistent pipeline execution:
Detector (Mock Pedestrian Detector)
      ↓
Tracker (Centroid Multi-Object Association & Trajectory Storage)
      ↓
Analytics (14 Spatiotemporal Feature Extraction Engine)
      ↓
Feature Window Manager (10s @ 2.5Hz Pure Buffer)
      ↓
Predictor (LightGBM Optimization Engine)
      ↓
Prediction Result (Probability, Binary, Risk Level, Horizon Y30)
      ↓
Hazard Event Engine (Active Registry, Escalation, Resolution)
      ↓
Monitoring Controller (Telemetry Snapshot & Annotated Visual Frame)
      ↓
Persistence Manager (Non-Blocking Disk Ingestion & JSON/CSV Session File Flushing)
"""

import sys
import unittest
import tempfile
import shutil
import json
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
from bhid.runtime import RuntimeOrchestrator, PipelineContext
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestPersistencePipelineIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.config = PersistenceConfig(storage_root=self.tmp_dir, session_id="integration_sess_001")
        self.persistence_manager = PersistenceManager(config=self.config)

        self.detector = MockPedestrianDetector(num_pedestrians=2, seed=555)
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=150.0)
        self.analytics_engine = CrowdAnalyticsEngine(pixel_to_meter_scale=0.05, default_zone_area_m2=100.0)
        self.event_engine = HazardEventEngine()
        self.monitoring_controller = MonitoringController()

        self.context = PipelineContext(active_scene="STATION_HUB_01", active_zone="MAIN_CONCOURSE")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_persistent_pipeline_execution(self):
        scene_id = "STATION_HUB_01"
        zone_id = "MAIN_CONCOURSE"
        start_ts = 3000.0
        time_step = 0.4

        # Run 10 frames through full persistent monitoring pipeline
        for f in range(10):
            ts = start_ts + f * time_step
            self.detector.set_pedestrian_count(15 + f * 25)
            det_batch = self.detector.detect(frame_id=f, timestamp=ts)
            track_batch = self.tracker.update(det_batch)

            out = self.orchestrator.process_persistent_monitoring_frame(
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

            self.assertTrue(out.get("persistence_active"))

        # Flush persistence files
        exports = self.persistence_manager.flush()
        self.assertIsNotNone(exports.get("predictions_json"))
        self.assertTrue(exports["predictions_json"].exists())
        self.assertTrue(exports["analytics_json"].exists())
        self.assertTrue(exports["monitoring_json"].exists())
        self.assertTrue(exports["manifest_json"].exists())
        self.assertTrue(exports["audit_json"].exists())

        # Verify predictions.json content
        with open(exports["predictions_json"], "r", encoding="utf-8") as f:
            preds = json.load(f)
        self.assertEqual(len(preds), 10)
        self.assertEqual(preds[0]["scene_id"], scene_id)
        self.assertEqual(preds[0]["zone_id"], zone_id)

        # Verify playback_manifest.json content
        with open(exports["manifest_json"], "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["total_frames_indexed"], 10)


if __name__ == "__main__":
    unittest.main()
