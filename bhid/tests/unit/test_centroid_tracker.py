"""
Unit tests for BHID CentroidTracker (Phase 4C).

Validates:
1. Track creation & centroid matching association
2. Track persistence & ID stability across frames
3. Track expiration after max_disappeared_frames
4. Non-reuse of track IDs across session (monotonically increasing IDs)
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
from bhid.vision.tracking.centroid_tracker import CentroidTracker


class TestCentroidTracker(unittest.TestCase):

    def setUp(self):
        self.tracker = CentroidTracker(max_disappeared_frames=2, max_match_distance=50.0, min_confidence=0.50)

    def test_initial_track_registration(self):
        d1 = Detection("d1", confidence=0.9, bbox_x1=0, bbox_y1=0, bbox_x2=10, bbox_y2=20, frame_id=1, timestamp=1.0)
        d2 = Detection("d2", confidence=0.8, bbox_x1=100, bbox_y1=100, bbox_x2=110, bbox_y2=120, frame_id=1, timestamp=1.0)
        batch = DetectionBatch(frame_id=1, timestamp=1.0, detections=[d1, d2])

        tb = self.tracker.update(batch)
        self.assertEqual(tb.active_count(), 2)
        track_ids = tb.get_track_ids()
        self.assertEqual(track_ids, [1, 2])

    def test_track_persistence_across_frames(self):
        # Frame 1
        d1 = Detection("d1", confidence=0.9, bbox_x1=0, bbox_y1=0, bbox_x2=10, bbox_y2=20, frame_id=1, timestamp=1.0)
        tb1 = self.tracker.update(DetectionBatch(frame_id=1, timestamp=1.0, detections=[d1]))
        self.assertEqual(tb1.get_track_ids(), [1])

        # Frame 2: detection moved slightly (center shifted from (5,10) to (7,12))
        d1_moved = Detection("d1_2", confidence=0.9, bbox_x1=2, bbox_y1=2, bbox_x2=12, bbox_y2=22, frame_id=2, timestamp=1.4)
        tb2 = self.tracker.update(DetectionBatch(frame_id=2, timestamp=1.4, detections=[d1_moved]))
        self.assertEqual(tb2.get_track_ids(), [1])
        
        # Verify trajectory has 2 points
        track = self.tracker.tracks[1]
        self.assertEqual(len(track.trajectory_history.points), 2)
        self.assertEqual(track.age_frames, 2)
        self.assertEqual(track.missed_frames, 0)

    def test_track_expiration(self):
        # Frame 1: Register track #1
        d1 = Detection("d1", confidence=0.9, bbox_x1=0, bbox_y1=0, bbox_x2=10, bbox_y2=20, frame_id=1, timestamp=1.0)
        self.tracker.update(DetectionBatch(frame_id=1, timestamp=1.0, detections=[d1]))
        self.assertIn(1, self.tracker.tracks)

        # Empty frames: missed count increments
        self.tracker.update(DetectionBatch(frame_id=2, timestamp=1.4, detections=[]))  # missed = 1
        self.assertIn(1, self.tracker.tracks)

        self.tracker.update(DetectionBatch(frame_id=3, timestamp=1.8, detections=[]))  # missed = 2
        self.assertIn(1, self.tracker.tracks)

        # 3rd empty frame: missed = 3 > max_disappeared_frames (2) -> track #1 expires
        tb4 = self.tracker.update(DetectionBatch(frame_id=4, timestamp=2.2, detections=[]))
        self.assertNotIn(1, self.tracker.tracks)
        self.assertEqual(tb4.active_count(), 0)

    def test_track_id_non_reuse(self):
        """Verify that track IDs are NEVER reused after expiration."""
        # 1. Register track #1
        d1 = Detection("d1", confidence=0.9, bbox_x1=0, bbox_y1=0, bbox_x2=10, bbox_y2=20, frame_id=1, timestamp=1.0)
        self.tracker.update(DetectionBatch(frame_id=1, timestamp=1.0, detections=[d1]))
        self.assertIn(1, self.tracker.tracks)

        # 2. Expire track #1 over 3 empty frames
        for f in range(2, 5):
            self.tracker.update(DetectionBatch(frame_id=f, timestamp=1.0 + f * 0.4, detections=[]))
        self.assertEqual(len(self.tracker.tracks), 0)

        # 3. Register a new detection -> Must be assigned track ID #2, NOT #1
        d2 = Detection("d2", confidence=0.9, bbox_x1=0, bbox_y1=0, bbox_x2=10, bbox_y2=20, frame_id=5, timestamp=3.0)
        tb5 = self.tracker.update(DetectionBatch(frame_id=5, timestamp=3.0, detections=[d2]))
        
        self.assertEqual(tb5.get_track_ids(), [2], "Track ID #1 must not be reused! Expected Track #2.")


if __name__ == "__main__":
    unittest.main()
