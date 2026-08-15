# Phase 7A: Web Platform Transformation Architecture Specification

## Executive Summary

Phase 7A transforms the existing headless BHID v1.0 engine into a full-stack localhost web application. By introducing a dedicated FastAPI REST API & WebSocket backend (`backend/`) and a React/Vite/TypeScript frontend dashboard (`frontend/`), BHID capabilities are accessible directly through a modern web browser while preserving all existing frozen analytics, prediction, event management, persistence, replay, reporting, validation, and release logic.

---

## Architectural Pattern: Router → Service → BHID Core Engine

```mermaid
flowchart TD
    subgraph Frontend [React / Vite / TypeScript Dashboard - http://localhost:5173]
        DB[Dashboard Page]
        SS[Sessions Page]
        RP[Replay Page]
        RE[Reports Page]
        VA[Validation Page]
    end

    subgraph Backend [FastAPI Dedicated Backend - http://localhost:8000]
        subgraph Routers [FastAPI Routers]
            R_H[health.py]
            R_M[monitoring.py]
            R_E[events.py]
            R_S[sessions.py]
            R_RP[replay.py]
            R_R[reports.py]
            R_V[validation.py]
            R_WS[telemetry_socket.py]
        end

        subgraph Services [Backend Service Layer]
            S_M[MonitoringService]
            S_E[EventService]
            S_S[SessionService]
            S_RP[ReplayService]
            S_R[ReportingService]
            S_V[ValidationService]
        end
    end

    subgraph Core [BHID Frozen Core Engine]
        RO[RuntimeOrchestrator]
        CAE[CrowdAnalyticsEngine]
        BP[BottleneckPredictor]
        HEE[HazardEventEngine]
        PM[PersistenceManager]
        PE[PlaybackEngine]
        RM[ReportingManager]
        VM[ValidationManager]
    end

    Frontend --> Routers
    Routers --> Services
    Services --> Core
```

---

## System Boundaries & Frozen Constraints

> [!IMPORTANT]
> **Frozen System Boundaries:**
> 1. **Zero Prediction Logic Modification:** `BottleneckPredictor`, `model_registry.json`, $Y_{30}$ horizon, decision threshold ($0.60$), and 14 approved spatiotemporal features remain strictly frozen.
> 2. **Decoupled Service Layer (`Router → Service → BHID Core`):** All API endpoints delegate business logic to services in `backend/services/`.
> 3. **Non-Blocking Telemetry Streaming:** `/ws/telemetry` streams live 2.5Hz crowd density and hazard probability without blocking HTTP router endpoints.
