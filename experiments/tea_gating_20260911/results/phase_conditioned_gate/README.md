# Phase-conditioned gating result

The experiment assigns each frame to its nearest normal action prototype and
fits a separate residual distribution for each phase using normal training
videos only. Sparse phases fall back to the global model.

| Score | ROC-AUC | AP |
|---|---:|---:|
| Effect-only | **0.6596** | **0.5176** |
| Phase-conditioned Mahalanobis gate | 0.6032 | 0.4598 |

Phase conditioning does not improve the effect-only baseline on the current Tea
split. The likely issue is that nearest-prototype phase assignment is noisy for
error frames, while the residual distributions are still strongly dominated by
error additions. This rejects the simplest unsupervised phase-gating variant.

The direction should now change from unsupervised gating to **supervised
calibration with task-level splits**: use a small labeled calibration subset to
learn phase/error-type weights, keep entire videos disjoint from test, and
compare against effect-only. If supervised gating cannot beat effect-only under
that protocol, effect/state modeling should become the primary method and
visual/order residuals should be used only for analysis.
