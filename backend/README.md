# BHID FastAPI Dedicated Backend Package

FastAPI backend service exposing BHID v1.0 core capabilities via REST APIs and WebSockets.

---

## Architecture Pattern

```text
Router → Service → BHID Core Engine
```

- **Routers (`backend/routers/`)**: Endpoint declarations, request validation, HTTP status codes.
- **Services (`backend/services/`)**: Business logic wrapping `RuntimeOrchestrator`, `HazardEventEngine`, `SessionManager`, `PlaybackEngine`, `ReportingManager`, and `ValidationManager`.
- **WebSocket (`backend/websocket/`)**: Realtime `/ws/telemetry` stream.

---

## Running Backend Independently

```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Launch FastAPI server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Swagger API Docs**: `http://localhost:8000/docs`
- **ReDoc API Docs**: `http://localhost:8000/redoc`
- **WebSocket Endpoint**: `ws://localhost:8000/ws/telemetry`
