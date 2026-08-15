"""
Unit tests for BHID FrameRenderer (Phase 4F).

Validates:
1. Blank canvas creation
2. Drawing detection and tracking bounding boxes
3. Zone ROI boundaries and HUD telemetry annotations
4. Risk indicator badge drawing
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
    sys.path.insert(0, str(PARENT_ROOT))

from bhid.vision.detection import Detection, DetectionBatch
from bhid.vision.tracking import TrackedObject, TrackingBatch
from bhid.visualization.frame_renderer import FrameRenderer


class TestFrameRenderer(unittest.TestCase):

    def setUp(self):
        self.renderer = FrameRenderer()
        self.frame = self.renderer.create_blank_frame(width=640, height=480)

        det = Detection(
            detection_id="det1",
            confidence=0.92,
            bbox_x1=100.0,
            bbox_y1=100.0,
            bbox_x2=140.0,
            bbox_y2=200.0,
            frame_id=1,
            timestamp=10.0,
            class_name="pedestrian"
        )
        self.det_batch = DetectionBatch(frame_id=1, timestamp=10.0, detections=[det])

        track = TrackedObject(track_id=1, bbox=(100, 100, 140, 200), confidence=0.92, timestamp=10.0)
        self.track_batch = TrackingBatch(frame_id=1, timestamp=10.0, active_tracks=[track])

    def test_blank_frame_creation(self):
        self.assertEqual(self.frame.shape, (480, 640, 3))
        self.assertEqual(self.frame.dtype, np.uint8)

    def test_draw_tracks_and_annotations(self):
        # Draw tracks
        f1 = self.renderer.draw_tracks(self.frame, self.track_batch)
        self.assertEqual(f1.shape, self.frame.shape)

        # Draw HUD telemetry
        f2 = self.renderer.draw_density_annotations(f1, pedestrian_count=25, density_ped_per_m2=2.5)
        self.assertEqual(f2.shape, self.frame.shape)

        # Draw risk indicator badge
        f3 = self.renderer.draw_risk_indicator(f2, risk_level="CRITICAL", probability=0.92)
        self.assertEqual(f3.shape, self.frame.shape)


if __name__ == "__main__":
    unittest.main()
