# GridGuard AI Validation and Model Card

## 1. Purpose

This document describes the current artificial-intelligence layer used by the GridGuard prototype.

The objective of GridGuard AI is not to replace deterministic electrical safety logic.

Its purpose is to provide:

- predictive early-warning advisory,
- behavioral anomaly detection,
- telemetry quality awareness,
- explainable model outputs,
- and a consensus layer combining deterministic and AI evidence.

All AI results described in this document are based on **synthetic prototype telemetry**.

They must not be interpreted as validated field performance.

---

## 2. AI Safety Position

GridGuard follows a layered decision architecture:

```text
Telemetry
    ↓
Deterministic Risk Engine
    +
AI Intelligence
    ↓
Consensus
    ↓
Operator Advisory
```

The deterministic risk engine remains the primary safety-oriented software layer.

The AI system is advisory.

AI cannot downgrade a deterministic CRITICAL state.

GridGuard does not currently perform autonomous switching or certified protection functions.

---

## 3. AI Components

The current GridGuard Intelligence layer contains four main components:

1. Predictive escalation model
2. Behavioral anomaly detector
3. AI Quality Guard
4. Consensus layer

An explainability layer is also used to expose important predictive-model drivers.

---

## 4. Synthetic Dataset

The GridGuard AI models are currently trained and evaluated using a synthetic prototype dataset.

Dataset summary:

| Item | Value |
|---|---:|
| Scenarios | 3,000 |
| Telemetry rows | 128,598 |
| Prediction horizon | 5 telemetry cycles |
| Early-warning eligible rows | 110,971 |
| Future escalation positive rows | 10,723 |
| Positive rate | 9.66% |
| HIGH / CRITICAL rows | 17,627 |

The dataset includes multiple operating patterns such as:

- normal behavior,
- noisy normal behavior,
- gradual overload,
- rapid overload,
- load-driven overheating,
- thermal degradation,
- ambient heating,
- gradual partial discharge,
- rapid partial discharge,
- humidity-related behavior,
- recovery,
- and sensor outliers.

The dataset is synthetic.

It is not utility field data and has not been validated against a real industrial panel fleet.

---

## 5. Predictive Task

The predictive model is designed to answer:

> Is this panel likely to escalate to HIGH or CRITICAL within the next five telemetry cycles while it is not already HIGH or CRITICAL?

This is a future-escalation classification problem.

The prediction horizon is:

```text
5 telemetry cycles
```

This horizon must not be confused with the demonstrated early-warning lead during the jury scenario.

The model may evaluate risk within a five-cycle future window, but the current canonical overheating demonstration has shown an advisory lead of **one telemetry cycle**.

---

## 6. Scenario-Based Data Split

To reduce leakage between highly related telemetry samples, GridGuard separates data by scenario.

Current split:

| Split | Scenarios | Rows |
|---|---:|---:|
| Training | 2,094 | 77,660 |
| Validation | 443 | 16,270 |
| Test | 463 | 17,041 |

This means telemetry from a single generated scenario is not intentionally distributed across training and test sets.

The current split uses:

```text
random_seed = 42
```

---

## 7. Predictive Model Selection

Two supervised models were evaluated:

- Logistic Regression
- XGBoost

Logistic Regression was used as a simpler baseline.

XGBoost was selected as the primary predictive model because it produced stronger held-out synthetic test performance.

---

## 8. Logistic Regression Baseline

Held-out synthetic test results:

| Metric | Result |
|---|---:|
| Accuracy | 91.53% |
| Precision | 53.62% |
| Recall | 93.22% |
| F1 Score | 68.08% |
| ROC-AUC | 0.9700 |
| PR-AUC | 0.7487 |

Confusion matrix:

| | Predicted Negative | Predicted Positive |
|---|---:|---:|
| Actual Negative | 14,057 | 1,332 |
| Actual Positive | 112 | 1,540 |

The baseline demonstrated that the synthetic predictive task contains learnable temporal information.

However, its false-positive count was substantially higher than the selected XGBoost model.

---

## 9. XGBoost Predictive Model

The selected GridGuard predictive model is XGBoost.

Current decision threshold:

```text
0.505644
```

Held-out synthetic test results:

| Metric | Result |
|---|---:|
| Accuracy | 95.33% |
| Precision | 68.77% |
| Recall | 94.92% |
| F1 Score | 79.76% |
| ROC-AUC | 0.9868 |
| PR-AUC | 0.8955 |

Test set:

```text
17,041 rows
1,652 positive rows
9.694% positive rate
```

Confusion matrix:

| | Predicted Negative | Predicted Positive |
|---|---:|---:|
| Actual Negative | 14,677 | 712 |
| Actual Positive | 84 | 1,568 |

---

## 10. Why Recall Matters

GridGuard is an early-warning prototype.

For this reason, missing a genuine future escalation is considered especially undesirable.

The XGBoost model achieved:

```text
Recall = 94.92%
```

on the held-out synthetic test set.

This means most synthetic future HIGH / CRITICAL escalation cases were identified within the defined predictive task.

However, this does not imply a 94.92% detection rate in real electrical installations.

Field performance has not yet been established.

---

## 11. Precision Trade-Off

The model achieved:

```text
Precision = 68.77%
```

This means not every predictive escalation advisory corresponds to a future positive event within the synthetic test definition.

GridGuard therefore does not use raw predictive probability as autonomous protection logic.

Instead, predictions are processed together with:

- temporal persistence,
- telemetry quality,
- deterministic risk,
- behavioral anomaly information,
- and the consensus layer.

This reduces the risk of treating every individual model output as a confirmed fault.

---

## 12. AI Quality Guard

The predictive model is surrounded by a Quality Guard.

The Quality Guard considers recent predictive outputs and telemetry trustworthiness.

Current prototype configuration includes:

```text
Recent window: 3 telemetry samples
Consecutive high predictions required: 2
Unreliable recent telemetry: HOLD
```

Conceptual decisions:

```text
SAFE
HOLD
ESCALATION
```

### SAFE

Predictive escalation evidence is not sufficiently strong.

### HOLD

The model may produce a high probability, but telemetry quality is not considered sufficiently trustworthy.

### ESCALATION

Persistent trustworthy predictive evidence supports an early-warning advisory.

---

## 13. Quality Guard Stress Test

The Quality Guard was evaluated using twelve synthetic robustness scenarios.

Results:

| Item | Result |
|---|---:|
| Total scenarios | 12 |
| Passed | 12 |
| Missed | 0 |
| Pass rate | 100% |

Decision distribution:

| Decision | Count |
|---|---:|
| SAFE | 6 |
| HOLD | 1 |
| ESCALATION | 5 |

The stress scenarios include examples such as:

- high ambient temperature without dangerous thermal delta,
- current rise without corresponding heating,
- high humidity alone,
- shifted but stable operating baseline,
- recovery trend,
- slow thermal escalation,
- load and thermal escalation,
- partial-discharge escalation,
- combined humidity and PD deterioration,
- subtle multi-signal escalation,
- noisy healthy telemetry,
- and an unreliable single-cycle spike.

The single unreliable spike scenario is intentionally prevented from immediately creating a strong escalation advisory.

---

## 14. Behavioral Anomaly Detection

GridGuard also contains an unsupervised behavioral anomaly detector based on Isolation Forest.

Unlike the predictive model, this component is trained only on healthy synthetic telemetry.

Its purpose is to identify behavior that differs substantially from learned normal operating patterns.

Training summary:

```text
Healthy training rows: 23,480
Training scenarios: 602
```

Calibration target:

```text
Healthy false-positive rate ≈ 5%
```

Selected anomaly threshold:

```text
-0.524649
```

---

## 15. Anomaly Detector Results

Held-out synthetic test results:

| Metric | Result |
|---|---:|
| Healthy specificity | 95.08% |
| Healthy false-positive rate | 4.92% |
| Abnormal detection rate | 73.22% |

The anomaly detector is not intended to diagnose a specific electrical fault.

Its role is to answer a different question:

> Does the current behavior look unusual compared with synthetic healthy operating behavior?

This signal is therefore treated as supporting evidence rather than a standalone protection decision.

---

## 16. Predictive vs Anomaly Models

The two AI models serve different purposes.

### Predictive Model

Question:

> Is the panel likely to escalate to HIGH or CRITICAL soon?

Output:

```text
Future escalation probability
```

### Anomaly Detector

Question:

> Does current behavior differ from learned healthy behavior?

Output:

```text
Behavioral anomaly score / level
```

Using both layers gives GridGuard two different perspectives:

```text
Future Risk
+
Current Behavioral Unusualness
```

---

## 17. Explainability

GridGuard exposes predictive model drivers to the operator.

The purpose is to avoid presenting AI output as an unexplained numerical score.

Examples of influential features can include:

- electrical current,
- cable temperature,
- cable-to-ambient temperature difference,
- partial-discharge trend,
- humidity,
- recent telemetry changes,
- and temporal rolling features.

The interface displays major contributing factors as AI drivers.

These explanations describe model contribution behavior.

They do not prove physical causality.

---

## 18. Consensus Layer

GridGuard combines evidence through a consensus layer.

Conceptually:

```text
Deterministic Risk
       +
Predictive AI
       +
Behavioral Anomaly
       +
Data Quality
       ↓
GridGuard Consensus
```

The consensus layer is designed to create a more understandable operator-level interpretation.

Possible situations include:

- deterministic and AI layers agree,
- AI identifies deterioration before deterministic thresholds are crossed,
- deterministic logic detects a severe condition immediately,
- AI evidence is withheld because telemetry quality is unreliable.

---

## 19. Deterministic Safety Override

The most important consensus rule is:

> AI cannot downgrade deterministic CRITICAL evidence.

For example:

```text
Deterministic Risk = CRITICAL
AI = SAFE
```

GridGuard must retain the CRITICAL condition.

This prevents an ML model from suppressing strong deterministic safety evidence.

---

## 20. Canonical Overheating Demonstration

The current GridGuard jury demonstration uses a synthetic overheating sequence.

The sequence gradually increases electrical load and cable temperature.

A simplified progression is:

| Step | Current | Cable Temperature | Deterministic State |
|---|---:|---:|---|
| 1 | 320 A | 45°C | NORMAL |
| 2 | 340 A | 48°C | NORMAL |
| 3 | 370 A | 54°C | NORMAL |
| 4 | 400 A | 60°C | WARNING |
| 5 | 435 A | 68°C | WARNING |
| 6 | 470 A | 76°C | HIGH |
| 7 | 500 A | 82°C | CRITICAL |

During the demonstrated prototype sequence:

```text
Step 3:
Deterministic state = NORMAL
Predictive AI = early-warning advisory

Step 4:
Deterministic state = WARNING
```

Therefore, the defensible demonstration claim is:

> In our synthetic overheating demonstration, GridGuard's predictive model issued an early-warning advisory one telemetry cycle before the deterministic risk engine crossed its WARNING threshold.

This is the preferred jury wording.

---

## 21. Important Interpretation of the Early-Warning Claim

The following statement would be misleading:

> GridGuard always predicts failures five cycles early.

GridGuard does not make that claim.

The model's classification target looks up to five telemetry cycles into the future.

That does not mean every event is detected five cycles before the deterministic system.

The currently demonstrated lead is:

```text
One telemetry cycle
```

in the synthetic overheating example.

---

## 22. Recovery Behavior

The jury sequence also demonstrates recovery.

Example recovery telemetry:

```text
315 A / 46°C
305 A / 45°C
300 A / 44°C
```

The deterministic risk returns to NORMAL and the active alarm can be resolved.

This demonstrates that GridGuard represents both deterioration and recovery rather than permanently retaining a dangerous state after conditions normalize.

---

## 23. Current AI Interface

The Operations Center exposes AI information including:

- consensus state,
- confidence,
- predictive risk probability,
- prediction horizon,
- behavioral anomaly state,
- data quality,
- layer agreement,
- major AI drivers,
- and the AI Early-Warning Timeline.

The AI Timeline compares:

```text
Predictive AI probability
vs.
Deterministic risk score
```

during the current live panel session.

This visualization allows the early-warning sequence to be demonstrated directly.

---

## 24. Limitations

The current AI validation has several important limitations.

### Synthetic Data

Training and evaluation use synthetic prototype telemetry.

### No Field Validation

The models have not been validated on a real fleet of low-voltage electrical panels.

### No Certified Protection Role

The models are not certified protection algorithms.

### Dataset Assumptions

Performance depends on the assumptions used by the synthetic scenario generator.

### Sensor Realism

Real industrial sensors may introduce noise, drift, calibration differences, missing data, electromagnetic interference, and failure patterns not fully represented in the synthetic dataset.

### Domain Shift

Real deployment conditions may differ from model-training conditions.

### Probability Calibration

Predictive probabilities should not automatically be interpreted as real-world failure probabilities.

### Limited Fault Coverage

The current dataset does not represent every possible electrical failure mechanism.

---

## 25. Required Future Validation

Before industrial use, GridGuard AI would require:

- real sensor data collection,
- field dataset construction,
- expert electrical labeling,
- independent validation datasets,
- multiple panel types,
- multiple operating environments,
- sensor calibration,
- domain-shift analysis,
- probability calibration,
- false-alarm analysis,
- missed-event analysis,
- long-duration monitoring,
- and prospective field trials.

Only after these stages could real-world performance claims be made.

---

## 26. Current Positioning

The correct description is:

> GridGuard uses deterministic risk logic together with synthetic-data-trained AI advisory models to investigate predictive early warning, behavioral anomaly detection, data-quality-aware decision support, and explainable panel monitoring.

The incorrect description is:

> GridGuard's AI has been proven to predict real electrical failures with 95% accuracy.

The current metrics represent synthetic prototype evaluation only.

---

## 27. Jury Summary

The AI contribution of GridGuard can be summarized as:

1. **Predictive AI** looks for future HIGH / CRITICAL escalation.
2. **Isolation Forest** detects unusual operating behavior.
3. **Quality Guard** prevents unreliable telemetry from creating strong AI advisories.
4. **Explainability** shows major model drivers.
5. **Consensus** combines deterministic and AI evidence.
6. **Deterministic CRITICAL always takes priority.**
7. **AI remains advisory.**
8. **Current validation is synthetic, not field-certified.**

The strongest demonstrated prototype result is:

> In our synthetic overheating demonstration, GridGuard's predictive model issued an early-warning advisory one telemetry cycle before the deterministic risk engine crossed its WARNING threshold.