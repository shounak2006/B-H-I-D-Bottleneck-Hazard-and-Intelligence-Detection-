"""
BHID Event Timeline Reconstructor.

Reconstructs historical hazard-event state transitions (ACTIVE, ESCALATED, RESOLVED)
and provides timestamp-based active hazard event lookups for replay.
"""

from typing import List, Dict, Any, Optional


class EventTimeline:
    """
    Chronological hazard-event timeline index builder and query interface.
    """

    def __init__(self, events: Optional[List[Dict[str, Any]]] = None):
        self._events: Dict[str, Dict[str, Any]] = {}
        if events:
            self.build_timeline(events)

    def build_timeline(self, events: List[Dict[str, Any]]) -> None:
        """Indexes raw persisted event records by event_id."""
        self._events.clear()
        for evt in events:
            eid = str(evt.get("event_id"))
            self._events[eid] = dict(evt)

    def get_active_events_at(self, timestamp: float) -> List[Dict[str, Any]]:
        """
        Returns list of hazard event dictionaries that were active at the given timestamp.
        An event is active at time T if start_timestamp <= T <= resolved_timestamp (or end of recording).
        """
        active = []
        for evt in self._events.values():
            start_ts = float(evt.get("start_timestamp", 0.0))
            last_ts = float(evt.get("last_updated_timestamp", start_ts))
            res_ts = evt.get("resolved_timestamp")
            end_ts = float(res_ts) if res_ts is not None else (last_ts + 1.0)

            if start_ts <= timestamp <= end_ts:
                active.append(dict(evt))

        return active

    def get_event_history(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Returns historical record for a specific event_id."""
        evt = self._events.get(str(event_id))
        return dict(evt) if evt else None

    def get_event_transitions(self) -> List[Dict[str, Any]]:
        """Returns chronologically ordered list of all hazard event status transitions."""
        transitions = []
        for evt in self._events.values():
            eid = evt.get("event_id")
            scene_id = evt.get("scene_id")
            zone_id = evt.get("zone_id")
            history = evt.get("prediction_history", [])

            for h in history:
                transitions.append({
                    "event_id": eid,
                    "scene_id": scene_id,
                    "zone_id": zone_id,
                    "timestamp": h.get("timestamp"),
                    "status": h.get("status"),
                    "prediction_probability": h.get("prediction_probability"),
                    "risk_level": h.get("risk_level")
                })

        transitions.sort(key=lambda x: float(x.get("timestamp", 0.0)))
        return transitions
