"""
MADRAS Dataset Data Adapter for BHID.
Parses microscopic trajectory CSV records [timestamp_ms, track_id, x_meters, y_meters, vx, vy, density]
into standardized BHID Trajectory and Track data objects.
"""

from typing import List, Dict, Tuple
from bhid.dataset.preparation.schemas import Track, Trajectory, Timestamp

class MADRASAdapter:
    """Adapter to parse MADRAS Lyon dataset CSV format into BHID standardized schema."""

    def __init__(self, scene_id: str = "madras_lyon_scene1", fps: float = 25.0):
        self.scene_id = scene_id
        self.fps = fps

    def parse_csv_line(self, line: str) -> Tuple[int, Track]:
        """
        Parses a single line of MADRAS trajectory CSV:
        Format: timestamp_ms, track_id, x_m, y_m, vx_m_s, vy_m_s, density_local
        """
        parts = [p.strip() for p in line.strip().split(',') if p.strip()]
        if len(parts) < 4:
            raise ValueError(f"Invalid MADRAS line: {line}")
            
        raw_ts = float(parts[0])
        track_id = int(parts[1])
        x_m = float(parts[2])
        y_m = float(parts[3])
        
        vx = float(parts[4]) if len(parts) > 4 else 0.0
        vy = float(parts[5]) if len(parts) > 5 else 0.0
        
        # Convert timestamp to seconds if given in milliseconds
        timestamp_sec = raw_ts / 1000.0 if raw_ts >= 100.0 else raw_ts
        frame_idx = int(round(timestamp_sec * self.fps)) + 1
        
        # Bounding box is approximated from ground coordinate for format compatibility
        bbox = [x_m - 0.25, y_m - 0.25, 0.5, 0.5]
        
        track = Track(
            track_id=track_id,
            frame_index=frame_idx,
            timestamp_seconds=timestamp_sec,
            bbox_xywh=bbox,
            confidence=1.0,
            velocity_xy=[vx, vy],
            world_pos_xy=[x_m, y_m],
            class_name="person"
        )
        return track_id, track

    def convert_csv_to_trajectories(self, csv_content: str) -> Dict[int, Trajectory]:
        """Converts MADRAS CSV text into map of track_id -> Trajectory."""
        trajectories: Dict[int, Trajectory] = {}
        
        for line in csv_content.strip().split('\n'):
            if not line.strip() or line.startswith('#') or line.lower().startswith('timestamp'):
                continue
                
            track_id, track = self.parse_csv_line(line)
            
            if track_id not in trajectories:
                trajectories[track_id] = Trajectory(
                    track_id=track_id,
                    dataset_provenance=f"MADRAS-{self.scene_id}",
                    camera_id=self.scene_id,
                    states=[]
                )
                
            trajectories[track_id].states.append(track)
            
        # Ensure chronological ordering of states
        for traj in trajectories.values():
            traj.states.sort(key=lambda t: t.timestamp_seconds)
            
        return trajectories
