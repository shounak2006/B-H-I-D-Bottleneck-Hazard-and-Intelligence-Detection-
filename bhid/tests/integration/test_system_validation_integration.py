"""
Integration test for BHID System Operational Validation Pipeline (Phase 4A - Phase 5D).

Validates complete end-to-end system evaluation across all pipeline stages:
Phase 5A Recording Session Execution & Persistent Storage
      ↓
Phase 5B Replay Engine Reconstruction
      ↓
Phase 5C Operational Reporting & Multi-Format Exporter
      ↓
Phase 5D Read-Only System Validation & Operational Readiness Scoring
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

from bhid.vision.detection import MockPedestrianDetector
from bhid.vision.tracking import CentroidTracker
from bhid.analytics import CrowdAnalyticsEngine
from bhid.events import HazardEventEngine
from bhid.visualization import MonitoringController
from bhid.persistence import PersistenceConfig, PersistenceManager
from bhid.validation import ValidationConfig, ValidationManager
from bhid.runtime import RuntimeOrchestrator, PipelineContext
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestSystemValidationIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.session_id = "integration_val_sess_001"
        self.p_config = PersistenceConfig(storage_root=self.tmp_dir, session_id=self.session_id)
        self.persistence_manager = PersistenceManager(config=self.p_config)

        self.detector = MockPedestrianDetector(num_pedestrians=2, seed=555)
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=150.0)
        self.analytics_engine = CrowdAnalyticsEngine(pixel_to_meter_scale=0.05, default_zone_area_m2=100.0)
        self.event_engine = HazardEventEngine()
        self.monitoring_controller = MonitoringController()

        self.context = PipelineContext(active_scene="AIRPORT_GATE_12", active_zone="WAITING_LOUNGE")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

        self.v_config = ValidationConfig(validation_output_directory=self.tmp_dir / "reports" / "validation")
        self.validation_manager = ValidationManager(config=self.v_config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_system_validation_pipeline_execution(self):
        scene_id = "AIRPORT_GATE_12"
        zone_id = "WAITING_LOUNGE"
        start_ts = 6000.0
        time_step = 0.4

        # 1. Record 10 persistent frames in Phase 5A
        for f in range(10):
            ts = start_ts + f * time_step
            self.detector.set_pedestrian_count(15 + f * 15)
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

        # 2. Run system validation via RuntimeOrchestrator entrypoint
        val_out = self.orchestrator.generate_validation_report(
            session_id=self.session_id,
            storage_root=self.tmp_dir,
            validation_manager=self.validation_manager
        )

        self.assertIn("evaluation", val_out)
        self.assertIn("exported_files", val_out)

        evaluation = val_out["evaluation"]
        self.assertEqual(evaluation["overall_status"], "PASSED")
        self.assertEqual(evaluation["readiness_score_pct"], 100.0)
        self.assertTrue(evaluation["ready_for_release"])

        exported_files = val_out["exported_files"]
        self.assertIn("json", exported_files)
        self.assertIn("markdown", exported_files)

        md_path = Path(exported_files["markdown"])
        self.assertTrue(md_path.exists())

        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()
        self.assertIn("# BHID Operational Readiness & Validation Report", md_text)
        self.assertIn("SYSTEM OPERATIONAL READINESS CONFIRMED", md_text)


if __name__ == "__main__":
    unittest.main()
