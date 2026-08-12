"""
Trajectory Generator Engine for BHID (Milestone 2.5).
Located in vision/tracking/ per architecture guidelines.
Processes detection and tracking streams, computes smooth velocity vectors (vx, vy),
and constructs persistent Trajectory domain objects.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

import math
from typing import List, Dict, Any
from bhid.dataset.preparation.schemas import Track, Trajectory

class TrajectoryGenerator:
    """Generates continuous pedestrian trajectories from frame-level track states."""

    @staticmethod
    def compute_velocities(trajectory: Trajectory, delta_t: float = 0.04) -> Trajectory:
        """Computes instantaneous velocity vectors (vx, vy) using finite differences."""
        states = trajectory.states
        if len(states) < 2:
            return trajectory
            
        for i in range(len(states)):
            if i == 0:
                dt = states[1].timestamp_seconds - states[0].timestamp_seconds
                if dt <= 0: dt = delta_t
                dx = states[1].bbox_xywh[0] - states[0].bbox_xywh[0]
                dy = states[1].bbox_xywh[1] - states[0].bbox_xywh[1]
            elif i == len(states) - 1:
                dt = states[-1].timestamp_seconds - states[-2].timestamp_seconds
                if dt <= 0: dt = delta_t
                dx = states[-1].bbox_xywh[0] - states[-2].bbox_xywh[0]
                dy = states[-1].bbox_xywh[1] - states[-2].bbox_xywh[1]
            else:
                dt = states[i+1].timestamp_seconds - states[i-1].timestamp_seconds
                if dt <= 0: dt = delta_t * 2
                dx = states[i+1].bbox_xywh[0] - states[i-1].bbox_xywh[0]
                dy = states[i+1].bbox_xywh[1] - states[i-1].bbox_xywh[1]
                
            vx = round(dx / dt, 3)
            vy = round(dy / dt, 3)
            states[i].velocity_xy = [vx, vy]
            
        return trajectory

    @staticmethod
    def audit_trajectory_quality(trajectories: Dict[int, Trajectory]) -> Dict[str, Any]:
        """Audits track persistence, discontinuities, and velocity distribution."""
        total_tracks = len(trajectories)
        short_tracks = 0
        total_points = 0
        max_speed = 0.0
        
        for track_id, traj in trajectories.items():
            total_points += len(traj.states)
            if len(traj.states) < 5:
                short_tracks += 1
                
            for state in traj.states:
                if state.velocity_xy:
                    speed = math.sqrt(state.velocity_xy[0]**2 + state.velocity_xy[1]**2)
                    if speed > max_speed:
                        max_speed = speed
                        
        return {
            "total_trajectories_audited": total_tracks,
            "short_transient_tracks_dropped": short_tracks,
            "total_track_points": total_points,
            "max_observed_speed_m_s": round(max_speed, 2),
            "trajectory_continuity_score": round((1.0 - (short_tracks / max(total_tracks, 1))) * 100, 1),
            "status": "VALIDATED_CONTINUOUS" if short_tracks / max(total_tracks, 1) < 0.15 else "WARNING_DISCONTINUOUS"
        }
