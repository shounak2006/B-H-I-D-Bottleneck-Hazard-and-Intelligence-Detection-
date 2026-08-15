"""
BHID Centroid Multi-Object Tracker.

Baseline centroid-based nearest-neighbor tracking implementation.
Enforces non-reusable monotonically increasing track IDs across the session.
"""

from typing import Dict, Any, Optional, List, Tuple
import math
from bhid.vision.detection.detection_batch import DetectionBatch
from bhid.vision.tracking.tracker_interface import BasePedestrianTracker
from bhid.vision.tracking.tracked_object import TrackedObject
from bhid.vision.tracking.tracking_batch import TrackingBatch


class CentroidTracker(BasePedestrianTracker):
    """
    Baseline centroid tracker using nearest-neighbor Euclidean distance association.
    
    Parameters:
        max_disappeared_frames: Number of consecutive frames a track can be missed before expiration.
        max_match_distance: Maximum centroid distance threshold in pixels for matching (default: 100.0 px).
        min_confidence: Minimum detection confidence threshold for tracking inputs (default: 0.50).
    """

    def __init__(
        self,
        max_disappeared_frames: int = 10,
        max_match_distance: float = 100.0,
        min_confidence: float = 0.50
    ):
        self.max_disappeared_frames = int(max_disappeared_frames)
        self.max_match_distance = float(max_match_distance)
        self.min_confidence = float(min_confidence)
        
        self.tracks: Dict[Any, TrackedObject] = {}
        self._next_track_id: int = 1
        self.is_initialized: bool = False

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initializes tracker state and parameters."""
        if config:
            if "max_disappeared_frames" in config:
                self.max_disappeared_frames = int(config["max_disappeared_frames"])
            if "max_match_distance" in config:
                self.max_match_distance = float(config["max_match_distance"])
            if "min_confidence" in config:
                self.min_confidence = float(config["min_confidence"])
        self.is_initialized = True

    def reset(self) -> None:
        """Resets active tracks and track ID counter."""
        self.tracks.clear()
        self._next_track_id = 1

    def shutdown(self) -> None:
        """Shuts down tracker and resets state."""
        self.reset()
        self.is_initialized = False

    def _register_track(
        self,
        bbox: Tuple[float, float, float, float],
        confidence: float,
        timestamp: float,
        frame_id: Any
    ) -> TrackedObject:
        """
        Creates a new TrackedObject with a monotonically increasing, non-reusable track ID.
        """
        track_id = self._next_track_id
        self._next_track_id += 1

        tracked_obj = TrackedObject(
            track_id=track_id,
            bbox=bbox,
            confidence=confidence,
            timestamp=timestamp,
            frame_id=frame_id
        )
        self.tracks[track_id] = tracked_obj
        return tracked_obj

    def update(self, detection_batch: DetectionBatch) -> TrackingBatch:
        """
        Updates active tracks with frame-level detection batch using centroid matching.
        """
        if not self.is_initialized:
            self.initialize()

        timestamp = detection_batch.timestamp
        frame_id = detection_batch.frame_id

        # 1. Filter detections by confidence threshold
        valid_batch = detection_batch.filter_by_confidence(min_confidence=self.min_confidence)
        det_list = valid_batch.detections

        # 2. Case: If no detections exist in current frame
        if not det_list:
            expired_ids = []
            for track_id, track in self.tracks.items():
                track.mark_missed()
                if track.missed_frames > self.max_disappeared_frames:
                    expired_ids.append(track_id)
            for track_id in expired_ids:
                del self.tracks[track_id]

            return TrackingBatch(
                frame_id=frame_id,
                timestamp=timestamp,
                active_tracks=list(self.tracks.values())
            )

        # Extract centroids for incoming detections
        det_bboxes = [(d.bbox_x1, d.bbox_y1, d.bbox_x2, d.bbox_y2) for d in det_list]
        det_centroids = [((b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0) for b in det_bboxes]
        det_confidences = [d.confidence for d in det_list]

        # 3. Case: If no active tracks currently exist
        if not self.tracks:
            for i in range(len(det_list)):
                self._register_track(
                    bbox=det_bboxes[i],
                    confidence=det_confidences[i],
                    timestamp=timestamp,
                    frame_id=frame_id
                )
            return TrackingBatch(
                frame_id=frame_id,
                timestamp=timestamp,
                active_tracks=list(self.tracks.values())
            )

        # 4. Case: Active tracks exist -> Compute Euclidean distance matrix
        track_ids = list(self.tracks.keys())
        track_centroids = [self.tracks[tid].get_center() for tid in track_ids]

        # Greedy nearest-neighbor association
        used_tracks = set()
        used_dets = set()

        # Build list of all candidate pairs (distance, track_idx, det_idx)
        pairs: List[Tuple[float, int, int]] = []
        for t_idx, (t_x, t_y) in enumerate(track_centroids):
            for d_idx, (d_x, d_y) in enumerate(det_centroids):
                dist = math.sqrt((t_x - d_x) ** 2 + (t_y - d_y) ** 2)
                if dist <= self.max_match_distance:
                    pairs.append((dist, t_idx, d_idx))

        # Sort candidate pairs by ascending distance
        pairs.sort(key=lambda x: x[0])

        for dist, t_idx, d_idx in pairs:
            if t_idx in used_tracks or d_idx in used_dets:
                continue

            # Match found
            tid = track_ids[t_idx]
            self.tracks[tid].update(
                bbox=det_bboxes[d_idx],
                confidence=det_confidences[d_idx],
                timestamp=timestamp,
                frame_id=frame_id
            )
            used_tracks.add(t_idx)
            used_dets.add(d_idx)

        # Mark unassigned tracks as missed and purge expired tracks
        expired_ids = []
        for t_idx, tid in enumerate(track_ids):
            if t_idx not in used_tracks:
                track = self.tracks[tid]
                track.mark_missed()
                if track.missed_frames > self.max_disappeared_frames:
                    expired_ids.append(tid)

        for tid in expired_ids:
            del self.tracks[tid]

        # Register unassigned detections as new tracks (incrementing _next_track_id)
        for d_idx in range(len(det_list)):
            if d_idx not in used_dets:
                self._register_track(
                    bbox=det_bboxes[d_idx],
                    confidence=det_confidences[d_idx],
                    timestamp=timestamp,
                    frame_id=frame_id
                )

        return TrackingBatch(
            frame_id=frame_id,
            timestamp=timestamp,
            active_tracks=list(self.tracks.values())
        )
