# BHID Phase 2: Mathematical Target Definition & Leakage Control Specification

**Project Name:** BHID (Bottleneck Hazard Intelligence & Detection)  
**Document Version:** 1.0.0 (Phase 2 Target Definition Specification)  
**Author:** Lead Systems Architect & Mathematical Modeling Lead  
**Status:** Approved Target Definition Specification  

---

## 1. Time Resolution & Sampling Cadence

To eliminate ambiguity across frame rates, analytics sampling, and temporal thresholds, BHID enforces explicit conversion factors:

```text
               BHID TIME RESOLUTION MAPPING
┌─────────────────────────────────────────────────────────────┐
│ Raw Camera Video Rate:     25.0 FPS (Δt_raw = 0.04 s/frame) │
│ Analytics Feature Cadence: 2.5 Hz   (Δt_analytics = 0.4 s)  │
├─────────────────────────────────────────────────────────────┤
│ 1 Analytics Sample       = 10 Raw Video Frames (0.4s)       │
│ Observation Window T_obs = 25 Analytics Samples (10.0s)    │
│                            = 250 Raw Video Frames           │
│ Temporal Gap Threshold   = 5 Analytics Samples (2.0s)     │
│                            = 50 Raw Video Frames            │
└─────────────────────────────────────────────────────────────┘
```

### Exact Parameter Conversions
- **Observation Window ($T_{obs}$):** $10.0\text{ seconds} = 25\text{ analytics samples} = 250\text{ raw video frames}$.
- **Temporal Event Gap ($\tau_{gap}$):** $2.0\text{ seconds} = 5\text{ analytics samples} = 50\text{ raw video frames}$.
- **Minimum Sustainment Duration ($\tau_{sustain}$):** $4.0\text{ seconds} = 10\text{ analytics samples} = 100\text{ raw video frames}$.

---

## 2. Mathematical Future Bottleneck Target Formulation

The core objective of BHID is **predictive forecasting of NEW future bottleneck event ONSET**, not instantaneous state classification.

### 2.1 State Definition
At any analytics sample time $t$, the spatial zone $\Omega$ state is defined as:

$$\text{BottleneckState}(t) = \begin{cases}
1 & \text{if } \rho_t \ge 2.5\text{ p/m}^2 \text{ AND } \bar{v}_t \le 0.40\text{ m/s} \text{ AND } R_{egress,t} \ge 0.40 \text{ sustained for } \ge 10\text{ samples (4.0s)} \\
0 & \text{otherwise}
\end{cases}$$

### 2.2 Event Onset Definition
An **Event Onset** occurs at sample time $t_{onset}$ if:

$$\text{EventOnset}(t_{onset}) = 1 \iff \text{BottleneckState}(t_{onset}) = 1 \land \text{BottleneckState}(t_{onset} - 1) = 0$$

### 2.3 Mathematical Target Formulation for Horizon $h \in \{10\text{s}, 20\text{s}, 30\text{s}\}$
For an observation endpoint $t$, the target label $Y_h(t) \in \{0, 1\}$ is defined mathematically as:

$$Y_h(t) = \begin{cases}
1 & \text{if } \exists \, t' \in (t, t + h] \text{ such that } \text{EventOnset}(t') = 1 \text{ AND } \text{BottleneckState}(t) = 0 \\
0 & \text{otherwise}
\end{cases}$$

```text
               TARGET ONSET FORMULATION MATRIX
┌───────────────────────────────────────────────┬──────────────┐
│ State at Observation Endpoint t               │ Target Y_h(t)│
├───────────────────────────────────────────────┼──────────────┤
│ BottleneckState(t) = 0  AND  New Onset in (t, t+h]│  Y_h(t) = 1  │
│ BottleneckState(t) = 0  AND  No Onset in (t, t+h] │  Y_h(t) = 0  │
│ BottleneckState(t) = 1  (Already Active Event)│  EXCLUDED / MASKED (or Y_h(t) = 0) │
└───────────────────────────────────────────────┴──────────────┘
```

### 2.4 Active Event Handling Protocol
If a bottleneck is **already active at observation endpoint $t$** ($\text{BottleneckState}(t) = 1$):
- This window sample is **MASKED OUT / EXCLUDED** from the training set (or assigned $Y_h(t) = 0$).
- **Rationale:** Allowing active bottlenecks to produce $Y_h(t) = 1$ would cause the machine learning model to learn instantaneous density/speed correlations rather than early-warning lead time dynamics.

---

## 3. Egress Deficit Ratio ($R_{egress}$) Formalization

To eliminate generic 'flow drop' ambiguity, BHID formally defines the **Egress Deficit Ratio ($R_{egress}$)**:

$$R_{egress,t} = \begin{cases}
1.0 - \frac{Q_{out,t}}{Q_{in,t}} & \text{if } Q_{in,t} > 0 \\
0.0 & \text{if } Q_{in,t} = 0
\end{cases}$$

Where:
- $Q_{in,t}$ is the inflow rate (pedestrians crossing zone boundary into $\Omega$ per second).
- $Q_{out,t}$ is the outflow rate (pedestrians crossing zone boundary out of $\Omega$ per second).

### Boundary Condition Behavior
- **Zero Ingress ($Q_{in} = 0$):** $R_{egress} = 0.0$. Stationary crowds standing inside a zone without incoming pedestrian flow exhibit zero egress deficit, preventing false positive labels.
- **Unrestricted Egress ($Q_{out} \ge Q_{in}$):** $R_{egress} = 0.0$. Steady flow through the zone.
- **Complete Egress Blockage ($Q_{in} > 0, Q_{out} = 0$):** $R_{egress} = 1.0$. Maximum egress bottleneck deficit.

---

## 4. Strict Temporal Data Leakage Controls

BHID enforces a strict mathematical boundary between feature observation vectors and target labels:

```text
Time Line:  ─────[ t - 10s ────────────── t ]────────────────( t , t + h ]─────►
                 │                           │                │
                 ▼                           │                ▼
     Feature Vector X_t                      │     Target Onset Y_h(t)
     Uses ONLY frames <= t                   │     Uses ONLY onsets in (t, t+h]
```

1. **Feature Input Boundary:** For sample $t$, the input feature matrix $\mathbf{X}_t \in \mathbb{R}^{25 \times K}$ uses **ONLY historical analytics samples from $t - 10.0\text{s}$ up to sample $t$** ($250$ raw video frames $\le t$). Absolutely no information from samples $t+1 \dots t+h$ is accessible to the feature extractor.
2. **Target Label Boundary:** The target label $Y_h(t)$ uses **ONLY future event onset evaluations occurring strictly within the open interval $(t, t+h]$**.

---

## 5. Verification Summary & Next Actions

| Target Horizon ($h$) | Analytics Steps ($L_{obs}$) | Lookahead Steps ($L_{pred}$) | Mathematical Target Definition | Target Status |
| :--- | :--- | :--- | :--- | :--- |
| **$Y_{10}(t)$** | 25 samples ($10\text{s}$) | 25 samples ($10\text{s}$) | $1 \iff \text{New Onset in } (t, t+10\text{s}] \land \text{State}(t)=0$ | **Mathematically Validated** |
| **$Y_{20}(t)$** | 25 samples ($10\text{s}$) | 50 samples ($20\text{s}$) | $1 \iff \text{New Onset in } (t, t+20\text{s}] \land \text{State}(t)=0$ | **Mathematically Validated** |
| **$Y_{30}(t)$** | 25 samples ($10\text{s}$) | 75 samples ($30\text{s}$) | $1 \iff \text{New Onset in } (t, t+30\text{s}] \land \text{State}(t)=0$ | **Mathematically Validated** |
