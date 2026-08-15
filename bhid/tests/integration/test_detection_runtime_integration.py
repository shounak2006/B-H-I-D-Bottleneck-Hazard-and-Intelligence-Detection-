"""
Integration test for BHID Vision Detection Layer & Runtime Orchestrator (Phase 4B).

Validates complete data flow:
Mock Detector (Synthetic Vision Ingestion)
      ↓
Detection Batch (Frame-Level Detections)
      ↓
Detection Adapter (Detection-Level Spatial Aggregation)
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

from bhid.vision.detection import MockPedestrianDetector, DetectionAdapter, DetectionBatch
from bhid.runtime import RuntimeOrchestrator, PipelineContext


class TestDetectionRuntimeIntegration(unittest.TestCase):

    def setUp(self):
        self.detector = MockPedestrianDetector(num_pedestrians=25, seed=777)
        self.adapter = DetectionAdapter(default_zone_area_m2=100.0)
        self.context = PipelineContext(active_scene="TEST_CAM_01", active_zone="ENTRANCE_ZONE")
        self.orchestrator = RuntimeOrchestrator(context=self.context)

    def test_mock_detector_to_adapter_flow(self):
        # 1. Generate frame detection batch
        batch = self.detector.detect(frame=None, frame_id=101, timestamp=500.0)
        self.assertEqual(batch.pedestrian_count(), 25)

        # 2. Adapt batch into detection observation
        obs = self.adapter.adapt_batch(batch, zone_area_m2=100.0, confidence_threshold=0.50)
        self.assertIn("pedestrian_count", obs)
        self.assertIn("density_ped_per_m2", obs)
        self.assertIn("occupancy_ratio", obs)
        self.assertIn("mean_confidence", obs)
        
        self.assertEqual(obs["pedestrian_count"], 25)
        self.assertEqual(obs["density_ped_per_m2"], 0.25)  # 25 peds / 100 m^2

    def test_detection_orchestrator_ingestion(self):
        # Process a sequence of 5 detection batches
        for frame_idx in range(5):
            ts = 1000.0 + (frame_idx * 0.4)
            self.detector.set_pedestrian_count(10 + frame_idx * 5)
            batch = self.detector.detect(frame_id=frame_idx, timestamp=ts)
            
            obs = self.orchestrator.process_detection_batch(
                detection_batch=batch,
                zone_area_m2=100.0,
                scene_id="SCENE_DET_01",
                zone_id="ZONE_GATE_A",
                adapter=self.adapter
            )

            self.assertEqual(obs["frame_id"], frame_idx)
            self.assertEqual(obs["pedestrian_count"], 10 + frame_idx * 5)

        # Verify context state updates
        ctx = self.orchestrator.get_context()
        self.assertEqual(ctx.active_scene, "SCENE_DET_01")
        self.assertEqual(ctx.active_zone, "ZONE_GATE_A")
        self.assertEqual(ctx.runtime_metadata["processed_frames"], 5)


if __name__ == "__main__":
    unittest.main()
