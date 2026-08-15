"""
BHID Crowd Flow Metrics Calculator.

Computes inflow rate, outflow rate, and net flow rate from track transitions.
"""

from typing import Set, Dict, Any, Optional
from bhid.vision.tracking.tracking_batch import TrackingBatch


class FlowMetricsCalculator:
    """
    Calculates crowd flow metrics based on track entry and exit events between consecutive frames.
    """

    def compute_flow_metrics(
        self,
        current_batch: TrackingBatch,
        prev_track_ids: Optional[Set[Any]] = None,
        dt_seconds: Optional[float] = 0.4
    ) -> Dict[str, float]:
        """
        Computes inflow_rate_per_s, outflow_rate_per_s, and net_flow_rate_per_s.
        
        Args:
            current_batch: Current frame TrackingBatch.
            prev_track_ids: Set of active track IDs from previous frame.
            dt_seconds: Time delta between frames in seconds (default: 0.4s for 2.5Hz).
            
        Returns:
            Dictionary containing computed flow metrics.
        """
        dt = float(dt_seconds) if dt_seconds is not None and dt_seconds > 0 else 0.4
        curr_track_ids = set(current_batch.get_track_ids())

        if prev_track_ids is None:
            # First frame in stream: no previous frame reference
            return {
                "inflow_rate_per_s": 0.0,
                "outflow_rate_per_s": 0.0,
                "net_flow_rate_per_s": 0.0
            }

        # Inflow: track IDs in curr_track_ids but not in prev_track_ids
        inflow_count = len(curr_track_ids - prev_track_ids)
        # Outflow: track IDs in prev_track_ids but not in curr_track_ids
        outflow_count = len(prev_track_ids - curr_track_ids)

        inflow_rate = inflow_count / dt
        outflow_rate = outflow_count / dt
        net_flow_rate = inflow_rate - outflow_rate

        return {
            "inflow_rate_per_s": round(inflow_rate, 4),
            "outflow_rate_per_s": round(outflow_rate, 4),
            "net_flow_rate_per_s": round(net_flow_rate, 4)
        }
