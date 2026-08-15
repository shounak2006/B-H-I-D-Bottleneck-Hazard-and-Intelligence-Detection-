"""
Unit tests for BHID EventRegistry (Phase 4E).

Validates:
1. Event registration & active list retrieval
2. Zone-level duplicate event suppression
3. Retrieval by ID and location lookup
4. Event resolution & active registry removal
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

from bhid.events.hazard_event import HazardEvent
from bhid.events.event_registry import EventRegistry


class TestEventRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = EventRegistry()
        self.e1 = HazardEvent("E1", "S1", "Z1", 100.0, 100.0, 0.70, "HIGH")

    def test_registration_and_duplicate_suppression(self):
        # Register E1
        success1 = self.registry.register_event(self.e1)
        self.assertTrue(success1)
        self.assertEqual(len(self.registry.get_active_events()), 1)

        # Attempt to register duplicate event for same zone (S1, Z1) -> Suppressed
        e1_dup = HazardEvent("E1_DUP", "S1", "Z1", 102.0, 102.0, 0.75, "HIGH")
        success2 = self.registry.register_event(e1_dup)
        self.assertFalse(success2)
        self.assertEqual(len(self.registry.get_active_events()), 1)

    def test_lookup_and_resolution(self):
        self.registry.register_event(self.e1)
        
        # Lookup by zone
        found = self.registry.get_active_event_for_zone("S1", "Z1")
        self.assertIsNotNone(found)
        self.assertEqual(found.event_id, "E1")

        # Resolve event
        resolved = self.registry.resolve_event("E1", timestamp=110.0)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.status, "RESOLVED")
        
        # Should no longer be active in registry
        self.assertEqual(len(self.registry.get_active_events()), 0)
        self.assertIsNone(self.registry.get_active_event_for_zone("S1", "Z1"))


if __name__ == "__main__":
    unittest.main()
