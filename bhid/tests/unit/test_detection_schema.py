"""
Unit tests for BHID Detection Schema (Phase 4B).

Validates:
1. Detection object creation & property computations (area, center, width, height)
2. Schema coordinate validation & invalid bounding box rejection
3. Confidence boundary validation
4. Dictionary serialization and deserialization
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

from bhid.vision.detection.detection_schema import Detection, DetectionValidationError


class TestDetectionSchema(unittest.TestCase):

    def test_valid_detection_creation(self):
        det = Detection(
            detection_id="det_001",
            class_name="pedestrian",
            confidence=0.92,
            bbox_x1=100.0,
            bbox_y1=150.0,
            bbox_x2=200.0,
            bbox_y2=450.0,
            frame_id=1,
            timestamp=10.5
        )
        self.assertEqual(det.detection_id, "det_001")
        self.assertEqual(det.class_name, "pedestrian")
        self.assertEqual(det.confidence, 0.92)
        self.assertEqual(det.width, 100.0)
        self.assertEqual(det.height, 300.0)
        self.assertEqual(det.area, 30000.0)
        self.assertEqual(det.center, (150.0, 300.0))

    def test_invalid_x_coordinates_rejection(self):
        with self.assertRaises(DetectionValidationError) as ctx:
            Detection(
                detection_id="det_bad_x",
                confidence=0.8,
                bbox_x1=200.0,  # x1 > x2
                bbox_y1=100.0,
                bbox_x2=100.0,
                bbox_y2=300.0
            )
        self.assertIn("Invalid bbox X coordinates", str(ctx.exception))

    def test_invalid_y_coordinates_rejection(self):
        with self.assertRaises(DetectionValidationError) as ctx:
            Detection(
                detection_id="det_bad_y",
                confidence=0.8,
                bbox_x1=100.0,
                bbox_y1=300.0,  # y1 > y2
                bbox_x2=200.0,
                bbox_y2=100.0
            )
        self.assertIn("Invalid bbox Y coordinates", str(ctx.exception))

    def test_invalid_confidence_rejection(self):
        with self.assertRaises(DetectionValidationError):
            Detection("det_bad_conf", confidence=1.5, bbox_x1=0, bbox_y1=0, bbox_x2=10, bbox_y2=10)

        with self.assertRaises(DetectionValidationError):
            Detection("det_bad_conf", confidence=-0.1, bbox_x1=0, bbox_y1=0, bbox_x2=10, bbox_y2=10)

    def test_to_dict_and_from_dict(self):
        det1 = Detection("det_002", confidence=0.85, bbox_x1=10.0, bbox_y1=20.0, bbox_x2=50.0, bbox_y2=100.0)
        d = det1.to_dict()
        self.assertEqual(d["detection_id"], "det_002")
        self.assertEqual(d["area"], 3200.0)

        det2 = Detection.from_dict(d)
        self.assertEqual(det2.detection_id, det1.detection_id)
        self.assertEqual(det2.confidence, det1.confidence)
        self.assertEqual(det2.bbox_x1, det1.bbox_x1)
        self.assertEqual(det2.area, det1.area)


if __name__ == "__main__":
    unittest.main()
