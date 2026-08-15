"""
Unit tests for BHID EventRenderer (Phase 4F).

Validates:
1. Active hazard event status card rendering
2. Multiple event banner stacking
3. Critical risk alert annotation banner
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
    sys.path.insert(0, str(PROJECT_ROOT))

from bhid.events.hazard_event import HazardEvent
from bhid.visualization.event_renderer import EventRenderer


class TestEventRenderer(unittest.TestCase):

    def setUp(self):
        self.renderer = EventRenderer()
        self.frame = np.zeros((480, 640, 3), dtype=np.uint8)

        self.event = HazardEvent(
            event_id="HAZARD_001",
            scene_id="SCENE_A",
            zone_id="ZONE_1",
            start_timestamp=100.0,
            last_updated_timestamp=105.0,
            prediction_probability=0.92,
            risk_level="CRITICAL",
            status="ACTIVE"
        )

    def test_event_rendering(self):
        f1 = self.renderer.draw_event_status(self.frame, self.event)
        self.assertEqual(f1.shape, self.frame.shape)

        f2 = self.renderer.draw_active_events(self.frame, [self.event])
        self.assertEqual(f2.shape, self.frame.shape)

        f3 = self.renderer.draw_alert_annotations(self.frame, self.event)
        self.assertEqual(f3.shape, self.frame.shape)


if __name__ == "__main__":
    unittest.main()
