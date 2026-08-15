"""
Integration test for BHID Vision Tracking Layer & Runtime Orchestrator (Phase 4C).

Validates complete data flow:
Mock Detector (Synthetic Vision Ingestion)
      ↓
Centroid Tracker (Multi-Object Association & Trajectory Generation)
      ↓
Tracking Batch (Frame-Level Active Tracks)
      ↓
Tracking Adapter (Trajectory Observation Aggregation)
      ↓
Runtime Orchestrator (Context State & Metadata Updates)
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
from bhid.vision.tracking import CentroidTracker, TrackingAdapter, TrackingBatch
from bhid.runtime import RuntimeOrchestrator, PipelineContext


class TestTrackingRuntimeIntegration(unittest.TestCase):

    def setUp(self):
        self.detector = MockPedestrianDetector(num_pedestrians=10, seed=999)
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=150.0)
        self.adapter = TrackingAdapter(pixel_to_meter_scale=0.05)
        self.context = PipelineContext(active_scene="CAM_SCENE_02", active_zone="MAIN_HALL")
        self.orchestrator = RuntimeOrchestrator(context=self.context)

    def test_detector_to_tracker_to_runtime_flow(self):
        # Process a sequence of 10 consecutive frames
        track_history = []

        for frame_idx in range(10):
            ts = 1000.0 + (frame_idx * 0.4)
            det_batch = self.detector.detect(frame_id=frame_idx, timestamp=ts)
            
            # Update tracker with detections
            tracking_batch = self.tracker.update(det_batch)
            self.assertIsInstance(tracking_batch, TrackingBatch)
            
            # Ingest tracking batch into runtime orchestrator
            obs = self.orchestrator.process_tracking_batch(
                tracking_batch=tracking_batch,
                zone_area_m2=100.0,
                scene_id="CAM_SCENE_02",
                zone_id="MAIN_HALL",
                adapter=self.adapter
            )

            self.assertEqual(obs["frame_id"], frame_idx)
            self.assertIn("active_track_count", obs)
            self.assertIn("track_ids", obs)
            self.assertIn("mean_speed_m_s", obs)
            
            track_history.append(obs["track_ids"])

        # Confirm context state tracking
        ctx = self.orchestrator.get_context()
        self.assertEqual(ctx.active_scene, "CAM_SCENE_02")
        self.assertEqual(ctx.active_zone, "MAIN_HALL")
        self.assertEqual(ctx.runtime_metadata["processed_frames"], 10)

        # Confirm trajectory history length of active tracks
        active_tracks = self.tracker.tracks.values()
        for track in active_tracks:
            self.assertGreaterEqual(len(track.trajectory_history.points), 1)


if __name__ == "__main__":
    unittest.main()
