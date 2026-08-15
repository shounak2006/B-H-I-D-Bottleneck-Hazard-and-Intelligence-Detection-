# BHID v1.0 - Operator & System Administration Guide

This guide provides operational procedures for system operators, security managers, and crowd analysts running the **Bottleneck Hazard and Intelligence Detection (BHID)** platform v1.0.

---

## 1. System Overview

BHID provides real-time spatiotemporal crowd bottleneck prediction, hazard event management, visual telemetry rendering, non-blocking data persistence, deterministic historical playback, multi-format operational reporting, and system readiness validation.

```text
Video Stream / Frame Sequence
        ↓
Detector Layer (Phase 4B)
        ↓
Centroid Tracker (Phase 4C)
        ↓
14-Feature Crowd Analytics Engine (Phase 4D)
        ↓
10s @ 2.5Hz Feature Window Manager (Phase 4A)
        ↓
BottleneckPredictor Engine (Phase 3D - Y30 Horizon, Threshold 0.60)
        ↓
Hazard Event Lifecycle Engine (Phase 4E)
        ↓
OpenCV Telemetry & Overlay Renderer (Phase 4F)
        ↓
Non-Blocking Persistence Manager (Phase 5A)
        ↓
Historical Replay Engine (Phase 5B) | Operational Reporting (Phase 5C) | System Validation (Phase 5D)
```

---

## 2. Real-Time Video Monitoring Workflow

To process incoming camera frame sequences and generate bottleneck risk predictions, run:

```python
from bhid.runtime import RuntimeOrchestrator, PipelineContext
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor
from bhid.persistence import PersistenceManager, PersistenceConfig

# 1. Initialize Context & Predictor
context = PipelineContext(active_scene="STATION_CONCOURSE", active_zone="NORTH_EXIT")
predictor = BottleneckPredictor()
orchestrator = RuntimeOrchestrator(predictor=predictor, context=context)

# 2. Setup Persistence
config = PersistenceConfig(session_id="live_monitoring_001")
pm = PersistenceManager(config=config)

# 3. Process Live Monitoring Frame Sequence
# (Pass incoming tracking_batch and OpenCV video frame)
result = orchestrator.process_persistent_monitoring_frame(
    tracking_batch=tracking_batch,
    frame=input_frame,
    persistence_manager=pm,
    scene_id="STATION_CONCOURSE",
    zone_id="NORTH_EXIT"
)

print("Current Hazard Risk Level:", result["prediction_result"]["risk_level"])
print("Bottleneck Probability (Y30):", f"{result['prediction_result']['prediction_probability']*100:.1f}%")
```

---

## 3. Hazard Event Lifecycle & Risk Levels

BHID categorizes bottleneck hazard predictions into 4 operational risk levels:

| Risk Level | Probability ($Y_{30}$) | System Action / Escalation Policy |
|---|---|---|
| **LOW** | $< 30\%$ | Normal crowd movement. Green HUD status badge. |
| **MODERATE** | $30\% \le P < 60\%$ | Emerging crowd density. Yellow HUD status badge. |
| **HIGH** | $60\% \le P < 85\%$ | **Hazard Threshold Breached ($P \ge 0.60$)**. Hazard event created (`ACTIVE`). Orange HUD alert banner. |
| **CRITICAL** | $\ge 85\%$ | **Severe Bottleneck Risk**. Event escalated (`ESCALATED`). Red screen-wide warning banner. |

### Resolution Policy
A hazard event remains active until **3 consecutive safe predictions ($P < 0.60$)** are recorded. Once resolved, the event status changes to `RESOLVED` and is permanently archived in history.

---

## 4. Historical Session Replay Workflow

To replay a previously recorded operational session deterministically without re-running model inference:

```python
from bhid.runtime import RuntimeOrchestrator

orchestrator = RuntimeOrchestrator()

# Replay historical session
replay_out = orchestrator.replay_historical_session(session_id="live_monitoring_001")

print("Total Replayed Frames:", replay_out["total_frames"])
print("Peak Density Observed:", replay_out["replay_summary"]["peak_density_ped_per_m2"], "ped/m²")

# Access reconstructed replay frames and rendered OpenCV images
for item in replay_out["replayed_frames"]:
    rf = item["replay_frame"]
    rendered_image = item["rendered_image"] # OpenCV BGR Image with [REPLAY MODE] watermark
```

---

## 5. Operational Reporting Workflow

To generate structured Markdown reports, JSON data files, and CSV KPI tables from recorded sessions:

```python
from bhid.runtime import RuntimeOrchestrator

orchestrator = RuntimeOrchestrator()

# Generate report for single session
report_out = orchestrator.generate_operational_report(session_id="live_monitoring_001")

print("Generated Markdown Report Path:", report_out["exported_files"]["markdown"])
print("\n--- Report Preview ---\n")
print(report_out["markdown_content"][:500])
```

Reports are automatically saved to `bhid/reports/`:
- `report_{session_id}.md`
- `report_{session_id}.json`
- `report_{session_id}.csv`

---

## 6. System Operational Validation Workflow

To run a read-only system validation audit and compute the operational readiness score:

```python
from bhid.runtime import RuntimeOrchestrator

orchestrator = RuntimeOrchestrator()

# Run system validation & export readiness report
val_out = orchestrator.generate_validation_report(session_id="live_monitoring_001")

eval_res = val_out["evaluation"]
print("Overall Readiness Status:", eval_res["overall_status"]) # PASSED / WARNING / FAILED
print("Readiness Score:", f"{eval_res['readiness_score_pct']:.1f}%")
print("Validation Report exported to:", val_out["exported_files"]["markdown"])
```

Validation reports are saved to `bhid/reports/validation/`:
- `validation_report.json`
- `validation_report.md`

---

## 7. Graceful System Shutdown Procedure

To cleanly terminate monitoring sessions and flush all pending persistence buffers:

```python
from bhid.runtime import RuntimeOrchestrator

orchestrator = RuntimeOrchestrator()

# Execute graceful platform shutdown
shutdown_status = orchestrator.shutdown_bhid(persistence_manager=pm)
print("Shutdown Status:", shutdown_status["status"])
```
