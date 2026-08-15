"""
BHID Monitoring Service.
Encapsulates runtime monitoring state, single-frame execution, and orchestrator initialization.
"""

from typing import Dict, Any, Optional
import time
from bhid.runtime.runtime_orchestrator import RuntimeOrchestrator
from bhid.vision.detection.mock_detector import MockPedestrianDetector
from bhid.vision.tracking.centroid_tracker import CentroidTracker
from bhid.persistence.persistence_config import PersistenceConfig
from bhid.persistence.persistence_manager import PersistenceManager


class MonitoringService:
    """Service wrapping live crowd monitoring pipeline execution."""

    def __init__(self):
        self.orchestrator = RuntimeOrchestrator()
        self.is_monitoring: bool = False
        self.detector: Optional[MockPedestrianDetector] = None
        self.tracker: Optional[CentroidTracker] = None
        self.persistence_manager: Optional[PersistenceManager] = None
        self.current_session_id: Optional[str] = None
        self.frame_count: int = 0
        self.last_result: Optional[Dict[str, Any]] = None

    def start_monitoring(self, scene_id: str = "LIVE_SCENE", zone_id: str = "ZONE_MAIN") -> Dict[str, Any]:
        """Starts live monitoring session."""
        init_res = self.orchestrator.initialize_bhid()
        self.detector = MockPedestrianDetector(num_pedestrians=35, seed=int(time.time()))
        self.tracker = CentroidTracker(max_disappeared_frames=5, max_match_distance=50.0)
        self.current_session_id = f"session_live_{int(time.time())}"
        p_config = PersistenceConfig(session_id=self.current_session_id)
        self.persistence_manager = PersistenceManager(config=p_config)
        self.is_monitoring = True
        self.frame_count = 0

        return {
            "status": "RUNNING",
            "session_id": self.current_session_id,
            "scene_id": scene_id,
            "zone_id": zone_id,
            "init_result": init_res
        }

    def stop_monitoring(self) -> Dict[str, Any]:
        """Stops live monitoring session."""
        self.is_monitoring = False
        shutdown_res = self.orchestrator.shutdown_bhid(persistence_manager=self.persistence_manager)
        
        session_id = self.current_session_id
        processed = self.frame_count
        self.current_session_id = None

        return {
            "status": "STOPPED",
            "session_id": session_id,
            "processed_frames": processed,
            "shutdown_result": shutdown_res
        }

    def process_next_frame(self) -> Dict[str, Any]:
        """Processes single monitoring frame and updates telemetry state."""
        if not self.is_monitoring or self.detector is None or self.tracker is None:
            # Auto-start if not running
            self.start_monitoring()

        self.frame_count += 1
        ts = time.time()
        
        det_batch = self.detector.detect(frame_id=self.frame_count, timestamp=ts)
        tracking_batch = self.tracker.update(det_batch)

        res = self.orchestrator.process_persistent_monitoring_frame(
            tracking_batch=tracking_batch,
            frame=None,
            persistence_manager=self.persistence_manager,
            scene_id="LIVE_SCENE",
            zone_id="ZONE_MAIN"
        )
        self.last_result = res
        return res

    def get_state(self) -> Dict[str, Any]:
        """Returns current monitoring state summary."""
        return {
            "is_monitoring": self.is_monitoring,
            "current_session_id": self.current_session_id,
            "processed_frames": self.frame_count,
            "last_prediction": self.last_result.get("prediction_result") if self.last_result else None
        }
