"""
Unit tests for BHID TrackedObject Model (Phase 4C).

Validates:
1. TrackedObject creation & initial state setup
2. Center point calculation from bounding box
3. State update & trajectory history appending
4. Missed-frame marking & age tracking
5. Serialization to dictionary representation
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

from bhid.vision.tracking.tracked_object import TrackedObject


class TestTrackedObject(unittest.TestCase):

    def test_creation_and_center(self):
        obj = TrackedObject(
            track_id=1,
            bbox=(100.0, 100.0, 200.0, 300.0),
            confidence=0.90,
            timestamp=10.0,
            frame_id=1
        )

        self.assertEqual(obj.track_id, 1)
        self.assertEqual(obj.current_bbox, (100.0, 100.0, 200.0, 300.0))
        self.assertEqual(obj.get_center(), (150.0, 200.0))
        self.assertEqual(obj.age_frames, 1)
        self.assertEqual(obj.missed_frames, 0)
        self.assertEqual(len(obj.trajectory_history.points), 1)

    def test_update_and_missed_handling(self):
        obj = TrackedObject(
            track_id=2,
            bbox=(0.0, 0.0, 10.0, 20.0),
            confidence=0.80,
            timestamp=100.0,
            frame_id=1
        )

        # Update track
        obj.update(bbox=(10.0, 0.0, 20.0, 20.0), confidence=0.85, timestamp=101.0, frame_id=2)
        self.assertEqual(obj.age_frames, 2)
        self.assertEqual(obj.missed_frames, 0)
        self.assertEqual(len(obj.trajectory_history.points), 2)
        self.assertEqual(obj.get_center(), (15.0, 10.0))

        # Mark missed
        obj.mark_missed()
        self.assertEqual(obj.age_frames, 3)
        self.assertEqual(obj.missed_frames, 1)
        self.assertEqual(len(obj.trajectory_history.points), 2)  # trajectory length unchanged

    def test_to_dict(self):
        obj = TrackedObject(
            track_id=7,
            bbox=(10.0, 10.0, 30.0, 50.0),
            confidence=0.95,
            timestamp=50.0,
            frame_id=10
        )
        d = obj.to_dict()
        self.assertEqual(d["track_id"], 7)
        self.assertEqual(d["current_bbox"], [10.0, 10.0, 30.0, 50.0])
        self.assertEqual(d["center"], [20.0, 30.0])
        self.assertEqual(d["age_frames"], 1)
        self.assertEqual(d["missed_frames"], 0)


if __name__ == "__main__":
    unittest.main()
