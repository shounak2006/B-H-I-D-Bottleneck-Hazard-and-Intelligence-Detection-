# BHID v1.0 - Platform System Capabilities Inventory

This document provides a comprehensive inventory of operational capabilities provided by the **Bottleneck Hazard and Intelligence Detection (BHID)** platform v1.0 across all 10 component layers.

---

## 1. Vision & Detection Layer Capabilities (`bhid/vision/detection`)
- **Standardized Detection Batch Schema**: `DetectionBatch` container encapsulating frame ID, timestamp, image dimensions, and bounding boxes.
- **Mock Pedestrian Detector**: `MockPedestrianDetector` producing synthetic pedestrian detections with configurable counts and random seeds for offline testing.
- **MOT Benchmark Adapters**: Adapters converting MOT20, SDD, and Madras dataset detections into standardized `DetectionBatch` formats.

---

## 2. Multi-Object Tracking Layer Capabilities (`bhid/vision/tracking`)
- **Centroid Tracker**: `CentroidTracker` associating detections across frames using Euclidean distance matching.
- **Persistent Non-Reusable Track IDs**: Guarantees `track_id` values are monotonically increasing and never reused during an operational session.
- **Trajectory History Generator**: Maintains trajectory motion trails and velocity vector history per track.

---

## 3. Crowd Analytics Engine Capabilities (`bhid/analytics`)
Computes the 14 approved spatiotemporal crowd features:
1. `feature_pedestrian_count`: Total active pedestrians in spatial ROI.
2. `feature_density_ped_per_m2`: Spatial crowd density in $\text{ped/m}^2$.
3. `feature_occupancy_ratio`: Ratio of spatial ROI occupied by crowd.
4. `feature_mean_speed_m_s`: Mean pedestrian movement speed in m/s.
5. `feature_velocity_variance`: Speed variance across active tracks.
6. `feature_acceleration_m_s2`: Rate of speed change over time.
7. `feature_directional_entropy`: Heading angle entropy ($0.0 \dots 1.0$).
8. `feature_inflow_rate_per_s`: Rate of new track entrances into ROI per second.
9. `feature_outflow_rate_per_s`: Rate of track exits from ROI per second.
10. `feature_net_flow_rate_per_s`: $\text{Inflow} - \text{Outflow}$ rate difference per second.
11. `feature_egress_deficit_ratio`: Ratio of flow bottleneck accumulation.
12. `feature_trajectory_convergence`: Trajectory vector convergence towards bottleneck exits.
13. `feature_temporal_density_change`: Rate of density change ($d\text{density}/dt$).
14. `feature_temporal_speed_change`: Rate of speed change ($d\text{speed}/dt$).

---

## 4. Machine Learning Bottleneck Prediction Capabilities (`bhid/prediction`)
- **Dual Model Support**: Loads LightGBM (`lightgbm_optimized.joblib`) or XGBoost model artifacts registered in `model_registry.json`.
- **Target Horizon $Y_{30}$**: Predicts bottleneck hazard formation 30 seconds ahead.
- **Decision Threshold $P \ge 0.60$**: Binary hazard label assigned iff probability $\ge 0.60$.
- **4-Tier Risk Level Classification**: `LOW` ($P < 0.30$), `MODERATE` ($0.30 \le P < 0.60$), `HIGH` ($0.60 \le P < 0.85$), `CRITICAL` ($P \ge 0.85$).

---

## 5. Hazard Event Engine Capabilities (`bhid/events`)
- **Active Zone Lock & Duplicate Suppression**: Prevents multiple active events in the same spatial zone concurrently.
- **Escalation Tracking**: Tracks risk escalation transitions (`LOW` $\rightarrow$ `MODERATE` $\rightarrow$ `HIGH` $\rightarrow$ `CRITICAL`).
- **Resolution Policy ($N=3$)**: Resolves active events after 3 consecutive safe predictions ($P < 0.60$).
- **Immutable Prediction History**: Appends timestamped prediction records to event histories.

---

## 6. Visual Telemetry & Rendering Capabilities (`bhid/visualization`)
- **OpenCV Composite Rendering**: Renders tracks, bounding boxes, centroid IDs, motion trails, and directional velocity vectors.
- **Density Heatmap Overlay**: Blends spatial density heatmaps over video frames ($\alpha = 0.4$).
- **HUD Telemetry Panels**: Renders real-time pedestrian count, density, and risk level badges.
- **Alert Banners**: Renders stacked hazard alert cards and screen-wide CRITICAL hazard banners.

---

## 7. Data Persistence & Audit Storage Capabilities (`bhid/persistence`)
- **Non-Blocking Exception Isolation**: All disk writes wrapped in `try/except` handlers; disk errors logged as `EXPORT_ERROR` to `AuditLog` without halting prediction pipelines.
- **Session Metadata & Directory Management**: Exports `session_metadata.json` and manages session directories under `bhid/data/sessions/`.
- **JSON & CSV File Exporters**: Persists predictions, analytics snapshots, hazard events, and monitoring telemetry to both JSON and CSV files.
- **Playback Manifest Indexing**: Indexes frame timelines in `playback_manifest.json` for offline replay.

---

## 8. Historical Session Replay Capabilities (`bhid/replay`)
- **Zero Model Re-Inference Replay**: Reconstructs historical session timelines directly from persisted Phase 5A artifacts without running model inference.
- **Event Timeline Reconstruction**: Synchronizes event state transitions (`ACTIVE`, `ESCALATED`, `RESOLVED`) across playback timestamps.
- **Timeline Controller**: Supports `play()`, `pause()`, `stop()`, `seek(frame_id)`, `next_frame()`, and `previous_frame()`.
- **Replay Telemetry Overlay**: Renders OpenCV replay frames featuring a `[REPLAY MODE]` visual watermark.

---

## 9. Operational Reporting Capabilities (`bhid/reporting`)
- **Operational KPI Engine**: Computes peak/average density, peak/average pedestrian count, peak risk probability, event counts, resolution rates (%), and average event durations.
- **Chronological Trend Analytics**: Computes density, flow, occupancy, and risk probability time-series trends.
- **Hazard Event Intelligence**: Ranks spatial ROI zones by critical event frequency and maximum risk probability.
- **Multi-Format Exporters**: Generates formatted GitHub-style Markdown reports (`report_{session_id}.md`), JSON data files, and CSV KPI tables.

---

## 10. System Operational Validation Capabilities (`bhid/validation`)
- **Read-Only Validation Suite**: Validates schema consistency, prediction integrity, hazard event lifecycle rules, persistence isolation, replay determinism, and reporting accuracy without mutating data.
- **Weighted Readiness Scoring Engine**: Evaluates formula $\text{Readiness Score} = \sum w_c S_c$ against component weights.
- **Health Status Assignment**: Assigns overall system status (`PASSED`, `WARNING`, `FAILED`) and exports `validation_report.json` and `validation_report.md`.
