# Tea residual-gating diagnostic

Command:

```text
python code/tea_gated_diagnostic.py
```

The gate is fitted with normal training videos only. It standardizes visual,
order, and effect residuals, estimates a shrunk covariance matrix, and uses a
Mahalanobis distance as an unsupervised gated anomaly score.

## Held-out test result

| Score | ROC-AUC | AP |
|---|---:|---:|
| Effect-only | **0.6596** | **0.5176** |
| Unsupervised Mahalanobis gate | 0.6152 | 0.4761 |

The learned unsupervised gate is worse than the effect-only baseline. This is a
useful negative result: residual covariance alone cannot decide which evidence
source is relevant for a mistake. The gate is especially dominated by
`Error_Addition`, while `Error_Modification` remains difficult.

## Direction update

Do not promote generic unsupervised residual fusion to the paper method. The
next viable mechanism is **phase-conditioned gating**: infer the current action
phase (nearest normal action prototype or task-graph state), then learn/calibrate
different residual weights and thresholds per phase using normal validation
videos. A stronger version can use a small number of labeled error videos for
supervised calibration, but must preserve a clean task-level split.

Current evidence supports effect/state inconsistency as the primary signal; the
other residuals should be auxiliary evidence selected conditionally rather than
added globally.
