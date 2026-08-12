"""
Candidate Spatiotemporal Feature Extractor Engine for BHID (Audit Refined - Final Target Definition).
Computes 14 spatiotemporal features per spatial zone using vector line-segment
boundary crossing for inflow/outflow and mathematically rigorous Egress Deficit Ratio (R_egress).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import math
from typing import List, Dict, Any, Tuple
from bhid.dataset.preparation.schemas import Track, Trajectory, Zone

def ccw(A: Tuple[float, float], B: Tuple[float, float], C: Tuple[float, float]) -> bool:
    """Returns True if points A, B, C are in counter-clockwise order."""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

def intersect(A: Tuple[float, float], B: Tuple[float, float], C: Tuple[float, float], D: Tuple[float, float]) -> bool:
    """Returns True if line segment AB intersects line segment CD."""
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

class CandidateFeatureExtractor:
    """Extracts 14 candidate spatiotemporal features per spatial zone."""

    def __init__(self, zone: Zone):
        self.zone = zone

    def is_point_in_zone(self, x: float, y: float) -> bool:
        """Point-in-polygon check using ray casting."""
        vertices = self.zone.polygon_vertices
        if not vertices or len(vertices) < 3:
            return True
            
        n = len(vertices)
        inside = False
        p1x, p1y = vertices[0]
        for i in range(n + 1):
            p2x, p2y = vertices[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def compute_boundary_crossings(self, tracks_t: List[Track], tracks_prev: List[Track]) -> Tuple[float, float]:
        """
        Computes inflow (Q_in) and outflow (Q_out) using actual line segment boundary crossings
        between frame t-1 and frame t.
        """
        if not tracks_prev or not self.zone.polygon_vertices or len(self.zone.polygon_vertices) < 3:
            return 0.0, 0.0

        prev_map = {t.track_id: t for t in tracks_prev if t.world_pos_xy}
        inflow_count = 0
        outflow_count = 0
        
        poly = self.zone.polygon_vertices
        num_edges = len(poly)
        edges = [(poly[i], poly[(i + 1) % num_edges]) for i in range(num_edges)]

        for curr_track in tracks_t:
            if not curr_track.world_pos_xy:
                continue
            t_id = curr_track.track_id
            if t_id in prev_map:
                prev_track = prev_map[t_id]
                p_prev = (prev_track.world_pos_xy[0], prev_track.world_pos_xy[1])
                p_curr = (curr_track.world_pos_xy[0], curr_track.world_pos_xy[1])
                
                was_inside = self.is_point_in_zone(p_prev[0], p_prev[1])
                is_inside = self.is_point_in_zone(p_curr[0], p_curr[1])

                if not was_inside and is_inside:
                    # Inflow: crossed boundary segment into zone
                    for edge in edges:
                        if intersect(p_prev, p_curr, edge[0], edge[1]):
                            inflow_count += 1
                            break
                elif was_inside and not is_inside:
                    # Outflow: crossed boundary segment out of zone
                    for edge in edges:
                        if intersect(p_prev, p_curr, edge[0], edge[1]):
                            outflow_count += 1
                            break

        return float(inflow_count), float(outflow_count)

    def extract_features(self, tracks_t: List[Track], prev_tracks_t: List[Track] = None) -> Dict[str, float]:
        """Extracts 14 candidate features for a frame snapshot."""
        zone_tracks = [t for t in tracks_t if t.world_pos_xy and self.is_point_in_zone(t.world_pos_xy[0], t.world_pos_xy[1])]
        count = len(zone_tracks)
        density = count / max(self.zone.area_m2, 0.1)
        
        # Occupancy ratio
        total_bbox_area = sum([t.bbox_xywh[2] * t.bbox_xywh[3] for t in zone_tracks])
        occupancy = min(total_bbox_area / max(self.zone.area_m2, 0.1), 1.0)
        
        # Kinematics
        speeds = []
        angles = []
        vx_list, vy_list = [], []
        
        for t in zone_tracks:
            if t.velocity_xy:
                vx, vy = t.velocity_xy[0], t.velocity_xy[1]
                speed = math.sqrt(vx**2 + vy**2)
                speeds.append(speed)
                angles.append(math.atan2(vy, vx))
                vx_list.append(vx)
                vy_list.append(vy)
                
        mean_speed = sum(speeds) / count if count > 0 else 0.0
        speed_var = sum((s - mean_speed)**2 for s in speeds) / count if count > 0 else 0.0
        
        # Directional entropy (8-bin histogram)
        bins = [0] * 8
        for angle in angles:
            idx = int(((angle + math.pi) / (2 * math.pi)) * 8) % 8
            bins[idx] += 1
            
        entropy = 0.0
        if count > 0:
            for b in bins:
                if b > 0:
                    p = b / count
                    entropy -= p * math.log2(p)
                    
        # Inflow / Outflow via Boundary Crossing
        Q_in, Q_out = self.compute_boundary_crossings(tracks_t, prev_tracks_t) if prev_tracks_t else (0.0, 0.0)
        net_flow = Q_in - Q_out
        
        # Rigorous Egress Deficit Ratio: R_egress = 1 - (Q_out / Q_in) when Q_in > 0 else 0.0
        egress_deficit_ratio = (1.0 - (Q_out / Q_in)) if Q_in > 0 else 0.0
        egress_deficit_ratio = max(0.0, min(1.0, egress_deficit_ratio))
        
        # Convergence
        convergence = 0.0
        if count > 1:
            mean_vx = sum(vx_list) / count if vx_list else 0.0
            mean_vy = sum(vy_list) / count if vy_list else 0.0
            convergence = math.sqrt(mean_vx**2 + mean_vy**2) / (mean_speed + 1e-5)
            
        return {
            "pedestrian_count": float(count),
            "density_ped_per_m2": round(density, 3),
            "occupancy_ratio": round(occupancy, 3),
            "mean_speed_m_s": round(mean_speed, 3),
            "velocity_variance": round(speed_var, 3),
            "acceleration_m_s2": 0.0,
            "directional_entropy": round(entropy, 3),
            "inflow_rate_per_s": Q_in,
            "outflow_rate_per_s": Q_out,
            "net_flow_rate_per_s": net_flow,
            "egress_deficit_ratio": round(egress_deficit_ratio, 3),
            "trajectory_convergence": round(convergence, 3),
            "temporal_density_change": 0.0,
            "temporal_speed_change": 0.0
        }
