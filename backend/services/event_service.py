"""
BHID Event Service.
Interacts with HazardEventEngine and HazardEvent domain classes.
"""

from typing import List, Dict, Any, Optional
from bhid.events.event_engine import HazardEventEngine


class EventService:
    """Service wrapping hazard event queries."""

    def __init__(self, event_engine: Optional[HazardEventEngine] = None):
        self.event_engine = event_engine or HazardEventEngine()

    def get_active_events(self) -> List[Dict[str, Any]]:
        """Returns active hazard events."""
        events = self.event_engine.get_active_events()
        return [e.to_dict() for e in events]

    def get_event_history(self) -> List[Dict[str, Any]]:
        """Returns event history log."""
        events = self.event_engine.get_event_history()
        return [e.to_dict() for e in events]

    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Returns hazard event by ID."""
        for e in self.event_engine.get_active_events():
            if e.event_id == event_id:
                return e.to_dict()
        return None
