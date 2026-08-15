"""
BHID Hazard Event Renderer Utilities.

Provides active hazard alert banners, event status overlays, and operational warning boxes on image frames.
"""

from typing import Dict, Any, List, Optional, Tuple
import cv2
import numpy as np
from bhid.visualization.visual_config import VisualConfig
from bhid.events.hazard_event import HazardEvent


class EventRenderer:
    """
    Hazard event visual alert renderer.
    
    Parameters:
        config: Optional VisualConfig instance.
    """

    def __init__(self, config: Optional[VisualConfig] = None):
        self.config = config or VisualConfig()

    def draw_event_status(
        self,
        frame: np.ndarray,
        event: HazardEvent,
        origin: Tuple[int, int] = (15, 100)
    ) -> np.ndarray:
        """
        Draws detailed status card for a single HazardEvent.
        """
        out_frame = frame.copy()
        ox, oy = origin
        
        color = self.config.get_risk_color(event.risk_level)

        # Alert box dimensions
        box_w, box_h = 320, 110
        cv2.rectangle(out_frame, (ox, oy), (ox + box_w, oy + box_h), (15, 15, 15), -1)
        cv2.rectangle(out_frame, (ox, oy), (ox + box_w, oy + box_h), color, 2)

        header = f"ALERT: {event.risk_level} ({event.status})"
        line1 = f"ID: {event.event_id}"
        line2 = f"ZONE: {event.scene_id} / {event.zone_id}"
        line3 = f"DURATION: {event.duration_seconds():.1f}s | ESC: {event.escalation_count}"

        cv2.putText(out_frame, header, (ox + 10, oy + 25), self.config.font_face, 0.6, color, 2, cv2.LINE_AA)
        cv2.putText(out_frame, line1, (ox + 10, oy + 50), self.config.font_face, 0.45, self.config.text_color, 1, cv2.LINE_AA)
        cv2.putText(out_frame, line2, (ox + 10, oy + 70), self.config.font_face, 0.45, self.config.text_color, 1, cv2.LINE_AA)
        cv2.putText(out_frame, line3, (ox + 10, oy + 92), self.config.font_face, 0.45, (0, 220, 255), 1, cv2.LINE_AA)

        return out_frame

    def draw_active_events(
        self,
        frame: np.ndarray,
        active_events: List[HazardEvent]
    ) -> np.ndarray:
        """
        Renders stacked alert banners for all currently active hazard events.
        """
        out_frame = frame.copy()
        if not active_events:
            return out_frame

        start_y = 100
        for i, event in enumerate(active_events):
            y_pos = start_y + (i * 125)
            if y_pos + 110 > out_frame.shape[0]:
                break
            out_frame = self.draw_event_status(out_frame, event, origin=(15, y_pos))

        return out_frame

    def draw_alert_annotations(
        self,
        frame: np.ndarray,
        event: HazardEvent
    ) -> np.ndarray:
        """
        Renders prominent center alert warning banner across screen if risk level is CRITICAL.
        """
        out_frame = frame.copy()
        if event.risk_level != "CRITICAL":
            return out_frame

        h, w = out_frame.shape[:2]
        banner_h = 50
        cv2.rectangle(out_frame, (0, 0), (w, banner_h), (0, 0, 255), -1)

        alert_msg = f"*** CRITICAL BOTTLENECK HAZARD DETECTED IN {event.zone_id} ***"
        txt_size = cv2.getTextSize(alert_msg, self.config.font_face, 0.65, 2)[0]
        text_x = max(10, (w - txt_size[0]) // 2)

        cv2.putText(out_frame, alert_msg, (text_x, 33), self.config.font_face, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
        return out_frame
