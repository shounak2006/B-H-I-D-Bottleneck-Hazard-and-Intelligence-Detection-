"""
BHID Egress Deficit Metrics Calculator.

Computes the frozen Rule-2 Egress Deficit Ratio (R_egress).
"""

from typing import Dict, Any


class EgressMetricsCalculator:
    """
    Calculates egress deficit ratio using frozen Phase 2 Rule-2 definition.
    """

    def compute_egress_deficit(
        self,
        inflow_rate_per_s: float,
        outflow_rate_per_s: float
    ) -> Dict[str, float]:
        """
        Computes egress_deficit_ratio based on inflow and outflow rates.
        
        Formula:
            R_egress = 1.0 - (Q_out / Q_in)  when Q_in > 0
            R_egress = 0.0                   otherwise
            
        Args:
            inflow_rate_per_s: Rate of inflow (Q_in).
            outflow_rate_per_s: Rate of outflow (Q_out).
            
        Returns:
            Dictionary containing computed egress_deficit_ratio.
        """
        q_in = float(inflow_rate_per_s)
        q_out = float(outflow_rate_per_s)

        if q_in > 0.0:
            r_egress = 1.0 - (q_out / q_in)
        else:
            r_egress = 0.0

        # Clamp egress deficit ratio to valid range [0.0, 1.0]
        r_egress_clamped = max(0.0, min(1.0, r_egress))

        return {
            "egress_deficit_ratio": round(r_egress_clamped, 4)
        }
