"""
BHID Event Lifecycle Manager.

Coordinates hazard event state transitions (NEW -> ACTIVE -> ESCALATED -> RESOLVED),
zone-level alert suppression, and safe condition tracking.
"""

from typing import Dict, Any, Optional, Tuple
from bhid.runtime.runtime_prediction_result import RuntimePredictionResult
from bhid.events.hazard_event import HazardEvent
from bhid.events.alert_policy import AlertPolicy
from bhid.events.event_registry import EventRegistry
from bhid.events.event_history import EventHistory


class EventLifecycleManager:
    """
    Manages state transition logic and alert suppression for hazard events.
    
    Parameters:
        alert_policy: Optional AlertPolicy instance.
        registry: Optional EventRegistry instance.
        history: Optional EventHistory instance.
    """

    def __init__(
        self,
        alert_policy: Optional[AlertPolicy] = None,
        registry: Optional[EventRegistry] = None,
        history: Optional[EventHistory] = None
    ):
        self.policy = alert_policy or AlertPolicy()
        self.registry = registry or EventRegistry()
        self.history = history or EventHistory()
        
        # consecutive safe predictions per (scene_id, zone_id)
        self._consecutive_safe_counts: Dict[Tuple[str, str], int] = {}

    def process_prediction(self, result: RuntimePredictionResult) -> Optional[HazardEvent]:
        """
        Ingests a RuntimePredictionResult, evaluates alert policy rules,
        updates event state transitions, and manages registry and history storage.
        
        Args:
            result: RuntimePredictionResult from Phase 3D BottleneckPredictor.
            
        Returns:
            Affected HazardEvent instance, or None if no event was created or active.
        """
        zone_key = (result.scene_id, result.zone_id)
        active_event = self.registry.get_active_event_for_zone(result.scene_id, result.zone_id)

        # Scenario A: An active event already exists for this zone
        if active_event is not None:
            # Check 1: Should we escalate active event?
            if self.policy.should_escalate_event(active_event, result):
                active_event.escalate(
                    probability=result.prediction_probability,
                    risk_level=result.risk_level,
                    timestamp=result.timestamp
                )
                self._consecutive_safe_counts[zone_key] = 0
                return active_event

            # Check 2: Is incoming prediction safe?
            is_safe_prediction = not self.policy.should_create_event(result)
            
            if is_safe_prediction:
                current_safe = self._consecutive_safe_counts.get(zone_key, 0) + 1
                self._consecutive_safe_counts[zone_key] = current_safe
                
                # Check 3: Have we reached sustained safe resolution threshold?
                if self.policy.should_resolve_event(active_event, current_safe):
                    resolved_event = self.registry.resolve_event(
                        event_id=active_event.event_id,
                        timestamp=result.timestamp
                    )
                    if resolved_event is not None:
                        self.history.archive_event(resolved_event)
                        self._consecutive_safe_counts[zone_key] = 0
                        return resolved_event
                else:
                    # Not resolved yet; record safe prediction in history
                    active_event.update_prediction(
                        probability=result.prediction_probability,
                        risk_level=result.risk_level,
                        timestamp=result.timestamp
                    )
                    return active_event
            else:
                # Active hazard continues; reset safe prediction counter
                self._consecutive_safe_counts[zone_key] = 0
                active_event.update_prediction(
                    probability=result.prediction_probability,
                    risk_level=result.risk_level,
                    timestamp=result.timestamp
                )
                return active_event

        # Scenario B: No active event currently exists for this zone
        else:
            if self.policy.should_create_event(result):
                event_id = f"HAZARD_{result.scene_id}_{result.zone_id}_{int(result.timestamp)}"
                new_event = HazardEvent(
                    event_id=event_id,
                    scene_id=result.scene_id,
                    zone_id=result.zone_id,
                    start_timestamp=result.timestamp,
                    last_updated_timestamp=result.timestamp,
                    prediction_probability=result.prediction_probability,
                    risk_level=result.risk_level,
                    target_horizon=result.target_horizon,
                    status="ACTIVE"
                )
                self.registry.register_event(new_event)
                self._consecutive_safe_counts[zone_key] = 0
                return new_event
            else:
                # Normal safe condition, no event active or created
                self._consecutive_safe_counts[zone_key] = self._consecutive_safe_counts.get(zone_key, 0) + 1
                return None

    def reset(self) -> None:
        """Resets registry, history, and safe count state memory."""
        self.registry.clear()
        self.history.clear()
        self._consecutive_safe_counts.clear()
