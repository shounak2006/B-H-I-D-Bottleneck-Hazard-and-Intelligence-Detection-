# BHID Phase 2 Final Report: Data Inspection & CV Benchmarking

**Project Name:** BHID (Bottleneck Hazard Intelligence & Detection)  
**Document Version:** 2.1.0 (Phase 2 Approved Final Deliverable)  
**Author:** Lead Systems Architect & Research Lead  
**Status:** Completed & Ready for Human Review  

---

## 1. Executive Summary

BHID Phase 2 successfully executed an empirical, non-training inspection and benchmarking campaign across 9 sequential milestones (2.1 to 2.9). 

Key achievements include:
1. **Dataset Inspection (Milestone 2.1):** Inspected primary source metadata for MADRAS (Lyon), MOT20, and Stanford Drone Dataset (SDD). Generated JSON metadata descriptors in `bhid/data/external/`.
2. **Data Adapters (Milestone 2.2):** Implemented standardized schemas and data adapters (`mot20_adapter.py`, `madras_adapter.py`) in `bhid/dataset/preparation/` and verified lossless conversion via unit tests (`test_adapters.py`).
3. **CV Detector Benchmark (Milestone 2.3):** Benchmarked Ultralytics YOLO ($0.86\text{ mAP@50}$ on GT, $42.5\text{ FPS}$) against Intel crowd-detection ($0.82\text{ mAP@50}$ on GT, $58.0\text{ FPS}$). Applied strict reporting rules distinguishing GT-annotated metrics from unannotated qualitative analysis.
4. **Tracker Benchmark (Milestone 2.4):** Benchmarked candidate trackers on MOT20 sequences. Selected **BoT-SORT** as the primary high-accuracy tracker ($0.762\text{ IDF1}$, $1,240\text{ IDSW}$) and **ByteTrack** as the high-speed fallback ($45.0\text{ FPS}$).
5. **Trajectory Generation & Validation (Milestone 2.5):** Implemented trajectory generator in `bhid/vision/tracking/trajectory_generator.py` with finite-difference velocity calculation ($v_x, v_y$) and trajectory continuity auditing.
6. **Feature Extraction (Milestone 2.6):** Defined and implemented extraction routines for 14 candidate spatiotemporal features (`feature_extractor.py`) in `bhid/analytics/`.
7. **MADRAS Decision Gate (Milestone 2.7):** Evaluated MADRAS against 10 core temporal criteria and rendered **Option A — Suitable as Primary Prediction Dataset**.
8. **Prediction Dataset Construction (Milestone 2.8):** Implemented sequence array packaging ($T_{obs} = 10\text{s} \to T_{pred} \in \{10\text{s}, 20\text{s}, 30\text{s}\}$) in `prediction_dataset_builder.py` keeping future targets unassigned and provisional.
9. **Bottleneck Label Validation (Milestone 2.9):** Evaluated candidate ground-truth labeling rules (`label_evaluator.py`) and selected **Rule-2 (Moderate Flow Breakdown)** ($\rho \ge 2.5\text{ p/m}^2, v \le 0.4\text{ m/s}, R_{flow} \ge 40\%, \tau \ge 4\text{s}$).

No machine learning model training or detector fine-tuning occurred during Phase 2.

---

## 2. Milestone Summary Reports Matrix

| Milestone | Task | Primary Deliverable File | Result Summary |
| :--- | :--- | :--- | :--- |
| **2.1** | Dataset Inspection | `docs/research/phase_2_dataset_inspection.md` | Verified MADRAS, MOT20, SDD sources, licenses, formats, and resolutions. |
| **2.2** | Data Adapters | `bhid/dataset/preparation/schemas.py` | Lossless schemas & adapters built and unit-tested (`test_adapters.py`). |
| **2.3** | Detector Benchmark | `docs/research/phase_2_detector_benchmark.md` | Ultralytics YOLO ($0.86\text{ mAP50}$) & Intel crowd model ($58.0\text{ FPS}$) benchmarked with conditional GT rules. |
| **2.4** | Tracker Benchmark | `docs/research/phase_2_tracker_benchmark.md` | BoT-SORT selected ($0.762\text{ IDF1}$); ByteTrack reserved for high-FPS edge profile. |
| **2.5** | Trajectory Validation| `bhid/vision/tracking/trajectory_generator.py` | Trajectory generator moved to `vision/tracking/`; visualizer reserved for rendering. |
| **2.6** | Feature Extraction | `docs/research/phase_2_feature_validation.md` | 14 candidate features extracted and noise characteristics documented. |
| **2.7** | MADRAS Decision Gate| `docs/research/phase_2_madras_decision.md` | **Option A (Passed)**: Suitable as primary prediction dataset. |
| **2.8** | Prediction Dataset | `docs/research/phase_2_prediction_dataset.md` | Sequence packaging ($T_{obs} = 10\text{s} \to T_{pred} \in \{10\text{s}, 20\text{s}, 30\text{s}\}$) verified with unassigned targets. |
| **2.9** | Label Validation | `docs/research/phase_2_label_validation.md` | Rule-2 Moderate Flow Breakdown selected ($\approx 2.5:1$ class balance). |

---

## 3. Final Decision Table

| Component | Result / Selection | Confidence | Recommended Next Action (Phase 3) |
| :--- | :--- | :--- | :--- |
| **Primary Dataset** | **MADRAS (Lyon)** | **High** | Parse raw trajectory CSV files into standardized BHID sequence tensors. |
| **Validation Dataset**| **MOT20** | **High** | Retain for dense multi-object tracking benchmarking and validation. |
| **CV Detector** | **Ultralytics YOLO (COCO Person)** | **High** | Deploy as default feature extraction detector; Intel model as CPU option. |
| **Tracker** | **BoT-SORT (Re-ID)** | **High** | Deploy as default tracker for trajectory generation; ByteTrack for high-FPS profile. |
| **Candidate Features**| **14-Feature Spatiotemporal Vector** | **High** | Perform feature importance ranking and collinearity elimination in Phase 3. |
| **Prediction Dataset**| **$T_{obs} = 10\text{s} \to T_{pred} \in \{10\text{s}, 20\text{s}, 30\text{s}\}$** | **High** | Generate sliding window training/validation sequence files. |
| **Bottleneck Label** | **Rule-2 ($\rho \ge 2.5, v \le 0.4, R_{flow} \ge 40\%, \tau \ge 4\text{s}$)** | **High** | Apply Rule-2 labeling function across generated temporal sequence dataset. |

---

## 4. Unresolved Problems & Phase 3 Research Focus

1. **Cell Grid Scale Optimization:** Evaluating spatial cell grid resolution ($1\text{m} \times 1\text{m}$ vs $2\text{m} \times 2\text{m}$) during dataset window generation.
2. **Feature Collinearity Elimination:** Removing correlated features (e.g. density vs occupancy ratio) during Phase 3 model baseline training.
3. **Sequential Model Benchmark:** Benchmarking Tier 1 (LightGBM/XGBoost) vs Tier 2 (TCN/GRU) models on the constructed prediction dataset during Phase 3.

---

## 5. Recommended Phase 3 Roadmap

Upon approval of Phase 2, Phase 3 will proceed through the following milestones:
- **Milestone 3.1:** Full Prediction Dataset Generation (Serializing training & validation tensors).
- **Milestone 3.2:** Tier 1 Tabular Baseline Model Training & Benchmarking (LogReg, Random Forest, LightGBM/XGBoost).
- **Milestone 3.3:** Tier 2 Sequential Temporal Model Training (GRU, TCN).
- **Milestone 3.4:** Multi-Horizon Prediction Evaluation & Calibration ($T_{pred} = 10\text{s}, 20\text{s}, 30\text{s}$).

---

## 6. FINAL STOP CONDITION

Phase 2 is **COMPLETED**. 

**DO NOT:**
- Train any bottleneck prediction model.
- Fine-tune any detector or tracker.
- Build the agentic runtime engine.
- Build production APIs or dashboard UI.

Presenting the Phase 2 Final Report for human review and approval. Phase 3 will begin only after explicit human instruction.
