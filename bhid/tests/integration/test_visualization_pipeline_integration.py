"""
Integration test for BHID End-to-End Visualization & Monitoring Pipeline (Phase 4A - Phase 4F).

Validates complete visual monitoring execution:
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
"""

import sys
import unittest
from pathlib import Path
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.vision.detection import MockPedestrianDetector
from bhid.vision.tracking import CentroidTracker
from bhid.analytics import CrowdAnalyticsEngine
from bhid.events import HazardEventEngine
from bhid.visualization import MonitoringController, MonitoringSnapshot
from bhid.runtime import RuntimeOrchestrator, PipelineContext
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestVisualizationPipelineIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.detector = MockPedestrianDetector(num_pedestrians=2, seed=555)
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=150.0)
        self.analytics_engine = CrowdAnalyticsEngine(pixel_to_meter_scale=0.05, default_zone_area_m2=100.0)
        self.event_engine = HazardEventEngine()
        self.monitoring_controller = MonitoringController()
        
        self.context = PipelineContext(active_scene="TERMINAL_GATE_04", active_zone="SECURITY_CHECKPOINT")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

    def test_full_visual_monitoring_pipeline(self):
        scene_id = "TERMINAL_GATE_04"
        zone_id = "SECURITY_CHECKPOINT"
        start_ts = 2000.0
        time_step = 0.4

        # Simulate 10 frames of escalating crowd density
        for f in range(10):
            ts = start_ts + f * time_step
            self.detector.set_pedestrian_count(10 + f * 20)
            det_batch = self.detector.detect(frame_id=f, timestamp=ts)
            track_batch = self.tracker.update(det_batch)

            raw_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

            out = self.orchestrator.process_monitoring_frame(
                tracking_batch=track_batch,
                frame=raw_frame,
                event_engine=self.event_engine,
                analytics_engine=self.analytics_engine,
                monitoring_controller=self.monitoring_controller,
                zone_area_m2=100.0,
                scene_id=scene_id,
                zone_id=zone_id,
                draw_heatmap=True,
                draw_trajectories=True
            )

            # Validate pipeline outputs
            self.assertIn("prediction_result", out)
            self.assertIn("monitoring_snapshot", out)
            self.assertIn("rendered_frame", out)
            self.assertIn("active_event_count", out)

            # Validate rendered frame
            rendered = out["rendered_frame"]
            self.assertIsInstance(rendered, np.ndarray)
            self.assertEqual(rendered.shape, (1080, 1920, 3))
            self.assertEqual(rendered.dtype, np.uint8)

            # Validate snapshot structure
            snap_dict = out["monitoring_snapshot"]
            self.assertEqual(snap_dict["frame_id"], f)
            self.assertEqual(snap_dict["scene_id"], scene_id)
            self.assertEqual(snap_dict["zone_id"], zone_id)
            self.assertIn("summary", snap_dict)

        # Confirm pipeline state history tracking
        ctx = self.orchestrator.get_context()
        self.assertEqual(ctx.active_scene, scene_id)
        self.assertEqual(ctx.active_zone, zone_id)
        self.assertEqual(ctx.runtime_metadata["processed_frames"], 10)


if __name__ == "__main__":
    unittest.main()
