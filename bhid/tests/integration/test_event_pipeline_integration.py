"""
Integration test for BHID Full Operational Intelligence Pipeline (Phase 4A - Phase 4E).

Validates complete end-to-end operational execution:
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
Hazard Event Engine (Event Creation, Escalation, Duplicate Suppression, Resolution, Archival)
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

from bhid.vision.detection import MockPedestrianDetector
from bhid.vision.tracking import CentroidTracker
from bhid.analytics import CrowdAnalyticsEngine
from bhid.events import HazardEventEngine, AlertPolicy
from bhid.runtime import RuntimeOrchestrator, PipelineContext
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor


class TestEventPipelineIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = BottleneckPredictor()

    def setUp(self):
        self.detector = MockPedestrianDetector(num_pedestrians=2, seed=555)
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=150.0)
        self.analytics_engine = CrowdAnalyticsEngine(pixel_to_meter_scale=0.05, default_zone_area_m2=100.0)
        self.alert_policy = AlertPolicy(safe_resolution_threshold=3, escalation_prob_delta=0.15)
        self.event_engine = HazardEventEngine(
            lifecycle_manager=None  # uses default AlertPolicy with safe_resolution_threshold=3
        )
        
        self.context = PipelineContext(active_scene="STATION_CAM_03", active_zone="CONCOURSE_ZONE")
        self.orchestrator = RuntimeOrchestrator(predictor=self.predictor, context=self.context)

    def test_full_pipeline_event_lifecycle(self):
        scene_id = "STATION_CAM_03"
        zone_id = "CONCOURSE_ZONE"
        start_ts = 1000.0
        time_step = 0.4

        # -------------------------------------------------------------
        # Phase 1: Low density flow (5 frames) -> Zero active events
        # -------------------------------------------------------------
        for f in range(5):
            ts = start_ts + f * time_step
            self.detector.set_pedestrian_count(2)
            det_batch = self.detector.detect(frame_id=f, timestamp=ts)
            track_batch = self.tracker.update(det_batch)

            out = self.orchestrator.process_prediction_event(
                tracking_batch=track_batch,
                event_engine=self.event_engine,
                analytics_engine=self.analytics_engine,
                zone_area_m2=100.0,
                scene_id=scene_id,
                zone_id=zone_id
            )

        self.assertEqual(len(self.event_engine.get_active_events()), 0, "Normal low-risk flow should produce no active hazard events")

        # -------------------------------------------------------------
        # Phase 2: Crowd density escalation (10 frames) -> Event Created & Escalated
        # -------------------------------------------------------------
        for f in range(5, 15):
            ts = start_ts + f * time_step
            self.detector.set_pedestrian_count(40 + (f - 5) * 20)
            det_batch = self.detector.detect(frame_id=f, timestamp=ts)
            track_batch = self.tracker.update(det_batch)

            out = self.orchestrator.process_prediction_event(
                tracking_batch=track_batch,
                event_engine=self.event_engine,
                analytics_engine=self.analytics_engine,
                zone_area_m2=100.0,
                scene_id=scene_id,
                zone_id=zone_id
            )

        active_events = self.event_engine.get_active_events()
        self.assertEqual(len(active_events), 1, "Zone-level duplicate suppression must enforce exactly 1 active event")
        event = active_events[0]
        self.assertEqual(event.scene_id, scene_id)
        self.assertEqual(event.zone_id, zone_id)
        self.assertIn(event.status, ["ACTIVE", "ESCALATED"])

        # -------------------------------------------------------------
        # Phase 3: Crowd clears back to low density (6 frames) -> Resolves after safe_threshold (3)
        # -------------------------------------------------------------
        for f in range(15, 21):
            ts = start_ts + f * time_step
            self.detector.set_pedestrian_count(2)
            det_batch = self.detector.detect(frame_id=f, timestamp=ts)
            track_batch = self.tracker.update(det_batch)

            out = self.orchestrator.process_prediction_event(
                tracking_batch=track_batch,
                event_engine=self.event_engine,
                analytics_engine=self.analytics_engine,
                zone_area_m2=100.0,
                scene_id=scene_id,
                zone_id=zone_id
            )

        # Confirm event was resolved and moved to history archive
        self.assertEqual(len(self.event_engine.get_active_events()), 0, "Event must resolve after sustained safe conditions")
        history = self.event_engine.get_event_history()
        self.assertEqual(len(history), 1, "Resolved event must be archived in immutable history")
        self.assertEqual(history[0].status, "RESOLVED")

        # Confirm summary metrics
        summary = self.event_engine.generate_summary()
        self.assertEqual(summary["active_event_count"], 0)
        self.assertEqual(summary["history_statistics"]["resolved_events"], 1)


if __name__ == "__main__":
    unittest.main()
