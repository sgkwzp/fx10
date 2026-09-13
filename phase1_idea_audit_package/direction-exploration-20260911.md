# Procedural Video Error Detection: Direction Exploration

Revision 3, 2026-09-11. Supersedes revision 2.
Major changes: decision-layer gap triple-confirmed; dangerous prior-art papers named;
full error-pool counts and object-coverage for all 5 tasks; CaptainCook4D validation
feasibility assessed; reviewer risk register updated with FAIL-Detect / FIDeL / PWR.

## Target and hard constraints

- Venue: CVPR/ICCV 2027 primary; IEEE TMM acceptable alternative.
- Compute: one rented RTX 4090.
- Data: no new annotation. Only existing labelled benchmarks (EgoPER, CaptainCook4D,
  Assembly101-O, EPIC-Tent-O, HoloAssist, IndustReal) plus the local Tea subset for
  development.
- Consequences: benchmark-construction routes are out. Large-scale video pretraining
  is out. Training anything VLM-scale is out. Explanation-faithfulness protocols needing
  human study are out. Viable space = frozen/pre-extracted features + lightweight heads,
  inference-only large models, or decision-layer/protocol contributions over existing
  benchmarks.

## What the literature pass established

1. **A training-free baseline now beats supervised SOTA.** ZeProM (arXiv 2606.21579)
   reports +4.4 EDA and +2.0 F1@0.5 over the strongest supervised methods, averaged
   over all five EgoPER tasks, with no training at all. It explicitly argues the field
   should abandon complex supervised pipelines. Any new supervised detector must clear
   this bar.

2. **The mechanism shelf is full.** Task graphs (DTG, GTG, task-graph MLE), action
   effects (AEM), probabilistic prototypes (PECC), earlier commitment (MistExit),
   explanation (MistSense, AXG-Reasoner, Mistake Attribution), procedural-vs-execution
   branch splitting with a learned gate (UE-MCM), prediction-inconsistency voting
   (ESTANet), belief knowledge bases (Every Mistake Counts).

3. **The decision layer is empty — triple-confirmed by independent evidence.**
   Three independent searches found nothing at the intersection of the decision layer
   and human procedural video error detection.

   - The survey (041.txt) Section VIII open challenges lists dataset gaps, definitional
     ambiguity, embedding-space mismatch, and neuro-symbolic reasoning. Calibration,
     false-alarm budgets, selective prediction, conformal prediction, and statistical
     guarantees are completely absent — the gap has not even been identified as an open
     problem in the survey literature.
   - Local paper scan (13 papers, 2024-2026, YETI / LIVEMAMBA / FIDeL / TRAFA / PWR /
     GuideMe / EGO-MC-BENCH etc.): no paper in the human procedural video domain frames
     the interrupt/silence decision with an alarm budget or statistical guarantee. TRAFA
     (2026) explicitly states "feedback timing is treated as an implicit consequence of
     system state changes rather than an explicit interaction design variable" — a direct
     citable admission of the gap. PWR (Meta, arXiv Jun 2026) comes closest, framing
     per-frame {interrupt, silent} as a first-class decision, but solves class imbalance
     through training (2× interrupt loss weight) rather than post-hoc calibration, and
     provides no statistical FAR guarantee at deployment time.
   - Web search: no paper combines conformal prediction with procedural video mistake
     detection. The closest prior art is in robotic manipulation: FAIL-Detect (Toyota
     Research Institute, arXiv Jun 2025) applies adaptive functional conformal prediction
     on successful demonstrations with an explicit distribution-free FPR guarantee at
     alpha=0.05; FIDeL (CEA/Inria, arXiv Apr 2026) extends CP-based thresholding for
     robot failure detection. Both are in the robotic domain and neither studies
     cross-task threshold transfer.

4. **The adjacent literature says naive answers will fail, which is what makes the
   question non-trivial.** Post-hoc calibration can align probabilities without improving
   correctness ranking, and ranking is what selective prediction needs (arXiv 2605.19369).
   VLM confidence is not epistemic: cutting VideoQA evidence from 18 frames to 6 barely
   moves it, median stays ~0.9 (arXiv 2601.00138). Conformal guarantees on streams need
   exchangeability and tightness auditing, not just assertion (arXiv 2606.15153,
   2105.11886).

5. **Robotics already frames this as runtime monitoring and is uncited in the procedural
   video literature.** Sentinel (Stanford/NVIDIA, arXiv Oct 2024) routes by latency
   tolerance and beats either branch alone by 18%. FAIL-Detect and FIDeL establish the
   CP-on-normal-demonstrations design pattern in robotics; this work is the first
   application and extension to human discrete-step procedural video, with the new
   technical challenges of discrete step structure, cross-task transfer, and extreme
   calibration sample scarcity.

## Dangerous prior-art papers

A systematic gap search identified three papers with the strongest potential to
narrow the "first" claim. None is blocking, but each requires explicit differentiation.

**FAIL-Detect (Toyota Research Institute, arXiv Jun 2025).** Adaptive functional
conformal prediction calibrated on successful robot demonstrations only (no failure
data). Distribution-free FPR guarantee at alpha=0.05 on manipulation failure detection.
Closest conceptual match to R1. Differentiation: (a) robotic manipulation = continuous
trajectory signals; human procedural video = discrete-step sequences — the exchangeability
and calibration-set construction problems are structurally different; (b) no cross-task
transfer evaluation (LOTO); (c) no abstention action — FAIL-Detect does not define a
region where the guarantee cannot certify either decision; (d) FAIL-Detect has ample
normal demonstration calibration data; EgoPER provides only 3 normal validation videos
per task, so the calibration sample-efficiency problem is a distinct technical contribution.

**FIDeL (CEA/Inria, arXiv Apr 2026).** CP-based thresholding with OC learning and
optimal transport for robot failure detection. Also robotic manipulation domain. Less
precise on FPR guarantee framing than FAIL-Detect. Same differentiation as above.

**PWR (Meta Reality Labs, arXiv Jun 2026).** Proactive wearable egocentric assistance
in the human procedural video domain. Explicitly models per-frame {interrupt, silent}
as a first-class decision; evaluates with G-Mean F1 on this decision. Addresses class
imbalance through 2× interrupt loss weight during training — a training heuristic.
Key differentiation: PWR requires retraining the decision head and is not score-agnostic;
R1 is entirely post-hoc, applying to any existing detector's score stream including
ZeProM, with zero retraining. PWR cannot be made to provide a statistical FAR guarantee
at deployment time without architectural change; R1 can.

## Error pool and data inventory (all five tasks)

Full error type counts from refined_label_v3, correctly parsed (pipe-delimited format):

| Task | Videos | Modification | Slip | Addition | Correction | Total error frames | Error rate |
|---|---|---|---|---|---|---|---|
| Coffee | 68 | 1,740 | 6,359 | 0 | 1,014 | 9,113 | 3.1% |
| Oatmeal | 77 | 3,556 | 1,247 | 3,195 | 1,276 | 9,274 | 5.0% |
| Pinwheels | 84 | 17,157 | 1,903 | 3,933 | 3,804 | 26,797 | 11.9% |
| Quesadilla | 80 | 2,459 | 2,053 | 3,066 | 1,982 | 9,560 | 13.2% |
| Tea | 80 | 4,163 | 3,242 | 3,231 | 3,098 | 13,734 | 12.3% |
| **Total** | **389** | **29,075** | **14,804** | **13,425** | **11,174** | **68,478** | **7.7%** |

Modification dominates at 29K frames across all tasks; Slip is second at 15K. Pinwheels
has by far the largest Modification pool (17K frames, 7.6% of its total), making it the
strongest single-task signal for Modification-specific analysis.

Object annotation coverage: active_object.json covers all 170 error-containing videos
across all five tasks (170/170). Any approach using object-state features as input or
ablation signal is fully feasible with no new annotation.

## CaptainCook4D second-domain validation feasibility

CaptainCook4D (CC4D) can serve as an independent cross-domain test but requires one
configuration pass before producing numbers.

What is present locally: step-level error annotations for all 384 recordings, 220 of
which contain at least one error step (57% error rate); 8-category taxonomy
(Preparation/Measurement/Order/Timing/Technique/Temperature/Missing Step/Other);
official combined train/val/test split; 20 task graphs; gopro/frames/tsm features
(2048-dim, 384 files) and gopro/segments/1s features (SlowFast 400-dim, text 1024-dim,
384 files each).

What is blocking: the GTG2Vid eval configs expect 256-dim videoclip/timesformer features
at 10fps under a path that does not exist locally. The existing gopro features are
400/1024/2048-dim from a different extraction pipeline. Adapting the configs to the
present features and adjusting input_dim is one to two days of configuration work, not
a data problem.

Taxonomy overlap: the only clean EgoPER↔CC4D mapping is CC4D Missing Step ≈ EgoPER
Omission. Addition and Correction have no CC4D parallel; Modification maps loosely
across three CC4D categories. Cross-dataset per-category comparison is not meaningful.
Binary step-level error detection metrics (error vs. normal step) are the correct
comparison unit.

## Root problem statement

Procedural error detectors are evaluated as rankers (AP, F1, EDA) but deployed as
decision-makers: an assistant must either interrupt the user or stay silent, at a
specific moment, under a tolerable false-alarm rate. Nothing in the literature connects
the two. A detector with excellent AP can be unusable if its scores are unrankable near
the operating threshold, if its threshold does not transfer across tasks, or if it cannot
abstain when evidence is insufficient. Under a no-annotation, single-GPU constraint,
this gap is also the only one that can actually be attacked.

The decision layer gap is now triple-confirmed: absent from the survey's open challenges,
absent from 10 streaming-assistance papers (2024-2026), and absent from the entire
conformal prediction literature applied to video. The closest existing work (FAIL-Detect,
FIDeL) is in robotic manipulation and does not address human discrete-step procedural
video, cross-task threshold transfer, or calibration sample scarcity.

## Recommended route

### R1. Risk-controlled selective procedural error detection (primary)

**Problem angle.** Given any existing detector's score stream — supervised (EgoPER SOTA,
AEM, ESTANet) or training-free (ZeProM) — decide when to alarm, when to stay silent,
and when to abstain, with a distribution-free guarantee on false alarms per minute that
holds under temporal dependence and transfers to unseen tasks.

**Why this is a real contribution, not a wrapper.** Three things are known to break and
must be fixed:

- Frames within an action segment are strongly dependent, so standard split-conformal
  calibration is invalid; the effective sample size is segments, not frames. A concrete
  violation must be demonstrated on this data, then a block/ensemble conformal or
  weighted-quantile fix applied.
- Calibration and ranking come apart. The paper must report AURC / risk-coverage curves,
  not just ECE, and show which one the distribution-free guarantee actually buys.
- A zero-shot VLM's confidence barely responds to evidence reduction (arXiv 2601.00138),
  so it cannot back an abstention rule as-is. Demonstrating this on procedural error
  detection data is a publishable diagnostic.
- EgoPER has only 3 normal validation videos per task. A supervised detector cannot use
  normal training videos for calibration (train/test contamination). A frozen VLM that
  saw no EgoPER data during training can. This asymmetry is a concrete technical reason
  why a training-free VLM plus conformal calibration is not equivalent to applying
  conformal to a supervised detector, and it motivates investigating both.

**Mechanism sketch.** Score stream → segment-level exchangeability-aware calibration
(block conformal, weighted quantiles under task shift, LOTO transfer test) → risk-controlled
alarm rule with an explicit false-alarms-per-minute budget → abstention region where the
guarantee cannot certify either decision. Evidence-sensitivity audit (frame subsampling,
context truncation) as a stability diagnostic for the VLM branch.

**Contribution type.** New problem + evaluation protocol + method. All three are cheap
under the constraints.

**Differentiation from robotics prior art.** FAIL-Detect (Toyota, 2025) and FIDeL
(CEA/Inria, 2026) apply CP to robot manipulation with continuous trajectory signals and
abundant normal-demonstration calibration data. This work is the first application and
extension to human discrete-step procedural video, with three new technical components:
(a) block/ensemble calibration for discrete-step temporal dependence structures;
(b) cross-task threshold transfer under the LOTO protocol with only 3 calibration videos
per task; (c) abstention action (FAIL-Detect has no abstain region; the guarantee covers
alarm vs. silence only).

**Differentiation from PWR (Meta, 2026).** PWR is trained end-to-end; R1 is entirely
post-hoc and score-agnostic. R1 can wrap ZeProM, AEM, ESTANet, or any future detector
without retraining. PWR cannot be made to provide a statistical FAR guarantee without
architectural change.

**Cost.** Inference only for VLM teacher; calibration is near-free. Fits one 4090.
The bottleneck is caching scores from 3-5 detectors across EgoPER's five tasks, which
requires either running the detectors locally or sourcing cached score files.

**Reviewer risks.** See detailed risk register below.

**Label:** primary. Verified-open gap, constraint-compatible, and the decisive first
experiment is one to two days.

### R2. VLM-teacher → streaming-student distillation (secondary, or a second contribution inside R1)

**Problem angle.** ZeProM's quality comes from a large VLM (Qwen3.5-397B GPTQ, 219 GiB)
that cannot run streaming on a 4090. Distil it into a small student that preserves
detection quality at a fraction of the compute.

**Why coherent.** No distillation work exists for this task. MOCHA (arXiv 2509.14001)
shows frozen-VLM-teacher → vision-only-student with no language at inference; DAIT
(arXiv 2603.15166) handles teacher-student architectural mismatch. Teacher labels are
free, satisfying the no-annotation constraint.

**Risk.** Reads as engineering unless the central claim is about what transfers — e.g.
that procedural-order knowledge distils well but fine-grained execution judgement does
not, demonstrated per error type. Without that diagnostic framing, it is a systems paper
at best.

**Label:** viable secondary. Strong as R1's companion: R1 says which scores are
trustworthy, R2 makes the trustworthy scores affordable. Weaker standalone novelty than R1.

### R3. Negative-result audit of zero-shot VLM mistake detection (fallback / workshop / R1 Section 4)

Ask whether ZeProM-style zero-shot scores are decision-usable at all: calibrated,
rankable, stable under evidence reduction, threshold-transferable. Given arXiv 2601.00138
the expected answer is no, which is a useful finding and a motivating section for R1.
Too thin for a standalone CVPR submission; strong as R1's opening diagnostic.

**Label:** fallback only.

## Retired routes

| Route | Status | Reason |
|---|---|---|
| A. Factorized procedural deviation detector | **retired** | Double-blocked by UE-MCM (two-branch gate) and MistSense (procedural + execution). Local evidence: Tea test split, effect-only ROC-AUC 0.660 / AP 0.518, fusion 0.627 / 0.404, Mahalanobis gate 0.615 / 0.476. The mechanism loses to its own single strongest branch. |
| B. Risk-calibrated early mistake detection | **absorbed into R1** | MistExit occupies "learn to exit earlier". R1 keeps the risk/latency framing but drops the earlier-commitment mechanism. |
| C. Counterfactual recoverability diagnosis | **retired** | Requires latent state/effect representation plus recovery-outcome supervision. Both require annotation. |
| D. Procedural error evaluation protocol (standalone) | **retired as standalone** | A pure benchmark paper needs annotation normalization across incompatible taxonomies and 5-8 reproduced baselines. R1 carries the protocol contribution attached to a method. |

## Minimum viable research question

For procedural video error detection, can a distribution-free risk-control procedure
that respects discrete-step temporal dependence turn an existing detector's heuristic
score — including a training-free VLM's — into an alarm/silence/abstain decision with
a valid and non-trivial false-alarm guarantee that transfers to unseen tasks?

Two sub-questions with independent value: does off-the-shelf conformal calibration
actually break on this data, and by how much? And is a zero-shot VLM's confidence
rankable and stable enough to support an abstention region?

## Decisive first experiment

Cache frame- and segment-level scores from one supervised detector already runnable
locally plus one zero-shot VLM (smallest ZeProM-compatible model feasible on 4090,
e.g. Qwen3.5-35B at ~17 GiB 4-bit), on all five EgoPER tasks. Then, with no training:

1. Fit split-conformal thresholds at a nominal false-alarm budget on frames; measure
   realized false-alarm rate. Expected: violated because frames are not exchangeable.
   Quantify the gap.
2. Repeat at segment level with block conformal. Measure validity and tightness.
3. Compute AURC / risk-coverage and ECE separately; check whether they agree on which
   detector is better.
4. Leave-one-task-out threshold transfer: fit on four tasks, deploy on the fifth.
   Report per-task FAR and bound tightness.
5. Frame-subsampling stability curve for the VLM score (18 → 12 → 6 → 3 frames per
   segment).

If step 1 shows a large violation and step 2 reduces it while step 4 still fails, the
paper has both a problem and a target mechanism. If off-the-shelf conformal already
works and transfers, R1 collapses to a wrapper and R2 becomes primary. This is a
one-to-two-day experiment and it decides the paper.

The decisive first experiment does not require CaptainCook4D. CC4D is the generalization
check that enters once the core method is established.

## Evidence package for full submission (R1)

**Claim 1: Off-the-shelf split-conformal calibration is invalid on procedural video
frame streams and the violation is significant.**
Datasets: EgoPER five tasks. Baselines: frame-level split conformal (naïve), isotonic
recalibration, temperature scaling. Metrics: empirical FAR vs. nominal alpha, violation
gap, effective sample size ratio. Ablations: vary segment length, vary coverage level.
Expected result: clear violation on frame-level, partial repair at segment level.

**Claim 2: A block/ensemble conformal procedure on segments achieves valid and
non-trivial false-alarm control and the guarantee transfers LOTO.**
Datasets: EgoPER LOTO. Baselines: naïve frame conformal, PWR G-Mean F1 framing (no
guarantee), isotonic threshold. Metrics: AURC, empirical FAR at each alpha, bound
tightness (Γ), time-to-detect at fixed FAR budget. Ablations: block size, weighted
vs. unweighted quantile, threshold vs. abstain region. Stress test: held-out task
with very different error distribution (Coffee has 3.1% error vs. Quesadilla 13.2%).

**Claim 3: Zero-shot VLM confidence is non-rankable near the operating threshold and
does not support abstention without further calibration.**
Datasets: EgoPER Tea + one other task. Evidence: evidence-sensitivity curve, ECE vs.
AURC split, failure cases where high confidence = error and low confidence = normal.
This is the motivating diagnostic section, not a standalone claim.

**Cross-domain generalization (CaptainCook4D):** once main results exist, run the
calibrated alarm procedure on CC4D using the binary error-detection framing. Report FAR
and AURC; do not compare per-category numbers (taxonomy mismatch). One to two days of
config adaptation required first.

## Reviewer-risk register (R1)

| Risk | Type | Repair |
|---|---|---|
| "This is just conformal prediction applied to a new task" | requires-new-result | Demonstrate a concrete failure of naïve off-the-shelf conformal under temporal dependence on EgoPER data; show the fix; report both the failure magnitude and the fixed result. The violation is the contribution, not the application. |
| "No AP/F1/EDA improvement" | writing/framing | State up front that the detector is held fixed and the claim is decision quality at controlled risk; include a fixed-budget comparison table where competing detectors reverse rank under the alarm constraint. |
| "FAIL-Detect already does this" | requires-differentiation | Cite FAIL-Detect; explain the three structural differences (continuous vs. discrete-step, no LOTO evaluation, no abstain action, calibration sample scarcity). Show that naïve transfer of FAIL-Detect's procedure to EgoPER produces a degenerate or invalid guarantee; show the fix. |
| "PWR (Meta 2026) solves the same problem" | requires-differentiation | PWR is trained end-to-end; cannot provide statistical FAR guarantee; not score-agnostic. One paragraph in related work; one row in comparison table showing PWR has no bound. |
| Calibration reported instead of ranking | evidence-fixable | Report AURC/risk-coverage as primary, ECE/Brier as secondary; show cases where they disagree (arXiv 2605.19369). |
| Guarantee valid but vacuous (bound too loose) | requires-new-result | Audit tightness explicitly (arXiv 2606.15153); a loose bound is not a result. Report Γ tightness ratio alongside every guarantee claim. |
| ZeProM extends into calibration first | external | Monitor; R1's temporal-dependence and cross-task transfer components are harder to scoop than a calibration table. R2 (distillation) is the backup if ZeProM directly publishes calibration. |
| Reads as statistics, not vision, at CVPR/ICCV | venue-fixable | Lead with the empirical audit of published vision detectors and the failure cases; keep TMM as alternative. Present the block-conformal component as a design decision about video structure, not a statistics paper. |
| Only 3 normal validation videos per task — degenerate bound | requires-new-result | Investigate using frozen-VLM non-EgoPER-trained calibration data (normal training videos) to expand the calibration set for the VLM branch; quantify the calibration pool size vs. guarantee tightness curve. |

## Overlap scan confirmation (local papers, 2024-2026)

40 local papers scanned. Two additional findings relevant to route selection:

**AEM (arXiv 2512.03474, ICLR 2026) — hard blocks any object-state-based detection route.**
Directly models action effects on object states and spatial arrangements as the primary
error signal, and shows improvement over action-only baselines. Any new route relying on
"verify execution via object state or object-object relations" walks into AEM. This
confirms Route A is correctly retired — its mechanism (two-branch action-identity vs.
execution split) is covered by UE-MCM, and the object-state sub-mechanism is covered by AEM.

**Direction C (VLM distillation) has zero overlap in the local scan.**
No paper among the 40 local papers instantiates a teacher-to-student VLM distillation
pipeline for procedural error detection. R2 is the most open direction mechanistically.

**PIE-V (arXiv 2604.15134, CVPRW 2026)** provides a framework for injecting controlled
errors into clean procedural videos. Not a competitor, but a potential future data-augmentation
resource if normal video supply becomes a calibration bottleneck for R1.

## Next work item

Run the decisive first experiment. Prerequisites in order:

1. Identify a supervised detector whose score caches are already computable locally
   without retraining (AEM or ESTANet are the most likely candidates — verify that
   the code and model weights are present).
2. Identify the smallest ZeProM-compatible VLM that fits the 4090 (Qwen3.5-35B at
   ~17 GiB 4-bit is the candidate; verify VRAM budget including KV cache).
3. Cache scores for both detectors over all five EgoPER tasks at frame level and
   segment level.
4. Run the five-step experiment above. One to two days total.

If supervisor detector score caches are not immediately runnable, start with the ZeProM
VLM diagnostic only (steps 3 and 5) and defer the joint comparison.
