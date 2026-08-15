"""
BHID Realtime Telemetry WebSocket Handler.
Streams density, pedestrian count, risk probability, risk level, active events, and frame metadata over /ws/telemetry.
"""

from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
from backend.services.monitoring_service import MonitoringService


async def telemetry_websocket_endpoint(websocket: WebSocket, monitoring_service: MonitoringService):
    """
    WebSocket endpoint streaming live crowd telemetry at 2.5Hz (400ms interval).
    """
    await websocket.accept()
    try:
        while True:
            # Process next monitoring frame
            res = monitoring_service.process_next_frame()
            
            # Extract lightweight JSON-serializable telemetry payload
            pred = res.get("prediction_result", {})
            snapshot = res.get("monitoring_snapshot", {})
            
            payload = {
                "timestamp": snapshot.get("timestamp"),
                "frame_id": snapshot.get("frame_id"),
                "scene_id": snapshot.get("scene_id"),
                "zone_id": snapshot.get("zone_id"),
                "pedestrian_count": snapshot.get("pedestrian_count", 0),
                "density_ped_per_m2": snapshot.get("density_ped_per_m2", 0.0),
                "prediction_probability": pred.get("prediction_probability", 0.0),
                "risk_level": pred.get("risk_level", "LOW"),
                "binary_prediction": pred.get("binary_prediction", 0),
                "active_events_count": snapshot.get("active_event_count", 0),
                "active_events": snapshot.get("active_events", [])
            }

            await websocket.send_json(payload)
            await asyncio.sleep(0.4)  # 2.5Hz streaming rate
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
