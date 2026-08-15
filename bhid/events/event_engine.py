"""
BHID Primary Hazard Event Engine.

Primary operational coordinator consuming prediction engine outputs and managing
hazard event creation, escalation, alert suppression, resolution, and history.
"""

from typing import Dict, Any, List, Optional
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.events.hazard_event import HazardEvent
from bhid.events.event_lifecycle_manager import EventLifecycleManager
from bhid.events.alert_policy import AlertPolicy


class HazardEventEngine:
    """
    Main hazard event engine orchestrating operational alert lifecycle.
    
    Parameters:
        lifecycle_manager: Optional EventLifecycleManager instance.
    """

    def __init__(self, lifecycle_manager: Optional[EventLifecycleManager] = None):
        self.lifecycle_manager = lifecycle_manager or EventLifecycleManager()

    def process_prediction(
        self,
        prediction_result: RuntimePredictionResult
    ) -> Optional[HazardEvent]:
        """
        Processes a RuntimePredictionResult and returns the impacted HazardEvent (if created or updated).
        
        Args:
            prediction_result: Output from Phase 3D BottleneckPredictor.
            
        Returns:
            Affected HazardEvent instance, or None if prediction is safe and no event is active.
        """
        return self.lifecycle_manager.process_prediction(prediction_result)

    def get_active_events(self) -> List[HazardEvent]:
        """Returns list of currently active and escalated hazard events."""
        return self.lifecycle_manager.registry.get_active_events()

    def get_event_history(self) -> List[HazardEvent]:
        """Returns list of archived historical events."""
        return self.lifecycle_manager.history.get_all_events()

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generates operational summary metrics for active events and archived history.
        """
        active_events = self.get_active_events()
        history_stats = self.lifecycle_manager.history.event_statistics()

        return {
            "active_event_count": len(active_events),
            "active_events": [e.to_dict() for e in active_events],
            "history_statistics": history_stats
        }

    def reset(self) -> None:
        """Resets engine state, active registry, and history."""
        self.lifecycle_manager.reset()
