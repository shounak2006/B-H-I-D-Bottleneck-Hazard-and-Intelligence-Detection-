"""
BHID Realtime Telemetry Manager.

Centralized WebSocket client manager and telemetry payload broadcaster.
"""

from typing import List, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json


class TelemetryManager:
    """Manages active WebSocket client connections and broadcasts frame telemetry."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    async def connect(self, websocket: WebSocket):
        """Accepts and registers a new WebSocket client connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Removes a disconnected WebSocket client."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_async(self, payload: Dict[str, Any]):
        """Asynchronously broadcasts telemetry payload to all active clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(payload)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

    def broadcast(self, payload: Dict[str, Any]):
        """Synchronous helper for background threads to broadcast telemetry."""
        if not self.active_connections:
            return

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.broadcast_async(payload))
            else:
                loop.run_until_complete(self.broadcast_async(payload))
        except RuntimeError:
            # Fallback when running inside background thread without running event loop
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            new_loop.run_until_complete(self.broadcast_async(payload))
            new_loop.close()


# Global Singleton Instance
telemetry_manager = TelemetryManager()
