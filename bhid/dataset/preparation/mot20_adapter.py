"""
MOT20 Dataset Data Adapter for BHID.
Parses MOT20 seqinfo.ini and gt/gt.txt annotations into standardized BHID Frame and Track objects.
"""

from typing import List, Dict, Tuple
from bhid.dataset.preparation.schemas import Frame, Detection, Track, Timestamp

class MOT20Adapter:
    """Adapter to parse MOT Challenge TXT format into BHID standardized schema."""
    
    def __init__(self, sequence_name: str = "MOT20-01", fps: float = 25.0, width: int = 1920, height: int = 1080):
        self.sequence_name = sequence_name
        self.fps = fps
        self.width = width
        self.height = height

    def parse_gt_line(self, line: str) -> Tuple[int, Track]:
        """
        Parses a single line of MOT20 ground-truth text:
        Format: frame, id, bb_left, bb_top, bb_width, bb_height, conf, class, visibility, unused
        """
        parts = [p.strip() for p in line.strip().split(',') if p.strip()]
        if len(parts) < 6:
            raise ValueError(f"Invalid MOT20 GT line: {line}")
            
        frame_idx = int(parts[0])
        track_id = int(parts[1])
        bb_left = float(parts[2])
        bb_top = float(parts[3])
        bb_width = float(parts[4])
        bb_height = float(parts[5])
        conf = float(parts[6]) if len(parts) > 6 else 1.0
        class_id = int(parts[7]) if len(parts) > 7 else 1
        
        # Calculate timestamp
        timestamp_sec = (frame_idx - 1) / self.fps
        
        track = Track(
            track_id=track_id,
            frame_index=frame_idx,
            timestamp_seconds=timestamp_sec,
            bbox_xywh=[bb_left, bb_top, bb_width, bb_height],
            confidence=conf,
            class_name="person" if class_id == 1 else f"class_{class_id}"
        )
        
        return frame_idx, track

    def convert_gt_text_to_frames(self, gt_text_content: str) -> Dict[int, Frame]:
        """Converts raw GT text content into a map of frame_index -> BHID Frame."""
        frames: Dict[int, Frame] = {}
        
        for line in gt_text_content.strip().split('\n'):
            if not line.strip() or line.startswith('#'):
                continue
            frame_idx, track = self.parse_gt_line(line)
            
            if frame_idx not in frames:
                frames[frame_idx] = Frame(
                    camera_id=self.sequence_name,
                    timestamp=Timestamp(frame_index=frame_idx, timestamp_seconds=track.timestamp_seconds, time_step_delta=1.0/self.fps),
                    frame_width=self.width,
                    frame_height=self.height,
                    detections=[],
                    dataset_provenance=f"MOT20-{self.sequence_name}"
                )
                
            detection = Detection(
                bbox_xywh=track.bbox_xywh,
                confidence=track.confidence,
                class_name=track.class_name
            )
            frames[frame_idx].detections.append(detection)
            
        return frames
