"""
Integration test for BHID Operational Reporting Pipeline (Phase 4A - Phase 5C).

Validates end-to-end reporting execution:
Phase 5A Recording Session
      ↓
Persisted Disk Artifacts (JSON / CSV Files)
      ↓
Reporting Manager (Ingestion of Session Artifacts)
      ↓
KPI Engine & Trend Analyzer & Event Analytics (Intelligence Computation)
      ↓
Session Report & Comparative Analysis (Report Aggregation)
      ↓
Report Generator (Markdown, JSON, and CSV File Generation)
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
from bhid.reporting import ReportConfig, ReportingManager
from bhid.runtime import RuntimeOrchestrator, PipelineContext
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestReportingPipelineIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.session_id = "integration_report_sess_001"
        self.p_config = PersistenceConfig(storage_root=self.tmp_dir, session_id=self.session_id)
        self.persistence_manager = PersistenceManager(config=self.p_config)

        self.detector = MockPedestrianDetector(num_pedestrians=2, seed=555)
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=150.0)
        self.analytics_engine = CrowdAnalyticsEngine(pixel_to_meter_scale=0.05, default_zone_area_m2=100.0)
        self.event_engine = HazardEventEngine()
        self.monitoring_controller = MonitoringController()

        self.context = PipelineContext(active_scene="STATION_PLAZA_05", active_zone="MAIN_HALL")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

        self.r_config = ReportConfig(report_output_directory=self.tmp_dir / "reports")
        self.reporting_manager = ReportingManager(config=self.r_config)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_full_reporting_pipeline_execution(self):
        scene_id = "STATION_PLAZA_05"
        zone_id = "MAIN_HALL"
        start_ts = 5000.0
        time_step = 0.4

        # 1. Record 10 persistent frames in Phase 5A
        for f in range(10):
            ts = start_ts + f * time_step
            self.detector.set_pedestrian_count(10 + f * 20)
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

        # 2. Generate operational report via RuntimeOrchestrator entrypoint
        out = self.orchestrator.generate_operational_report(
            session_id=self.session_id,
            reporting_manager=self.reporting_manager,
            storage_root=self.tmp_dir
        )

        self.assertEqual(out["session_id"], self.session_id)
        self.assertIn("session_report", out)
        self.assertIn("markdown_content", out)
        self.assertIn("exported_files", out)

        # Verify exported report files
        exported_files = out["exported_files"]
        self.assertIn("json", exported_files)
        self.assertIn("csv", exported_files)
        self.assertIn("markdown", exported_files)

        md_path = Path(exported_files["markdown"])
        self.assertTrue(md_path.exists())

        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()
        self.assertIn("# BHID Operational Intelligence Report", md_text)
        self.assertIn("Operational Key Performance Indicators (KPIs)", md_text)


if __name__ == "__main__":
    unittest.main()
