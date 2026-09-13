# Decision-layer direction: feasibility checkpoint (2026-09-11)

## Local prerequisite audit

- GPU available locally: NVIDIA RTX 2060, 6 GiB. This is insufficient to test a 35B VLM and should not be used as a proxy for the planned rented 4090/A100.
- Python environment has `torch`, but not `transformers` or `bitsandbytes`; Qwen3.5-35B cannot be benchmarked locally until a rented GPU environment and the inference stack are provisioned.
- No local AEM/ESTANet checkpoint or inference repository was found. The workspace contains the ESTANet paper and multiple existing EgoPER/CaptainCook4D GTG2Vid checkpoints. Therefore the supervised detector branch can start from GTG2Vid/AMNAR outputs, while AEM/ESTANet requires obtaining public code/weights or replacing the branch.

## Feasibility judgment

The decision-layer hypothesis is viable as a research question, but the strongest claim must be statistical control at the intervention/video level. With only three normal validation videos per EgoPER task, naive task-wise frame-level conformal calibration will have coarse quantiles and invalid nominal guarantees under temporal dependence. This is a testable limitation and likely the central technical problem to solve, rather than a reason to abandon the direction.

## Decisive audit

1. Run a frozen detector on all five EgoPER tasks and export frame scores plus timestamps.
2. Compare iid frame split, contiguous block split, video-level split, and leave-one-video-out calibration.
3. Evaluate empirical false-positive rate, detection delay/coverage, intervention count per video, and calibration intervals at target budgets (e.g. 1%, 5%, 10%).
4. Add task-pooled and hierarchical calibration to quantify whether three-video task calibration is salvageable.
5. Stress-test shift across users/tasks and report failures; use these results to choose R1 primary or R2 primary.

## Recommended positioning

Frame the contribution as a statistically budgeted interrupt/silence policy for online procedural-video error detectors. Differentiate from robot conformal work through few-normal-video, temporally dependent, human egocentric calibration and an intervention utility objective. Treat PWR as a detector/policy baseline and FAIL-Detect/FIDeL as calibration-related prior art.

## Decision rule

- Keep R1 primary if block/video-level calibration yields useful detection delay at controlled false-alarm budgets on EgoPER and transfers to CaptainCook4D.
- Make R2 primary or a joint paper if guarantees collapse under realistic splits and no stable correction is found within one week.
