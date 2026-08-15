"""
Integration test for BHID Crowd Analytics Engine & Full Runtime Pipeline (Phase 4D).

Validates complete end-to-end execution:
Mock Detector (Vision Detection Ingestion)
      ↓
Centroid Tracker (Multi-Object Association & Trajectory Storage)
      ↓
Tracking Batch (Frame Tracks Container)
      ↓
Crowd Analytics Engine (14-Feature Spatiotemporal Extraction)
      ↓
Feature Window Manager (Pure 10s @ 2.5Hz Rolling Buffer)
      ↓
Bottleneck Predictor (Phase 3D LightGBM Engine)
      ↓
Runtime Prediction Result (Risk Probability, Binary, Horizon Y30)
      ↓
Pipeline Context State Update
"""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARENT_ROOT = PROJECT_ROOT.parent
if str(PARENT_ROOT) not in sys.path:
    sys.path.insert(0, str(PARENT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.vision.detection import MockPedestrianDetector
from bhid.vision.tracking import CentroidTracker
from bhid.analytics import CrowdAnalyticsEngine, AnalyticsSnapshot
from bhid.runtime import RuntimeOrchestrator, PipelineContext, RuntimePredictionResult
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestAnalyticsRuntimeIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.detector = MockPedestrianDetector(num_pedestrians=20, seed=555)
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=150.0)
        self.analytics_engine = CrowdAnalyticsEngine(pixel_to_meter_scale=0.05, default_zone_area_m2=100.0)
        self.context = PipelineContext(active_scene="TEST_PLAZA_01", active_zone="MAIN_GATE")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

    def test_full_detector_to_predictor_pipeline(self):
        # Simulate 15 consecutive frames (6 seconds of crowd stream at 2.5Hz)
        results = []

        for frame_idx in range(15):
            ts = 1000.0 + (frame_idx * 0.4)
            # Escalating crowd density over sequence
            self.detector.set_pedestrian_count(10 + frame_idx * 15)
            
            # 1. Vision Detection
            det_batch = self.detector.detect(frame_id=frame_idx, timestamp=ts)
            
            # 2. Multi-Object Tracking
            tracking_batch = self.tracker.update(det_batch)
            
            # 3. Analytics & Prediction via RuntimeOrchestrator
            result = self.orchestrator.process_tracking_batch_with_analytics(
                tracking_batch=tracking_batch,
                analytics_engine=self.analytics_engine,
                zone_area_m2=100.0,
                scene_id="TEST_PLAZA_01",
                zone_id="MAIN_GATE"
            )

            self.assertIsInstance(result, RuntimePredictionResult)
            self.assertEqual(result.scene_id, "TEST_PLAZA_01")
            self.assertEqual(result.zone_id, "MAIN_GATE")
            self.assertEqual(result.target_horizon, "Y30")
            self.assertEqual(result.threshold_used, 0.60)
            self.assertIn(result.risk_level, ["LOW", "MODERATE", "HIGH", "CRITICAL"])
            self.assertGreaterEqual(result.prediction_probability, 0.0)
            self.assertLessEqual(result.prediction_probability, 1.0)
            
            results.append(result)

        # Confirm context state tracking
        ctx = self.orchestrator.get_context()
        self.assertEqual(ctx.active_scene, "TEST_PLAZA_01")
        self.assertEqual(ctx.active_zone, "MAIN_GATE")
        self.assertEqual(ctx.runtime_metadata["total_predictions"], 15)
        self.assertEqual(ctx.runtime_metadata["processed_frames"], 15)
        self.assertIsNotNone(ctx.latest_prediction)

        # Confirm risk escalation as pedestrian density increased from 10 to 220
        first_prob = results[0].prediction_probability
        last_prob = results[-1].prediction_probability
        self.assertGreater(last_prob, first_prob, "Risk probability should escalate with high crowd density")


if __name__ == "__main__":
    unittest.main()
