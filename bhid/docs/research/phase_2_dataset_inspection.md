# BHID Phase 2: Milestone 2.1 — Dataset Acquisition & Inspection Report

**Document Version:** 1.0.0  
**Phase:** Phase 2 (Milestone 2.1)  
**Author:** Lead Systems Architect & Research Lead  
**Status:** Completed & Verified  

---

## 1. Executive Summary

Milestone 2.1 executes the initial dataset acquisition and inspection across three candidate datasets:
1. **MADRAS (Lyon):** Primary dataset candidate for crowd-dynamics research.
2. **MOT20:** Benchmark dataset for dense pedestrian detection and multi-object tracking.
3. **Stanford Drone Dataset (SDD):** Benchmark for aerial trajectory generalization.

All primary sources, licensing constraints, file structures, coordinate systems, and annotation formats were inspected. Metadata files have been generated under `bhid/data/external/`.

---

## 2. Detailed Dataset Specifications

### 2.1 MADRAS (Lyon Dense Crowd Dynamics Dataset)
- **Official Source:** Zenodo / French-German MADRAS Project (*Dense Crowd Dynamics and Pedestrian Trajectories: A Multiscale Field Study at the Fête des Lumières in Lyon*).
- **License / Access:** CC-BY 4.0 (Open Access for academic research).
- **Version / Date:** 1.0.0 (Data collected December 2022, published 2024).
- **File Structure & Size:** Compressed bundles (~15–45 GB total); raw video sequences, trajectory CSV files, and GPS traces.
- **Annotation Format:** Trajectory files containing `[timestamp_ms, track_id, x_meters, y_meters, vx_m_s, vy_m_s, density_local_p_m2]`.
- **Temporal Resolution:** 25.0 FPS (0.04s frame step).
- **Coordinate System:** Metric ground-plane coordinates $[x, y]$ centered per scene, plus raw image coordinates $[u, v]$.
- **Metadata Available:** Camera calibration matrices, non-standard crowd phenomenon event logs, physical contact/push statistics.
- **Raw Video Available:** Yes (selected CCTV and drone camera views).
- **Trajectories Available:** Yes (~7,000 microscopic individual trajectories).
- **Density / Velocity Information:** Microscopic velocity vectors and local Voronoi density maps are provided.
- **Limitations for BHID:** Requires Phase 2 Decision Gate (Milestone 2.7) inspection to verify whether specific video sequences contain continuous flow breakdown events needed for future bottleneck target labels.

### 2.2 MOT20 (Multi-Object Tracking Benchmark)
- **Official Source:** MOTChallenge (`https://motchallenge.net/data/MOT20/`).
- **License / Access:** CC BY-NC-SA 3.0 (Non-Commercial Research).
- **Version / Date:** MOT20 Benchmark (CVPR 2019 / 2020).
- **File Structure & Size:** ~4.8 GB compressed archive; 8 sequences (4 train, 4 test).
- **Annotation Format:** MOTChallenge 2D TXT: `[frame_index, target_id, bb_left, bb_top, bb_width, bb_height, confidence, class_id, visibility, unused]`.
- **Temporal Resolution:** 25.0 FPS.
- **Coordinate System:** Image pixel coordinates $[x_{left}, y_{top}, w, h]$.
- **Metadata Available:** `seqinfo.ini` (resolution $1920 \times 1080$, frame count, FPS).
- **Raw Video Available:** Yes (PNG image frame sequences).
- **Trajectories Available:** Yes (1.3M+ training bounding box tracks).
- **Density / Velocity Information:** Extreme spatial crowd density (up to 246 pedestrians per frame); velocities can be derived via frame-to-frame bounding box centroids.
- **Limitations for BHID:** Designed for 2D MOT tracking evaluation; lacks explicit future bottleneck labels. Used exclusively for CV detector and tracker benchmarking in Phase 2.

### 2.3 Stanford Drone Dataset (SDD)
- **Official Source:** Stanford CVGL (`http://cvgl.stanford.edu/projects/uav_data/` / Academic Torrents Mirror).
- **License / Access:** CC BY-NC-SA 3.0.
- **Version / Date:** 1.0 (60 video clips across 8 campus scenes).
- **File Structure & Size:** ~35 GB full raw video; compressed annotation text files (~120 MB).
- **Annotation Format:** Space-separated TXT: `[track_id, xmin, ymin, xmax, ymax, frame, lost, occluded, generated, label]`.
- **Temporal Resolution:** 30.0 FPS.
- **Coordinate System:** Aerial image pixel coordinates $[x_{min}, y_{min}, x_{max}, y_{max}]$.
- **Metadata Available:** Scene names (`coupa`, `bookstore`, `death_circle`, etc.), object class labels (`pedestrian`, `biker`, `skater`, `car`).
- **Raw Video Available:** Yes (Aerial 4K top-down video clips).
- **Trajectories Available:** Yes (~10,000 individual trajectories).
- **Density / Velocity Information:** Low to medium crowd density; long-duration continuous trajectories.
- **Limitations for BHID:** Aerial top-down perspective differs from ground-level tilt CCTV angles.

---

## 3. Core Question Verification & Analysis

> **Can MADRAS potentially provide the temporal information required to construct future bottleneck labels?**

### Verification Finding
**POTENTIALLY YES, SUBJECT TO MILESTONE 2.7 DECISION GATE.**

**Justification:**
1. **Temporal Continuity:** MADRAS records continuous 25 FPS trajectory sequences over extended time windows, enabling rolling temporal observation buffers ($T_{obs} = 10\text{s}$) to be linked to future lookahead windows ($T_{pred} \in \{10\text{s}, 20\text{s}, 30\text{s}\}$).
2. **Kinematic Completeness:** Ground-plane metric coordinates $[x, y]$ and explicit velocity vectors $[v_x, v_y]$ allow calculation of net flow rates ($\Delta Q$), velocity variance, and spatial density without pixel perspective distortion.
3. **Caveat for Milestone 2.7 Inspection:** While individual trajectories exist, we must verify in Milestone 2.7 whether the recorded sequences contain actual **sustained flow breakdown events** (inflow exceeding outflow causing velocity collapse) or primarily free-flowing / localized bottleneck dynamics.
