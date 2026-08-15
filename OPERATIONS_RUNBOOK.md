# BHID v1.0 - Operations Runbook

This runbook provides step-by-step operational instructions for system operators running the **Bottleneck Hazard and Intelligence Detection (BHID)** platform v1.0.

---

## 1. System Initialization (`initialize_bhid()`)

Before launching video monitoring workflows, run pre-flight environment validation and component startup checks:

```python
from bhid.runtime import RuntimeOrchestrator, PipelineContext

context = PipelineContext(active_scene="MAIN_TERMINAL", active_zone="NORTH_CONCOURSE")
orchestrator = RuntimeOrchestrator(context=context)

# 1. Execute system pre-flight startup initialization
init_status = orchestrator.initialize_bhid()
print("Startup Status:", init_status["status"]) # INITIALIZED
```

---

## 2. Real-Time Video Monitoring (`process_persistent_monitoring_frame()`)

To process live video tracking batches, generate predictions, update hazard events, render visual overlays, and persist data non-blockingly:

```python
from bhid.persistence import PersistenceConfig, PersistenceManager

# Setup Persistence Manager
p_config = PersistenceConfig(session_id="session_2026_08_16_01")
pm = PersistenceManager(config=p_config)

# Process incoming frame
frame_result = orchestrator.process_persistent_monitoring_frame(
    tracking_batch=tracking_batch,
    frame=input_frame,
    persistence_manager=pm,
    scene_id="MAIN_TERMINAL",
    zone_id="NORTH_CONCOURSE"
)

# Extract telemetry
prediction = frame_result["prediction_result"]
print("Bottleneck Probability (Y30):", f"{prediction['prediction_probability']*100:.1f}%")
print("Current Risk Level:", prediction["risk_level"])
print("Active Events Count:", frame_result["active_event_count"])
```

---

## 3. Historical Session Replay (`replay_historical_session()`)

To replay a previously recorded operational session deterministically without re-running model inference:

```python
# Replay historical session
replay_out = orchestrator.replay_historical_session(session_id="session_2026_08_16_01")

print("Replayed Frames Count:", replay_out["total_frames"])
summary = replay_out["replay_summary"]
print("Peak Density Observed:", summary["peak_density_ped_per_m2"], "ped/m²")
```

---

## 4. Operational Report Generation (`generate_operational_report()`)

To generate structured Markdown operational reports, JSON summaries, and CSV KPI tables:

```python
# Generate operational report
report_out = orchestrator.generate_operational_report(session_id="session_2026_08_16_01")

print("Exported Markdown Path:", report_out["exported_files"]["markdown"])
print("Exported JSON Path:", report_out["exported_files"]["json"])
print("Exported CSV Path:", report_out["exported_files"]["csv"])
```

---

## 5. System Validation & Health Assessment (`generate_validation_report()`)

To perform a read-only audit and compute system operational readiness scores:

```python
# Execute system validation
val_out = orchestrator.generate_validation_report(session_id="session_2026_08_16_01")

eval_res = val_out["evaluation"]
print("Validation Status:", eval_res["overall_status"]) # PASSED
print("Readiness Score:", f"{eval_res['readiness_score_pct']:.1f}%")
```

---

## 6. Graceful System Shutdown (`shutdown_bhid()`)

To cleanly close active recording sessions and flush pending persistence buffers:

```python
# Execute graceful platform shutdown
shutdown_status = orchestrator.shutdown_bhid(persistence_manager=pm)
print("Shutdown Status:", shutdown_status["status"]) # SHUTDOWN_COMPLETE
```
