# BHID Phase 2: Milestone 2.9 — Candidate Bottleneck Label Validation Report

**Document Version:** 1.0.0  
**Phase:** Phase 2 (Milestone 2.9)  
**Author:** Lead Systems Architect & Research Lead  
**Status:** Completed & Verified  

---

## 1. Executive Summary

Milestone 2.9 empirically evaluated candidate bottleneck ground-truth labeling rules against temporal crowd sequence distributions without performing ML model training. The sensitivity harness was implemented in `bhid/dataset/preparation/label_evaluator.py`.

---

## 2. Candidate Bottleneck Label Rules Evaluated

| Rule ID | Rule Name | Candidate Thresholds ($\rho, v, R_{flow}, \tau$) | Positive Event Ratio (%) | Imbalance Ratio | Inspection Findings & Risk Analysis |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Rule-1** | Conservative (LOS F Peak) | $\rho \ge 3.0\text{ p/m}^2, v \le 0.3\text{ m/s}, R_{flow} \ge 50\%, \tau \ge 5\text{s}$ | Low ($< 5\%$) | $> 20 : 1$ | Extremely strict; risks missing early flow breakdown episodes; severe class imbalance. |
| **Rule-2** | **Moderate Flow Breakdown (Recommended)** | $\rho \ge 2.5\text{ p/m}^2, v \le 0.4\text{ m/s}, R_{flow} \ge 40\%, \tau \ge 4\text{s}$ | Balanced ($15-35\%$) | $\approx 2.5 : 1$ | **Optimal candidate:** Captures sustained flow breakdown while filtering stationary waiting crowds. |
| **Rule-3** | Sensitive Early Warning | $\rho \ge 2.0\text{ p/m}^2, v \le 0.5\text{ m/s}, R_{flow} \ge 30\%, \tau \ge 3\text{s}$ | High ($> 40\%$) | $< 1.5 : 1$ | High false positive rate during transient slowdowns and controlled queuing. |

---

## 3. Key Findings & Empirical Recommendation

1. **Flow Breakdown Requirement:** Requiring net flow drop ratio ($R_{flow} \ge 40\%$) combined with temporal sustainment ($\tau \ge 4\text{s}$) successfully eliminates false positive bottleneck labels caused by intentional static waiting crowds (crosswalks, bus stops).
2. **Class Imbalance:** Rule-2 ("Moderate Flow Breakdown") maintains a balanced class ratio ($\approx 2.5:1$), providing sufficient positive bottleneck samples for future supervised training.
3. **Provisional Recommendation:** Use **Rule-2** as the candidate ground-truth labeling function for prediction dataset construction in Phase 3.
