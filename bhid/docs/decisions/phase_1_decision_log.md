# BHID Phase 1: Architectural Decision Records (ADR Log)

**Project Name:** BHID (Bottleneck Hazard Intelligence & Detection)  
**Document Version:** 1.2.0 (Refined Approved Version)  
**Author:** Lead Systems Architect & Research Lead  
**Status:** Approved ADR Log Framework  

---

## ADR-001: Decoupling Numerical CV/ML Prediction Pipeline from LLM Agent Orchestration

### Context
There is a temptation in modern AI projects to pass raw video frames or high-level density metrics directly to Large Language Models (LLMs) to perform end-to-end hazard detection.

### Decision
We strictly isolate numerical computer vision (detection, tracking, feature extraction) and predictive machine learning models ($P(\text{bottleneck})$ scoring) into a **numerical pipeline that is deterministic or controlled-stochastic and does not depend on an LLM**. The Agentic AI layer (LLM agents) is strictly reserved for high-level orchestration, policy-based decision evaluation, anomaly explanations, and alert/report generation.

### Consequences
- **Positive:** Eliminates LLM hallucination risk in mathematical flow metrics; ensures fast inference execution without LLM latency bottlenecks.
- **Negative:** Requires maintaining separate traditional ML inference runtimes alongside LLM orchestration environments.

---

## ADR-002: Multi-Dataset Strategy (MADRAS Candidate Inspection + MOT20 + SDD)

### Context
No single publicly available dataset provides raw video footage, extreme multi-object tracking annotations, microscopic individual pedestrian trajectories, and pre-labeled future bottleneck ground truths.

### Decision
Adopt a three-tiered hybrid dataset strategy:
1. **MADRAS (Lyon):** Primary dataset candidate for crowd-dynamics research, subject to an explicit Phase 2 dataset inspection decision gate to verify whether its temporal properties support the BHID prediction target.
2. **MOT20:** Secondary benchmark dataset for dense pedestrian detection and multi-object tracking evaluation.
3. **Stanford Drone Dataset (SDD):** Benchmark for evaluating aerial trajectory generalization.

### Consequences
- **Positive:** Avoids forcing one dataset to perform tasks outside its design scope; ensures multi-scale testing.
- **Negative:** Requires building data inspection adapters in `dataset/preparation/` before committing to final dataset selection.

---

## ADR-003: Object Detector Selection Hypothesis & Evaluation Protocol

### Context
Selecting a specific object detector family prior to empirical evaluation on BHID footage creates premature architectural lock-in.

### Decision
Treat detector selection as a **provisional hypothesis to evaluate during Phase 2**. Benchmark currently accessible candidate models (e.g. Ultralytics YOLO family, Intel crowd models, custom person detectors) on MOT20 and BHID sample footage during Phase 2 benchmarking.

### Consequences
- **Positive:** Ensures data-driven selection based on empirical precision, recall, FPS, and occlusion robustness.
- **Negative:** Requires building a standardized detector evaluation harness in Phase 2.

---

## ADR-004: Multi-Object Tracker Selection Benchmark (ByteTrack vs BoT-SORT vs Deep OC-SORT)

### Context
Dense crowd tracking suffers from frequent occlusions and identity switching. ByteTrack prioritizes speed through low-confidence association; BoT-SORT adds camera motion compensation and appearance Re-ID; Deep OC-SORT handles non-linear maneuvers.

### Decision
Maintain a **hypothesis-driven benchmark framework** comparing ByteTrack, BoT-SORT, and Deep OC-SORT on MOT20 dense tracking sequences evaluating IDF1, HOTA, MOTA, and ID Switches.

### Consequences
- **Positive:** Identifies the optimal trade-off between tracking accuracy (IDF1) and frame rate (FPS) for production deployment.
- **Negative:** Requires supporting modular tracker interfaces in `vision/tracking/`.

---

## ADR-005: Empirical Bottleneck Label Formulation & Parameter Investigation

### Context
Fruin's Level of Service (LOS) provides a theoretical reference for crowd service capacity, but LOS E/F does **not** automatically equal a bottleneck ground truth (e.g., stationary crowds waiting at a crosswalk exhibit high density and low speed without flow breakdown).

### Decision
Distinguish theoretical Fruin LOS reference concepts from the BHID ground-truth label. Ground truth must be validated against observed **temporal flow breakdown** ($\rho, v, \Delta Q, \tau$). Candidate numerical thresholds are treated as provisional parameters to validate empirically against dataset distributions.

### Consequences
- **Positive:** Prevents false bottleneck alerts on static standing crowds; ensures physical validity.
- **Negative:** Requires running parameter grid search over threshold ranges to maximize label quality.

---

## ADR-006: Multi-Horizon Prediction Strategy

### Context
Safety personnel require actionable advance notice to prevent bottlenecks. Predicting too far in advance (e.g., 60 seconds) introduces high variance, while predicting too late (e.g., 2 seconds) renders alerts useless.

### Decision
Formulate the prediction module to output multi-horizon risk probabilities: $P(\text{Bottleneck at } t + h)$ for $h \in \{10\text{s}, 20\text{s}, 30\text{s}\}$ using a historical observation window ($T_{obs}$).

### Consequences
- **Positive:** Provides operators with early warning lead times and explicit lead-time decay visibility.
- **Negative:** Requires evaluating model performance across three target horizons during training.

---

## ADR-007: Progressive Machine Learning Experimentation Hierarchy

### Context
Declaring a specific deep learning model (e.g., LSTM or Transformer) as the final choice prior to baseline testing violates scientific rigor.

### Decision
Evaluate machine learning models across a **progressive three-tier hierarchy**:
- **Tier 1 (Baselines):** Logistic Regression, Random Forest, XGBoost / LightGBM.
- **Tier 2 (Sequential Temporal):** GRU, LSTM, Temporal Convolutional Networks (TCN).
- **Tier 3 (Advanced Spatiotemporal):** Temporal Transformers, ST-GCN.

### Consequences
- **Positive:** Establishes a strict performance baseline; prevents unnecessary model complexity if simpler models achieve target accuracy.
- **Negative:** Requires implementing standardized dataset loading and evaluation loops across multiple model classes.

---

## ADR-008: Provisional Application Layer & Infrastructure Stack

### Context
Application-layer infrastructure choices (e.g., database storage engine, frontend rendering framework) should not distract from or constrain core computer vision and crowd dynamics prediction research.

### Decision
Treat application-layer choices (TimescaleDB, FastAPI, React + WebGL UI) as **provisional implementation preferences**, to be formally evaluated and finalized post-validation of the CV/ML pipeline.

### Consequences
- **Positive:** Keeps core focus on CV, tracking, dynamics, and prediction research during Phase 2 and Phase 3.
- **Negative:** Application-layer integration details will be finalized in later phases.
