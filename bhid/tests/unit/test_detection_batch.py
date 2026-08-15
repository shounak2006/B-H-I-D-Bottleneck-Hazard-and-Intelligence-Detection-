"""
Unit tests for BHID DetectionBatch Container (Phase 4B).

Validates:
1. Batch initialization & detection aggregation
2. Pedestrian count filtering with confidence thresholds
3. Statistical confidence summary computation
4. Class-level filtering and confidence thresholding
5. Bounding box list extraction & serialization
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

from bhid.vision.detection.detection_schema import Detection
from bhid.vision.detection.detection_batch import DetectionBatch


class TestDetectionBatch(unittest.TestCase):

    def setUp(self):
        self.d1 = Detection("det_01", confidence=0.90, bbox_x1=0, bbox_y1=0, bbox_x2=10, bbox_y2=20, class_name="pedestrian")
        self.d2 = Detection("det_02", confidence=0.70, bbox_x1=10, bbox_y1=10, bbox_x2=30, bbox_y2=40, class_name="pedestrian")
        self.d3 = Detection("det_03", confidence=0.40, bbox_x1=50, bbox_y1=50, bbox_x2=70, bbox_y2=90, class_name="pedestrian")
        self.d4 = Detection("det_04", confidence=0.95, bbox_x1=100, bbox_y1=100, bbox_x2=120, bbox_y2=140, class_name="vehicle")

        self.batch = DetectionBatch(
            frame_id=42,
            timestamp=100.0,
            detections=[self.d1, self.d2, self.d3, self.d4],
            image_width=1920.0,
            image_height=1080.0
        )

    def test_pedestrian_count(self):
        self.assertEqual(self.batch.pedestrian_count(confidence_threshold=0.0), 3)
        self.assertEqual(self.batch.pedestrian_count(confidence_threshold=0.50), 2)
        self.assertEqual(self.batch.pedestrian_count(confidence_threshold=0.92), 0)

    def test_confidence_summary(self):
        summary = self.batch.confidence_summary()
        self.assertEqual(summary["count"], 4)
        self.assertAlmostEqual(summary["mean"], (0.90 + 0.70 + 0.40 + 0.95) / 4.0, places=3)
        self.assertEqual(summary["min"], 0.40)
        self.assertEqual(summary["max"], 0.95)

    def test_filter_by_class(self):
        peds = self.batch.filter_by_class("pedestrian")
        self.assertEqual(len(peds), 3)
        vehicles = self.batch.filter_by_class("vehicle")
        self.assertEqual(len(vehicles), 1)

    def test_filter_by_confidence(self):
        filtered = self.batch.filter_by_confidence(min_confidence=0.50)
        self.assertIsInstance(filtered, DetectionBatch)
        self.assertEqual(len(filtered.detections), 3)  # d1, d2, d4
        self.assertEqual(filtered.frame_id, 42)

    def test_get_bboxes(self):
        bboxes = self.batch.get_bboxes()
        self.assertEqual(len(bboxes), 4)
        self.assertEqual(bboxes[0], (0.0, 0.0, 10.0, 20.0))

    def test_serialization(self):
        d = self.batch.to_dict()
        self.assertEqual(d["frame_id"], 42)
        self.assertEqual(d["count"], 4)
        self.assertEqual(d["pedestrian_count"], 3)
        self.assertIn("confidence_summary", d)


if __name__ == "__main__":
    unittest.main()
