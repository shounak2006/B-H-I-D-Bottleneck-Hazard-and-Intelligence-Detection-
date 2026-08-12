# BHID Phase 2: Milestone 2.6 — Candidate Feature Extraction & Validation Report

**Document Version:** 1.0.0  
**Phase:** Phase 2 (Milestone 2.6)  
**Author:** Lead Systems Architect & Analytics Lead  
**Status:** Completed & Verified  

---

## 1. Executive Summary

Milestone 2.6 established the mathematical formulation, input specifications, noise behaviors, and feature extraction routines for the **14 Candidate Spatiotemporal Features**. Feature extraction routines were implemented in `bhid/analytics/feature_extractor.py` and validated on synthetic and dataset-derived trajectory streams.

---

## 2. Detailed Specification of 14 Candidate Features

| Feature Name | Mathematical Definition | Units | Spatial / Temporal Window | Missing Data Behavior | Expected Noise Sources |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Pedestrian Count ($N_t$)** | $N_t = \sum_{i \in \text{tracks}} \mathbb{I}(\text{pos}_i \in \Omega)$ | Count | Spatial zone $\Omega$, Instantaneous frame $t$ | Defaults to 0 | False positive detections, bounding box duplication. |
| **2. Crowd Density ($\rho_t$)** | $\rho_t = N_t / \text{Area}(\Omega)$ | $\text{p/m}^2$ | Zone $\Omega$, Instantaneous $t$ | Defaults to 0.0 | Ground area calibration errors, camera perspective tilt. |
| **3. Occupancy Ratio ($O_t$)** | $O_t = \sum \text{Area}(\mathcal{B}_i) / \text{Area}(\Omega)$ | Ratio $[0.0, 1.0]$ | Zone $\Omega$, Instantaneous $t$ | Defaults to 0.0 | Scale variations in perspective distortion. |
| **4. Mean Speed ($\bar{v}_t$)** | $\bar{v}_t = \frac{1}{N_t} \sum \|v_i\|$ | $\text{m/s}$ | Zone $\Omega$, 3-frame rolling window | Defaults to 0.0 | Kalman filter smoothing delay, detection jitter. |
| **5. Velocity Variance ($\sigma^2_{v,t}$)** | $\sigma^2_{v,t} = \frac{1}{N_t} \sum (\|v_i\| - \bar{v}_t)^2$ | $(\text{m/s})^2$ | Zone $\Omega$, 3-frame rolling window | Defaults to 0.0 | Measurement noise in individual trajectory velocities. |
| **6. Acceleration ($\bar{a}_t$)** | $\bar{a}_t = (\bar{v}_t - \bar{v}_{t-\Delta t}) / \Delta t$ | $\text{m/s}^2$ | Zone $\Omega$, $\Delta t = 1.0\text{s}$ window | Defaults to 0.0 | Finite difference derivative amplification of noise. |
| **7. Directional Entropy ($H_{dir,t}$)** | $H_{dir,t} = -\sum_{b=1}^8 p_b \log_2(p_b)$ | Bits $[0, 3]$ | Zone $\Omega$, Instantaneous $t$ | Defaults to 0.0 (uniform) | Discretization artifacts across 8 directional angle bins. |
| **8. Inflow Rate ($Q_{in,t}$)** | $Q_{in,t} = |\{\text{IDs}_t\} \setminus \{\text{IDs}_{t-\Delta t}\}|$ | $\text{ped/s}$ | Zone $\Omega$, $\Delta t = 1.0\text{s}$ window | Defaults to 0.0 | Identity switches falsely appearing as new inflows. |
| **9. Outflow Rate ($Q_{out,t}$)** | $Q_{out,t} = |\{\text{IDs}_{t-\Delta t}\} \setminus \{\text{IDs}_t\}|$ | $\text{ped/s}$ | Zone $\Omega$, $\Delta t = 1.0\text{s}$ window | Defaults to 0.0 | Track loss falsely appearing as outflows. |
| **10. Net Flow Rate ($\Delta Q_t$)** | $\Delta Q_t = Q_{in,t} - Q_out,t$ | $\text{ped/s}$ | Zone $\Omega$, $\Delta t = 1.0\text{s}$ window | Defaults to 0.0 | Combination of inflow/outflow identity noise. |
| **11. Flow Drop Ratio ($R_{flow,t}$)** | $R_{flow,t} = \frac{Q_{in,t} - Q_{out,t}}{\max(Q_{in,t}, 1)}$ | Ratio $[-1, 1]$ | Zone $\Omega$, $\Delta t = 1.0\text{s}$ window | Defaults to 0.0 | Zero inflow edge cases. |
| **12. Trajectory Convergence ($C_{traj,t}$)** | $C_{traj,t} = \frac{\|\sum \vec{v}_i\|}{N_t \cdot \bar{v}_t + \epsilon}$ | Ratio $[0, 1]$ | Zone $\Omega$, Instantaneous $t$ | Defaults to 0.0 | Uniform multidirectional crowds canceling net velocity. |
| **13. Temporal Density Change ($\Delta \rho_t$)** | $\Delta \rho_t = (\rho_t - \rho_{t-3s}) / 3.0$ | $\text{p/m}^2/\text{s}$ | Zone $\Omega$, 3-second rolling window | Defaults to 0.0 | Sudden camera occlusion drops. |
| **14. Temporal Speed Change ($\Delta \bar{v}_t$)** | $\Delta \bar{v}_t = (\bar{v}_t - \bar{v}_{t-3s}) / 3.0$ | $\text{m/s}^2$ | Zone $\Omega$, 3-second rolling window | Defaults to 0.0 | Brief pedestrian pauses. |
