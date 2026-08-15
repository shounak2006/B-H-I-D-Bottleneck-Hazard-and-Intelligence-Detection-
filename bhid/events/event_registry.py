"""
BHID Active Hazard Event Registry.

Maintains active and escalated hazard events in memory and enforces zone-level
duplicate suppression.
"""

from typing import Dict, Any, List, Optional, Tuple
from bhid.events.hazard_event import HazardEvent


class EventRegistry:
    """
    In-memory registry tracking currently active hazard events.
    Keyed by unique event_id and spatial location tuple (scene_id, zone_id).
    """

    def __init__(self):
        self._active_events_by_id: Dict[str, HazardEvent] = {}
        self._active_events_by_zone: Dict[Tuple[str, str], HazardEvent] = {}

    def register_event(self, event: HazardEvent) -> bool:
        """
        Registers a new active HazardEvent.
        
        Args:
            event: HazardEvent instance.
            
        Returns:
            True if registered successfully, False if an active event already exists for zone.
        """
        zone_key = (event.scene_id, event.zone_id)
        if zone_key in self._active_events_by_zone:
            # Active event already exists for this zone -> Suppress duplicate creation
            return False

        self._active_events_by_id[event.event_id] = event
        self._active_events_by_zone[zone_key] = event
        return True

    def get_active_events(self) -> List[HazardEvent]:
        """Returns list of all currently active hazard events."""
        return list(self._active_events_by_id.values())

    def get_active_event_for_zone(
        self,
        scene_id: str,
        zone_id: str
    ) -> Optional[HazardEvent]:
        """
        Retrieves active HazardEvent for the specified scene and zone, or None if no active event exists.
        Provides primary lookup for alert suppression.
        """
        return self._active_events_by_zone.get((str(scene_id), str(zone_id)))

    def get_event_by_id(self, event_id: str) -> Optional[HazardEvent]:
        """Retrieves active event by its unique event ID."""
        return self._active_events_by_id.get(str(event_id))

    def resolve_event(
        self,
        event_id: str,
        timestamp: float
    ) -> Optional[HazardEvent]:
        """
        Marks active event as RESOLVED and removes it from active registry.
        
        Returns:
            Resolved HazardEvent, or None if event ID was not found.
        """
        event = self.get_event_by_id(event_id)
        if event is None:
            return None

        event.resolve(timestamp=timestamp)
        zone_key = (event.scene_id, event.zone_id)
        
        del self._active_events_by_id[event.event_id]
        if zone_key in self._active_events_by_zone:
            del self._active_events_by_zone[zone_key]

        return event

    def clear(self) -> None:
        """Clears all active events from registry."""
        self._active_events_by_id.clear()
        self._active_events_by_zone.clear()
