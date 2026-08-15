"""
BHID Vision Detection Adapter.

Converts frame-level DetectionBatch objects into structured detection observations
for pipeline ingestion without computing Phase 2 temporal engineered features.
"""

from typing import Dict, Any, Optional
from bhid.vision.detection.detection_batch import DetectionBatch


class DetectionAdapter:
    """
    Adapter converting vision detection outputs into standardized frame observations.
    """

    def __init__(self, default_zone_area_m2: float = 100.0):
        self.default_zone_area_m2 = float(default_zone_area_m2)

    def adapt_batch(
        self,
        batch: DetectionBatch,
        zone_area_m2: Optional[float] = None,
        confidence_threshold: float = 0.50
    ) -> Dict[str, Any]:
        """
        Transforms a DetectionBatch into a detection-level observation dictionary.
        
        Args:
            batch: Input DetectionBatch object.
            zone_area_m2: Optional spatial zone area in square meters.
            confidence_threshold: Minimum detection confidence threshold.
            
        Returns:
            Dictionary containing frame-level detection statistics.
        """
        area_m2 = float(zone_area_m2) if zone_area_m2 is not None else self.default_zone_area_m2
        
        # Filter detections by confidence score
        filtered_batch = batch.filter_by_confidence(min_confidence=confidence_threshold)
        ped_count = filtered_batch.pedestrian_count()
        conf_stats = filtered_batch.confidence_summary()
        
        # Compute spatial density (pedestrians per m^2)
        density = ped_count / area_m2 if area_m2 > 0 else 0.0

        # Compute area occupancy ratio relative to image dimensions or zone area
        total_bbox_area = sum(d.area for d in filtered_batch.detections)
        if batch.image_width and batch.image_height:
            total_img_area = batch.image_width * batch.image_height
            occupancy = min(1.0, total_bbox_area / total_img_area) if total_img_area > 0 else 0.0
        else:
            occupancy = min(1.0, total_bbox_area / (area_m2 * 1000.0))  # fallback scaling

        return {
            "frame_id": batch.frame_id,
            "timestamp": batch.timestamp,
            "pedestrian_count": ped_count,
            "density_ped_per_m2": round(density, 4),
            "occupancy_ratio": round(occupancy, 4),
            "mean_confidence": conf_stats["mean"],
            "detection_count": len(filtered_batch.detections),
            "zone_area_m2": area_m2,
            "bounding_boxes": filtered_batch.get_bboxes()
        }
