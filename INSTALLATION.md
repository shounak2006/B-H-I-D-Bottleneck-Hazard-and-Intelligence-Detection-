# BHID v1.0 - System Installation & Deployment Guide

This guide provides step-by-step instructions for installing, configuring, verifying, and deploying the **Bottleneck Hazard and Intelligence Detection (BHID)** platform v1.0.

---

## 1. System Prerequisites

### Hardware Requirements
- **CPU**: Dual-core x86_64 / ARM64 processor (Quad-core recommended for real-time video stream processing).
- **RAM**: 8 GB minimum (16 GB recommended).
- **Disk Space**: 2 GB free disk space for base platform installation and session recording storage.

### Software Prerequisites
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), or macOS (11.0+).
- **Python**: Python `3.9`, `3.10`, `3.11`, or `3.12` (64-bit).
- **Git**: Git 2.25+ for repository cloning.

---

## 2. Installation Steps

### Step 2.1: Clone the BHID Repository

```bash
git clone https://github.com/shounak2006/B-H-I-D-Bottleneck-Hazard-and-Intelligence-Detection-.git
cd B-H-I-D-Bottleneck-Hazard-and-Intelligence-Detection-
```

### Step 2.2: Create Virtual Environment

It is strongly recommended to use an isolated Python virtual environment:

#### On Windows (PowerShell / CMD):
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### On Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2.3: Install Required Dependencies

Upgrade `pip` and install all platform dependencies from `requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r bhid/requirements.txt
```

#### Core Package Inventory
- `numpy`: Numerical vector & spatial array operations
- `pandas`: Tabular feature data processing
- `opencv-python`: Image frame rendering & spatial annotation
- `lightgbm`: Machine learning model inference (Y30 horizon)
- `xgboost`: Machine learning model inference
- `scikit-learn`: Feature processing & statistical metrics
- `scipy`: Spatial density & geometric calculations

---

## 3. Model Artifact Verification

BHID uses pre-trained bottleneck prediction model artifacts registered in `bhid/models/model_registry.json`.

Run the following command to verify model artifact integrity:

```python
from bhid.prediction.inference.predict_bottleneck import BottleneckPredictor

predictor = BottleneckPredictor()
print("Model Registry Loaded Successfully:", predictor.is_ready())
```

---

## 4. First-Run System Initialization

Verify your local installation by initializing the BHID platform and running pre-flight environment checks:

```python
from bhid.runtime import RuntimeOrchestrator, PipelineContext

context = PipelineContext(active_scene="TEST_LOCATION", active_zone="MAIN_HALL")
orchestrator = RuntimeOrchestrator(context=context)

# Pre-flight environment check and initialization
init_status = orchestrator.initialize_bhid()
print("BHID Pre-flight Initialization Status:", init_status["status"])
```

---

## 5. Release Smoke Testing

Run the automated release smoke test suite to verify all 8 platform layers:

```python
from bhid.release import SmokeTestRunner

results = SmokeTestRunner.run_smoke_tests()
print("Smoke Test Verification Passed:", results["passed"])
print("Passed Component Layers:", f"{results['passed_layers_count']}/{results['total_layers_tested']}")
```

Alternatively, run unit and integration regression test discovery:

```bash
python -m unittest discover -s bhid/tests/unit
python -m unittest discover -s bhid/tests/integration
```

---

## 6. Troubleshooting & Support

### Common Issues

1. **`ImportError: No module named 'cv2'`**
   - Solution: Install OpenCV via `pip install opencv-python`.

2. **`FileNotFoundError: model_registry.json`**
   - Solution: Verify you are running Python commands from the project root directory containing `bhid/models/model_registry.json`.

3. **Permission Errors when writing reports**
   - Solution: Ensure your user account has write permissions to `bhid/reports/` and `bhid/data/sessions/`.
