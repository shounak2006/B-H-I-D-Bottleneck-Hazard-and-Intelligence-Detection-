# BHID Phase 3A: Dataset Statistics & Feature Distributions

---

## 1. Overview Statistics

- **Total Samples:** 7,428
- **Unique Scenes:** 4
- **Unique Spatial Zones:** 4
- **Feature Column Count:** 14

---

## 2. Target Class Distributions

- **Y10 Positive Onsets (0-10s):** 265 (3.57%) | Negatives: 7163
- **Y20 Positive Onsets (0-20s):** 487 (6.56%) | Negatives: 6941
- **Y30 Positive Onsets (0-30s):** 689 (9.28%) | Negatives: 6739

---

## 3. Feature Distribution Statistics (Mean ± Std [Min, Max])

| Feature Name | Mean | Std | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| `feature_pedestrian_count` | 486.2811 | 181.6277 | 306.0 | 1600.0 |
| `feature_density_ped_per_m2` | 1.2384 | 0.4016 | 1.02 | 3.58 |
| `feature_occupancy_ratio` | 0.3096 | 0.1004 | 0.255 | 0.895 |
| `feature_mean_speed_m_s` | 1.0814 | 0.1892 | 0.207 | 1.2 |
| `feature_velocity_variance` | 0.1298 | 0.0227 | 0.025 | 0.144 |
| `feature_acceleration_m_s2` | 0.0014 | 0.0038 | -0.001 | 0.019 |
| `feature_directional_entropy` | 1.3046 | 0.1606 | 0.368 | 1.392 |
| `feature_inflow_rate_per_s` | 1.3173 | 0.3398 | 1.12 | 3.482 |
| `feature_outflow_rate_per_s` | 1.2099 | 0.1334 | 0.307 | 1.33 |
| `feature_net_flow_rate_per_s` | 0.1074 | 0.4682 | -0.21 | 3.175 |
| `feature_egress_deficit_ratio` | 0.0869 | 0.1781 | 0.0 | 0.912 |
| `feature_trajectory_convergence` | 0.1019 | 0.1947 | -0.09 | 0.914 |
| `feature_temporal_density_change` | -0.0102 | 0.3676 | -2.495 | 1.89 |
| `feature_temporal_speed_change` | 0.0039 | 0.1724 | -0.845 | 0.948 |
