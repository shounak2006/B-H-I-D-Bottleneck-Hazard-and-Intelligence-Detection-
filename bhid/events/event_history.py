"""
BHID Immutable Event History Archive.

Archives resolved hazard event records permanently and computes operational statistics.
"""

from typing import Dict, Any, List
import copy
from bhid.events.hazard_event import HazardEvent


class EventHistory:
    """
    Immutable historical archive for resolved hazard events.
    """

    def __init__(self):
        self._history: List[HazardEvent] = []

    def archive_event(self, event: HazardEvent) -> None:
        """
        Archives a resolved HazardEvent by storing an immutable deep copy.
        """
        archived_copy = copy.deepcopy(event)
        self._history.append(archived_copy)

    def get_all_events(self) -> List[HazardEvent]:
        """Returns deep copies of all archived historical events."""
        return [copy.deepcopy(e) for e in self._history]

    def event_statistics(self) -> Dict[str, Any]:
        """
        Computes operational event statistics over archived event history.
        """
        total = len(self._history)
        if total == 0:
            return {
                "total_events": 0,
                "resolved_events": 0,
                "average_duration_seconds": 0.0,
                "total_escalations": 0,
                "max_probability_observed": 0.0
            }

        resolved_count = sum(1 for e in self._history if e.status == "RESOLVED")
        durations = [e.duration_seconds() for e in self._history]
        avg_duration = sum(durations) / float(total)
        total_escalations = sum(e.escalation_count for e in self._history)
        max_prob = max(e.prediction_probability for e in self._history)

        return {
            "total_events": total,
            "resolved_events": resolved_count,
            "average_duration_seconds": round(avg_duration, 4),
            "total_escalations": total_escalations,
            "max_probability_observed": round(max_prob, 4)
        }

    def clear(self) -> None:
        """Clears event history archive."""
        self._history.clear()
