"""
BHID FastAPI Primary Application Entrypoint.

Provides REST API routers, Swagger /docs documentation, CORS middleware for localhost frontend,
and WebSocket realtime telemetry streaming endpoint /ws/telemetry.
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.routers import (
    health_router,
    monitoring_router,
    events_router,
    sessions_router,
    replay_router,
    reports_router,
    validation_router,
)
from backend.websocket.telemetry_socket import telemetry_websocket_endpoint
from backend.routers.monitoring import monitoring_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager handling startup and shutdown events."""
    print("[INFO] Starting BHID FastAPI Dedicated Backend Service...")
    yield
    print("[INFO] Shutting down BHID FastAPI Dedicated Backend Service...")
    monitoring_service.stop_monitoring()


app = FastAPI(
    title="BHID API - Bottleneck Hazard & Intelligence Detection",
    description="FastAPI Backend for BHID Spatiotemporal Crowd Safety Platform v1.0",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware enabling localhost React/Vite frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(health_router)
app.include_router(monitoring_router)
app.include_router(events_router)
app.include_router(sessions_router)
app.include_router(replay_router)
app.include_router(reports_router)
app.include_router(validation_router)


# Realtime Telemetry WebSocket Endpoint
@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await telemetry_websocket_endpoint(websocket, monitoring_service)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
