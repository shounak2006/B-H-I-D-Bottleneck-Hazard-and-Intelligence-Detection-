# BHID Phase 2: Milestone 2.8 — Candidate Prediction Dataset Construction Report

**Document Version:** 1.1.0  
**Phase:** Phase 2 (Milestone 2.8)  
**Author:** Lead Systems Architect & Data Engineering Lead  
**Status:** Completed & Verified  

---

## 1. Executive Summary

Milestone 2.8 proved that the temporal data structure required for near-future bottleneck risk modeling can be constructed from sliding window feature streams ($T_{obs} = 10\text{s} \to T_{pred} \in \{10\text{s}, 20\text{s}, 30\text{s}\}$). The candidate prediction dataset builder was implemented in `bhid/dataset/preparation/prediction_dataset_builder.py` and validated on temporal sequences without performing ML model training.

> [!IMPORTANT]
> **Provisional Labeling Constraint:** Per BHID Phase 2 guidelines, Milestone 2.8 constructs temporal observation/future-window structures **without treating future placeholders as validated ground-truth labels**. All future target placeholders remain unassigned and provisional until Milestone 2.9 empirically evaluates candidate bottleneck definitions.

---

## 2. Dataset Array Architecture & Structure

```text
Sequence Window Index t
┌────────────────────────────────────────────────────────┐
│ Observation Feature Sequence X_{t-10s : t}            │
│ Shape: [25 steps × K candidate features] (@ 2.5 Hz)    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│ Metadata & Provisional Future Window Payload           │
│ - Scene ID: "MADRAS_Lyon_Scene1"                      │
│ - Zone ID: "Zone_Cell_Grid_u4_v8"                     │
│ - Timestamp: t (seconds)                               │
│ - Prediction Horizons: [10s, 20s, 30s]                │
│ - Target Placeholders (Unassigned): [Provisional]      │
└────────────────────────────────────────────────────────┘
```

---

## 3. Data Schema & Memory Footprint

- **Sample Record Shape:** Each record comprises a $[25 \times 14]$ float32 feature tensor ($1.4\text{ KB}$ per window instance).
- **Temporal Cadence:** Windows are sampled every $0.4\text{s}$ ($2.5\text{ Hz}$).
- **Data Provenance Preservation:** Every sample retains original `scene_id`, `camera_id`, `zone_id`, `timestamp_sec`, and dataset provenance tag.
- **Verification Result:** Confirmed that temporal sliding window tensors can be constructed, padded, and serialized cleanly while keeping future target labels unassigned.
