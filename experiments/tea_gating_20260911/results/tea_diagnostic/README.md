# Tea factorized-deviation diagnostic

Run command:

```text
python code/tea_diagnostic.py
```

The script builds references from normal training videos and compares four frame-level scores:

- `visual`: distance to the closest normal action prototype;
- `order`: temporal transition residual relative to normal training transitions;
- `effect`: distance to a normal feature manifold using a cosine kNN proxy;
- `factorized_fused`: standardized sum of the three scores.

## Result

The validation split contains only normal videos, so ROC-AUC/AP are undefined there. On the held-out test split:

| Score | ROC-AUC | Average Precision |
|---|---:|---:|
| visual | 0.5719 | 0.3670 |
| order | 0.5898 | 0.3356 |
| effect | **0.6596** | **0.5176** |
| factorized_fused | 0.6267 | 0.4043 |

The current result does **not** support the claim that naive factor fusion improves detection. The effect residual is the strongest single signal, while the order and visual residuals add noise when standardized and summed without calibration. This is still a useful mechanism result: state/effect inconsistency appears more promising than generic appearance novelty on this Tea split, but the factorization needs learned weighting, temporal aggregation, and a leakage/semantic audit before it can support a paper claim.

The fused score separates some error types unevenly: `Error_Addition` and `Error_Correction` have high mean scores, while `Error_Modification` is close to normal. This suggests error-type-specific modeling is necessary.

## Limitations

- This is a lightweight feasibility diagnostic, not a trained model.
- Frame-level labels are expanded from 10-fps annotations; temporal correlation is not corrected.
- The validation split has no positive videos in the provided split files.
- The effect score is a normal-manifold proxy, not a causal action-effect model.
- Results use the 256-D `vc_v_features_10fps` features and only the local Tea subset.

## Decision

Keep the factorized-deviation direction only in a refined form: learn a calibrated gate that selects visual/order/effect evidence conditioned on action phase and error type. Before scaling to CaptainCook4D or EgoPER, run a temporal segment-level evaluation and compare learned gating against the strong `effect`-only baseline.
