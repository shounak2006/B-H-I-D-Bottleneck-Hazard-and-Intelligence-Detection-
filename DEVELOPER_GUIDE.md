# BHID v1.0 - Developer & Onboarding Guide

This document provides technical guidelines for developers, computer vision engineers, and software architects extending or maintaining the **Bottleneck Hazard and Intelligence Detection (BHID)** platform v1.0.

---

## 1. Repository Directory Structure

```text
BHID/
├── bhid/
│   ├── vision/          # Detection schemas, MOT adapters, Centroid Tracker
│   ├── analytics/       # 14-feature crowd analytics calculators
│   ├── prediction/      # LightGBM/XGBoost inference engine & model registry
│   ├── events/          # Hazard event lifecycle state machine & alert policies
│   ├── visualization/   # OpenCV rendering, heatmaps, HUD panels, alert banners
│   ├── persistence/     # Non-blocking storage manager, session stores, audit log
│   ├── replay/          # Historical replay engine & timeline navigation controllers
│   ├── reporting/       # KPI engine, trend analyzers, Markdown/JSON/CSV exporters
│   ├── validation/      # Read-only schema validators & readiness scoring engine
│   ├── release/         # Environment validator, startup/shutdown, smoke tests
│   ├── runtime/         # RuntimeOrchestrator primary execution entrypoints
│   ├── models/          # model_registry.json & optimized .joblib model artifacts
│   ├── reports/         # Operational report output directory
│   └── tests/
│       ├── unit/        # Component unit test suites
│       └── integration/ # End-to-end pipeline integration test suites
├── ARCHITECTURE_GUIDE.md
├── DEVELOPER_GUIDE.md
├── MAINTENANCE_GUIDE.md
├── OPERATIONS_RUNBOOK.md
├── TESTING_GUIDE.md
├── RELEASE_NOTES_v1.0.md
├── SYSTEM_CAPABILITIES.md
├── HANDOVER_PACKAGE.md
├── INSTALLATION.md
└── OPERATOR_GUIDE.md
```

---

## 2. Coding Standards & Conventions

1. **Python Version Compatibility**: All code must execute cleanly on Python `3.9`, `3.10`, `3.11`, and `3.12`.
2. **PEP 8 Formatting**: Standard 4-space indentation, clear variable names, and 120-character line length limit.
3. **Type Annotations**: All public methods and functions must include type annotations (`typing.Dict`, `typing.List`, `typing.Optional`).
4. **Docstrings**: Public classes and methods must include Google-style docstrings describing parameters, return values, and exceptions.
5. **Frozen System Constraints**:
   - Do NOT modify the 14 approved spatiotemporal features.
   - Do NOT alter target horizon $Y_{30}$ or decision threshold $0.60$.
   - Do NOT retrain or alter model artifacts in production.
   - All persistence calls must remain wrapped in non-blocking exception handlers (`try/except`).

---

## 3. Extension Points

### 3.1 Adding a Custom Vision Detector
To integrate a custom object detector (e.g. YOLO, Faster R-CNN, or Haar cascades), inherit from `PedestrianDetectorInterface` in `bhid/vision/detection/pedestrian_detector_interface.py`:

```python
from bhid.vision.detection.pedestrian_detector_interface import PedestrianDetectorInterface
from bhid.vision.detection.detection_batch import DetectionBatch

class CustomYOLOv8Detector(PedestrianDetectorInterface):
    def detect(self, frame_id: int, timestamp: float, image_array=None) -> DetectionBatch:
        # Run custom YOLO inference
        detections = [] # list of DetectionObject
        return DetectionBatch(frame_id=frame_id, timestamp=timestamp, detections=detections)
```

### 3.2 Adding Custom Analytics Sub-Metrics
To add internal telemetry calculations without altering the 14 frozen features, extend calculators under `bhid/analytics/`.

---

## 4. Testing & Regression Workflow

Always execute the complete regression test suite before submitting pull requests:

```bash
# Run unit tests
python -m unittest discover -s bhid/tests/unit

# Run integration tests
python -m unittest discover -s bhid/tests/integration

# Run pre-flight release verification
python -c "from bhid.runtime import RuntimeOrchestrator; orchestrator = RuntimeOrchestrator(); print(orchestrator.run_release_verification())"
```

---

## 5. Debugging Workflow

1. **Inspect Audit Log**: Check `bhid/data/sessions/{session_id}/audit/audit_log.json` for `EXPORT_ERROR` or system state events.
2. **Run Validation Suite**: Execute `orchestrator.run_system_validation(session_id="target_session")` to isolate schema or prediction anomalies.
