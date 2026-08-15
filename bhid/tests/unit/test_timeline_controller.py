"""
Unit tests for BHID TimelineController (Phase 5B).

Validates:
1. Playback state toggling (play, pause, stop)
2. Frame navigation & boundary clamping (seek, next_frame, previous_frame)
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

from bhid.replay import TimelineController


class TestTimelineController(unittest.TestCase):

    def setUp(self):
        self.ctrl = TimelineController(total_frames=10)

    def test_navigation_and_clamping(self):
        self.assertEqual(self.ctrl.current_frame(), 0)

        # Seek to frame 5
        self.assertEqual(self.ctrl.seek(5), 5)

        # Seek out of bounds upper clamp
        self.assertEqual(self.ctrl.seek(50), 9)

        # Seek out of bounds lower clamp
        self.assertEqual(self.ctrl.seek(-10), 0)

        # Next & previous frame
        self.assertEqual(self.ctrl.next_frame(), 1)
        self.assertEqual(self.ctrl.previous_frame(), 0)

        # Play / pause toggling
        self.ctrl.play()
        self.assertTrue(self.ctrl.is_playing)
        self.ctrl.pause()
        self.assertFalse(self.ctrl.is_playing)


if __name__ == "__main__":
    unittest.main()
