"""
Unit tests for BHID MockPedestrianDetector (Phase 4B).

Validates:
1. Detector lifecycle management (initialize, detect, shutdown)
2. Deterministic synthetic detection generation
3. Dynamic pedestrian count configuration updates
4. Valid DetectionBatch creation with valid Detection items
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

from bhid.vision.detection.mock_detector import MockPedestrianDetector
from bhid.vision.detection.detection_batch import DetectionBatch


class TestMockDetector(unittest.TestCase):

    def setUp(self):
        self.detector = MockPedestrianDetector(num_pedestrians=15, seed=123)

    def test_lifecycle_and_initialization(self):
        self.assertFalse(self.detector.is_initialized)
        self.detector.initialize({"num_pedestrians": 20})
        self.assertTrue(self.detector.is_initialized)
        self.assertEqual(self.detector.num_pedestrians, 20)

        self.detector.shutdown()
        self.assertFalse(self.detector.is_initialized)

    def test_detect_generation(self):
        batch = self.detector.detect(frame=None, frame_id=1, timestamp=10.0)
        self.assertIsInstance(batch, DetectionBatch)
        self.assertEqual(batch.frame_id, 1)
        self.assertEqual(batch.timestamp, 10.0)
        self.assertEqual(len(batch.detections), 15)
        self.assertEqual(batch.pedestrian_count(), 15)

    def test_deterministic_reproducibility(self):
        det1 = MockPedestrianDetector(num_pedestrians=5, seed=42)
        batch1 = det1.detect(frame_id=10, timestamp=5.0)

        det2 = MockPedestrianDetector(num_pedestrians=5, seed=42)
        batch2 = det2.detect(frame_id=10, timestamp=5.0)

        bboxes1 = batch1.get_bboxes()
        bboxes2 = batch2.get_bboxes()
        self.assertEqual(bboxes1, bboxes2)

    def test_set_pedestrian_count(self):
        self.detector.set_pedestrian_count(8)
        batch = self.detector.detect(frame_id=2, timestamp=2.0)
        self.assertEqual(batch.pedestrian_count(), 8)


if __name__ == "__main__":
    unittest.main()
