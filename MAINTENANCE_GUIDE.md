# BHID v1.0 - Maintenance & System Administration Guide

This guide details routine system maintenance procedures, dependency updates, model artifact replacement rules, storage cleanup, session retention policies, and troubleshooting procedures for the **Bottleneck Hazard and Intelligence Detection (BHID)** platform v1.0.

---

## 1. Updating Dependencies

### Dependency Guidelines
- Platform dependencies are pinned in `bhid/requirements.txt`.
- Minor patch updates to `numpy`, `pandas`, `opencv-python`, `scikit-learn`, or `scipy` may be installed directly.
- **Critical Requirement**: Always run the full regression test suite after updating any dependency package:

```bash
pip install -r bhid/requirements.txt --upgrade
python -m unittest discover -s bhid/tests/unit
python -m unittest discover -s bhid/tests/integration
```

---

## 2. Model Artifact Management

BHID prediction models are registered in `bhid/models/model_registry.json`.

```json
{
  "active_model": "LightGBM_Optimized",
  "model_path": "models/lightgbm_optimized.joblib",
  "target_horizon": "Y30",
  "threshold": 0.60
}
```

### Model Replacement Rules
1. Any replacement model artifact must be trained strictly on the 14 approved spatiotemporal features.
2. The replacement `.joblib` model file must be placed in `bhid/models/`.
3. Update `model_path` in `bhid/models/model_registry.json`.
4. Run `PredictionValidator` to verify inference determinism and threshold enforcement ($0.60$):

```python
from bhid.validation import PredictionValidator
# Verify new model load via BottleneckPredictor
```

---

## 3. Storage Cleanup & Session Retention

BHID persists operational recording sessions to `bhid/data/sessions/{session_id}/`. Over time, old recording sessions consume disk space.

### Session Retention Policy
- Active sessions: Retain indefinitely until archived.
- Historical sessions older than $N$ days (default: 30 days) may be archived or deleted.

### Automated Cleanup Script Command
To clean historical sessions older than 30 days while preserving reports:

```powershell
# Example Windows PowerShell command to delete sessions older than 30 days
Get-ChildItem -Path "bhid/data/sessions" -Directory | Where-Language { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Recurse -Force
```

---

## 4. Troubleshooting Procedures

| Symptom / Issue | Cause | Corrective Action |
|---|---|---|
| `EXPORT_ERROR` in audit log | Target storage drive full or read-only directory permissions | Verify disk space on storage drive and check write permissions for `bhid/data/sessions/`. Persistence operates non-blockingly, so pipeline execution will continue normally. |
| Model registry missing error | Executing script from incorrect working directory | Always run Python scripts from the project root directory. |
| High memory utilization | Large frame trail history buffer | Adjust `max_track_history` in `VisualConfig` (`bhid/visualization/visual_config.py`). |
| Read-Only validation failure | Schema drift or altered features | Run `ConsistencyValidator` to verify all 14 frozen features exist in `AnalyticsSnapshot`. |
