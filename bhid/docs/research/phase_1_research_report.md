# BHID Phase 1: Research & Architecture Handoff Report

**Project Name:** BHID (Bottleneck Hazard Intelligence & Detection)  
**Document Version:** 1.3.0 (Refined Approved Version)  
**Author:** Lead Research & Systems Architecture Agent  
**Status:** Approved Phase 1 Deliverable  

---

## 1. Executive Summary

BHID (Bottleneck Hazard Intelligence & Detection) is an AI-powered crowd intelligence architecture designed to analyze pedestrian movement video, compute spatial and temporal crowd dynamics, predict near-future bottleneck risks (10–30 second lead time), and orchestrate high-level decision-making, alerts, explanations, and reporting through an agentic AI layer.

Phase 1 establishes a comprehensive, scientifically defensible research foundation and systems architecture. Rather than making premature locked decisions on detectors, trackers, ML models, or static numerical bottleneck thresholds, this report formulates an **empirical, hypothesis-driven evaluation framework**. All model choices, feature sets, numerical thresholds, frame rates, hardware benchmarks, and framework choices are treated as **provisional hypotheses to validate empirically** during implementation phases.

Key principles established in Phase 1 include:
1. **Separation of Numerical Pipeline from LLM Reasoning:** The CV object detection, tracking, spatiotemporal feature engineering, and bottleneck risk scoring pipeline is **deterministic or controlled-stochastic and does not depend on an LLM**. The Agentic AI layer is strictly reserved for high-level orchestration, policy execution, decision explanation, and alert/report generation.
2. **Temporal Prediction Target:** BHID explicitly targets near-future bottleneck formation risk ($P(\text{bottleneck at } t+h)$ for $h \in \{10\text{s}, 20\text{s}, 30\text{s}\}$) rather than instantaneous crowd density monitoring.
3. **Empirical Bottleneck Definition:** Distinguishes theoretical Fruin Level of Service (LOS) reference concepts from the empirical BHID ground-truth label, which must be validated against observed temporal flow breakdown events in the dataset.
4. **MADRAS Inspection Decision Gate:** Identifies **MADRAS (Lyon)** as the **primary dataset candidate for crowd-dynamics research**, subject to a explicit Phase 2 inspection decision gate to verify whether its data format and temporal properties support the BHID prediction target.
5. **Progressive Machine Learning Hierarchy:** Evaluates models across three structured tiers: Baseline (Logistic Regression, Random Forest, XGBoost/LightGBM) $\to$ Sequential Temporal (GRU, LSTM, TCN) $\to$ Advanced Spatiotemporal (Temporal Transformers, ST-GCN).
6. **Data Inspection Phase 2 Roadmap:** Phase 2 begins with dataset acquisition, annotation inspection, data adapter construction, and pretrained detector/tracker benchmarking—strictly avoiding premature model training.

---

## 2. Taxonomy of Knowledge & Verification Status

To maintain strict scientific rigor, all architectural components, dataset assumptions, and design choices are categorized into five distinct verification buckets:

```text
                               BHID TAXONOMY MATRIX
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. Established Research Findings  │ Qualitative & physics principles in literature │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│ 2. Proposed Hypotheses & Targets  │ Testable design ideas & engineering targets │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│ 3. System Assumptions             │ Baseline operational constraints           │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│ 4. Architectural Decisions        │ Structural boundary choices (ADRs)          │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│ 5. Phase 2 Empirical Items        │ Inspection tasks & empirical benchmarks     │
└───────────────────────────────────┴─────────────────────────────────────────────┘
```

### 2.1 Established Research Findings (Peer-Reviewed Literature)
- Real-world dense crowd movement exhibits non-linear speed-density relationships (Fundamental Diagram of Pedestrian Flow), though exact critical density thresholds vary significantly based on environment, geometry, measurement methodology, and flow direction.
- Static crowd density monitoring fails to predict structural flow collapse; temporal flow breakdown is preceded by changes in speed variance, directional entropy, and trajectory convergence.
- Random k-fold cross-validation on sequential video frames causes catastrophic temporal data leakage due to autocorrelation across adjacent frames.
- Re-ID appearance embeddings combined with Kalman filter motion prediction (e.g., BoT-SORT) improve tracking identity persistence under long occlusions compared to motion-only trackers.

### 2.2 Proposed Hypotheses & Initial Engineering Targets
- **Hypothesis H-1 (Detector Benchmark):** Benchmark single-stage detectors fine-tuned on person bounding boxes against specialized crowd density map estimators on dense crowd video to evaluate mAP, precision/recall, and occlusion handling.
- **Hypothesis H-2 (Tracker Benchmark):** Evaluate whether BoT-SORT yields measurably higher IDF1 scores than ByteTrack on dense scenes, justifying the additional Re-ID embedding computational overhead.
- **Hypothesis H-3 (Predictive Lead Time):** Evaluate predictive F1-score degradation across multi-horizon targets ($T_{pred} = 10\text{s}$, $20\text{s}$, $30\text{s}$) to determine maximum reliable warning lead times.
- **Hypothesis H-4 (ML Model Hierarchy):** Evaluate whether tabular gradient boosting (LightGBM/XGBoost) with rolling temporal lag features provides a stronger baseline than sequential deep models (GRU/TCN) on structured cell grid feature vectors.
- **Engineering Target (Hardware Profile):** Target real-time edge processing ($\ge 15\text{ FPS}$) and low-latency prediction ($< 20\text{ms}$) across candidate GPU/CPU profiles, to be validated post-detector selection.

### 2.3 System Assumptions
- Input CCTV video streams provide usable resolution (e.g., 720p/1080p) with a clear camera perspective.
- Pedestrian crowds behave as unconstrained self-organizing agents subject to physical boundary geometry (corridors, turnstiles, bottlenecks).
- Target inference environments provide sufficient computational capacity (CPU/GPU) to process video frames and run numerical inference.

### 2.4 Architectural Decisions (Binding Constraints)
- **Decoupled Engine:** Complete separation between the numerical CV/ML prediction pipeline (which is deterministic or controlled-stochastic) and the LLM Agentic orchestration layer.
- **Multi-Dataset Hybrid Strategy:** Division of tasks across specialized candidate datasets (MADRAS candidate for dynamics, MOT20 for tracking validation, SDD for aerial transfer).
- **Multi-Horizon Risk Target:** Outputting explicit probability scores $P(\text{Bottleneck at } t + h)$ for $h \in \{10\text{s}, 20\text{s}, 30\text{s}\}$.
- **Configurable Cadence:** Frame ingestion rate, CV detection interval, tracker update frequency, and ML prediction cadence are fully configurable parameters, not fixed architectural constants.

### 2.5 Items Requiring Phase 2 Empirical Validation
- Dataset inspection of MADRAS to verify if trajectory formatting, frame rates, and scene dynamics support the BHID prediction target.
- Detector benchmarking across accessible YOLO variants and Intel crowd models.
- Tracker benchmarking across ByteTrack, BoT-SORT, and Deep OC-SORT on MOT20 sequences (evaluating IDF1, HOTA, MOTA, and ID Switches).
- Parameter grid search for empirical ground-truth bottleneck label thresholds ($\rho_{thresh}, v_{thresh}, R_{flow}, \tau_{sustain}$).
- Feature selection, collinearity elimination, and predictive ranking across candidate spatiotemporal features.

---

## 3. Verified Problem Definition

Standard crowd management systems suffer from a critical limitation: they act reactively by detecting crowding only after high density has already materialized. By that time, crushing hazards, fluid-like instabilities, or severe egress delays are already in progress.

BHID shifts the paradigm from **instantaneous state monitoring** to **predictive hazard forecasting**:

$$\text{Instantaneous Monitoring (Reactive): } f(\mathbf{I}_t) \to \text{Density}_t$$

$$\text{Predictive Hazard Forecasting (Proactive): } g(\mathbf{F}_{t-T_{obs}:t}) \to P(\text{Bottleneck}_{t + T_{pred}} \mid \mathbf{F}_{t-T_{obs}:t})$$

Where:
- $\mathbf{I}_t$ is the video frame at time $t$.
- $\mathbf{F}_{t-T_{obs}:t}$ is the extracted spatiotemporal feature sequence over an observation window $T_{obs}$ (e.g., 10 seconds).
- $T_{pred}$ is the future prediction horizon (e.g., 10s, 20s, or 30s).
- $P(\text{Bottleneck}_{t + T_{pred}})$ is the probability that a defined spatial zone will experience a sustained flow breakdown/bottleneck state at time $t + T_{pred}$.

---

## 4. Dataset Comparison

We evaluated five prominent crowd and pedestrian datasets against seven critical dimensions required for BHID.

| Dataset | Primary Task Focus | Video Perspective | Density Range | Trajectory Annotations | Temporal Resolution | Candidate Role in BHID |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MADRAS (Lyon)** | Microscopic crowd dynamics & flow | Real-world multi-scale (CCTV & drone) | Up to 4.0+ $\text{p/m}^2$ | Yes (7,000+ individual trajectories) | High (25 FPS) | **Primary Candidate (Subject to Phase 2 Inspection)** |
| **MOT20** | Extremely dense pedestrian tracking | Real-world CCTV (street level) | Up to 246 pedestrians / frame | Yes (1.3M+ bounding box tracks) | High (25 FPS) | **Secondary (CV Detector & Tracker Validation)** |
| **Stanford Drone (SDD)** | Multi-agent trajectory forecasting | Aerial (Top-down view) | Low to Medium | Yes (Long-duration trajectories) | High (30 FPS) | **External Validation (Aerial Generalization)** |
| **CrowdFlow** | Aggregate optical flow & motion fields | Synthetic / CCTV | Medium | Partial (Flow vectors) | High | **Supplementary (Motion Field Analysis)** |
| **UCF-QNRF** | Dense crowd counting & localization | Static images | Extreme (up to 12,000+ per image) | **No** (Point annotations only, no time) | N/A (Static images) | **Unsuitable** (Lacks temporal sequences) |

---

## 5. MADRAS Dataset Inspection Decision Gate

Rather than assuming MADRAS is a guaranteed final training dataset, Phase 2 implements a strict **Dataset Inspection Decision Gate**:

```text
                  Phase 2 MADRAS Dataset Acquisition
                                   │
                                   ▼
             [ Empirical Data Format & Trajectory Inspection ]
             - Inspect temporal continuity & frame rates
             - Verify velocity vector density & scene geometries
             - Evaluate whether flow breakdown events are present
                                   │
                     ┌─────────────┴─────────────┐
                     ▼                           ▼
        [ Supports BHID Target? ]   [ Data Insufficient / Incomplete ]
                     │                           │
                     ▼                           ▼
         Candidate Training Data     Revise Dataset Strategy
         for Bottleneck Pipeline     (Integrate alternative datasets)
```

---

## 6. Computer Vision Model Comparison Protocol

BHID establishes an **empirical benchmark protocol** to evaluate practically accessible candidate detectors during Phase 2.

### Candidate Detector Categories
1. **Ultralytics YOLO Family (Current Accessible Models):** Real-time single-stage object detectors. Native TensorRT/ONNX export capability, adaptable anchor configurations for dense bounding boxes.
2. **Intel / Hugging Face Crowd Detection (`intel/crowd-detection`):** OpenVINO-optimized crowd detection variant designed for edge platform occupancy.
3. **Custom / Domain-Tuned Person Detectors:** Bounding box detectors fine-tuned specifically on pedestrian crowd benchmarks.

---

## 7. Tracking Model Comparison Protocol

Multi-Object Tracking (MOT) in dense pedestrian environments is prone to frequent occlusions and identity switches. BHID formulates a three-candidate evaluation protocol.

| Tracker Candidate | Primary Mechanism | Motion Model | Re-ID Feature Embedding | Camera Motion Compensation (CMC) | Expected Strength in Dense Crowds |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ByteTrack** | Association of high + low confidence detections | Kalman Filter | No | No | Extreme speed & efficiency; simple baseline. |
| **BoT-SORT** | Motion + Appearance + Camera Compensation | Kalman Filter | **Yes (Optional)** | **Yes (GMC)** | Superior ID persistence across long occlusions & moving cameras. |
| **Deep OC-SORT** | Dynamic appearance + adaptive motion prediction | Adaptive Kalman | **Yes** | **Yes** | Robust association under non-linear pedestrian maneuvers. |

---

## 8. Candidate Feature Set Engineering

The Computer Vision and Tracking layers output frame-level bounding boxes $\mathcal{B}_t = \{(x_i, y_i, w_i, h_i, \text{ID}_i, v_{x,i}, v_{y,i})\}_{i=1}^{N_t}$. 

The Analytics layer aggregates these tracks over localized spatial zones $\Omega$ (or cell grid cells $\mathbf{c}_{u,v}$) across a rolling temporal observation window $T_{obs}$.

We propose a **Candidate Feature Set of 14 Spatiotemporal Features**, whose individual predictive value and collinearity will be evaluated empirically during Phase 2 feature selection:

```text
Candidate Spatiotemporal Feature Set (Zone Ω)
 ├── Count & Occupancy
 │    ├── 1. Pedestrian Count (N_t)
 │    ├── 2. Crowd Density (ρ_t = N_t / Area(Ω)) [pedestrians / m²]
 │    └── 3. Zone Occupancy Ratio (O_t) [% of area occupied by bounding box footprints]
 ├── Kinematics & Velocity
 │    ├── 4. Mean Speed (v̄_t = (1/N_t) ∑ ||v_i||) [m/s]
 │    ├── 5. Velocity Variance (σ²_v,t = Var(||v_i||))
 │    ├── 6. Acceleration / Deceleration Rate (ā_t = Δv̄_t / Δt) [m/s²]
 │    └── 7. Directional Entropy (H_dir,t = -∑ p_θ log p_θ) [0 = uniform motion, high = chaos]
 ├── Flow & Flux
 │    ├── 8. Inflow Rate (Q_in,t = count of IDs entering Ω per second)
 │    ├── 9. Outflow Rate (Q_out,t = count of IDs exiting Ω per second)
 │    ├── 10. Net Flow Rate (ΔQ_t = Q_in,t - Q_out,t)
 │    └── 11. Flow Drop Ratio (R_flow,t = (Q_in,t - Q_out,t) / max(Q_in,t, 1))
 └── Spatial Dynamics & Trajectories
      ├── 12. Trajectory Convergence Index (C_traj,t = average dot product of velocity vectors toward zone center)
      ├── 13. Temporal Density Change (Δρ_t / Δt over rolling window)
      └── 14. Temporal Speed Change (Δv̄_t / Δt over rolling window)
```

---

## 9. Bottleneck Definition: Theoretical Reference vs Ground Truth

A critical distinction must be maintained between academic crowd service frameworks and empirical bottleneck ground truths:

```text
  Fruin Level of Service (LOS)          BHID Ground-Truth Bottleneck Label
 ┌──────────────────────────────┐     ┌──────────────────────────────────┐
 │ Theoretical reference for    │     │ Validated against observed       │
 │ pedestrian comfort & service │  ≠  │ temporal flow breakdown in       │
 │ capacity (LOS A through F).  │     │ specific scene trajectories.     │
 └──────────────────────────────┘     └──────────────────────────────────┘
```

### Distinguishing Fruin LOS from BHID Bottleneck Ground Truth
- **Fruin LOS E/F:** Provides a theoretical reference for high density and reduced walking speeds. However, Fruin LOS E/F does **NOT** automatically equal a bottleneck ground truth. For example, a stationary group of pedestrians waiting at a crosswalk or bus stop operates at high density with zero velocity, but represents intentional waiting rather than a hazardous bottleneck flow breakdown.
- **BHID Empirical Ground-Truth Label:** Requires observed **temporal flow breakdown** where inflow significantly exceeds outflow ($R_{flow} \ge \Delta Q_{thresh}$), forward velocity drops to shuffling ($v \le v_{thresh}$), and high density is **sustained over a duration $\tau \ge \tau_{sustain}$**.

### Candidate Parameter Range for Empirical Validation
Rather than hardcoding arbitrary static thresholds, BHID formulates a candidate parameter range $[\rho_{thresh}, v_{thresh}, \Delta Q_{thresh}, \tau_{sustain}]$ to be validated against dataset trajectories:

$$\text{BottleneckState}(t) = \begin{cases} 
1 & \text{if } \rho_t \ge \rho_{thresh} \text{ AND } \bar{v}_t \le v_{thresh} \text{ AND } R_{flow,t} \ge \Delta Q_{thresh} \text{ for duration } \tau \ge \tau_{sustain} \\
0 & \text{otherwise}
\end{cases}$$

---

## 10. Label Generation Methodology

To generate ground-truth labels for training machine learning models from trajectory datasets:

```text
Time Window T
├───────────────────────────────┼──────────────────────────────────────────────┤
│  Observation Window T_obs     │        Prediction Horizon T_pred             │
│  (e.g., t - 10s to t)         │        (e.g., t to t + 20s)                  │
│  Extract Feature Vector X_t   │  Evaluate BottleneckState(t') for t' ∈ T_pred│
└───────────────────────────────┴──────────────────────────────────────────────┘
                                                       ↓
                                          Target Label Y_t ∈ {0, 1}
```

---

## 11. Machine Learning Model Comparison Hierarchy

BHID adopts a **Progressive Machine Learning Hierarchy** across three distinct complexity tiers:

```text
Tier 1: Tabular Baselines
 ├── Logistic Regression (Benchmark baseline)
 ├── Random Forest
 └── LightGBM / XGBoost (With engineered rolling lag features)
       ↓
Tier 2: Sequential Temporal Models
 ├── Gated Recurrent Unit (GRU)
 ├── Long Short-Term Memory (LSTM)
 └── Temporal Convolutional Network (TCN)
       ↓
Tier 3: Advanced Spatiotemporal Models
 ├── Temporal Transformer (Self-attention across time steps)
 └── Spatiotemporal Graph Convolutional Network (ST-GCN)
```

---

## 12. Recommended Prediction Architecture

```text
[ Incoming Spatiotemporal Vectors (Candidate K features @ Configurable Cadence) ]
                           │
                           ▼
              [ Sliding Window Buffer ]
              (Shape: L steps × K features)
                           │
                           ▼
          [ Feature Standardizer / Imputer ]
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
  [ Baseline Tree Classifier ]   [ Sequential TCN Network ]
  (Flat lag feature vector)      (L × K sequence tensor)
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
             [ Primary Binary Risk Head ]
             P(Bottleneck in 10s / 20s / 30s) ∈ [0.0, 1.0]
                           │
                           ▼ (Optional Extension)
             [ Secondary Density Regressor ]
             Predicted Density ρ̂_{t+h}
```

---

## 13. Agentic AI Architecture

### Architectural Principle
**The CV/ML numerical pipeline is deterministic or controlled-stochastic and does not depend on an LLM. LLM Agents handle reasoning, policy execution, contextual decisions, and explanation.**

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│          NUMERICAL CV / ML PIPELINE (DETERMINISTIC / CONTROLLED-STOCHASTIC) │
│ Frame Ingest ──► CV Detection ──► Tracking ──► Analytics ──► ML Prediction │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Real-time Risk Score & Feature Vectors
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      AGENTIC AI ORCHESTRATION LAYER                         │
│                                                                             │
│  ┌───────────────────┐  Risk > Threshold  ┌──────────────────────────────┐  │
│  │ Orchestrator Agent│ ─────────────────► │ Decision Agent               │  │
│  │ (State Graph)     │                    │ (Policy & Threshold Engine)  │  │
│  └─────────┬─────────┘                    └──────────────┬───────────────┘  │
│            │                                             │                  │
│            ├──────────────────────────┬──────────────────┴──────────────┐   │
│            ▼                          ▼                                 ▼   │
│  ┌───────────────────┐      ┌───────────────────┐             ┌───────────┐ │
│  │ Vision Agent      │      │ Analytics Agent   │             │ Reporting │ │
│  │ (Camera Health /  │      │ (Zone Diagnostics │             │ Agent     │ │
│  │ Occlusion Check)  │      │ & Flow Trends)    │             │ (Alerts & │ │
│  └───────────────────┘      └───────────────────┘             │ Summaries)│ │
│                                                               └───────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. End-to-End System Architecture

BHID is organized into **6 Decoupled Software Layers**:

```text
LAYER 6: APPLICATION & PRESENTATION
├── FastAPI REST Server
├── WebSocket Live Stream Server
├── WebGL Dashboard (Provisional Choice)
└── Emergency Alert Dispatcher

LAYER 5: AGENTIC INTELLIGENCE
├── Orchestrator Agent
├── Decision & Policy Agent
└── Reporting & Explanation Agent

LAYER 4: PREDICTION & INFERENCE
├── Sliding Window Feature Buffer
├── ML Inference Engine (LightGBM / TCN)
└── Multi-Horizon Risk Evaluator

LAYER 3: CROWD ANALYTICS & FEATURES
├── Spatial Zone Grid Mapper
├── Kinematics & Velocity Engine
└── Candidate Feature Extractor

LAYER 2: MULTI-OBJECT TRACKING
├── Bounding Box Association
├── Kalman Filter Motion Prediction
└── Re-ID Appearance Feature Embedding (BoT-SORT / ByteTrack)

LAYER 1: COMPUTER VISION & DETECTION
├── Video Frame Ingestion
├── Object Detector (Accessible YOLO Family / Intel OpenVINO)
└── Frame Preprocessing & ROI Cropping
```

---

## 15. System Operational Cadence (Configurable Parameters)

System frame rates and inference execution intervals are **configurable operational parameters** managed per deployment profile, not hardcoded architectural constants:

- **Source Video Ingestion Rate:** Configurable (e.g., 15 FPS, 25 FPS, 30 FPS based on RTSP camera stream).
- **CV Detection Cadence:** Configurable (e.g., every 1st, 2nd, or 3rd frame depending on GPU budget).
- **Tracker Update Cadence:** Configurable (per frame or per keyframe).
- **Feature Aggregation & ML Prediction Cadence:** Configurable (e.g., 1 Hz to 5 Hz based on temporal window granularity).

---

## 16. Hardware Sizing & Initial Engineering Targets

The following deployment profiles represent **initial engineering target hypotheses**, to be validated empirically post-detector selection:

| Deployment Profile | Target Hardware Profile | Stream Capacity Target | Expected CV FPS Target | Prediction Latency Target | Memory Footprint Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Edge Appliance** | NVIDIA Jetson AGX Orin (64GB) | Multi-stream (1080p) | Real-time target (20–30 FPS) | Target $< 15\text{ms}$ | $< 8\text{ GB}$ VRAM |
| **Cloud Server** | NVIDIA A10G / T4 GPU (Cloud) | Scalable Multi-stream | High-throughput target (30+ FPS) | Target $< 5\text{ms}$ | $< 16\text{ GB}$ VRAM |
| **Edge CPU Profile** | Intel Core i7 / Xeon (OpenVINO) | Standard stream (720p/1080p) | Edge CPU target (15–20 FPS) | Target $< 25\text{ms}$ | $< 4\text{ GB}$ System RAM |

---

## 17. Data Leakage Prevention

BHID enforces **Three Leakage Controls**:

1. **Chronological Splitting:** Partition sequences strictly by time.
2. **Non-Overlapping Window Isolation:** A buffer period equal to $T_{obs} + T_{pred}$ is dropped between train and validation splits.
3. **Scene-Isolated Cross-Validation:** Validation and testing are evaluated on completely unseen video scenes/cameras.

---

## 18. Recommended Development Phases

```text
PHASE 0: Initial Repository Setup (COMPLETED)
   │
PHASE 1: Research Handoff & Architecture Validation (CURRENT)
   │
PHASE 2: Data Inspection, Adapter Construction & Tracker Benchmarks
   │  ├── Acquire & inspect datasets (MADRAS candidate inspection gate, MOT20)
   │  ├── Understand annotations & build data adapters
   │  ├── Run pretrained candidate detectors (YOLO, Intel crowd model)
   │  ├── Run tracker benchmarks (ByteTrack vs BoT-SORT vs Deep OC-SORT)
   │  ├── Generate trajectories & validate feature extraction
   │  └── Construct prediction dataset (NO MODEL TRAINING IN PHASE 2 INIT)
   │
PHASE 3: Bottleneck Labeling & Progressive ML Experimentation
   │  ├── Validate empirical bottleneck flow breakdown thresholds
   │  ├── Tier 1 Baseline ML models (LogReg, Random Forest, LightGBM/XGBoost)
   │  └── Tier 2/3 Sequential temporal models (GRU, TCN, Transformers)
   │
PHASE 4: Agentic AI Layer & Core API Integration
   │  ├── Orchestrator, Decision, and Reporting Agents
   │  └── FastAPI REST & WebSocket streaming server
   │
PHASE 5: Dashboard Visualization, End-to-End Testing & Deployment
      ├── WebGL real-time crowd UI
      └── Hardware performance benchmarking
```

---

## 19. Exact Phase 2 Roadmap (No Premature Training)

Phase 2 will proceed strictly through the following sequential inspection and benchmarking tasks:

1. **Acquire & Inspect Datasets (`dataset/preparation/`):** Download sample MADRAS and MOT20 files; execute MADRAS Decision Gate inspection to verify temporal suitability.
2. **Understand Annotations & Build Data Adapters:** Create standardized converters from raw trajectory formats to BHID internal data schemas.
3. **Benchmark Pretrained Candidate Detectors:** Evaluate accessible YOLO models and Intel crowd model on sample frames for precision, recall, and FPS.
4. **Benchmark Candidate Trackers (`scripts/` & `tests/evaluation/`):** Evaluate ByteTrack, BoT-SORT, and Deep OC-SORT on MOT20 sequences for IDF1, HOTA, and ID switches.
5. **Generate Trajectories & Validate Feature Extractor (`analytics/`):** Compute candidate spatiotemporal features on extracted trajectories and verify mathematical correctness.
6. **Construct Prediction Dataset:** Assemble feature sequence arrays $\mathbf{X}_t$ and candidate bottleneck target labels $Y_t$.
7. **Strict Stop Condition:** Complete dataset construction and empirical threshold validation before initiating any model training.

---

## 20. Final Decision Matrix (Hypothesis-Driven Framework)

| Component | Candidate Options | Hypothesis / Recommendation | Evidence / Rationale | Evaluation Status |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Dataset** | MADRAS, MOT20, SDD | **MADRAS (Lyon) Primary Candidate** | Microscopic trajectories & dense dynamics (Subject to Ph2 inspection gate) | **Primary Candidate (To Inspect)** |
| **CV Detector** | Accessible YOLO family, Intel crowd model | **Accessible candidate models** | Benchmark precision, recall, FPS, and occlusion handling | **Provisional Hypothesis (Phase 2)** |
| **Tracker** | ByteTrack, BoT-SORT, Deep OC-SORT | **ByteTrack vs BoT-SORT vs Deep OC-SORT** | Benchmark IDF1, HOTA, MOTA, and ID Switches on MOT20 | **Provisional Hypothesis (Phase 2)** |
| **Density Method** | Spatial Cell Grid vs Density Map | **Spatial Cell Grid Density Map** | Converts discrete track points to continuous local density grid | **Provisional Hypothesis (Phase 2)** |
| **Feature Set** | 14 Candidate Features | **Candidate Feature Set** | Evaluate predictive importance & feature collinearity empirically | **Provisional Candidate Set** |
| **Bottleneck Def.** | Theoretical Fruin LOS vs Flow Breakdown | **Observed temporal flow breakdown** | Grounded in LOS reference but validated on flow breakdown | **Provisional Parameter Set** |
| **Prediction Horizon** | 10s, 20s, 30s | **Multi-horizon evaluation (10s, 20s, 30s)**| Evaluates F1 lead-time decay curve across horizons | **Multi-Horizon Benchmark Set** |
| **Baseline ML Model**| LogReg, Random Forest, LightGBM / XGBoost | **XGBoost / LightGBM baseline** | Fast, strong tabular time-series baseline | **Progressive Hierarchy (Tier 1)** |
| **Sequential ML** | GRU, LSTM, TCN | **GRU/LSTM vs Temporal ConvNet (TCN)** | Evaluates sequence context capture & latency | **Progressive Hierarchy (Tier 2)** |
| **Advanced ML** | Temporal Transformer, ST-GCN | **Temporal Transformer / ST-GCN** | Evaluates advanced spatiotemporal modeling gains | **Progressive Hierarchy (Tier 3)** |
| **Agent Framework**| Custom lightweight vs Agent framework | **Decoupled Orchestrator Interface** | Latency, deterministic safety, tool calling reliability | **Architectural Principle** |
| **Backend Framework**| FastAPI Async Engine | **FastAPI + Async WebSockets** | Real-time streaming, lightweight API routes | **Provisional Implementation Choice** |
| **Database** | PostgreSQL / TimescaleDB | **TimescaleDB** | Time-series storage candidate | **Provisional Choice (Revisit post-ML)** |
| **Dashboard Tech** | Vite + React + WebGL Canvas | **Vite + React + WebGL Canvas** | Real-time crowd rendering candidate | **Provisional Choice (Revisit post-ML)** |
