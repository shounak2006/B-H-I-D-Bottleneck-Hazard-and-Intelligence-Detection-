"""
Unit tests for BHID HeatmapRenderer (Phase 4F).

Validates:
1. Crowd density heatmap accumulation
2. OpenCV colormap application
3. Alpha blending heatmap overlays over video frames
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

from bhid.vision.tracking import TrackedObject, TrackingBatch
from bhid.visualization.heatmap_renderer import HeatmapRenderer


class TestHeatmapRenderer(unittest.TestCase):

    def setUp(self):
        self.renderer = HeatmapRenderer()
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)

        t1 = TrackedObject(track_id=1, bbox=(100, 100, 140, 200), confidence=0.9, timestamp=10.0)
        t2 = TrackedObject(track_id=2, bbox=(200, 200, 240, 300), confidence=0.8, timestamp=10.0)
        self.track_batch = TrackingBatch(frame_id=1, timestamp=10.0, active_tracks=[t1, t2])

    def test_heatmap_generation(self):
        heatmap = self.renderer.generate_density_heatmap(self.track_batch, image_width=640, image_height=480)
        self.assertEqual(heatmap.shape, (480, 640, 3))
        self.assertEqual(heatmap.dtype, np.uint8)

    def test_heatmap_overlay(self):
        blended = self.renderer.overlay_heatmap(self.frame, self.track_batch, alpha=0.4)
        self.assertEqual(blended.shape, self.frame.shape)
        self.assertEqual(blended.dtype, np.uint8)


if __name__ == "__main__":
    unittest.main()
