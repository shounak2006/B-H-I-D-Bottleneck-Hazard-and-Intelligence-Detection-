# BHID Phase 3A: Final Prediction Dataset Generation Report

**Project Name:** BHID (Bottleneck Hazard Intelligence & Detection)  
**Document Version:** 3.1.0 (Phase 3A Final Deliverable)  
**Author:** Lead Data Engineer & Research Architect  
**Status:** Completed & Verified — Ready for Google Colab Training  

---

## 1. Executive Summary

BHID Phase 3A successfully executed the construction, auditing, and packaging of the final machine-learning-ready prediction dataset (`bhid_prediction_dataset.csv` and `.parquet`). All core parameter definitions, target onset formulations, active-event masking constraints, and 14 feature definitions from Phase 1 and Phase 2 remain strictly frozen and verified.

---

## 2. Frozen Configuration Specifications

- **Observation Window ($T_{obs}$):** $10.0\text{s} = 25\text{ analytics samples} = 250\text{ raw video frames}$ (@ $2.5\text{ Hz} / \Delta t = 0.4\text{s}$).
- **Target Horizons ($h$):** $Y_{10}$ (10s), $Y_{20}$ (20s), $Y_{30}$ (30s).
- **Target Onset Logic:** $Y_h(t) = 1 \iff \text{BottleneckState}(t) = 0 \land \exists \, t' \in (t, t+h] \text{ such that } \text{EventOnset}(t') = 1$.
- **Active-Event Masking:** All samples where $\text{BottleneckState}(t) = 1$ are strictly excluded from the prediction dataset.
- **Rule-2 Moderate Flow Breakdown:** Density $\ge 2.5\text{ ped/m}^2 \land \bar{v} \le 0.40\text{ m/s} \land R_{egress} \ge 0.40 \text{ for } \ge 4.0\text{s}$.
- **Egress Deficit Ratio:** $R_{egress} = 1 - (Q_{out} / Q_{in})$ when $Q_{in} > 0$, else $0.0$.

---

## 3. Dataset Dimensions & Class Balance

| Metric | Total Dataset | Train Split (52.6%) | Validation Split (23.5%) | Test Split (23.8%) |
| :--- | :--- | :--- | :--- | :--- |
| **Total Valid Samples** | **7,428** | **3,908** | **1,749** | **1,771** |
| **Scenes Assigned** | 4 Scenes | Scene1, Scene4 | Scene2 | Scene3 |
| **Distinct Events** | 14 Events | 7 Events | 4 Events | 3 Events |
| **$Y_{10}$ Positive Count (%)** | **265 (3.57%)** | 139 (3.56%) | 97 (5.55%) | 29 (1.64%) |
| **$Y_{20}$ Positive Count (%)** | **487 (6.56%)** | 264 (6.76%) | 169 (9.66%) | 54 (3.05%) |
| **$Y_{30}$ Positive Count (%)** | **689 (9.28%)** | 389 (9.95%) | 221 (12.64%) | 79 (4.46%) |

---

## 4. Filtering & Audit Summary

- **Total Sliding Windows Evaluated:** 7,875
- **Invalid / Edge Truncated Windows Removed:** 396
- **Active Bottleneck Event Samples Excluded:** 51
- **Final Leakage Status:** **PASS — ZERO DATA LEAKAGE**

---

## 5. Approved 14 Feature Column Schema

1. `feature_pedestrian_count` (Pedestrian Count)
2. `feature_density_ped_per_m2` (Crowd Density)
3. `feature_occupancy_ratio` (Occupancy Ratio)
4. `feature_mean_speed_m_s` (Mean Speed)
5. `feature_velocity_variance` (Velocity Variance)
6. `feature_acceleration_m_s2` (Acceleration)
7. `feature_directional_entropy` (Directional Entropy)
8. `feature_inflow_rate_per_s` (Inflow Rate $Q_{in}$)
9. `feature_outflow_rate_per_s` (Outflow Rate $Q_{out}$)
10. `feature_net_flow_rate_per_s` (Net Flow Rate)
11. `feature_egress_deficit_ratio` (Egress Deficit Ratio $R_{egress}$)
12. `feature_trajectory_convergence` (Trajectory Convergence)
13. `feature_temporal_density_change` (Density Change over 10s)
14. `feature_temporal_speed_change` (Speed Change over 10s)

---

## 6. Output Files Location Summary

- Main Dataset: `bhid/data/processed/bhid_prediction_dataset.csv` / `.parquet`
- Split Datasets: `train.csv`, `val.csv`, `test.csv` (`.csv` and `.parquet`)
- Schema & Metadata: `dataset_schema.json`, `dataset_statistics.json`, `split_statistics.json`
- Leakage Audit: `docs/research/phase_3A_leakage_audit.md`
- Dataset Statistics Report: `docs/research/phase_3A_dataset_statistics.md`

NO ML MODEL TRAINING HAS BEEN PERFORMED.
