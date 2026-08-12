# BHID Phase 1: Systems Architecture Specification

**Project Name:** BHID (Bottleneck Hazard Intelligence & Detection)  
**Document Version:** 1.2.0 (Refined Approved Version)  
**Author:** Lead Systems Architect  
**Status:** Approved Architectural Specification Framework  

---

## 1. System Architecture Diagram

```mermaid
graph TD
    subgraph Layer 1: Computer Vision & Detection
        RTSP[RTSP / Video Streams] --> Decode[Frame Ingestion & Preprocessing]
        Decode --> Detector[Candidate Detector: Accessible YOLO Family / Intel OpenVINO]
        Detector --> BBox[Detection Tensor: Bounding Boxes + Confidence]
    end

    subgraph Layer 2: Multi-Object Tracking
        BBox --> Tracker[Multi-Object Tracker: ByteTrack / BoT-SORT / Deep OC-SORT Benchmark]
        Tracker --> Traj[Persistent Trajectories: Track IDs + Velocities + BBoxes]
    end

    subgraph Layer 3: Crowd Analytics & Features
        Traj --> ZoneMapper[Spatial Cell Grid & Zone Mapper]
        ZoneMapper --> FeatEngine[Candidate Spatiotemporal Feature Extractor]
        FeatEngine --> FeatVec[Candidate Spatiotemporal Feature Vector Sequence X_t]
    end

    subgraph Layer 4: Prediction & Inference
        FeatVec --> Buffer[Sliding Ring Buffer - Configurable Length]
        Buffer --> MLModel[ML Inference Engine: LightGBM / TCN Progressive Hierarchy]
        MLModel --> RiskOut[Risk Score Output: P_Bottleneck in 10s/20s/30s]
    end

    subgraph Layer 5: Agentic Intelligence Layer
        RiskOut --> Orchestrator[Orchestrator Agent State Graph]
        Orchestrator -->|Risk > Threshold| DecisionAgent[Decision & Policy Agent]
        Orchestrator -->|Health Check| VisionAgent[Vision & Camera Health Agent]
        Orchestrator -->|Diagnostic| AnalyticsAgent[Analytics Agent]
        DecisionAgent --> ReportingAgent[Reporting Agent]
    end

    subgraph Layer 6: Application & Presentation (Provisional Choices)
        RiskOut --> DB[(Time-Series Storage - Provisional Choice)]
        DecisionAgent --> AlertDispatcher[Emergency Alert Dispatcher]
        ReportingAgent --> WS[WebSocket Live Streamer]
        WS --> UI[Live Dashboard - Provisional UI Stack]
        FastAPI[FastAPI REST Engine] --> UI
    end
```

---

## 2. Decoupled 6-Layer Architecture Specification

### Layer 1 — Computer Vision & Detection
- **Purpose:** Ingest raw video streams and detect person class instances in every frame.
- **Input:** RTSP/MP4 video stream. Frame ingestion cadence is a **configurable operational parameter**.
- **Output:** Frame detection payload containing array of bounding boxes $\mathbf{B}_t = [x_{min}, y_{min}, x_{max}, y_{max}, \text{confidence}, \text{class\_id}]$.
- **Decoupling Boundary:** Does not perform state tracking across frames or calculate speeds. Candidate detectors evaluated empirically in Phase 2.

### Layer 2 — Multi-Object Tracking
- **Purpose:** Associate bounding boxes across temporal frames to maintain persistent identity and compute frame-to-frame velocity vectors.
- **Input:** Detection payload $\mathbf{B}_t$ and historical track states $\mathbf{S}_{t-1}$.
- **Output:** Active trajectories $\mathbf{T}_t = [\text{track\_id}, x_c, y_c, w, h, v_x, v_y, \text{track\_age}]$.
- **Decoupling Boundary:** Purely kinematic state tracker. Does not aggregate spatial zones or calculate density maps. Trackers evaluated empirically in Phase 2.

### Layer 3 — Crowd Analytics & Candidate Feature Extraction
- **Purpose:** Map discrete trajectories into spatial cell grids ($\Omega$), aggregate kinematics, and compute candidate spatiotemporal features over a rolling observation window $T_{obs}$.
- **Input:** Stream of active trajectories $\mathbf{T}_t$.
- **Output:** Feature vector $\mathbf{X}_t \in \mathbb{R}^K$ per spatial zone at configurable cadence.
- **Decoupling Boundary:** Computes deterministic mathematical candidate features. Does not run predictive ML models.

### Layer 4 — Prediction & Machine Learning
- **Purpose:** Consume feature sequences $\mathbf{X}_{t-L:t}$ from a ring buffer and infer near-future bottleneck probabilities.
- **Input:** Ring buffer sequence tensor $\mathbb{R}^{L \times K}$.
- **Output:** Risk score $\hat{P}^{(h)} \in [0.0, 1.0]$ for $h \in \{10\text{s}, 20\text{s}, 30\text{s}\}$.
- **Decoupling Boundary:** Purely numerical ML model evaluated progressively (Tier 1 $\to$ Tier 2 $\to$ Tier 3). Execution is **deterministic or controlled-stochastic and does not depend on an LLM**. Does not make operational policy decisions or generate human text.

### Layer 5 — Agentic AI Layer
- **Purpose:** Orchestrate multi-agent tools, evaluate operational threshold policies, check system health, and generate natural language summaries and alerts.
- **Input:** Numerical risk scores $\hat{P}^{(h)}$, feature vectors $\mathbf{X}_t$, and operational policy rules.
- **Output:** Structured action payloads, operational alerts, and explanation summaries.
- **Decoupling Boundary:** High-level decision layer. Does NOT perform object detection, tracking, or density calculations.

### Layer 6 — Application Layer (Provisional Choices)
- **Purpose:** Expose REST endpoints, stream real-time WebSockets to the user interface, store time-series metrics, and dispatch external notifications.
- **Input:** Real-time data streams from Layers 1–5.
- **Output:** WebGL UI dashboard (provisional choice), REST API responses, push alerts.
- **Note:** Database and UI technology choices are provisional implementation preferences to be revisited post-CV/ML pipeline validation.

---

## 3. Core JSON Data Schemas

### 3.1 Detection Frame Schema (`DetectionFrameSchema`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DetectionFrameSchema",
  "type": "object",
  "properties": {
    "camera_id": { "type": "string" },
    "frame_index": { "type": "integer", "minimum": 0 },
    "timestamp": { "type": "number" },
    "frame_width": { "type": "integer" },
    "frame_height": { "type": "integer" },
    "detections": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "bbox": {
            "type": "array",
            "items": { "type": "number" },
            "minItems": 4,
            "maxItems": 4
          },
          "confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "class_id": { "type": "integer" }
        },
        "required": ["bbox", "confidence", "class_id"]
      }
    }
  },
  "required": ["camera_id", "frame_index", "timestamp", "frame_width", "frame_height", "detections"]
}
```

### 3.2 Candidate Spatiotemporal Feature Vector Schema (`SpatiotemporalFeatureVectorSchema`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SpatiotemporalFeatureVectorSchema",
  "type": "object",
  "properties": {
    "zone_id": { "type": "string" },
    "timestamp": { "type": "number" },
    "window_size_seconds": { "type": "number" },
    "candidate_features": {
      "type": "object",
      "properties": {
        "pedestrian_count": { "type": "integer" },
        "density_ped_per_m2": { "type": "number" },
        "occupancy_ratio": { "type": "number" },
        "mean_speed_m_s": { "type": "number" },
        "velocity_variance": { "type": "number" },
        "acceleration_m_s2": { "type": "number" },
        "directional_entropy": { "type": "number" },
        "inflow_rate_per_s": { "type": "number" },
        "outflow_rate_per_s": { "type": "number" },
        "net_flow_rate_per_s": { "type": "number" },
        "flow_drop_ratio": { "type": "number" },
        "trajectory_convergence": { "type": "number" },
        "temporal_density_change": { "type": "number" },
        "temporal_speed_change": { "type": "number" }
      },
      "required": [
        "pedestrian_count", "density_ped_per_m2", "occupancy_ratio",
        "mean_speed_m_s", "velocity_variance", "acceleration_m_s2",
        "directional_entropy", "inflow_rate_per_s", "outflow_rate_per_s",
        "net_flow_rate_per_s", "flow_drop_ratio", "trajectory_convergence",
        "temporal_density_change", "temporal_speed_change"
      ]
    }
  },
  "required": ["zone_id", "timestamp", "window_size_seconds", "candidate_features"]
}
```

### 3.3 Bottleneck Risk Output Schema (`BottleneckRiskPredictionSchema`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BottleneckRiskPredictionSchema",
  "type": "object",
  "properties": {
    "zone_id": { "type": "string" },
    "timestamp": { "type": "number" },
    "model_version": { "type": "string" },
    "risk_scores": {
      "type": "object",
      "properties": {
        "horizon_10s": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "horizon_20s": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "horizon_30s": { "type": "number", "minimum": 0.0, "maximum": 1.0 }
      },
      "required": ["horizon_10s", "horizon_20s", "horizon_30s"]
    },
    "predicted_density_optional": { "type": ["number", "null"] }
  },
  "required": ["zone_id", "timestamp", "model_version", "risk_scores"]
}
```

### 3.4 Agent Action Payload Schema (`AgentActionPayloadSchema`)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AgentActionPayloadSchema",
  "type": "object",
  "properties": {
    "event_id": { "type": "string" },
    "timestamp": { "type": "number" },
    "zone_id": { "type": "string" },
    "alert_level": { "type": "string", "enum": ["INFO", "WARNING", "CRITICAL"] },
    "trigger_reason": { "type": "string" },
    "explanation": { "type": "string" },
    "recommended_actions": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["event_id", "timestamp", "zone_id", "alert_level", "trigger_reason", "explanation", "recommended_actions"]
}
```

---

## 4. Operational Cadence (Configurable Parameters)

System frame rates and inference execution intervals are **configurable operational parameters** managed per deployment profile, not hardcoded architectural constants:

- **Source Video Ingestion Rate:** Configurable parameter (e.g., 15 FPS, 25 FPS, 30 FPS based on RTSP camera stream).
- **CV Detection Cadence:** Configurable parameter (e.g., every 1st, 2nd, or 3rd frame depending on GPU budget).
- **Tracker Update Cadence:** Configurable parameter (per frame or per keyframe).
- **Feature Aggregation & ML Prediction Cadence:** Configurable parameter (e.g., 1 Hz to 5 Hz based on temporal window granularity).

---

## 5. Hardware Sizing & Initial Engineering Target Hypotheses

The following deployment profiles represent **initial engineering target hypotheses**, to be validated empirically post-detector selection:

| Component Profile | Target Hardware Profile | Stream Capacity Target | Expected CV FPS Target | Prediction Latency Target | Memory Footprint Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Edge Appliance** | NVIDIA Jetson AGX Orin (64GB) | Multi-stream target | Real-time target (20–30 FPS) | Target $< 15\text{ms}$ | $< 8\text{ GB}$ VRAM |
| **Cloud Server** | NVIDIA A10G / T4 GPU (Cloud) | Scalable Multi-stream | High-throughput target (30+ FPS) | Target $< 5\text{ms}$ | $< 16\text{ GB}$ VRAM |
| **Edge CPU Profile** | Intel Core i7 / Xeon (OpenVINO) | Standard stream target | Edge CPU target (15–20 FPS) | Target $< 25\text{ms}$ | $< 4\text{ GB}$ System RAM |
