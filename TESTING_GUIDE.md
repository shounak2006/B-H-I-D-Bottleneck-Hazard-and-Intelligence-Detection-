# BHID v1.0 - Testing Strategy & Verification Guide

This document details the testing architecture, unit test suites, integration pipelines, smoke test runners, read-only operational validation, and regression verification procedures for the **Bottleneck Hazard and Intelligence Detection (BHID)** platform v1.0.

---

## 1. Testing Architecture Overview

BHID employs a 4-tier testing hierarchy to guarantee prediction accuracy, cross-phase schema consistency, non-blocking persistence isolation, historical replay determinism, reporting precision, and operational release readiness.

```text
Tier 1: Unit Test Suites (bhid/tests/unit/)
        ↓
Tier 2: Integration Test Suites (bhid/tests/integration/)
        ↓
Tier 3: Release Smoke Test Verification (SmokeTestRunner)
        ↓
Tier 4: Read-Only System Operational Validation (ValidationManager)
```

---

## 2. Unit Testing Strategy

Unit tests isolate individual modules and verify contracts independently:

- **`test_detection_schema.py` & `test_mock_detector.py`**: Verifies bounding box bounding algorithms and detection object schemas.
- **`test_centroid_tracker.py`**: Verifies Euclidean track association and persistent non-reusable track IDs.
- **`test_speed_metrics.py` ... `test_egress_metrics.py`**: Verifies math formulas for all 14 frozen spatiotemporal features.
- **`test_inference.py`**: Verifies `BottleneckPredictor` LightGBM/XGBoost inference, probability bounds $[0,1]$, threshold enforcement ($0.60$), target horizon ($Y_{30}$), and 4-tier risk level mapping.
- **`test_hazard_event.py` & `test_event_engine.py`**: Verifies hazard event creation, zone duplicate locks, escalation counters, and $N=3$ safe prediction resolution rules.
- **`test_session_manager.py` ... `test_persistence_manager.py`**: Verifies persistence store ingestion, session closure, audit log immutability, and **non-blocking exception isolation** (simulated disk permission write failures).
- **`test_playback_loader.py` ... `test_playback_engine.py`**: Verifies artifact loading, event timeline reconstruction, and playback cursor navigation.
- **`test_kpi_engine.py` ... `test_reporting_manager.py`**: Verifies operational KPI math, trend extraction, Markdown report rendering, and multi-format exports.
- **`test_consistency_validator.py` ... `test_validation_manager.py`**: Verifies read-only schema checking, prediction auditing, and weighted readiness scoring ($\sum w_c S_c$).
- **`test_environment_validator.py` ... `test_packaging_manager.py`**: Verifies pre-flight environment checks, startup/shutdown orchestration, and release packaging.
- **`test_documentation_completeness.py`**: Verifies existence and required section headers of all root Markdown guides.

---

## 3. Integration Testing Strategy

Integration tests evaluate complete multi-phase pipeline flows:

- **`test_pipeline_integration.py`**: Verifies `Detection → Tracking → Feature Window → Predictor → Hazard Event Engine`.
- **`test_visualization_pipeline_integration.py`**: Verifies OpenCV visual frame rendering and HUD annotation overlays.
- **`test_persistence_pipeline_integration.py`**: Verifies end-to-end persistent recording to disk storage.
- **`test_replay_pipeline_integration.py`**: Verifies offline historical playback from persisted session files.
- **`test_reporting_pipeline_integration.py`**: Verifies operational report generation from recorded sessions.
- **`test_system_validation_integration.py`**: Verifies end-to-end read-only validation audits and readiness scoring.
- **`test_release_pipeline_integration.py`**: Verifies complete pre-flight release verification, startup, smoke tests, packaging, and shutdown.

---

## 4. Smoke Testing & Release Verification

Pre-release smoke tests execute fast, lightweight instantiation checks across all 8 platform layers without retraining models or modifying persisted session files:

```python
from bhid.release import SmokeTestRunner

results = SmokeTestRunner.run_smoke_tests()
print("Smoke Tests Passed:", results["passed"])
```

---

## 5. Read-Only Operational Validation Workflow

The read-only validation suite computes the operational readiness score ($0.0 \dots 100.0\%$) using explicit component weights:

```python
from bhid.validation import ValidationManager

vm = ValidationManager()
eval_res = vm.run_all_validations(session_id="target_session_id")
print("System Readiness Status:", eval_res["overall_status"]) # PASSED
```

---

## 6. Running Full Regression Discovery

To execute the complete regression test suite across all 120+ unit and integration tests:

```bash
# Run unit test suite
python -m unittest discover -s bhid/tests/unit

# Run integration test suite
python -m unittest discover -s bhid/tests/integration
```
