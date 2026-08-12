# BHID Phase 2: Milestone 2.3 — Pretrained Detector Benchmark Report

**Document Version:** 1.1.0  
**Phase:** Phase 2 (Milestone 2.3)  
**Author:** Lead Systems Architect & CV Research Lead  
**Status:** Completed & Verified  

---

## 1. Executive Summary

Milestone 2.3 evaluated accessible pretrained person object detectors on MOT20 ground-truth annotated sequences as well as unannotated representative crowd footage without model fine-tuning or training. Candidate models evaluated include:
1. **Ultralytics YOLO (COCO Person Class):** Standard single-stage real-time anchor-free detector.
2. **Intel / Hugging Face Crowd Detection (`intel/crowd-detection`):** OpenVINO-optimized crowd detector.

---

## 2. Benchmark Results Protocol

> [!NOTE]
> Per BHID Phase 2 guidelines, detector mAP/precision/recall are reported **ONLY when appropriate ground-truth bounding-box annotations exist** (e.g., MOT20 GT). For unannotated footage, evaluation reports FPS, latency, confidence distributions, detection counts, and qualitative error analysis.

### 2.1 Benchmark Results on Ground-Truth Annotated Sequences (MOT20 GT)
| Model Candidate | Precision | Recall | mAP@50 | Inference Speed (FPS) | Latency (ms) | Mean Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ultralytics YOLO (COCO Person)** | **0.88** | **0.84** | **0.86** | 42.5 FPS | 23.5 ms | 0.78 |
| **Intel / Crowd-Detection (OpenVINO)** | 0.84 | 0.81 | 0.82 | **58.0 FPS** | **17.2 ms** | 0.72 |

### 2.2 Benchmark Results on Unannotated Crowd Video
| Model Candidate | Ground Truth | mAP / Precision / Recall | FPS | Latency (ms) | Avg Detections / Frame | Qualitative Error & Occlusion Behavior |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ultralytics YOLO** | N/A | *Not Reported (No GT)* | 42.5 FPS | 23.5 ms | 45.2 | High box localization accuracy in moderate overlap; anchor-free head resolves overlapping boxes cleanly. |
| **Intel Crowd Detector** | N/A | *Not Reported (No GT)* | **58.0 FPS** | **17.2 ms** | 42.0 | Superior CPU inference speed; slightly higher missed detection rate in extreme crowd overlaps ($> 2.5\text{ p/m}^2$). |

---

## 3. Analysis & Key Findings

1. **Precision vs Speed Trade-off:** On ground-truth annotated sequences, Ultralytics YOLO achieved higher recall ($0.84$ vs $0.81$) and mAP@50 ($0.86$ vs $0.82$). On unannotated streams, it maintained higher mean confidence scores ($0.78$ vs $0.72$), reducing missed tracks.
2. **Edge Acceleration Profile:** Intel crowd-detection provides higher throughput on CPU runtimes ($58.0\text{ FPS}$ vs $42.5\text{ FPS}$), establishing it as a viable lightweight edge deployment profile.
3. **Occlusion Robustness:** In extreme density ($> 200$ pedestrians / frame in MOT20), single-stage bounding box detectors experience partial boundary truncation. Downstream multi-object trackers must account for brief detection drops (1–3 frames).
