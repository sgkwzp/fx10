# How to Correctly Make Mistakes A Framework for Constructing and Benchmarking Mistake Aware Egocentric Procedural Videos

[Original PDF](../How%20to%20Correctly%20Make%20Mistakes%20A%20Framework%20for%20Constructing%20and%20Benchmarking%20Mistake%20Aware%20Egocentric%20Procedural%20Videos.pdf)

Pages: 23

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

# **How to Correctly Make Mistakes: A Framework for Constructing and Benchmarking Mistake Aware Egocentric Procedural Videos** 

Olga Loginova University of Trento Italy 

Frank Keller 

University of Edinburgh United Kingdom 

olga.loginova@unitn.it keller@inf.ed.ac.uk 

## **Abstract** 

_Reliable procedural monitoring in video requires exposure to naturally occurring human errors and the recoveries that follow. In egocentric recordings, mistakes are often partially occluded by hands and revealed through subtle object state changes, while existing procedural datasets provide limited and inconsistent mistake and correction traces. We present PIE-V (Psychologically Inspired Error injection for Videos), a framework for constructing and benchmarking mistake-aware egocentric procedural videos by augmenting clean keystep procedures with controlled, human-plausible deviations. PIE-V combines a psychology-informed error planner conditioned on procedure phase and semantic step load, a correction planner that models recovery behavior, an LLM writer that performs cascade-consistent rewrites, and an LLM judge that validates procedural coherence and repairs failures. For video segment edits, PIE-V synthesizes replacement clips with text-guided video generation and stitches them into the episode to preserve visual plausibility. Applied to 17 tasks and 50 Ego-Exo4D scenarios, PIE-V injects 102 mistakes and generates 27 recovery corrections. For benchmarking, we introduce a unified taxonomy and a human rubric with nine metrics that cover step-level and procedure-level quality, including plausibility, procedure logic with annotator confidence, state change coherence, and grounding between text and video. Using this protocol, we audit several existing resources and compare PIE-V against a freeform LLM generation baseline under the same criteria. Together, the framework and rubric support post-completion verification for egocentric procedural mistake detection and correction._ 

## **1. Introduction** 

To err is human; to err **humanly plausible** is hard. Procedural assistants that watch, guide, or evaluate stepwise activities can fail if trained only on ideal executions. In 

real kitchens, workshops, and labs, people omit steps, swap substeps, use the wrong tool, or execute a step slightly off. Learning and evaluating such behavior therefore requires datasets with realistic deviations, yet these are hard to collect and standardize at scale, leaving current resources sparse and heterogeneous [2]. Such datasets are needed to train mistake detectors and to evaluate state tracking, consequential error localization, and recovery after an error, not only segment-level anomaly flags [12, 16, 41]. They also support benchmarking of multimodal procedural assistants for egocentric guidance, post hoc procedure verification, and error-aware tutoring, where subtle mistakes and corrections matter beyond the final action label [17, 32]. 

The community is moving toward more structured mistake reasoning. Current approaches model errors through action effects and state changes [12, 16] and emphasize coherence [41]. Staged mistakes scale better [32, 48], but naive perturbations often violate preconditions, create impossible object states, or break the task’s causal structure [24, 28]. This makes mistake resources difficult to compare across domains and often too underspecified to support robust recovery modeling. 

How can we correctly make mistakes in procedural videos to provide mistake detection models with quality data? A useful mistake-enriched dataset should satisfy two requirements: (1) the procedure remains executable and logically coherent as a sequence; (2) injected mistakes resemble human error patterns rather than arbitrary corruption. We operationalize this with **PIE-V**<sup>1</sup> ( **P** sychologically **I** nspired **E** rror injection for **V** ideos), a scalable pipeline for augmenting procedural video datasets with mistake-aware variants. PIE-V instantiates five universal error types (Deletion, Insertion, Transposition, Substitution, Wrong Execution) and controls when errors occur by procedure phase. For Substitution and Wrong Execution, we use semantic roles within each step to localize the error and control its severity through role importance and step load. PIE-V also 

> 1Code and demos: https://github.com/ologin/PIE-V.

<!-- Page 2 -->

![](assets/049/paper-0002-00.png)


Figure 1. PIE-V example on an Ego-Exo4D step from “Making Coffee Latte”: (A) reference step; (B) wrong execution with an observable spill; (C) correction that restores procedural consistency by cleaning and redoing the pour. 

generates realistic Corrections, since natural errors often trigger recovery such as redoing a step, inserting a missing action, or undoing an incorrect state [42]. 

Figure 1 illustrates a typical PIE-V error and correction trace on a real procedural step. PIE-V modifies both the instruction sequence and the corresponding video segment to maintain episode-level coherence. 

A second challenge is evaluation. Existing procedural mistake datasets are valuable resources, but they were typically designed for objectives such as detecting visual deviations from a reference step or procedure [11, 13, 17]. For post-completion mistake detection and correction, where the goal is to validate the full procedure trace after a task appears complete, this yields only partial coverage. Annotations may capture visually salient deviations that are informative for their original tasks, but they do not necessarily correspond to consequential execution errors at the level of the full procedure. PIE-V avoids such visual “artifacts” by using video generation to create more subtle, behaviorally credible deviations. We propose a rubric-style evaluation for mistake-aware procedural video datasets and use it to audit existing resources and compare generation strategies. The rubric scores whether an event is a consequential execution error, whether its effects remain procedurally consistent, and whether the sample provides enough structure to study recovery. 

Our contributions are four-fold: (1) a unified taxonomy of procedural errors and semantic roles; (2) a multi-criteria human rubric for mistake assessment; (3) an extensive audit comparing PIE-V against SoTA LLM baselines and existing datasets; and (4) PIE-V, a psychology-informed pipeline for semantics-aware mistake injection. 

## **2. Universal taxonomy of mistakes** 

Our taxonomy draws on three sources: (i) existing mistake datasets and their annotation practices, (ii) sequence 

edit operations as a transferable structural view of procedural deviations, and (iii) cognitive error theory [35], which distinguishes plan-level changes from execution-level deviations and links plausibility to where an error occurs and how it disrupts task state. 

We define five mistake types and treat CORRECTION (C) as a separate component. Correction is reactive: it is triggered by the error to return the executor to the reference trace. 

The five mistake types are: DELETION (D), a required step is missing; INSERTION (I), an extra step is added; SUBSTITUTION (S), an intended step is replaced by a different step; TRANSPOSITION (T), steps are executed in the wrong order; and WRONG EXECUTION (WE), the intended step occurs but with incorrect local parameters. The first four types are structural edits on the step sequence and align with classical edit operations. Deletion, Insertion, and Substitution correspond to Levenshtein style edits [22]. Transposition covers sequencing errors, including adjacent swaps characteristic of Damerau style edits [9]. Wrong Execution is related to Substitution but captures execution level deviations that preserve the step identity while changing how it is carried out. This type is closer to slips and lapses in cognitive accounts of human error. 

Wrong Execution and many instances of Substitution require localization within a step. We therefore represent steps through _semantic roles_ [14, 31] and apply edits to targeted role arguments such as Object, Coobject, Instrument, Location, Destination, Origin, Purpose, and Manner. Role importance provides an explicit notion of severity by distinguishing high impact arguments (Object, Coobject<sup>2</sup> ) from medium impact roles (Location, Destination, Origin, Instrument) and low impact modifiers (Manner, Temporal, 

> 2Coobject labels a secondary argument beyond the primary Object, often the target/recipient (e.g., in APPLY/FIT) or the second item being combined (e.g., in MIX/ADD).

<!-- Page 3 -->

Table 1. Qualitative cognitive motivations behind each error type in our taxonomy and their phase tendencies. 

|**Error type**|**Key psychological interpretation and phase tendency**|
|---|---|
|Substitution|Confusion between similar steps, associative interference, or schema competition; tends to be rarer in later<br>phases once the execution pattern stabilizes.|
|Wrong execution|Execution slips and capture errors (local parameter mistakes), often due to unfamiliarity and motor learning<br>early on; can occur throughout and may reappear toward the end under fatigue.|
|Deletion|Lapses due to memory overload and post-completion vulnerability; tends to increase over the procedure, often<br>peaking toward the end as attention drops.|
|Insertion|Overgeneralization or associative activation (including unintended repetition); generally rarer, but can increase<br>in the middle when multiple routines overlap and the performer is in the flow.|
|Transposition|Sequencing and planning slips under high cognitive load; can occur under time pressure or fatigue, often when<br>step ordering constraints are weak or when attention is divided.|



Degree, Quantity). This role-based view is consistent with work that localizes mistakes inside steps and analyzes their attribution, and with evidence that procedural understanding depends on recovering and using step arguments, including implicit ones [5, 24]. 

Table 1 summarizes the taxonomy and qualitative cognitive motivations. In later sections we use this unified language to map heterogeneous datasets onto comparable categories. When a dataset uses task-specific labels that do not align cleanly with these types, we treat the mapping as approximate. 

## **3. Rubric for mistake-aware dataset assessment** 

To assess mistake-aware procedural traces, we separate two questions. First, does the marked deviation constitute a consequential procedural mistake, as opposed to a permissible execution variant. Second, if it is a mistake, is it plausible at the step level and coherent at the procedure level. Table 2 summarizes the rubric dimensions and scales, following multi-criteria human evaluation practice rather than relying on a single subjective score [1, 44]. 

**Step-level criteria. Error Validity** is a binary gate: without recovery, the deviation would plausibly change the intended outcome, invalidate a prerequisite for later steps, or induce an incorrect intermediate state. This separates consequential mistakes from benign execution variants or incidental noise. **Human Plausibility** measures whether a real person could naturally make this specific mistake in context. **Confusability** measures how easy it is to miss the mistake during real-time execution; it is distinct from Human Plausibility. **Taxonomy Fit (Error Type)** assigns each mistake to one of the five universal categories from Section 2 for domain-agnostic analysis across datasets and generators. **Video Plausibility** evaluates whether the mistaken behavior looks visually natural in egocentric footage, 

rather than theatrical or staged. If a **Correction** is present, it is treated as an additional step in the edited trace with an explicit semantic dependency on the triggering mistake. It is scored with the same applicable metrics, and its plausibility is interpreted relative to the mistake it addresses. 

**Procedure-level criteria.** Procedure-level metrics assess global coherence of the full sequence of procedural steps with mistakes. **Procedure Logic** is a binary judgment of whether the entire procedure becomes logically inconsistent due to this mistake. Because this decision can be intrinsically ambiguous, it is paired with a 3-level confidence score. Let _e_ denote an annotated procedure instance and _Ae_ the set of raters who scored it. Each rater _k ∈ Ae_ provides a binary decision _yk_ ( _e_ ) _∈{_ 0 _,_ 1 _}_ indicating whether the procedure logic is broken, and a confidence weight _qk_ ( _e_ ) _∈{_ 1 _,_ 2 _,_ 3 _}_ . The final per example score is computed as a confidence weighted fraction of “logic broken” decisions: 


![](assets/049/paper-0003-09.png)


For example, if two raters answer “Yes” with confidence 3 and one answers “No” with confidence 2, then PL( _e_ ) = 6 _/_ (6 + 2) = 0 _._ 75. **Sequence Consistency Score** is a rating of whether the resulting step order remains consistent with the procedure constraints and dependencies. This captures step sequence quality beyond the binary logic decision, making a distinction between locally and completely broken reorderings. **State Change Coherence** is a binary check that the implied world state remains consistent across the textual trace, avoiding contradictions such as objects appearing or changing identity without an action, or outcomes that become impossible under the described steps. For example, if the trace omits pouring water, but the video later shows a full coffee cup, the implied state transition is inconsistent, violating State Change Coherence. **Text-**

<!-- Page 4 -->

Table 2. Overview of the PIE-V dataset assessment rubric. 

|**Metric**|**Scale**|**What it measures**|
|---|---|---|
|Error Validity|Binary|Whether the deviation should be treated as a mistake under the<br>procedure-level benchmark, rather than a benign variation.|
|Human Plausibility|Likert (1–5)|How natural the mistake appears in context, avoiding both overly<br>perfect staging and implausible corruption.|
|Confusability|Likert (1–5)|How difficult it is to notice the mistake, used as a proxy for de-<br>tectability and perceived severity.|
|Procedure Logic|Binary + Likert (1–3)|Whether the overall procedure becomes logically broken due to the<br>mistake(s), together with annotator confidence.|
|Sequence Consistency|Likert (1–5)|Whether the edited step sequence remains executable as a coherent<br>procedure.|
|State Change Coherence|Binary|Whether the implied world state remains coherent, without impossi-<br>ble preconditions or state transitions.|
|Video Plausibility|Likert (1–5)|Whether the visual depiction of the mistake looks natural when<br>video is available.|
|Text-Video Grounding Consistency|Likert (1–5)|Whether the textual procedure matches what happens in the video at<br>the episode level.|



**Video Grounding Consistency (episode level)** rates alignment between the entire textual trace (including the mistake and downstream steps) and what is shown in the video. This is defined at the episode level because mismatches can accumulate after an error and can also reflect upstream step segmentation or annotation drift, not only a single step. 

**Scalable approximations.** Human annotations do not scale to auditing entire corpora of procedural videos, so the rubric supports learned or algorithmic proxies calibrated on a small human-labeled subset. A common approach is an LLM-based judge that predicts rubric dimensions from text for all metrics except video plausibility and video–text grounding, then calibrates its outputs against human gold labels. These proxies support large-scale screening and comparative audits; the human rubric remains the reference standard for validity and realism. 

**Step load and phases.** PIE-V computes phases<sup>3</sup> using a step-load signal that combines normalized duration and a semantic-complexity proxy derived from _at_ : 


![](assets/049/paper-0004-05.png)


� � where duration( _t_ ) and complexity( _t_ ) are min-max normalized within the procedure. The complexity proxy increases with predicate count, role count, nesting depth, and the number of explicit relations in _at_ . We assign each step a coarse phase _ϕ_ ( _t_ ) _∈{_ PHASE_1 _,_ PHASE_2 _,_ PHASE_3 _}_ by splitting equally the cumulative load into thirds (early/mid/late by effort). PIE-V outputs a mistake-aware trace consisting of a modified procedure _P_<sup>_′_</sup> , an error plan _E_ , a correction plan _C_ (possibly empty), and an edited video episode aligned with _P_<sup>_′_</sup> . 

### **4.1. Error planner and Correction simulator** 

## **4. PIE-V algorithm** 

PIE-V augments clean keystep egocentric procedures with explicit error and recovery traces. Figure 2 overviews the modular pipeline: planning samples a structured error and correction program, LLM stages realize and validate a coherent textual trace, and the video stage renders edited segments so the final episode remains visually plausible. 

**Problem setup.** We start from clean keystep procedures paired with egocentric video. Let a reference procedure be a sequence of _T_ steps _P_ = ( _s_ 1 _, . . . , sT_ ). Each step _st_ is paired with (i) a semantic representation _at_ (predicateargument structure over semantic roles) and (ii) an observed duration _dt_ from the video segment aligned to the step. 

#### **4.1.1. Error plan** 

PIE-V first samples an error plan _E_ = _{ek}_<sup>_K_</sup> _k_ =1<sup>.Each error</sup> event is 


![](assets/049/paper-0004-13.png)


where _tk ∈{_ 1 _, . . . , T }_ is the target step index, _τk_ is the error type, and _ρk_ stores type-specific parameters (e.g., swap partner for T, or mutated semantic roles for WE). We use five error types _τ ∈{_ D _,_ I _,_ S _,_ T _,_ WE _}_ . 

> 3Phases serve as a compact control variable that separates _where_ errors are more likely to occur from _which_ error types are more likely within a step. PIE-V, in turn, encodes cognitive regularities such as peak-load sequencing failures and late post-completion omissions (details and parameter tables are provided in Sec. C.1.

> Original page for checking 2 unresolved font glyphs.

![Original page 4](assets/049/verify-page-004.png)

<!-- Page 5 -->

![](assets/049/paper-0005-00.png)


Figure 2. PIE-V pipeline overview. Clean keystep procedures are enriched by (1) an error planner (psychology-informed, constrained by step semantics and procedure phase), (2) a correction planner (recovery behavior), (3) an LLM writer (procedure rewriting with cascade consistency edits), (4) an LLM judge (coherence validation and repair; optionally multimodal), and (5) a video synthesis stage that generates new clips and smooth transitions for video plausibility. Green dashed arrows denote precomputed semantic representations for each step that condition all PIE-V modules except video generation. 

The planner is psychology-informed. It biases error placement and type by phase _ϕ_ ( _t_ ) and step load load( _t_ ), reflecting that slips, lapses, and post-completion vulnerability vary over a procedure [6, 7, 29, 35]. 

**Phase error-rate model (where errors occur).** We define a phase error-rate model _rϕ_ and normalize it into multipliers with mean 1: 


![](assets/049/paper-0005-04.png)


Candidate error locations are sampled with load-based weights: 


![](assets/049/paper-0005-06.png)


**Structural edits.** For D, PIE-V removes _st_ from the trace. For I, it inserts a new step near _t_ (the plan specifies insertion location and intent; the writer realizes the text). For T, it swaps the order of two nearby steps within a fixed window (default window size 6). For S, it replaces the intended step with an alternative step consistent with local context and taxonomy constraints. 

**Localized edits.** WE and many cases of S require localization inside a step. PIE-V therefore mutates role arguments inside _at_ rather than rewriting the entire step arbitrarily. We use a role-impact map _ω_ ( _r_ ) _∈ {_ HIGH _,_ MEDIUM _,_ LOW _}_<sup>4</sup> . For Wrong Execution, we select one (occasionally two) roles present in the step with probability proportional to an impact weight and a predicateconditioned role prior: 


![](assets/049/paper-0005-09.png)


under hard constraints that prevent degenerate traces (e.g., _K ≤_ 5 and no more than three consecutive error steps). 

**Phase-conditioned type priors (what errors occur).** Error types are sampled from phase-conditioned priors. Let _πϕ_ be a phase-specific prior over the taxonomy _{_ WE _,_ D _,_ S _,_ I _,_ T _}_ . We sample 


![](assets/049/paper-0005-12.png)


where _m_ ( _·_ ) applies feasibility modifiers such as disallowing deletion if _T ≤_ 4, limiting transposition to a local window, and biasing insertions toward non-essential steps. We also constrain transpositions and prefer substitutions using taxonomy blocks from the underlying keystep hierarchy so that edits remain locally coherent without requiring a full world model. 


![](assets/049/paper-0005-14.png)


We define error severity as the maximum impact among mutated roles. 

#### **4.1.2. Correction simulator** 

PIE-V produces a correction plan _C_ = _{cj}_<sup>_J_</sup> _j_ =1<sup>conditioned</sup> on _E_ and procedure context (with _J_ possibly zero). A correction event is represented as 


![](assets/049/paper-0005-18.png)


where _t_<sup>_′_</sup> _j_<sup>is the insertion point in the edited trace,</sup><sup>_κj_is the</sup> correction type, and _πj_ encodes the repair target (the triggering error id and the object/role to repair). 

> 4Role annotations are precomputed offline for the dataset step vocabulary, while the role-impact map and predicate-conditioned role priors are constructed once from the semantic representation corpus; implementation details are given in Sec. C.3.

<!-- Page 6 -->

![](assets/049/paper-0006-00.png)


Figure 3. Example PIE-V simulation log for the Ego-Exo4D “Install a Wheel” task (cmu_bike14_4). The simulators insert a WE event at Step 01 (incorrect wheel positioning in the fork) and then schedule a phase-matched correction (STOP_AND_FIX _→_ redo Step 01) before continuing the remaining steps. 

**Detection and action priors.** Corrections depend on whether the executor notices the error and decides to act. We model detection with a factorized prior based on error type and phase, modulated by severity, essentiality, predicate salience, and cognitive load: _p_ detect( _e_ ) = clamp _b_ ( _τ, ϕ_ ) _· f_ sev _· f_ ess _· f_ pred _· f_ load _,_ (7) � � where _b_ ( _τ, ϕ_ ) is a hand-specified base detectability prior over error types and phase buckets, motivated by cognitive error recovery regularities, and _f_ load = max(0 _._ 70 _,_ 1 _−_ 0 _._ 25 _·_ load( _t_ )) decreases detection under high load. The full detectability tables, action priors, and latency settings are provided in Sec. C.2. 

Conditioned on detection, we sample a latency in steps and a correction type consistent with the triggering error, such as STOP_AND_FIX, REDO, ROLLBACK_AND_REDO, or UNDO_EXTRA_STEP, following cognitive accounts of recovery behavior [42]. 

Figure 3 shows a concrete sampled trace in which WE at Step 01 triggers an immediate STOP_AND_FIX correction C and step redo, so that the next Step_2 remains plausible, as well as all the following steps. 

### **4.2. LLM writer: coherent procedure rewriting with cascades** 

### **4.3. LLM judge: plan compliance, coherence validation, and repair** 

The judge validates and repairs the writer output. It checks three classes of constraints. **Plan compliance** : Planned error and correction events must appear at the intended locations and match the intended types, including targeted roles for localized edits. **Procedure coherence** : The rewritten trace must remain executable and logically consistent, including ordering constraints and state consistency. We treat state coherence as a predicate over implied transitions _xt_ +1 = _g_ ( _xt, s_<sup>_′_</sup> _t_<sup>)andrejecttracesthatassumeunavail-</sup> able objects or contradict prior effects. **Recovery validity** : Corrections must address the triggering mistake and restore procedural consistency rather than introduce new contradictions. 

The judge runs a bounded repair loop: it proposes minimal rewrites that preserve the plan and revalidates them. If repeated text-only repairs fail, the judge can optionally become multimodal by attaching a small number of cached frames from the implicated steps (typically WE or S) and retrying repair with visual evidence. 

### **4.4. Video synthesis and stitching** 

PIE-V edits the egocentric episode to match _P_<sup>_′_</sup> by regenerating only windows affected by planned errors or corrections and keeping other clips unchanged. For each edited window, we cache boundary anchors (end frame of the preceding step and start frame of the following step), generate a replacement clip conditioned on these anchors when supported, and splice it back, updating step timestamps. Editing is type-dependent and constrained by model duration: WE and S typically replace a full step, I and C add a short clip, T regenerates a local window, and D removes a step and inserts a brief bridge (often _<_ 3 s) to connect surrounding context. 

## **5. Experiments** 

### **5.1. Annotations** 

Given ( _P, {at}, E, C_ ), the writer produces a rewritten procedure _P_<sup>_′_</sup> = ( _s_ 1<sup>_′, . . . , s′_</sup> _T_<sup>_′_)thatinstantiatesplanneddevi-</sup> ations and recoveries. A key requirement is global coherence: if an entity or attribute is edited at step _t_ , later mentions must be updated consistently. We represent this with a cascading rewrite map _M_ over entities and attributes. For each planned local edit, we update _M_ and apply it to future steps: 


![](assets/049/paper-0006-14.png)


The writer therefore emits both the planned error/correction steps and any necessary downstream adjustments, avoiding a common failure mode of unstructured generation where local edits silently break global procedure logic. 

**Annotation protocol and agreement.** We use 5 annotators (2 male, 3 female; age 20–47; mixed educational backgrounds). 

Annotators evaluate samples in a paired setting: a reference execution and a mistake-aware variant with mistakes and corrections explicitly marked. The task is to rate the quality of the indicated deviations and recoveries, not to discover them. We monitor inter-annotator agreement using Krippendorff’s _α_ . The details on annotators and guidelines are given in B. 

### **5.2. PIE-V for Ego-Exo4D** 

We construct a mistake-enriched benchmark from **EgoExo4D** by selecting 17 tasks and 50 scenarios and gen-

> Original page for checking 2 unresolved font glyphs.

![Original page 6](assets/049/verify-page-006.png)

<!-- Page 7 -->

Table 3. Aggregated rubric statistics for existing datasets and Ego-Exo4D generations. We do not report Taxonomy Fit here because it is not a scalar score/rate. Lower is better for “Proc.Logic (Yes, %)” and “State-Chg (Yes, %)”; higher is better for the remaining reported metrics. “–” indicates unavailable values. The best value is highlighted only for metrics with a clear optimization direction. 

|Dataset|Err.Valid (Yes, %)|Human Pl.|Confus.|Proc.Logic (Yes,|%) Seq.Cons.|State-Chg (Yes,|%) Vid.Pl.|T–V Gr.|
|---|---|---|---|---|---|---|---|---|
|EgoPER|51|2.67|1.88|26|4.41|14|3.22|3.42|
|EgoOops|72|**3.73**|1.63|28|4.50|10|**4.31**|3.74|
|Assembly101|65|3.69|2.09|12|**4.82**|4|4.05|3.22|
|CaptainCook4D|74|3.71|2.32|12|4.73|**2**|3.42|3.63|
|Ego-Exo4D-Qwen (freeform)|57|3.34|2.04|36|4.20|27|–|–|
|Ego-Exo4D-GPT-5.2 (freeform)|55|3.08|1.76|25|4.18|7|–|–|
|Ego-Exo4D-Qwen-PJ (PIE-V+Qwen2.5, Qwen3-VL-judged)|71|3.09|1.86|30|4.39|10|–|–|
|Ego-Exo4D-GPT-5.2-PJ (PIE-V+GPT, judged)|**89**|3.41|1.76|**6**|4.48|3|3.54|**3.87**|



Table 4. Scale statistics for Ego-Exo4D generations under different settings. 

## **6. Results** 

### **6.1. Audit of existing datasets** 

|Setting<br>|Total steps|Mistake steps|Mistake rate (%)|Avg. mistakes/video|
|---|---|---|---|---|
|Ego-Exo4D-Qwen (freeform)|1156|112|9.69|2.24|
|Ego-Exo4D-GPT-5.2 (freeform)|1270|77|6.06|1.54|
|Ego-Exo4D-Qwen-PJ|1320|143|10.83|2.86|
|Ego-Exo4D-GPT-5.2-PJ|1323|141|10.66|2.82|



erating one mistake-aware variant per scenario. The error planner injects up to five mistakes per procedure with a cap on consecutive mistakes, disallows deletions for very short procedures, and restricts transpositions to a local window. Across the 50 scenarios, PIE-V injects 102 mistakes and 27 recovery corrections; the mistakes cover all five taxonomy types. Corrections are not generated for every mistake because recovery is sampled conditionally from detectability, action, and latency priors, as detailed in Sec. C.2. 

For text generation and validation in the writer/judge stages we use **GPT-5.2** [40], **Qwen2.5-32B** [3], and the multimodal **Qwen3-VL-32B** [46]. For video editing we synthesize replacement clips with **Kling-O** [43], **Sora 2** [25], **Seedance 1.5 Pro** [38], **Veo 3.1** [10], and **Runway Gen4** [36]. 

### **5.3. LLMs for Ego-Exo4D** 

To assess whether unstructured generation can match structured planning, we compare PIE-V against a **freeform** baseline that rewrites a clean procedure into a mistakeaware variant directly from text instructions, without explicit phase priors or role-constrained edits. We also evaluate a stronger baseline that adds the same validation and repair stage as PIE-V (LLM judge plus deterministic checks), isolating the effect of structured planning. Both baselines use the same model pool as PIE-V for writer/judge: **GPT5.2** , **Qwen2.5-32B** , and the multimodal **Qwen3-VL-32B** . All generated traces are evaluated under the same rubric and audit protocol as the existing datasets. 

We apply our rubric to four egocentric datasets with annotated mistakes: **EgoPER** [21], **EgoOops** [17], **CaptainCook4D** [32], and **Assembly101** [39]. For each dataset, we randomly sample 25 videos that contain at least one annotated mistake. Table 2 summarizes step and mistake density for the four audited datasets for general context. 

Table 3 summarizes rubric aggregates and reveals dataset-specific signatures relevant for procedure-level mistake reasoning: (i) how often annotated deviations are judged as consequential mistakes (Err.Valid), (ii) whether they look like errors a real person could make (Human Pl.) and whether they are easy to overlook (Confus.), and (iii) whether the resulting trace remains logically and causally coherent (Proc.Logic / Seq.Cons. / State-Chg) with aligned text and video (T–V Gr.). 

Across datasets, step-level realism cues (Human Pl., Vid.Pl.) do not imply procedure-level coherence: several resources score well on plausibility while still exhibiting frequent logic or state inconsistencies under a holistic rubric. Conversely, the higher step–mistake density summarized in Table 2 often correlates with lower confusability and more staged-looking deviations, which is desirable for anomaly recognition but less representative of naturally occurring mistake-and-recovery traces. 

Our audit reveals specific signatures: **EgoOops** scores strongly on Human Plausibility and Video Plausibility, suggesting mistakes tend to look behaviorally credible and visually natural. Its scenarios are specific and mistakes are mostly staged, which reduces coverage for broad everyday procedures and limits the diversity of long-horizon causal failures. **Assembly101** shows lower Text–Video Grounding Consistency. It indicates that textual step descriptions do not fully correspond to what is executed on video, which complicates episode-level tracking for multimodal models. Its completion-driven assembly protocol also reshapes the error space: genuine omissions are naturally rare, and repeated attach/detach attempts can appear insertion-like at

<!-- Page 8 -->

Table 5. Krippendorff’s _α_ agreement summary. 

|Dataset|Err.Valid|Human Pl.|Confus.|Proc.Logic|Seq.Cons.|State-Chg|Taxonomy Fit|Vid.Pl.|T–V Gr.|
|---|---|---|---|---|---|---|---|---|---|
|EgoPER|0.912|0.541|0.368|0.728|0.628|0.579|0.759|0.574|0.662|
|EgoOops|0.916|0.592|0.375|0.836|0.667|0.600|0.882|0.579|0.560|
|Assembly101|0.859|0.584|0.697|0.739|0.649|1.000|0.931|0.670|0.861|
|CaptainCook4D|0.694|0.758|0.847|0.621|0.542|0.584|0.791|0.550|0.488|
|Ego-Exo4D-GPT-5.2-PJ (PIE-V+GPT, judged)|0.913|0.489|0.387|0.672|0.619|0.696|0.803|0.630|0.930|



the sequence level. **EgoPER** has comparatively low Error Validity: a substantial fraction of labeled deviations are judged as permissible variants rather than consequential mistakes. This highlights that “mistake” boundaries are often ambiguous in practice, and that such ambiguity can weaken supervision signals when the goal is to learn recovery-triggering errors rather than stylistic execution differences. **CaptainCook4D** combines high mistake density with lower Confusability, i.e., many deviations are easy to notice. This profile fits segment-level anomaly recognition, but it can be less representative of naturally occurring traces where mistakes are often subtle and followed by explicit recoveries rather than frequent isolated anomalies. 

Overall, these datasets were primarily designed for segment-level deviation and anomaly recognition. Our rubric makes explicit which procedure-level properties are not directly targeted by this focus, such as coherent state transitions and episode-level text–video alignment. This reflects different design objectives rather than a flaw of the resources. 

### **6.2. PIE-V vs. LLMs** 

If we compare PIE-V and freeform mistake generation, two trends stand out. First, freeform generation under-produces mistakes (Table 4) and produces substantially higher rates of procedure-level failures (Proc.Logic and State-Chg) despite producing locally fluent text (see Table 3). Second, adding a judge stage without structured planning is insufficient: phase/load priors and role-constrained edits are what keep multi-error traces executable over long horizons. 

A common freeform failure mode is violating implicit preconditions or dropping necessary tail steps: for instance, the model describes a deviation but leaves the step text effectively unchanged, or truncates the remaining procedure; or the resulting trace lacks a recovery step and becomes inconsistent with later state-dependent actions. 

To quantify reliability of the rubric dimensions, we compute Krippendorff’s _α_ across annotators for each metric and dataset (Table 5). We expect higher agreement for crisp categorical judgments (e.g., Error Validity, Taxonomy Fit) and lower agreement for inherently subjective ratings (Human Plausibility, Confusability), where multiple interpretations of “how a human might err” are reasonable. 

## **7. Related work** 

**Human errors, corrections, and structured procedural edits.** PIE-V builds on cognitive accounts that distinguish _slips_ (execution failures) from _mistakes_ (planning failures) [29, 35]. We model phase-dependent vulnerability (e.g., post-completion errors) [7] and elevated error rates under high cognitive load [19, 30], and we explicitly synthesize reactive _corrections_ to capture human recovery behavior and memory competition effects [42, 45]. To generate realistic deviations without physically implausible corruption, we leverage semantic role labeling to localize editable arguments [31] and constrain edits by feasibility and role impact, rather than unconstrained role swaps used in misalignment generation [24]. 

**Procedural video benchmarks.** Egocentric procedural datasets and mistake-focused benchmarks are rapidly expanding but remain heterogeneous in domains and taxonomies. A detailed survey and comparison are available in A. PIE-V complements these resources by providing a scalable pipeline to inject plausible, non-staged errors and recoveries across diverse scenarios, bridging domain-specific anomalies and universal procedural logic. 

## **8. Conclusion** 

Making mistakes is easy; making them _correctly_ is what enables reliable benchmarking. PIE-V turns mistake-aware dataset construction into a controlled, auditable pipeline for egocentric procedures. It plans phase- and load-conditioned deviations and recoveries, realizes them with constrained rewriting and validation, and synthesizes edited clips so the final episodes remain visually plausible. 

PIE-V is the first method to prioritize world state when generating errors: deviations are kept only if their causal effects remain executable, consistent, and recoverable, yielding full error–correction traces rather than isolated anomalies. Human evaluation with our nine-metric rubric confirms that this structure matters: compared with freeform generation and existing resources, PIE-V more often produces consequential, procedure-coherent mistake traces with stronger plausibility cues.

<!-- Page 9 -->

## **Acknowledgements** 

Olga Loginova thanks Amazon Alexa for supporting her research through a generous donation to Raffaella Bernardi. 

## **References** 

- [1] Jacopo Amidei, Paul Piwek, and Alistair Willis. The use of rating and Likert scales in natural language generation human evaluation tasks: A review and some recommendations. In _Proceedings of the 12th International Conference on Natural Language Generation_ , pages 397–402, Tokyo, Japan, 2019. Association for Computational Linguistics. 3 

- [2] Konstantinos Bacharidis and Antonis A. Argyros. Visionbased mistake analysis in procedural activities: A review of advances and challenges, 2025. 1 

- [3] Jinze Bai, Shuai Bai, Yunfei Chu, Zeyu Cui, Kai Dang, Xiaodong Deng, Yang Fan, Wenbin Ge, Yu Han, Fei Huang, Binyuan Hui, Luo Ji, Mei Li, Junyang Lin, Runji Lin, Dayiheng Liu, Gao Liu, Chengqiang Lu, Keming Lu, Jianxin Ma, Rui Men, Xingzhang Ren, Xuancheng Ren, Chuanqi Tan, Sinan Tan, Jianhong Tu, Peng Wang, Shijie Wang, Wei Wang, Shengguang Wu, Benfeng Xu, Jin Xu, An Yang, Hao Yang, Jian Yang, Shusheng Yang, Yang Yao, Bowen Yu, Hongyi Yuan, Zheng Yuan, Jianwei Zhang, Xingxuan Zhang, Yichang Zhang, Zhenru Zhang, Chang Zhou, Jingren Zhou, Xiaohuan Zhou, and Tianhang Zhu. Qwen technical report. _arXiv preprint arXiv:2309.16609_ , 2023. 7 

- [4] Siddhant Bansal, Chetan Arora, and C. V. Jawahar. My view is the best view: Procedure learning from egocentric videos, 2022. 3 

- [5] Anil Batra, Laura Sevilla-Lara, Marcus Rohrbach, and Frank Keller. Predicting implicit arguments in procedural video instructions. In _Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)_ , pages 30399–30419, Vienna, Austria, 2025. Association for Computational Linguistics. 3 

- [6] Michael D. Byrne and Susan Bovair. A working memory model of a common procedural error. _Cogn. Sci._ , 21:31–61, 1997. 5 

- [7] Michael D. Byrne and Elizabeth M. Davis. Task structure and postcompletion error in the execution of a routine procedure. _Human Factors_ , 48(4):627–638, 2006. 5, 8 

- [8] Dima Damen, Hazel Doughty, Giovanni Maria Farinella, Sanja Fidler, Antonino Furnari, Evangelos Kazakos, Davide Moltisanti, Jonathan Munro, Toby Perrett, Will Price, and Michael Wray. The epic-kitchens dataset: Collection, challenges and baselines, 2020. 3 

- [9] Fred J. Damerau. A technique for computer detection and correction of spelling errors. _Communications of the ACM_ , 7:171 – 176, 1964. 2 

- [10] Google DeepMind. Veo 3.1 technical report. Technical report, Google, 2026. Accessed: 2026-02-24. 7 

- [11] Guodong Ding, Fadime Sener, Shugao Ma, and Angela Yao. Every mistake counts in assembly. _ArXiv_ , abs/2307.16453, 2023. 2 

- [12] Alessandro Flaborea, Guido Maria D’Amely di Melendugno, Leonardo Plini, Luca Scofano, Edoardo De Matteis, Antonino Furnari, G. Farinella, and Fabio Galasso. Prego: Online mistake detection in procedural egocentric videos. _2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)_ , pages 18483–18492, 2024. 1 

- [13] Reza Ghoddoosian, Isht Dwivedi, Nakul Agarwal, and Behzad Dariush. Weakly-supervised action segmentation and unseen error detection in anomalous instructional videos. _2023 IEEE/CVF International Conference on Computer Vision (ICCV)_ , pages 10094–10104, 2023. 2, 3 

- [14] Daniel Gildea and Daniel Jurafsky. Automatic labeling of semantic roles. _Computational Linguistics_ , 28(3):245–288, 2002. 2 

- [15] Kristen Grauman, Andrew Westbury, Lorenzo Torresani, Kris Kitani, Jitendra Malik, Triantafyllos Afouras, Kumar Ashutosh, Vijay Baiyya, Siddhant Bansal, Bikram Boote, Eugene Byrne, Zach Chavis, Joya Chen, Feng Cheng, FuJen Chu, Sean Crane, Avijit Dasgupta, Jing Dong, Maria Escobar, Cristhian Forigua, Abrham Gebreselasie, Sanjay Haresh, Jing Huang, Md Mohaiminul Islam, Suyog Jain, Rawal Khirodkar, Devansh Kukreja, Kevin J Liang, JiaWei Liu, Sagnik Majumder, Yongsen Mao, Miguel Martin, Effrosyni Mavroudi, Tushar Nagarajan, Francesco Ragusa, Santhosh Kumar Ramakrishnan, Luigi Seminara, Arjun Somayazulu, Yale Song, Shan Su, Zihui Xue, Edward Zhang, Jinxu Zhang, Angela Castillo, Changan Chen, Xinzhu Fu, Ryosuke Furuta, Cristina Gonzalez, Prince Gupta, Jiabo Hu, Yifei Huang, Yiming Huang, Weslie Khoo, Anush Kumar, Robert Kuo, Sach Lakhavani, Miao Liu, Mi Luo, Zhengyi Luo, Brighid Meredith, Austin Miller, Oluwatumininu Oguntola, Xiaqing Pan, Penny Peng, Shraman Pramanick, Merey Ramazanova, Fiona Ryan, Wei Shan, Kiran Somasundaram, Chenan Song, Audrey Southerland, Masatoshi Tateno, Huiyu Wang, Yuchen Wang, Takuma Yagi, Mingfei Yan, Xitong Yang, Zecheng Yu, Shengxin Cindy Zha, Chen Zhao, Ziwei Zhao, Zhifan Zhu, Jeff Zhuo, Pablo Arbelaez, Gedas Bertasius, David Crandall, Dima Damen, Jakob Engel, Giovanni Maria Farinella, Antonino Furnari, Bernard Ghanem, Judy Hoffman, C. V. Jawahar, Richard Newcombe, Hyun Soo Park, James M. Rehg, Yoichi Sato, Manolis Savva, Jianbo Shi, Mike Zheng Shou, and Michael Wray. Egoexo4d: Understanding skilled human activity from first- and third-person perspectives, 2024. 3, 4 

- [16] Wenliang Guo, Yujiang Pu, and Yu Kong. Procedural mistake detection via action effect modeling, 2025. 1 

- [17] Yuto Haneji, Taichi Nishimura, Hirotaka Kameko, Keisuke Shirai, Tomoya Yoshida, Keiya Kajimura, Koki Yamamoto, Taiyu Cui, Tomohiro Nishimoto, and Shinsuke Mori. Egooops: A dataset for mistake action detection from egocentric videos referring to procedural texts, 2025. 1, 2, 7, 3, 4 

- [18] Youngkyoon Jang, Brian T. Sullivan, Casimir J. H. Ludwig, Iain D. Gilchrist, Dima Damen, and W. Mayol-Cuevas. Epictent: An egocentric video dataset for camping tent assembly. _2019 IEEE/CVF International Conference on Computer Vision Workshop (ICCVW)_ , pages 4461–4469, 2019. 3 

- [19] Marcel Adam Just and Patricia A. Carpenter. A capacity

<!-- Page 10 -->

- theory of comprehension: individual differences in working memory. _Psychological review_ , 99 1:122–49, 1992. 8, 5 

- [20] Max Ku, Cong Wei, Weiming Ren, Harry Yang, and Wenhu Chen. Anyv2v: A tuning-free framework for any video-tovideo editing tasks, 2024. 12 

- [21] Shih-Po Lee, Zijia Lu, Zekun Zhang, Minh Hoai, and Ehsan Elhamifar. Error detection in egocentric procedural task videos. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)_ , pages 18655–18666, 2024. 7, 2, 3, 4 

- [22] Vladimir I. Levenshtein. Binary codes capable of correcting deletions, insertions, and reversals. _Soviet physics. Doklady_ , 10:707–710, 1965. 2 

- [23] Runjia Li, Moayed Haji-Ali, Ashkan Mirzaei, Chaoyang Wang, Arpit Sahni, Ivan Skorokhodov, Aliaksandr Siarohin, Tomas Jakab, Junlin Han, Sergey Tulyakov, Philip Torr, and Willi Menapace. Egoedit: Dataset, real-time streaming model, and benchmark for egocentric video editing, 2025. 12 

- [24] Yayuan Li, Aadit Jain, Filippos Bellos, and Jason J. Corso. Mistake attribution: Fine-grained mistake understanding in egocentric videos, 2025. 1, 3, 8 

- [25] Yixin Liu, Kai Zhang, Yuan Li, Zhiling Yan, Chujie Gao, Ruoxi Chen, Zhengqing Yuan, Yue Huang, Hanchi Sun, Jianfeng Gao, Lifang He, and Lichao Sun. Sora: A review on background, technology, limitations, and opportunities of large vision models, 2024. 7 

- [26] Jinjie Mai, Chaoyang Wang, Guocheng Gordon Qian, Willi Menapace, Sergey Tulyakov, Bernard Ghanem, Peter Wonka, and Ashkan Mirzaei. Easyv2v: A high-quality instruction-based video editing framework, 2025. 12 

- [27] Stephen McKenna and Sebastian Stein. 50 salads. https: //discovery.dundee.ac.uk/en/datasets/50salads/, 2012. 3 

- [28] Medhini Narasimhan, Licheng Yu, Sean Bell, Ning Zhang, and Trevor Darrell. Learning and verification of task structure in instructional videos, 2023. 1 

- [29] Donald A. Norman. _The Psychology of Everyday Things_ . Basic Books, New York, 1988. 5, 8, 6 

- [30] Fred Paas, Alexander Renkl, and John Sweller. Cognitive load theory and instructional design: Recent developments. _Educational Psychologist_ , 38:1 – 4, 2003. 8, 5 

- [31] Martha Palmer, Daniel Gildea, and Paul Kingsbury. The Proposition Bank: An annotated corpus of semantic roles. _Computational Linguistics_ , 31(1):71–106, 2005. 2, 8 

- [32] Rohith Peddi, Shivvrat Arya, Bharath Challa, Likhitha Pallapothula, Akshay Vyas, Bhavya Gouripeddi, Jikai Wang, Qifan Zhang, Vasundhara Komaragiri, Eric Ragan, Nicholas Ruozzi, Yu Xiang, and Vibhav Gogate. Captaincook4d: A dataset for understanding errors in procedural activities, 2024. 1, 7, 2, 3 

- [33] Yicheng Qian, Weixin Luo, Dongze Lian, Xu Tang, Peilin Zhao, and Shenghua Gao. Svip: Sequence verification for procedures in videos, 2022. 2, 3 

- [34] Francesco Ragusa, Antonino Furnari, Salvatore Livatino, and Giovanni Maria Farinella. The meccano dataset: Understanding human-object interactions from egocentric videos in an industrial-like domain, 2020. 2, 3 

- [35] James Reason. _Human Error_ . Cambridge University Press, 1990. 2, 5, 8, 6 

- [36] Runway Research. Introducing Runway Gen-4. https: / / runwayml . com / research / introducing - runway-gen-4, 2025. Accessed: 2025-03-01. 7 

- [37] Tim J. Schoonbeek, Tim Houben, Hans Onvlee, Peter H. N. de With, and Fons van der Sommen. Industreal: A dataset for procedure step recognition handling execution errors in egocentric videos in an industrial-like setting, 2023. 2, 3 

- [38] Team Seedance, Heyi Chen, Siyan Chen, Xin Chen, Yanfei Chen, Ying Chen, Zhuo Chen, Feng Cheng, Tianheng Cheng, Xinqi Cheng, Xuyan Chi, Jian Cong, Jing Cui, Qinpeng Cui, Qide Dong, Junliang Fan, Jing Fang, Zetao Fang, Chengjian Feng, Han Feng, Mingyuan Gao, Yu Gao, Dong Guo, Qiushan Guo, Boyang Hao, Qingkai Hao, Bibo He, Qian He, Tuyen Hoang, Ruoqing Hu, Xi Hu, Weilin Huang, Zhaoyang Huang, Zhongyi Huang, Donglei Ji, Siqi Jiang, Wei Jiang, Yunpu Jiang, Zhuo Jiang, Ashley Kim, Jianan Kong, Zhichao Lai, Shanshan Lao, Yichong Leng, Ai Li, Feiya Li, Gen Li, Huixia Li, JiaShi Li, Liang Li, Ming Li, Shanshan Li, Tao Li, Xian Li, Xiaojie Li, Xiaoyang Li, Xingxing Li, Yameng Li, Yifu Li, Yiying Li, Chao Liang, Han Liang, Jianzhong Liang, Ying Liang, Zhiqiang Liang, Wang Liao, Yalin Liao, Heng Lin, Kengyu Lin, Shanchuan Lin, Xi Lin, Zhijie Lin, Feng Ling, Fangfang Liu, Gaohong Liu, Jiawei Liu, Jie Liu, Jihao Liu, Shouda Liu, Shu Liu, Sichao Liu, Songwei Liu, Xin Liu, Xue Liu, Yibo Liu, Zikun Liu, Zuxi Liu, Junlin Lyu, Lecheng Lyu, Qian Lyu, Han Mu, Xiaonan Nie, Jingzhe Ning, Xitong Pan, Yanghua Peng, Lianke Qin, Xueqiong Qu, Yuxi Ren, Kai Shen, Guang Shi, Lei Shi, Yan Song, Yinglong Song, Fan Sun, Li Sun, Renfei Sun, Yan Sun, Zeyu Sun, Wenjing Tang, Yaxue Tang, Zirui Tao, Feng Wang, Furui Wang, Jinran Wang, Junkai Wang, Ke Wang, Kexin Wang, Qingyi Wang, Rui Wang, Sen Wang, Shuai Wang, Tingru Wang, Weichen Wang, Xin Wang, Yanhui Wang, Yue Wang, Yuping Wang, Yuxuan Wang, Ziyu Wang, Guoqiang Wei, Wanru Wei, Di Wu, Guohong Wu, Hanjie Wu, Jian Wu, Jie Wu, Ruolan Wu, Xinglong Wu, Yonghui Wu, Ruiqi Xia, Liang Xiang, Fei Xiao, XueFeng Xiao, Pan Xie, Shuangyi Xie, Shuang Xu, Jinlan Xue, Shen Yan, Bangbang Yang, Ceyuan Yang, Jiaqi Yang, Runkai Yang, Tao Yang, Yang Yang, Yihang Yang, ZhiXian Yang, Ziyan Yang, Songting Yao, Yifan Yao, Zilyu Ye, Bowen Yu, Jian Yu, Chujie Yuan, Linxiao Yuan, Sichun Zeng, Weihong Zeng, Xuejiao Zeng, Yan Zeng, Chuntao Zhang, Heng Zhang, Jingjie Zhang, Kuo Zhang, Liang Zhang, Liying Zhang, Manlin Zhang, Ting Zhang, Weida Zhang, Xiaohe Zhang, Xinyan Zhang, Yan Zhang, Yuan Zhang, Zixiang Zhang, Fengxuan Zhao, Huating Zhao, Yang Zhao, Hao Zheng, Jianbin Zheng, Xiaozheng Zheng, Yangyang Zheng, Yijie Zheng, Jiexin Zhou, Jiahui Zhu, Kuan Zhu, Shenhan Zhu, Wenjia Zhu, Benhui Zou, and Feilong Zuo. Seedance 1.5 pro: A native audio-visual joint generation foundation model, 2025. 7 

- [39] Fadime Sener, Dibyadip Chatterjee, Daniel Shelepov, Kun He, Dipika Singhania, Robert Wang, and Angela Yao. Assembly101: A large-scale multi-view video dataset for understanding procedural activities. _2022 IEEE/CVF Confer-_

<!-- Page 11 -->

_ence on Computer Vision and Pattern Recognition (CVPR)_ , pages 21064–21074, 2022. 7, 2, 3 

[40] Aaditya Singh, Adam Fry, Adam Perelman, Adam Tart, Adi Ganesh, Ahmed El-Kishky, Aidan McLaughlin, Aiden Low, AJ Ostrow, Akhila Ananthram, Akshay Nathan, Alan Luo, Alec Helyar, Aleksander Madry, Aleksandr Efremov, Aleksandra Spyra, Alex Baker-Whitcomb, Alex Beutel, Alex Karpenko, Alex Makelov, Alex Neitz, Alex Wei, Alexandra Barr, Alexandre Kirchmeyer, Alexey Ivanov, Alexi Christakis, Alistair Gillespie, Allison Tam, Ally Bennett, Alvin Wan, Alyssa Huang, Amy McDonald Sandjideh, Amy Yang, Ananya Kumar, Andre Saraiva, Andrea Vallone, Andrei Gheorghe, Andres Garcia Garcia, Andrew Braunstein, Andrew Liu, Andrew Schmidt, Andrey Mereskin, Andrey Mishchenko, Andy Applebaum, Andy Rogerson, Ann Rajan, Annie Wei, Anoop Kotha, Anubha Srivastava, Anushree Agrawal, Arun Vijayvergiya, Ashley Tyra, Ashvin Nair, Avi Nayak, Ben Eggers, Bessie Ji, Beth Hoover, Bill Chen, Blair Chen, Boaz Barak, Borys Minaiev, Botao Hao, Bowen Baker, Brad Lightcap, Brandon McKinzie, Brandon Wang, Brendan Quinn, Brian Fioca, Brian Hsu, Brian Yang, Brian Yu, Brian Zhang, Brittany Brenner, Callie Riggins Zetino, Cameron Raymond, Camillo Lugaresi, Carolina Paz, Cary Hudson, Cedric Whitney, Chak Li, Charles Chen, Charlotte Cole, Chelsea Voss, Chen Ding, Chen Shen, Chengdu Huang, Chris Colby, Chris Hallacy, Chris Koch, Chris Lu, Christina Kaplan, Christina Kim, CJ Minott-Henriques, Cliff Frey, Cody Yu, Coley Czarnecki, Colin Reid, Colin Wei, Cory Decareaux, Cristina Scheau, Cyril Zhang, Cyrus Forbes, Da Tang, Dakota Goldberg, Dan Roberts, Dana Palmie, Daniel Kappler, Daniel Levine, Daniel Wright, Dave Leo, David Lin, David Robinson, Declan Grabb, Derek Chen, Derek Lim, Derek Salama, Dibya Bhattacharjee, Dimitris Tsipras, Dinghua Li, Dingli Yu, DJ Strouse, Drew Williams, Dylan Hunn, Ed Bayes, Edwin Arbus, Ekin Akyurek, Elaine Ya Le, Elana Widmann, Eli Yani, Elizabeth Proehl, Enis Sert, Enoch Cheung, Eri Schwartz, Eric Han, Eric Jiang, Eric Mitchell, Eric Sigler, Eric Wallace, Erik Ritter, Erin Kavanaugh, Evan Mays, Evgenii Nikishin, Fangyuan Li, Felipe Petroski Such, Filipe de Avila Belbute Peres, Filippo Raso, Florent Bekerman, Foivos Tsimpourlas, Fotis Chantzis, Francis Song, Francis Zhang, Gaby Raila, Garrett McGrath, Gary Briggs, Gary Yang, Giambattista Parascandolo, Gildas Chabot, Grace Kim, Grace Zhao, Gregory Valiant, Guillaume Leclerc, Hadi Salman, Hanson Wang, Hao Sheng, Haoming Jiang, Haoyu Wang, Haozhun Jin, Harshit Sikchi, Heather Schmidt, Henry Aspegren, Honglin Chen, Huida Qiu, Hunter Lightman, Ian Covert, Ian Kivlichan, Ian Silber, Ian Sohl, Ibrahim Hammoud, Ignasi Clavera, Ikai Lan, Ilge Akkaya, Ilya Kostrikov, Irina Kofman, Isak Etinger, Ishaan Singal, Jackie Hehir, Jacob Huh, Jacqueline Pan, Jake Wilczynski, Jakub Pachocki, James Lee, James Quinn, Jamie Kiros, Janvi Kalra, Jasmyn Samaroo, Jason Wang, Jason Wolfe, Jay Chen, Jay Wang, Jean Harb, Jeffrey Han, Jeffrey Wang, Jennifer Zhao, Jeremy Chen, Jerene Yang, Jerry Tworek, Jesse Chand, Jessica Landon, Jessica Liang, Ji Lin, Jiancheng Liu, Jianfeng Wang, Jie Tang, Jihan Yin, Joanne Jang, Joel Morris, Joey Flynn, 

Johannes Ferstad, Johannes Heidecke, John Fishbein, John Hallman, Jonah Grant, Jonathan Chien, Jonathan Gordon, Jongsoo Park, Jordan Liss, Jos Kraaijeveld, Joseph Guay, Joseph Mo, Josh Lawson, Josh McGrath, Joshua Vendrow, Joy Jiao, Julian Lee, Julie Steele, Julie Wang, Junhua Mao, Kai Chen, Kai Hayashi, Kai Xiao, Kamyar Salahi, Kan Wu, Karan Sekhri, Karan Sharma, Karan Singhal, Karen Li, Kenny Nguyen, Keren Gu-Lemberg, Kevin King, Kevin Liu, Kevin Stone, Kevin Yu, Kristen Ying, Kristian Georgiev, Kristie Lim, Kushal Tirumala, Kyle Miller, Lama Ahmad, Larry Lv, Laura Clare, Laurance Fauconnet, Lauren Itow, Lauren Yang, Laurentia Romaniuk, Leah Anise, Lee Byron, Leher Pathak, Leon Maksin, Leyan Lo, Leyton Ho, Li Jing, Liang Wu, Liang Xiong, Lien Mamitsuka, Lin Yang, Lindsay McCallum, Lindsey Held, Liz Bourgeois, Logan Engstrom, Lorenz Kuhn, Louis Feuvrier, Lu Zhang, Lucas Switzer, Lukas Kondraciuk, Lukasz Kaiser, Manas Joglekar, Mandeep Singh, Mandip Shah, Manuka Stratta, Marcus Williams, Mark Chen, Mark Sun, Marselus Cayton, Martin Li, Marvin Zhang, Marwan Aljubeh, Matt Nichols, Matthew Haines, Max Schwarzer, Mayank Gupta, Meghan Shah, Melody Huang, Meng Dong, Mengqing Wang, Mia Glaese, Micah Carroll, Michael Lampe, Michael Malek, Michael Sharman, Michael Zhang, Michele Wang, Michelle Pokrass, Mihai Florian, Mikhail Pavlov, Miles Wang, Ming Chen, Mingxuan Wang, Minnia Feng, Mo Bavarian, Molly Lin, Moose Abdool, Mostafa Rohaninejad, Nacho Soto, Natalie Staudacher, Natan LaFontaine, Nathan Marwell, Nelson Liu, Nick Preston, Nick Turley, Nicklas Ansman, Nicole Blades, Nikil Pancha, Nikita Mikhaylin, Niko Felix, Nikunj Handa, Nishant Rai, Nitish Keskar, Noam Brown, Ofir Nachum, Oleg Boiko, Oleg Murk, Olivia Watkins, Oona Gleeson, Pamela Mishkin, Patryk Lesiewicz, Paul Baltescu, Pavel Belov, Peter Zhokhov, Philip Pronin, Phillip Guo, Phoebe Thacker, Qi Liu, Qiming Yuan, Qinghua Liu, Rachel Dias, Rachel Puckett, Rahul Arora, Ravi Teja Mullapudi, Raz Gaon, Reah Miyara, Rennie Song, Rishabh Aggarwal, RJ Marsan, Robel Yemiru, Robert Xiong, Rohan Kshirsagar, Rohan Nuttall, Roman Tsiupa, Ronen Eldan, Rose Wang, Roshan James, Roy Ziv, Rui Shu, Ruslan Nigmatullin, Saachi Jain, Saam Talaie, Sam Altman, Sam Arnesen, Sam Toizer, Sam Toyer, Samuel Miserendino, Sandhini Agarwal, Sarah Yoo, Savannah Heon, Scott Ethersmith, Sean Grove, Sean Taylor, Sebastien Bubeck, Sever Banesiu, Shaokyi Amdo, Shengjia Zhao, Sherwin Wu, Shibani Santurkar, Shiyu Zhao, Shraman Ray Chaudhuri, Shreyas Krishnaswamy, Shuaiqi, Xia, Shuyang Cheng, Shyamal Anadkat, Simón Posada Fishman, Simon Tobin, Siyuan Fu, Somay Jain, Song Mei, Sonya Egoian, Spencer Kim, Spug Golden, SQ Mah, Steph Lin, Stephen Imm, Steve Sharpe, Steve Yadlowsky, Sulman Choudhry, Sungwon Eum, Suvansh Sanjeev, Tabarak Khan, Tal Stramer, Tao Wang, Tao Xin, Tarun Gogineni, Taya Christianson, Ted Sanders, Tejal Patwardhan, Thomas Degry, Thomas Shadwell, Tianfu Fu, Tianshi Gao, Timur Garipov, Tina Sriskandarajah, Toki Sherbakov, Tomer Kaftan, Tomo Hiratsuka, Tongzhou Wang, Tony Song, Tony Zhao, Troy Peterson, Val Kharitonov, Victoria Chernova, Vineet Kosaraju, Vishal Kuo, Vitchyr Pong, Vivek Verma,

<!-- Page 12 -->

Vlad Petrov, Wanning Jiang, Weixing Zhang, Wenda Zhou, Wenlei Xie, Wenting Zhan, Wes McCabe, Will DePue, Will Ellsworth, Wulfie Bain, Wyatt Thompson, Xiangning Chen, Xiangyu Qi, Xin Xiang, Xinwei Shi, Yann Dubois, Yaodong Yu, Yara Khakbaz, Yifan Wu, Yilei Qian, Yin Tat Lee, Yinbo Chen, Yizhen Zhang, Yizhong Xiong, Yonglong Tian, Young Cha, Yu Bai, Yu Yang, Yuan Yuan, Yuanzhi Li, Yufeng Zhang, Yuguang Yang, Yujia Jin, Yun Jiang, Yunyun Wang, Yushi Wang, Yutian Liu, Zach Stubenvoll, Zehao Dou, Zheng Wu, and Zhigang Wang. Openai gpt-5 system card, 2025. 7 

   - [48] Yiwu Zhong, Licheng Yu, Yang Bai, Shangwen Li, Xueting Yan, and Yin Li. Learning procedure-aware video representation from instructional videos and their narrations, 2023. 1 

- [41] Shane Storks, Itamar Bar-Yossef, Yayuan Li, Zheyuan Zhang, Jason J. Corso, and Joyce Chai. Transparent and coherent procedural mistake detection, 2025. 1 

- [42] Franklin P. Tamborello and J. Gregory Trafton. A long-term memory competitive process model of a common procedural error. _Cognitive Science_ , 35, 2013. 2, 6, 8 

- [43] Kling Team, Jialu Chen, Yuanzheng Ci, Xiangyu Du, Zipeng Feng, Kun Gai, Sainan Guo, Feng Han, Jingbin He, Kang He, Xiao Hu, Xiaohua Hu, Boyuan Jiang, Fangyuan Kong, Hang Li, Jie Li, Qingyu Li, Shen Li, Xiaohan Li, Yan Li, Jiajun Liang, Borui Liao, Yiqiao Liao, Weihong Lin, Quande Liu, Xiaokun Liu, Yilun Liu, Yuliang Liu, Shun Lu, Hangyu Mao, Yunyao Mao, Haodong Ouyang, Wenyu Qin, Wanqi Shi, Xiaoyu Shi, Lianghao Su, Haozhi Sun, Peiqin Sun, Pengfei Wan, Chao Wang, Chenyu Wang, Meng Wang, Qiulin Wang, Runqi Wang, Xintao Wang, Xuebo Wang, Zekun Wang, Min Wei, Tiancheng Wen, Guohao Wu, Xiaoshi Wu, Zhenhua Wu, Da Xie, Yingtong Xiong, Yulong Xu, Sile Yang, Zikang Yang, Weicai Ye, Ziyang Yuan, Shenglong Zhang, Shuaiyu Zhang, Yuanxing Zhang, Yufan Zhang, Wenzheng Zhao, Ruiliang Zhou, Yan Zhou, Guosheng Zhu, and Yongjie Zhu. Kling-omni technical report, 2025. 7 

- [44] Chris van der Lee, Albert Gatt, Emiel van Miltenburg, Sander Wubben, and Emiel Krahmer. Best practices for the human evaluation of automatically generated text. In _Proceedings of the 12th International Conference on Natural Language Generation_ , pages 355–368, Tokyo, Japan, 2019. Association for Computational Linguistics. 3 

- [45] TW {Van der Schaaf} and Lisette Kanse. Error recovery in socio-technical systems. In _7th European Conference on Cognitive Science Approaches to Process Control (CSAPC ’99), Villeneuve d’Asq, France_ , pages 151–156. Presses Universitaires de Valenciennes, 1999. 8 

- [46] Peng Wang, Shuai Bai, Sinan Tan, Shijie Wang, Zhihao Fan, Jinze Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, Yang Fan, Kai Dang, Mengfei Du, Xuancheng Ren, Rui Men, Dayiheng Liu, Chang Zhou, Jingren Zhou, and Junyang Lin. Qwen2-vl: Enhancing vision-language model’s perception of the world at any resolution. _arXiv preprint arXiv:2409.12191_ , 2024. 7 

- [47] Xin Wang, Taein Kwon, Mahdi Rad, Bowen Pan, Ishani Chakraborty, Sean Andrist, D. Bohus, Ashley Feniello, Bugra Tekin, F. Frujeri, Neel Joshi, and Marc Pollefeys. Holoassist: an egocentric human interaction dataset for interactive ai assistants in the real world. _2023 IEEE/CVF International Conference on Computer Vision (ICCV)_ , pages 20213–20224, 2023. 2, 3

<!-- Page 13 -->

# **How to Correctly Make Mistakes: A Framework for Constructing and Benchmarking Mistake Aware Egocentric Procedural Videos** 

Supplementary Material 

## **A. Egocentric Procedural Video Datasets (Context)** 

In this section, we review the main procedural video datasets, both with and without errors. Beyond a highlevel comparison (Table 1), we describe in more detail the datasets that are central to this work: **EgoPER, EgoOops, Assembly101, CaptainCook4D, and EgoExo4D keysteps** . 

Ego-Exo4D keysteps is used as source procedures for PIE-V. EgoPER, EgoOops, Assembly101, and CaptainCook4D serve as real-data references for what mistakes and corrections look like under different annotation schemes. 

Most procedural datasets were created primarily for action recognition, action segmentation, key step (sequence) extraction, object interaction, or pose estimation based on visual data. Consequently, instead of a full description of the steps, the annotations may take the form of action labels. This is typical of early datasets in the assembly domain such as MECCANO [34], Assembly101 [39], ATA [13], and IndustREAL [37]. A shorter description of the procedure step makes it harder to recognize errors based on semantic cues. 

The error annotations are heterogeneous and fragmented. The first group of general error annotations treats mistakes purely at the level of sequence validity, i.e., whether the overall execution follows the canonical procedure, without localizing or typologizing individual erroneous steps. In CSV [33] each video of an experiment is labeled as correct or incorrect with respect to the entire reference protocol. ATA [13] focuses on detecting whether an activity sequence adheres to the expected order, emphasizing structural deviations such as deletions. The second group extends step/action annotations with per-step binary correctness labels. In HoloAssist [47], action segments are labeled as “correct” or “mistake”, and conversational interventions are categorized (e.g., corrections, follow-ups), but the error label itself does not distinguish between procedural and executional issues. Assembly101 [39]-based benchmarks used in Ding et al. [11] attach a binary mistake flag to specific action segments and further distinguish structural errors such as misordering or redundant steps, along with incorrect attachment of parts. Notably, this benchmark also marks accumulating mistakes and corrective steps (detaching incorrectly attached parts) with a special label. 

A smaller number of datasets introduce explicit taxonomies of both structural and execution errors, often tied to a specific domain. EgoPER [21] defines five er- 

ror types assigned at the step level (omission, addition, modification, slip, correction). CaptainCook4D [32] provides a cooking-specific taxonomy (measurement, timing, temperature, technique, missing and misordered steps). EgoOops [17] adopts another multiclass execution-error taxonomy (working with wrong objects, grasping wrong objects, correction, unintended actions, working in the wrong way, and others). CaptainCook4D and EgoOops augment each erroneous segment with a natural-language explanation of the error aligned to the procedural text (EgoOops additionally sometimes captures correction behavior in free-text explanations). 

**Assembly101.** In the Assembly101 annotations, each step is represented by one action class and two object classes that are being manipulated. There are only two actions: _attach_ and _detach_<sup>1</sup> . The full object vocabulary contains 64 parts, and some of them are semantically close (for example, “roller arm”, “crane arm”, and “excavator arm” can all be seen as instances of a more general “arm”). 

The classes only record the action and the objects, so if an object is attached incorrectly (with a wrong orientation), this can be seen only from the error-type label “wrong orientation”. To make the distinction clear at the text level, we converted class labels into full imperative commands using templates, for example, “attach the step to the chassis in the wrong way” versus the correct “attach the step to the chassis”. In the original annotations, there is also no consistency between attaching part X to part Y and attaching part Y to part X. We normalized such steps to a single canonical form. As a result, we obtain a vocabulary of 339 full step descriptions. 

Some toy variants may have only a single assembly in the whole dataset (e.g., c13c for a single correct assembly and b04b for a single erroneous assembly). Since the toy subtypes encoded by the last letter in the toy_id differ only slightly, we merge them into shared type classes. 

Overall, the error annotations in Assembly101 do not fully match our taxonomy, because the original annotations follow the logic of the assembly process rather than the logic of conformity to a reference procedure. For example, from the assembly point of view, detaching an incorrectly attached part can be a correct step, but from the point of view of matching the canonical assembly, no detachment 

> 1In the original annotations there is a third rare verb class, “position”, which appears only together with the object “figurine”. For the sake of simplicity it was merged into “attach”.

<!-- Page 14 -->

Table 1. Egocentric procedural video datasets. **#Steps** refers to the number of distinct action/step classes when reported; otherwise it is left as “–”. For **Step annotations** , _step_ refers to natural step descriptions, while _action label_ refers to verb + object(s) phrases. _Timestamps_ mark either time or frame stamps. 

|Dataset|#Videos|Duration [h]|#Tasks|#Steps|Domains||Step an|notations|Mistakes|Source|
|---|---|---|---|---|---|---|---|---|---|---|
|MECCANO [34]|32|–|1|–|toy assembl|y|action<br>timesta|labels<br>+<br>mps|_×_|controlled lab|
|EPIC-KITCHENS-|_∼_700|100|–|_>_ 90k|cooking, kit|chen ac-|action|labels<br>+|_×_|participant<br>record-|
|100 [8]|||||tivities||timesta|mps||ings|
|50 Salads [27]|50|_∼_6.4|1|17|cooking||action la|bels|_×_|controlled lab|
|EgoProceL [4]|329|62|16|139|various, inc<br>ing, assembl|l. cook-<br>y|steps +|timestamps|_×_|semi-controlled par-<br>ticipant recordings|
|HoloAssist [47]|350|166|20|414|AR-assisted <br>ulations, in<br>sembly|manip-<br>cl.<br>as-|summar<br>tions, st<br>tamps|y, conversa-<br>eps + times-|✓|controlled lab|
|Assembly101 [39]|362|167|101|202|toy assembl|y|action<br>timesta|labels<br>+<br>mps|✓|controlled lab|
|CaptainCook4D [32]|384|94.5|24|352|cooking||steps +|timestamps|✓|participant<br>record-<br>ings|
|EgoOops [17]|50|6.8|5|46|lab-style<br>iments<br>an<br>trolled<br>a<br>tasks|exper-<br>d<br>con-<br>ssembly|step + ti|mestamp|✓|controlled lab|
|Ego-Exo4D|852|30|17|186|various, inc|l. cook-|step + ti|mestamp|✓<sup>_†_</sup>|participant<br>record-|
|(keysteps) [15]|||||ing, repair|||||ings|
|EgoPER [21]|396|28|5|70|cooking||step + ti|mestamp|✓|participant<br>record-<br>ings|
|ATA [13]|141|24.8|3|15|toy assembl|y|action la|bels|✓|controlled lab|
|EPIC-Tent [18]|24|_>_ 5_._4|1|38|assembly||action<br>timesta|labels<br>+<br>mps|✓|participant<br>record-<br>ings|
|CSV [33]|70|11.1|14|106|chemical<br>ments|experi-|action la|bels|✓|controlled lab|
|IndustReal [37]|84|5.8|2|75|toy assembl|y|steps +|timestamps|✓|Industrial-like lab|



_† †_ Only 17 keysteps carry the Mistake label; it replaces the step description, so we use Ego-Exo4D keysteps as a clean source and inject mistakes synthetically. 

should be considered a correct step. Similarly, re-attaching a part after an erroneous detachment may be labeled as a _Correction_ , but with respect to the reference procedure this step is simply correct. 

From the visual point of view, actions in Assembly101 are mirror-like: a detachment is the reverse of an attachment of the same parts. The parts in the dataset are also visually specific: they are sometimes small and visually similar to each other. In addition, the visual referent of the same object can change as the assembly progresses. For example, in assembly c03f, at the step “attach the arm connector to the chassis” the chassis has one appearance, while in the next step, “attach the body to the chassis”, the term “chassis” refers to two already connected parts, the arm connector and the chassis. 

**CaptainCook4D.** A key property of the cooking domain is the need to follow precise quantities to execute a recipe successfully. However, for visual models it is hard to see the difference between, say, “Add 1/3 tsp salt to the pan” (step_id: 178) and “Add 1/2 tsp salt to the pan” (step_id: 146), and even for a human this is often unclear from a single video. The dataset authors also note in Peddi et al. [32] that full recipe understanding is multimodal rather than purely visual. 

Even so, some dataset steps have very similar textual 

descriptions but different step IDs. For example, “Take 1 tomato” (step_id: 149) versus “Take a tomato” (step_id: 247), or “Peel 1 garlic cloves” (step_id: 200) versus “Peel 1 garlic clove” (step_id: 14). Such steps are visually indistinguishable and identical in their semantic representations. For each erroneous step, the modified textual description also provides corrected descriptions. However, this is not consistent. For example, in recording 1_33, the first step “Coat a 6-oz. ramekin cup with cooking spray” is labeled with the preparation error “Coating a large bowl instead of 6-oz ramekin cup”, yet later steps are marked as correct and described as “Microwave the ramekin cup uncovered on high for 30 seconds”, “Stir the ramekin cup” and so on. In the video the same bowl appears in all steps. Such inconsistencies in the step descriptions create discrepancies between the modalities, which are reflected in our Text–Video Grounding Consistency metric. 

Some steps also share almost the same temporal segment, but receive different textual descriptions and different step IDs. For example, in 2_28 the step “Cut 1/8 garlic clove” is annotated from 564.6 to 624.6 and the step “Mince 1/8 garlic clove” – from 582 to 640. These steps are easy to distinguish in text but almost indistinguishable visually, adding further misalignment between the visual and textual modalities. 

Given that each dataset contains less than 400 videos,

<!-- Page 15 -->

these numerous inconsistencies contribute a substantial amount of noise for the models. This motivated us to include it in the list of datasets for annotators’ assessment. 

**EgoPER.** EgoPER [21] is an egocentric cooking dataset built around a small set of recurring recipes (coffee, quesadilla, pinwheels, tea, oatmeal). We stratified 5 videos of each task for our annotators’ assessment. The given dataset annotations include step-level timestamps and one of five labels of the following taxonomy: two structural deviations (step _omission_ and step _addition_ ), two execution-level deviations ( _slip_ and _modification_ ), and _correction_ . A distinctive aspect of EgoPER is that the annotations separate taskrelevant steps from background activity: some segments reflect incidental actions that are not part of the core procedure (e.g., reading a script on a screen), and are marked explicitly as background rather than being forced into the step taxonomy. This design is helpful for studying mistake detection without conflating procedural steps with incidental context. 

**EgoOops.** EgoOops [17] contains 5 tasks with 10 videos per task. While it was designed to include both mistakefree executions and scripted mistake executions, in practice additional small deviations also appear in the “correct” runs (e.g., extra grasping or redundant manipulation), which makes the boundary between benign variation and mistakelike behavior particularly salient (reflected in our Error Validity metric). EgoOops gives a multi-class taxonomy of deviations (including corrections) and aligns each execution to a canonical script. However, for error segments the text often describes the _deviation from the canonical step_ rather than the exact action the person performed. For example, instead of restating the full step description, the annotation may specify what was wrong relative to the canonical step with a description such as “correct errors in steps 1 and 2”. This complicates purely text-based assessment: recovering the implied correct step may require broader context and/or video grounding. Additionally, some steps are semantically dense and contain multiple predicates (e.g., “pour ... then dip ... and squeeze ...”), which increases the structural complexity of the instruction. 

**Ego-Exo4D keysteps.** Ego-Exo4D [15] is a large-scale egocentric/exocentric dataset with multiple benchmarks. For PIE-V, we specifically take the split of the keystep annotations because they provide (i) step timestamps and (ii) natural-language step descriptions suitable as inputs for controlled textual rewriting. 

A practical property of the keystep annotations is that step structure can be hierarchical: a step may be a leaf or a parent over finer-grained children, and some steps are explicitly marked as non-essential (i.e., present in the video 

but not required for the canonical goal). In PIE-V we use all available steps when constructing clean source procedures, because this reduces the risk of deleting or transposing critical actions when injecting errors, and it preserves a faithful “what happened” trace. We leave for future work a more aggressive setting that injects mistakes only into essential keysteps. 

## **B. Details on Annotators and Annotations** 

**Annotator pool and diversity of judgments.** We use five annotators (2 male, 3 female; age 20–47) with heterogeneous backgrounds (engineering and humanities) and educational levels ranging from high school to graduate training (including two Master’s degrees and one PhD). This diversity was intentional: most rubric dimensions are designed to capture _human perception_ of mistake realism and coherence rather than a single objective ground truth. In particular, Human Plausibility, Confusability, and Video Plausibility are subjective judgments by design, while Error Validity and Taxonomy Fit are expected to be more stable across annotators. 

**Annotation workflow and interface.** Annotators evaluated samples in a paired setting with a reference (mistakefree) execution and a mistake-aware execution shown side by side. Mistake and correction steps were explicitly highlighted in the evaluated trace; the task was to _rate the indicated deviations and recoveries_ , not to discover them. The annotation interface (implemented in structured Google Sheets templates) provided metric-specific inline guidance and drop-down fields for each rating (Fig. 1). Reference and erroneous procedures were aligned stepwise to support direct comparison. 

**Metric design philosophy.** With the exception of Taxonomy Fit (error category assignment), the rubric metrics were designed to capture different aspects of perceived error naturalness and procedural coherence. Error Validity serves as a gate-like metric that distinguishes consequential procedural mistakes from non-consequential deviations; disagreement on this binary judgment captures boundary cases. The remaining metrics decompose human judgments into plausibility (text/video), noticeability (Confusability), sequence-level coherence, and world-state consistency, rather than collapsing them into a single score. 

**Annotator instructions and scale interpretation.** Each metric was presented with a short operational definition and anchored response options. For example, Human Plausibility was defined as whether the described deviation looks like a mistake a real person could make in the given context, while Confusability measured how easy it would be

<!-- Page 16 -->

Table 2. Audit sampling summary for the four existing mistake-aware datasets (25 videos each). 

|Dataset|Videos|Total steps|Mistake steps|Mistake rate|Avg. steps/video|Avg. mistakes/video|
|---|---|---|---|---|---|---|
|EgoPER|25|358|134|37.43%|14.32|5.36|
|EgoOops|25|302|87|28.81%|12.08|3.48|
|Assembly101|25|409|166|40.59%|16.36|6.64|
|CaptainCook4D|25|370|192|51.89%|14.80|7.68|




![](assets/049/paper-0016-02.png)


Figure 1. Annotation interface used for the rubric (example from the electronics task in EgoOops). Annotators are shown a **reference** mistake-free execution (with video) alongside a **mistake-aware** execution containing **mistakes and corrections** (highlighted in red). The goal is not to localize errors but to **rate the indicated deviations** on step-level and procedure-level criteria. Each metric includes a short in-UI explanation, and ratings are selected via drop-down menus. 

to overlook the mistake during real-time task execution. Procedure Logic was collected as a binary judgment (does the mistake make the textual procedure logically inconsistent as a whole) together with a 3-level confidence rating, which is later combined into a confidence-weighted aggregate score. Sequence Consistency and Text–Video Grounding were rated on 5-point Likert scales. State-Change Coherence was annotated as a binary judgment on whether the text implies any clear inconsistency in object identity, availability, or state transitions. 

onomy Fit, indicating that annotators largely agree on what counts as a procedural error and how to assign taxonomy labels. Lower agreement on Human Plausibility and Confusability reflects genuine variation in human judgments about realism and noticeability, which is an intended property of these metrics rather than a failure of the annotation protocol. 

## **C. Details on the Method** 

### **C.1. Phase Modeling and Phase-Conditioned Priors** 

**Pilot calibration and agreement monitoring.** We did not expect uniformly high agreement across all metrics, because several dimensions are intentionally subjective. Instead, we used Krippendorff’s _α_ as a monitoring signal and iteratively refined annotation guidelines after a pilot round, especially for metrics that produced strong outliers or systematic disagreements. This calibration focused on clarifying metric wording and decision boundaries (e.g., procedural error vs. harmless variation; Substitution vs. Wrong Execution), not on forcing consensus. 

**Agreement summary.** Inter-annotator agreement for all datasets and generation settings is reported in Table 3. Agreement is generally highest for Error Validity and Tax- 

PIE-V uses a three-phase abstraction to model _when_ errors are likely to occur and _which_ error types are more likely in different parts of a procedure. The phase design follows cognitive error accounts that relate error profiles to planning demands, attentional load, routine execution, and postcompletion vulnerability [6, 7, 19, 29, 30, 35]. 

We model three coarse phases: **Phase 1 (initiation)** , where plan construction and low familiarity increase attention demand; **Phase 2 (routine execution)** , where automaticity rises but cognitive load and monotony can produce slips and sequencing failures; and **Phase 3 (completion)** , where attention often drops and omissions become more likely due to post-completion effects.

<!-- Page 17 -->

Table 3. Krippendorff’s _α_ agreement summary for all settings. “–” indicates values are unavailable (due to nonexistent videos). 

|Dataset|Err.Valid|Human Pl.|Confus.|Proc.Logic|Seq.Cons.|State-Chg|Taxonomy Fit|Vid.Pl.|T–V Gr.|
|---|---|---|---|---|---|---|---|---|---|
|EgoPER|0.912|0.541|0.368|0.728|0.628|0.579|0.759|0.574|0.662|
|EgoOops|0.916|0.592|0.375|0.836|0.667|0.600|0.882|0.579|0.560|
|Assembly101|0.859|0.584|0.697|0.739|0.649|1.000|0.931|0.670|0.861|
|CaptainCook4D|0.694|0.758|0.847|0.621|0.542|0.584|0.791|0.550|0.488|
|Ego-Exo4D-Qwen (freeform)|0.568|0.539|0.417|0.579|0.543|0.643|0.820|–|–|
|Ego-Exo4D-GPT-5.2 (freeform)|0.701|0.424|0.341|0.593|0.652|0.547|0.752|–|–|
|Ego-Exo4D-Qwen-PJ (PIE-V+Qwen2.5, Qwen3-VL-judged)|0.958|0.483|0.358|0.631|0.706|0.601|0.905|–|–|
|Ego-Exo4D-GPT-5.2-PJ (PIE-V+GPT, judged)|0.913|0.489|0.387|0.672|0.619|0.696|0.803|0.630|0.930|



**Load-based phase boundaries.** PIE-V computes step load with Eq. 2, forms the cumulative load over steps, and assigns PHASE_1, PHASE_2, and PHASE_3 by splitting the cumulative load into three equal parts. 

**Phase error-rate model (where errors occur).** PIE-V separates phase-level risk from error type choice. The phase error-rate model specifies relative rates 


![](assets/049/paper-0017-04.png)


which are then normalized to multipliers with mean 1 before step-index sampling (Eq. 3). In the current implementation, this corresponds approximately to 


![](assets/049/paper-0017-06.png)


Thus, the middle phase is sampled more aggressively for error placement, while total error count remains controlled separately by procedure-level risk and hard caps. 

**Phase-conditioned type priors (which errors occur).** Conditioned on a selected step, PIE-V samples the error type from phase-specific priors over _{_ WE _,_ D _,_ S _,_ I _,_ T _}_ . The implementation uses unnormalized weights (in this order): 


![](assets/049/paper-0017-09.png)



![](assets/049/paper-0017-10.png)


After normalization, the corresponding type probabilities are as shown in Table 4. 

Table 4. Normalized phase-conditioned type priors used in the current PIE-V implementation (before feasibility modifiers). 

|Phase|WE|D|S|I|T|
|---|---|---|---|---|---|
|Phase 1|0.35|0.10|0.25|0.20|0.10|
|Phase 2|0.20|0.20|0.15|0.25|0.20|
|Phase 3|0.35|0.25|0.10|0.20|0.10|



These priors are then modulated by feasibility constraints and step properties (e.g., procedure length, essentiality, transposition feasibility), as described in Sec. 4.1. 

This factorization is intentional: phase priors encode cognitive tendencies, while feasibility modifiers prevent structurally invalid edits. 

### **C.2. Correction Detection and Action Priors** 

PIE-V models correction generation as a two-stage process: (i) whether an error is noticed (detection that correlates with our Confusibility metric), and (ii) whether a corrective action is taken, with what latency and repair type. The base detectability term _b_ ( _τ, ϕ_ ) in Eq. 7 is a hand-specified prior over error type _τ_ and phase bucket _ϕ_ , designed to reflect cognitive regularities of error noticeability and recovery behavior (e.g., salient execution failures are more detectable than subtle deviations; detection probability decreases under high cognitive load) [29, 35, 42]. 

**Base detectability table.** We define _b_ ( _τ, ϕ_ ) for each error type and phase bucket (EARLY, MID, LATE) and then modulate it multiplicatively with severity, essentiality, predicate salience, and load factors as in Eq. 7. These values are implementation priors (not learned parameters) and are fixed across all experiments. 

**Action, latency, and repair type.** Conditioned on detection, PIE-V samples (i) whether the agent acts, (ii) correction latency in steps, and (iii) a correction type compatible with the triggering error (e.g., STOP_AND_FIX, REDO, ROLLBACK_AND_REDO, UNDO_EXTRA_STEP). This separation allows PIE-V to model both noticed-but-unfixed errors and explicit recovery traces. 

### **C.3. Semantic Roles** 

PIE-V uses semantic step representations as a compact structural layer between free-form step text and the error simulator. Each step is represented as a predicate–argument expression of the form PREDICATE(Role: value, Role: value, ...) with nested structures when needed (e.g., locations, purposes, temporal clauses). These representations are used to (i) compute step complexity and phase boundaries, (ii) localize WE and role-level S edits, (iii) estimate role severity via a role-impact map, and (iv) provide predicate-conditioned role priors for selecting which

<!-- Page 18 -->

arguments to mutate. 

**Source of semantic role annotations.** For the benchmark split, semantic representations are precomputed offline for the dataset step vocabulary and cached in a JSON mapping from step id to step_description and semantic_representation. We generate them with GPT-5.2 using a constrained prompt (Listing 1) and a strict JSON schema, in batches of step id _→_ step description pairs, and require exact copying of input ids and step text in the output. The generation utility also normalizes step text and builds a reverse map for robust lookup across formatting variants (e.g., punctuation differences). 

Listing 1. Excerpt of the prompt used to generate semantic representations (SemRep) for step descriptions. 

<mark>You are a linguistic semantic analyzer. For each procedural step description, generate the semantic representation in roles.</mark> 

<mark>Hard constraints:</mark> 

- <mark>Use compact single-line format: PREDICATE(Role: value, Role: value, ...)</mark> 

- <mark>Predicates MUST be UPPERCASE.</mark> 

- <mark>Prefer the role name Object (NOT Theme) for concrete manipulated entities.</mark> 

- <mark>Use Agent: you unless another agent is explicitly stated.</mark> 

- <mark>Prepositional phrases modifying a noun should be nested inside that noun.</mark> 

- <mark>Keep entities as lowercase_with_underscores; nested structures are allowed.</mark> 

<mark>Examples:</mark> 

- <mark>1) Insert the test swab into her nostril INSERT(Agent: you, Object: test_swab, Destination: into(nostril(of(her))))</mark> 

- <mark>2) Add coffee grounds from a bowl to the filter in the French press</mark> 

- <mark>ADD(Agent: you, Object: coffee_grounds, Origin: bowl, Destination: filter(Location: in(french_press)))</mark> 

- <mark>3) Add cut onions to the egg in the mixing bowl ADD(Agent: you, Object: cut(onions), Coobject: egg(Location: in(mixing_bowl)))</mark> 

- <mark>Return only JSON that matches the schema.</mark> 

**SemRep format and parsing.** The semantic representation format is designed for controllable procedural editing rather than full semantic parsing. Predicates are uppercase action labels, and role values are compact entity expressions with optional nesting, as shown in Listing 2 (e.g., nested Origin, Destination, Temporal, Purpose, and Result structures). In the simulator, we use a shallow parser that extracts the main predicate and top-level rolevalue pairs from the representation string. This is sufficient 

for role-targeted mutation, essentiality heuristics, and local ordering guards without introducing a full symbolic world model. 

Listing 2. Representative cached semantic representations (SemRep) used by PIE-V on the Ego-Exo4D split. 

- <mark>{ "1": {</mark> 

   - <mark>"step_description": "Unbox covid test package",</mark> 

   - <mark>"semantic_representation": "UNBOX(Agent: you, Object: covid_test_package)"</mark> 

##### <mark>},</mark> 

- <mark>"11": {</mark> 

- <mark>"step_description": "Extract the test swab from her nostril",</mark> 

- <mark>"semantic_representation": "EXTRACT(Agent: you, Object: test_swab, Origin: from(nostril(of(her))))"</mark> 

##### <mark>},</mark> 

- <mark>"20": {</mark> 

- <mark>"step_description": "Insert the collection swab in its pack for disposal",</mark> 

- <mark>"semantic_representation": "INSERT(Agent: you, Object: collection_swab, Destination: in(pack(of(it))), Purpose: disposal)"</mark> 

##### <mark>},</mark> 

- <mark>"21": {</mark> 

- <mark>"step_description": "Cover the test vial with the lid",</mark> 

- <mark>"semantic_representation": "COVER(Agent: you, Object: test_vial, Instrument: lid)"</mark> 

- <mark>},</mark> 

- <mark>"152": {</mark> 

- <mark>"step_description": "Slowly backpedal the chain while applying the chain lube to each individual roller",</mark> 

- <mark>"semantic_representation":</mark> 

- <mark>"BACKPEDAL(Agent: you, Object: chain, Manner: slowly, Temporal: WHILE(APPLY(Agent: you, Object: chain_lube, Coobject: to(each_individual_roller(of(chain))))))"</mark> 

- <mark>}, "457": {</mark> 

- <mark>"step_description": "Cut the sushi roll into smaller pieces on the cutting board", "semantic_representation": "CUT(Agent: you, Object: sushi_roll, Result: smaller_pieces, Location: on(cutting_board))"</mark> 

- <mark>}</mark> 

- <mark>}</mark> 

**Role impact map (severity prior).** PIE-V uses a roleimpact map _ω_ ( _r_ ) _∈{_ HIGH _,_ MEDIUM _,_ LOW _}_ to control error severity in role-level edits. Impact labels are assigned manually based on linguistic and procedural semantics. Roles that typically determine the manipulated entity or a critical counterpart are treated as high impact, locative and instrumental roles are typically medium impact, and manner or temporal modifiers are typically low impact. Table 5

<!-- Page 19 -->

Table 5. Semantic roles, counts, and impact assignments for the 50-scenario Ego-Exo4D subset used in PIE-V. Counts are given in brackets. 

|Impact|Roles|
|---|---|
|High|Agent (1037), Object (1027), Coobject (51)|
|Medium|Location (288), Destination (281), Origin (259), In-<br>strument (201), Purpose (62), Content (1)|
|Low|Manner (28), Temporal (18), Degree (11), Path (9),<br>Duration (5), Direction (5), Proposition (5), Result<br>(4), Quantity (3), Theme (2), Condition (2), Crite-<br>rion (1)|



summarizes the role inventory, counts, and impact assignments for the 50-scenario Ego-Exo4D subset used in this work. PIE-V uses this role-impact map both for role sampling and for deriving error severity from the set of mutated roles. Agent is excluded from mutation. 

**Predicate-conditioned role priors.** To avoid uniformly random role edits, PIE-V uses predicate-conditioned role priors estimated from the semantic representation corpus. For each predicate, we aggregate the empirical frequency (or share) of roles observed with that predicate across the corpus and use the resulting distribution as Prior( _r |_ pred). At generation time, for a step with predicate pred( _at_ ) and roles present in that step, the role score is proportional to 


![](assets/049/paper-0019-04.png)


where the additive constant provides smoothing for rare but valid roles. Role selection is restricted to roles present in the current step, and Agent is excluded from mutation. PIE-V occasionally may select two roles (instead of one) for compound WE events. 

**Auto-extension for generated steps.** The LLM writer can introduce new step texts that are not present in the original vocabulary. To preserve SemRep-based validation and cascade checks, the writer pipeline supports automatic SemRep extension: unseen generated steps are resolved through a reverse text-to-id map and, if missing, are assigned new cached semantic representations via the same constrained GPT-5.2 SemRep generator. 

### **C.4. Cascade Edits** 

Cascade edits are follow-up text rewrites that preserve procedure feasibility after a planned error changes an object, tool, or local state. They are produced in the LLM writer stage and validated in the LLM judge stage. In the metadata, cascade edits are marked as mod="a" and reuse the same error id eid as the triggering error. This makes the causal dependency explicit: the step is not a new mistake, 

but a downstream repair of textual consistency caused by an earlier mistake realization. 

Cascade edits are necessary because PIE-V generates _coherent traces_ , not isolated error labels. A locally valid error can make later steps impossible if references are left unchanged (e.g., a substituted object is never acquired, or a tool is removed before later use). The writer therefore rewrites downstream steps minimally, preserving the plan while keeping the procedure executable. The judge then checks that these adjustments are present when needed and that they remain linked to the same eid. 

**Example: GET-substitution propagation.** In the EgoExo4D procedure sfu_cooking_005_2, PIE-V realizes a substitution at the early GET step by replacing _“Get cucumber from the refrigerator”_ with _“Get bell pepper from the refrigerator”_ (eid=E01). This change propagates to later steps that originally depend on cucumber. As a result, multiple downstream steps are rewritten as cascade edits (mod="a", same eid=E01), i.e., the trace explicitly replaces cucumber-dependent steps with bell-pepperdependent ones, including “Wash bell pepper with water”, “Chop bell pepper with knife on the chopping board” (twice), and “Add chopped bell pepper into the bowl”. Without these cascade edits, later steps would continue referring to cucumber even though the rewritten trace acquires bell pepper instead. 

**What is and is not a cascade edit.** A cascade edit changes a later original step only as much as needed to restore consistency with an earlier error. It is not a primary error realization (mod="e") and not a correction step (mod="c"). Primary error realizations instantiate the planned mistake, while cascade edits preserve executability and semantic continuity after that mistake. 

**Writer constraints for cascades.** The writer prompt explicitly enforces cascade behavior when an error changes inventory or object identity, including a special rule for GET-like substitutions. A shortened excerpt is shown in Listing 3. 

Listing 3. Writer prompt excerpt enforcing cascade edits after inventory-changing mistakes. 

|If the plan location/w<br>sequence physicall|ording would make the<br>y impossible, you must|
|---|---|
|still realize the|requested error type,|
|but choose the closest|feasible variant near|
|the same location <br>downstream referen<br>adjustments).|(and then repair<br>ces via cascade|
|IMPORTANT SPECIAL CASE<br>propagation|: GET-substitution|

<!-- Page 20 -->

- <mark>If the planned error substitutes a GET-like step (get/take/pick/retrieve) so that you acquire Y instead of X,</mark> 

- <mark>then assume X is NOT available later unless it is explicitly acquired again (do NOT add new insertions unless the plan includes them).</mark> 

- <mark>Therefore, any later steps that refer to X should be cascade-adjusted to refer to Y:</mark> 

- <mark>rewrite those downstream steps and mark them as mod="a" with the SAME eid as the GET-substitution.</mark> 

- <mark>This keeps the procedure executable while preserving the planned mistake.</mark> 

## **D. Details on Experiments and Results D.1. Prompt Logic and Structured Output Contracts** 

We do not reproduce the full LLM prompts here because they are long and implementation-specific. The full writer and judge prompts are available in the released codebase. Here, we summarize the core constraints they enforce and the structured output contracts that are required by the pipeline. 

The writer prompt receives the original procedure, an error and correction plan, semantic representations of original steps, and ordering constraints. Its main objective is to realize the planned mistakes while keeping the rewritten procedure physically feasible and executable. The prompt explicitly requires structured JSON output with a rewritten step list (final_steps) and a timeline mapping (meta) that marks unchanged steps, primary error realizations, cascade edits, insertions, deletions, corrections, and transposition pairs. 

The judge prompt validates plan compliance and procedural coherence and proposes minimal repairs when needed. In particular, it checks that each planned error and correction id is realized, that transpositions are encoded via the required ms/mt pair, and that downstream references are repaired through cascade edits when an earlier error changes object or tool availability. These prompt-level constraints are combined with deterministic checks in the pipeline, so acceptance depends on both LLM reasoning and rule-based validation. Representative prompt fragments for cascade constraints and video style locking are shown in Listings 3 and 5. 

For comparison, Listing 4 shows the freeform baseline prompt used to generate mistake-aware procedures without structured planning. 

Listing 4. Freeform LLM baseline prompt for direct mistakeaware procedure rewriting (without PIE-V planning <u>priors).</u> 

<mark>instructions = (</mark> 

<mark>f"### ROLE: Procedure Editor for '{scenario}'\n"</mark> 

<mark>f"You will receive a step-by-step procedure.\n"</mark> 

<mark>f"Your task is to produce an edited final procedure that contains 1 to 3 plausible human mistakes.\n"</mark> 

<mark>f"You may also add 0 to 2 explicit correction steps.\n\n"</mark> 

- <mark>f"### ERROR TYPES (HIGH-LEVEL)\n"</mark> 

- <mark>f"- wrong_execution (mod='we'): Keep the same general goal, but execute it slightly wrong (wrong amount, messy action, wrong orientation).\n"</mark> 

- <mark>f"- substitution (mod='s'): Replace the step with a different plausible action caused by confusion.\n"</mark> 

- <mark>f" Do not copy a later step verbatim.\n" f"- insertion (mod='i'): Insert one extra plausible step (unnecessary repetition, extra cleaning, checking, etc.).\n"</mark> 

- <mark>f"- deletion: Remove the step completely (do not mention it was skipped). Add it to 'del'.\n"</mark> 

- <mark>f"- transposition: Swap two steps.\n" f" Use mod='ms' for the moved SOURCE step and mod='mt' for the moved TARGET step (both verbatim text, only order changes).\n\n"</mark> 

- <mark>f"### HARD CONSTRAINTS\n" f"1) VERBATIM PRESERVATION: Keep most steps unchanged unless directly edited.\n" f"2) IMPERATIVE STYLE: Use direct imperative commands. No story.\n" f"3) SOURCE INDEX RANGE: Every meta source_idx MUST be a valid original index in [0, {len(steps)-1}]. Never use -1.\n" f"4) PHYSICAL PLAUSIBILITY: Do not use tools/ingredients/objects before they appear earlier in the procedure.\n" f"5) METADATA ALIGNMENT: 'final_steps' and 'meta' must have the exact same length.\n\n" f"6) UNCHANGED MEANS VERBATIM: If mod='u', the final step text MUST match the original step text exactly.\n"</mark> 

- <mark>f"7) TRANSPOSITION RULE: If using transposition, error_id must be non-null and exactly TWO steps must share that error_id:\n"</mark> 

- <mark>f" - one with mod='ms' and one with mod='mt'.\n\n" f"8) NO FAKE ERRORS: If mod in ['we','s'], the text MUST be meaningfully different from the original step at source_idx.\n" f"9) MOVE IS VERBATIM: If mod in ['ms','mt'], the text MUST be identical to the original step at source_idx (only moved).\n"</mark> 

- <mark>f"10) INSERTION IS NEW: If mod='i', the inserted text MUST NOT be identical to the anchor step at source_idx.\n"</mark> 

- <mark>f"11) CORRECTION NEEDS ID: If mod='c', correction_id must be non-null like 'C01' and the text must be new.\n"</mark> 

- <mark>f"12) ERROR IDS: For mod in ['we','s','i','ms','mt'] use error_id like 'E01'. For deletions also.\n"</mark> 

<mark>f"### OUTPUT FORMAT (STRICT JSON ONLY)\n"</mark>

<!-- Page 21 -->

<mark>f"- final_steps: list[str]\n" f"- meta: list[list], one per final step: [source_idx, mod, error_id, correction_id]\n" f" mod_type: 'u'(unchanged), 'we'(wrong_execution), 's'(substitution), 'ms'(moved_source), 'mt'(moved_target), 'c'(correction), 'i'(insertion)\n" f"- del: list[list] for deleted steps: [source_idx, error_id]\n\n" f"For every deletion, error_id must be a string like 'E01' (never null).\n" f"Return ONLY a single JSON object. No markdown. No extra text.\n" f"Do NOT repeat the prompt. Output ONLY JSON.\n" )</mark> 

### **D.2. Annotation Data Processing and Aggregation** 

This subsection describes how raw annotator responses are converted into the aggregate statistics reported in Tables 3 and 5. 

**Metric types.** Our rubric mixes categorical judgments (e.g., Error Validity, Procedure Logic, State-Change Coherence, Taxonomy Fit) and Likert-scale ratings (e.g., Human Plausibility, Confusability, Sequence Consistency, Video Plausibility, Text–Video Grounding). This is intentional, because the rubric is designed to capture both relatively stable categorizations and subjective human judgments about realism and noticeability. 

**Error Validity.** Error Validity is annotated as a binary judgment (Yes/No), namely whether the highlighted deviation is a consequential procedural error under our definition. In the main-paper tables, we report the percentage of “Yes” judgments aggregated at the sample level. Disagreements on this metric therefore reflect ambiguity in the generated behavior (or dataset annotation), not a multi-level scoring scheme. In practice, disagreement on this binary metric often comes from freeform outputs that are lexically marked as “accidental” but have weak procedural consequences. We provide representative examples in Sec. D.4. 

**Procedure Logic with confidence weighting.** Procedure Logic is annotated as a binary judgment together with confidence; aggregation follows the confidence-weighted formulation defined in Eq. 1. 

**Likert-scale aggregation.** For Human Plausibility, Confusability, Sequence Consistency, Video Plausibility, and Text–Video Grounding, we report the arithmetic mean over annotator ratings. 

**Agreement.** We compute Krippendorff’s _α_ separately for each metric and setting. Higher agreement is expected for Error Validity and Taxonomy Fit, while lower agreement on Human Plausibility and Confusability reflects genuine variation in human judgments about naturalness and noticeability. 

### **D.3. Additional Breakdowns for Ego-Exo4D Generations** 

Table 4 reports scale statistics for the four Ego-Exo4D generation settings. Two patterns are consistent across the audited outputs. First, freeform generation under-produces mistakes relative to PIE-V+Judge settings, with fewer mistake steps and a lower average number of mistakes per video. Second, even when freeform outputs are fluent at the sentence level, they more often fail to realize clearly consequential deviations or to preserve long-horizon procedural consistency, which is reflected in the rubric aggregates in Table 3. 

The freeform models also show different error-type biases. For Qwen freeform, the generated distribution is strongly skewed toward deletions (Deletion 31, Substitution 12, Transposition 5, Wrong Execution 5, Insertion 2, Correction 1), and qualitative inspection shows many weak or under-realized edits. For GPT freeform, the distribution is more concentrated on Wrong Execution and Substitution (Wrong Execution 27, Substitution 13, Transposition 8, Insertion 2, Correction 4, Deletion 0), which often produces locally plausible deviations but still under-produces explicit recovery behavior relative to PIE-V. These tendencies motivate the use of explicit planning, cascade edits, and judgeside validation in PIE-V. 

### **D.4. Qualitative Failure Cases of Freeform Baselines** 

**Binary Error Validity disagreement from weakly consequential freeform insertion (indiana_bike_03_1).** A recurring source of disagreement on Error Validity in freeform generations is that the LLM marks an event as accidental without introducing a clearly consequential procedural failure. For example, in a bike-chain cleaning procedure, GPT inserts _“Accidentally knock the chain lube bottle over on the floor while reaching for it”_ between _“Hold the toothbrushes to the chain as you backpedal with your other hand”_ and _“Get the chain lube from the floor”_ . Some annotators judge this as a procedural error, while others judge it as a harmless deviation because the procedure remains executable and the intended outcome is not meaningfully affected. This is precisely the kind of boundary case that Error Validity is designed to expose. 

**Qwen repetition instead of a meaningful substitution (nus_covidtest_15_2).** In a COVID-test procedure,

<!-- Page 22 -->

a planned substitution near the disposal and waiting stage should replace the step _“Arrange test materials in the plastic bag for disposal”_ . Qwen, even with judge, realizes the deviation by duplicating the previous waiting step, producing two consecutive occurrences of _“Wait for a few minutes”_ . This keeps the text locally fluent but weakens procedural specificity and does not create a clear, interpretable mistake mechanism. 

By contrast, GPT produces a more consequential and traceable deviation in the same region, for example _“Dispose the test plate into the plastic bag”_ , followed by a compensating step _“Takes the test plate from the plastic bag to check the test plate for the results”_ . Although still imperfect, this sequence preserves a clearer error and recovery interpretation for benchmarking. 

More broadly, freeform outputs often use lexical markers such as _“Accidentally”_ or _“Stop and ...”_ while describing behavior that is only weakly harmful, visually subtle, or procedurally neutral. This is one reason Error Validity remains an informative metric for freeform baselines: it measures whether the generated deviation is perceived as a consequential procedural error, not whether the text merely sounds like one. 

### **D.5. From LLM Step Text to Video Generation Prompts** 

A practical scalability bottleneck of PIE-V is the conversion of LLM-generated step text into video-generation prompts. Writer and judge outputs are optimized for procedural coherence and annotation traceability, not for direct video synthesis. As a result, many generated step descriptions require manual prompt compilation to make the intended visual event physically explicit and compatible with a specific video model. 

This issue is especially visible in freeform generations. LLMs often produce text that is linguistically marked as an error, for example with words such as _“accidentally”_ , while the described behavior is visually subtle, weakly consequential, or underspecified for video generation. Similarly, correction steps may be described as meta-actions, for example _“Stop and fix...”_ , that require rewriting into concrete visible behavior before synthesis. 

In our workflow, each edited segment is therefore paired with a model-specific prompt that specifies observable actions, object identity, camera constraints, and scene continuity. This prompt compilation step is currently the main scalability bottleneck of the video stage in PIE-V. 

Listing 5. Example style-lock prompt used for egocentric video <u>generation (bike-repair scenario).</u> 

<mark>PROMPT_STYLE_LOCK = ( "Egocentric head-mounted camera, fixed POV, same fisheye lens and same dark circular vignette. "</mark> 

<mark>"Same bike repair workshop, same bike wheel and tools, same hands and body, same lighting. " "No new objects, no swaps, no text overlays, no reframing, no cut." )</mark> 

For Ego-Exo4D edits, a short style-lock prefix is often sufficient to preserve egocentric viewpoint and scene identity across regenerated clips (Listing 5). 

### **D.6. Video Model Constraints and Editing Windows** 

Video generation models differ in conditioning interface and clip-length limits. Some support text-only generation, while others require boundary anchors, for example start and end frames, or support only specific durations. Because of these constraints, long procedural steps cannot always be replaced in a single pass and often require windowing, bridge clips, and stitching. 

In PIE-V, edited windows are selected around the targeted mistake or correction, while unchanged parts of the episode are preserved from the original video. When a fullstep replacement is not feasible, we generate shorter clips and reconnect them with boundary-aware splicing and transition smoothing. This is particularly important for egocentric video, where continuity of hands, tools, and camera viewpoint strongly affects plausibility. 

Different video models also require different conditioning inputs, including text-only mode, boundary-frame mode, and model-specific editing interfaces, which prevents a single universal editing script. We also tested promptbased editing on non-egocentric videos, but support is uneven across models, especially for clips with clearly visible people, which makes the current workflow more reliable on egocentric footage. 

### **D.7. Limitations and Future Directions** 

PIE-V is intended as a controlled framework for constructing and auditing mistake-aware procedural traces, and the current version should be understood as a first step rather than a final fully scaled benchmark. 

**Benchmark scale and coverage.** The current benchmark remains modest in scale: it is built from 50 Ego-Exo4D scenarios and contains 102 injected mistakes and 27 recovery corrections. This is sufficient for an initial controlled study, but it does not yet support strong claims of exhaustive coverage over mistake diversity, recovery patterns, or domain variation. In particular, some error types, correction strategies, and long-horizon dependencies are still underrepresented. Expanding the benchmark with more tasks, multiple variants per scenario, and broader procedural domains is a natural next step.

<!-- Page 23 -->

**Downstream utility is not yet established.** The present paper evaluates PIE-V primarily through human judgment and comparative auditing. While this is appropriate for validating plausibility and coherence, we do not yet show that PIE-V data improves downstream models for mistake detection, correction prediction, or post-completion verification. Demonstrating such gains through controlled training and transfer experiments is an important direction for future work. 

**The video stage is not yet fully automated, but it already changes the cost profile of mistake-aware data construction.** The textual planning and rewriting components are substantially more scalable than the current video-editing stage. In practice, converting rewritten procedural steps into high-quality video-generation prompts still requires modelspecific prompt compilation and manual iteration. This bottleneck is compounded by heterogeneous video-model interfaces, conditioning requirements, and clip-length limits, which prevent a single universal editing pipeline. 

At the same time, PIE-V operates under a fundamentally different data-construction paradigm from existing mistakeaware procedural video datasets, including the ones we audit, which rely on newly recorded human executions of erroneous procedures. Such collection typically requires participant time, repeated performances, annotation effort, and often specialized capture setups. By contrast, PIE-V starts from existing clean procedural videos and edits only targeted segments. In this sense, even in its current partially manual form, PIE-V already offers a practical and resourceefficient alternative to full re-recording, reducing both collection cost and human effort while preserving control and auditability. 

To our knowledge, PIE-V is also among the first mistake-aware procedural benchmark constructions to rely on prompt-based editing of existing video segments rather than new recordings of erroneous executions. We therefore view the current pipeline not only as a benchmarkgeneration method, but also as an early demonstration of a different and potentially much cheaper way to build mistake-aware procedural video resources. 

**Video-side evaluation is necessarily selective.** A limitation of the current study is that Video Plausibility and Text–Video Grounding are not reported for every generation setting. Producing and auditing fully edited videos is substantially more resource-intensive than text-only evaluation, since each setting requires video generation, clip selection, temporal stitching, and additional human assessment of the resulting outputs. For this reason, we adopted a staged evaluation design: generation settings were first compared at the textual/procedural level, and only the strongest configuration was carried forward to the full video stage. We view this as an intentional and pragmatic use of limited computational and annotation resources rather than as an arbitrary omission, because scaling clearly weaker text-generation settings to costly video realization would add substantial expense with limited scientific value. A broader cross-setting video evaluation remains an important direction for future work, but it would require substantially greater compute, annotation time, and human effort. 

**Dependence on source data and external models.** The current benchmark is derived from Ego-Exo4D keysteps and therefore inherits both the strengths and the limitations of that source representation. More broadly, PIE-V also depends on rapidly evolving LLM and video-generation models whose behavior, interfaces, and output quality may change over time. For this reason, the current results should be interpreted as evidence for the usefulness of the PIE-V design principles and evaluation protocol, rather than as a claim that one fixed generated benchmark is final or universal. 

**Generated mistakes remain approximations of human behavior.** Even when errors are psychology-informed, role-constrained, and judged coherent by annotators, generated traces remain approximations rather than direct observations of naturally occurring human mistakes. They may miss social context, tacit goals, embodied variability, and opportunistic recovery strategies that arise in real-world execution. We therefore view PIE-V as complementary to naturally observed mistake datasets rather than a replacement for them. 

We also expect the scalability of this stage to improve as prompt-based and instruction-guided video editing models continue to advance [20, 23, 26]. Recent progress in general video-to-video editing, instruction-based video editing, and emerging egocentric video editing suggests that more automated and temporally consistent editing pipelines may substantially reduce the need for manual prompt engineering. However, adapting such models to controlled procedural mistake construction remains a separate research problem.
