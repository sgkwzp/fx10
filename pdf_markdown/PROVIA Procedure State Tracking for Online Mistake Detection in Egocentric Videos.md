# PROVIA Procedure State Tracking for Online Mistake Detection in Egocentric Videos

[Original PDF](../PROVIA%20Procedure%20State%20Tracking%20for%20Online%20Mistake%20Detection%20in%20Egocentric%20Videos.pdf)

Pages: 9

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

# **PROVIA: Procedure State Tracking for Online Mistake Detection in Egocentric Videos** 

Di Wen<sup>1</sup><sup>_,†_</sup> , Kailun Yang<sup>2</sup> , Jimmy Weissert<sup>1</sup> , Luc Maria Scherrer<sup>1</sup> , Cedric Z¨ollner<sup>1</sup> , Ruiping Liu<sup>1</sup> , Yufan Chen<sup>1</sup> , Jiale Wei<sup>1</sup> , Junwei Zheng<sup>1</sup> , and Kunyu Peng<sup>1</sup><sup>_,∗_</sup> 

**_Abstract_ — An assistant watching egocentric video should notice a mistake from past frames alone, before the next step begins, and keep working once the person recovers. A mistake changes the state of the work, so every later step has to be read against what was done rather than against the plan. The first-mistake protocol that current online methods report on cuts each recording at its first mistake, so a fixedtime rule that never looks at the video is right on every case. We evaluate on complete trials, where mistakes and recoveries arise naturally, under a validation false-alarm budget and against controls that use timing alone. PROVIA keeps two records apart: a factual state, a learned summary of the steps each actor performed, mistakes included, and the accepted progress, an exact posterior over the state of an automaton induced from correct demonstrations by Bayesian state merging and over the execution status of each actor. Procedure-state transitions occur only in the correct-status branch; the mistake and correction branches retain the source state. A sequential test turns the per-frame mistake probability into alarms. With one filter and one optimization rule, PROVIA ranks mistakes best among the evaluated controlled baselines on CaptainCook4D, IndustReal, HoloAssist and IMPACT-ego. At a validation budget of 0.1 false alarms per minute it recalls .154 against .128 on CaptainCook4D and .034 against .015 on HoloAssist, where it leads at every budget. The pipeline runs at 58–70 frames per second. The source code is available at https://github.com/Kratos-Wen/PROVIA.** 

## I. INTRODUCTION 

A mistake in a procedure has no single form. What counts as one depends on the domain: a dish is spoiled by the wrong ingredient or the wrong order, an assembly by a part seated the wrong way or a tool used on the wrong fastener. It depends on scale, since some actions unfold slowly enough to be watched and others are over almost as soon as they begin. And it depends on who is acting, because a procedure carried out by two hands gives each of them a different role, and the progress of the work depends on the actions of both. 

Seen from a running egocentric camera, the problem is harder still. The observer holds a growing prefix. It does not know where the current step began, cannot look ahead, and cannot select a threshold on the recordings it will be judged on. Two properties of procedures shape the problem. Independent steps commute, so what is correct after a prefix is a set of continuations rather than one next step. And a mistake changes the state of the work, so every later step 

> 1The authors are with the Karlsruhe Institute of Technology, Karlsruhe 76131, Germany. 

> 2The author is with Hunan University, Changsha 410012, China. 

> _†_ First author (email: di.wen@kit.edu). _∗_ Corresponding author (email: kunyu.peng@kit.edu). 

must be read against what was actually done rather than against the plan. The person does not stop at the mistake; they may repair it, and they may err again. An alarm triggers an intervention: a spoken correction, a highlighted part, or a robot that holds back the next part. Each false alarm interrupts the person, so an assistant runs at a false-alarm budget, and an alarm is most useful before the next step begins. 

Evaluation has not kept pace with either difficulty. The protocol that current online methods report on [1], [2] places the mistake at one designated moment, the first, cuts the recording there, and asks which of the method’s own segments was last. A procedure that emits two events at fixed times, without reading a frame, is scored as perfectly correct on both of its benchmarks, and most of the test participants are also seen in training. We evaluate instead on complete trials as they were performed, where mistakes and the repairs that follow them occur where the person made them, under a stated budget of false alarms, against controls that see only elapsed time, and with every threshold fixed on validation. 

PROVIA treats the question as inference about the state of the procedure while the video streams in, and it keeps apart the two things a mistake separates: what the person did and how far the procedure has correctly advanced. A factual state, updated after every completed step, remembers what each actor was observed to do, mistakes and corrections included. An exact posterior over the state of a procedure automaton and over the execution status of each actor’s current step, correct, mistake, or correction, holds the progress that was accepted. The automaton is induced from correct demonstrations by Bayesian state merging. Procedure-state transitions occur only in the correct-status branch, while the mistake and correction branches retain the source state, so the next step is read against what was performed rather than against progress the mistake did not make. One execution status is carried per actor, so a task described for the performer as a whole and a bimanual task described per hand are read by the same model. A sequential test turns the per-frame mistake probability into alarms at a stated false-alarm budget. Our contributions are: 

- an account of why the protocol current online methods report on admits a perception-free solution with perfect F1, and an evaluation of mistake detection on complete trials, under a stated false-alarm budget and against controls that use no perception; 

- an online model that keeps the execution as performed apart from the progress it accepts: a factual state of

<!-- Page 2 -->

the steps each actor performed, and an exact posterior over procedure state and per-actor execution status on an automaton induced from correct demonstrations by Bayesian state merging; 

- the highest step-level average precision (AP) and area under the ROC curve (AUROC) among controlled online baselines on four benchmarks that differ in domain, in granularity and in how many hands are described, with one filter and one optimization rule, and ablations showing that removing the record of what was performed at inference costs accuracy on all three singleactor benchmarks. 

## II. RELATED WORK 

_a) Benchmarks for procedural mistakes.:_ Assembly101 made multi-step procedures observable at scale and recorded corrections beside mistakes [3], and per-step correct, mistake and correction labels followed [4]. Later benchmarks widened the definition: deliberate and natural cooking errors [5], execution errors in industrial-like assembly [6], incorrect actions in real-world tasks [7], typed errors in cooking [8], and a six-category anomaly taxonomy for bimanual industrial work in which each hand is annotated separately [9], [10]. 

_b) Offline and online mistake detection.:_ Offline methods read a segment whose boundaries are given or a recording that has ended: learned prototypes per step [8], actionaware reconstruction [11], the visual effect an action should leave [12], task graphs the step is checked against [13], [14], and zero-shot vision–language models [15]. Online methods read a growing prefix: PREGO and TI-PREGO segment the stream and compare the recognized step with one a language model anticipates [1], [16], differentiable task graphs anticipate with a learned prior [2], MistSense scores a causal window with hand pose [17], STORM-PSR recognizes completed steps under occlusion [18], and MistExit, given a step, learns when it has seen enough of it [19]. In PREGO and DTGL the recognized steps, mistakes included, become the history that the next prediction conditions on, and in the prototype, effect and task-graph methods the reference is fixed, so a mistake leaves no trace in it. This work keeps what was performed apart from what was accepted and scores complete trials at a stated false-alarm rate. 

_c) Procedural assistance.:_ An assistant needs the step in progress, whether it was done correctly, and what may follow [7], [6], resting on recognition that stays reliable outside the training vocabulary [20]. GuideMe [21] and PlanWatch-Recover [22] pass a running recording to a language model that decides when to speak, but neither states a rate at which speaking is wrong. PROVIA keeps the procedure itself as the latent variable, induced from demonstrations by Bayesian state merging [23], and reports detection at a stated false-alarm rate. 

## III. EVALUATING ONLINE MISTAKE DETECTION 

**The first-mistake protocol.** PREGO and DTGL evaluate on Assembly101-O and EPIC-Tent-O [1], [2]: each test video 

is cut at its first mistake, the method segments it, the _last predicted segment_ is labeled as the mistake, and the F1 of the correct and mistake classes over predicted segments is averaged. Four measurements show what it rewards. _(i)_ Nothing after the first mistake is tested, although 73% of the 707 mistakes in the full Assembly101 annotations [4] follow an earlier one. _(ii)_ The method chooses the unit and the label goes to the last one: two fixed-time events per execution, the second labeled a mistake, give average F1 1.000 on both benchmarks with no perception, where DTGL reports .54 and .47 [2]. _(iii)_ The label is a position prior: length and step-count priors trained on correct executions only reach average F1 .50 on Assembly101-O and .52 on EPIC-Tent-O, above the .33 and .29 reported for PREGO and at the level of DTGL’s .54 and .47 [2], and the normalized position of an event alone separates the terminal event with AUROC .971 on EPIC-Tent-O. _(iv)_ The split is not participant-disjoint: 35 of 47 Assembly101-O test participants also appear in training. The metric reimplementation was checked against the released DTGL evaluator [2]; the evaluation below removes the first three on every benchmark and the fourth where participants are identified. 

**Alarm-level protocol.** A recording is scored whole, correct executions included. A method reads frames as they arrive and may raise an alarm at each of its decisions, here the completions of the shared step segmentation (Sec. IV-B); it is told the task and nothing else about the recording. Every annotated step owns its completion cell, the times closer to its annotated completion than to any other. An alarm credits a mistake when it is raised at a decision of the method inside that mistake’s cell or at the next decision after the last of them; each mistake is credited once, and one alarm may credit two consecutive mistakes. An alarm inside the cell of a correct step is false even when it also credits the mistake before it, and a mistake whose cell holds no decision counts against recall. False alarms are counted per minute of correct operation, the recording time outside mistake steps. Every method’s per-segment score passes through the same sequential rule (Sec. IV-E), with the training-fold mistake prevalence in place of _γi_ where a method has no prior of its own. For budgets of 0.1, 0.5 and 1 false alarm per minute, each method, seed and budget receives the threshold of highest validation recall among those whose validation rate meets the budget, at which the test recordings are scored. We report the recall of all mistakes and the recall of the decoded mistakes that follow another decoded mistake of the same execution. Three controls pass through the same rule without looking at the video: they score a decision by its index, by the time elapsed, or by how often a training step at that index was a mistake. A method is credited with detection only where it exceeds every control on the benchmark. **Step-level metrics.** AP and AUROC are computed over the annotated step segments. Each segment takes the highest mistake score reached, over the causal prefixes, by any predicted segment whose completion falls in its cell; a segment the model never decoded scores zero. Segments shorter than 0.5 s are not scored.

<!-- Page 3 -->

## IV. METHOD 

One filtering formulation handles one or more actors (Fig. 1). 

## _A. Problem Formulation_ 

Let _x_ 1: _T_ be a query video and let _D_<sup>ref</sup> be the set of correct executions of the same task in the training partition; a task without a complete correct recording falls back on the deterministic medoid of its decoded step sequences, without labels. At query time the model receives only _x≤t_ and the task of the recording, which selects _D_<sup>ref</sup> : no query step boundary, step label, correctness label, or future frame. 

A procedure is carried out by _K_ actors: _K_ = 1 when its steps describe the person as a whole, _K_ = 2 when each hand carries a distinct part of the work. Each actor _k_ carries a descriptor _vt_<sup>(</sup><sup>_k_)</sup> per frame. From _v≤_<sup>(</sup><sup>_k_</sup> _t_<sup>)thesegmentation</sup> model produces, at every frame, soft step factors **_π_** _t_ = _{_ **_π_**<sup>verb</sup> _t ,_ **_π_**<sup>noun</sup> _t ,_ **_π_**<sup>tool</sup> _t }_ and a completion hazard _ht_ , and it partitions the actor’s observations exhaustively into predicted step segments: a segment closes at the model’s decision and the next opens at once, so every actor always carries an open step. Segments are indexed _i_ = 1 _, . . . , I_ in the order of their completions across all actors, an open segment receiving its index at completion; _ki_ denotes the actor of segment _i_ , and _bi_ and _ei_ its predicted start and completion. For a segment observed up to time _t_ , the filter returns _p_<sup>M</sup> _i,t_<sup>=</sup><sup>_p_(</sup><sup>_mi_=M</sup><sup>_|_</sup> _x≤t, D_<sup>ref</sup> ), where _mi ∈M_ = _{_ C _,_ M _,_ Cr _}_ is the execution status of the segment: correct, mistake, or correction. Where the segmentation model can propose a segment that belongs to no step of the procedure, _M_ carries a fourth status, insertion (Ins). The reported output is _ai,t_ = _ci,t p_<sup>M</sup> _i,t_<sup>,where</sup> the completion gate _ci,t ∈_ [0 _,_ 1] is the mass of the segment’s status that has been decided by frame _t_ (Sec. IV-E). 

## _B. Online Step Segmentation_ 

For every actor the segmentation model is the same causal marked point process with shared parameters: its event types follow the annotation and its marks are the step labels. A causal network reads the descriptor stream and outputs, at every frame, an intensity _λt_ per event type (softplus, offset by the fold base rate) and the step factors **_π_** _t_ through one head per factor, giving the hazard _ht_ = 1 _− e_<sup>_−λtδ_</sup> for the frame interval _δ_ . Training minimizes the point-process negative loglikelihood of the annotated event times, piecewise constant over frames, plus the step-label negative log-likelihood corrected by the Jeffreys class prior of the fold; mistake labels are not used, and the event and mark branches are selected separately by their validation likelihood. Decoding is the causal posterior median of the next event time: an event is decoded at the first frame at which the survival<sup>�</sup> _ν_<sup>(1</sup><sup>_−hν_)</sup> accumulated since the preceding decoded event falls to one half, with no score, duration, gap, or suppression threshold, and the same rule forms segments from events under either annotation. When steps are annotated as intervals of the performer there is one event type, step completion, and every decoded event closes the open segment and opens the next. When they are annotated per hand, the events are the phase 

changes of that hand among idle, approach and interaction, with one intensity per change as competing risks; a hand’s segment opens when it leaves idle or renews directly out of an interaction, its mark is fixed at the interaction onset, and it closes when the hand leaves the interaction. 

## _C. Procedure Automaton Induction_ 

Because correct executions differ in local order and one path per execution memorizes the training set, we induce a probabilistic finite automaton from the decoded demonstrations _D_<sup>ref</sup> . Each demonstration is decoded on all _K_ of its actors, and the decoded steps are interleaved by completion time into one sequence of actor-tagged steps ( _k, u_ ); the automaton is the prefix tree of these sequences, keeping every observed branch and revisit. With _K_ = 2 the order of the two hands’ steps is part of the language. 

The tree is then reduced by Bayesian state merging [23]: two histories share a state when they predict the same continuation law. For a state _s_ , let **n** _s_ count termination and the next step label, with _Ns_ =<sup>�</sup> _u_<sup>_ns,u_.Itsintegrated</sup> evidence _E_ ( **n** _s_ ) is the product of a Jeffreys Beta–Bernoulli evidence for termination and a Jeffreys–Dirichlet evidence for the next step label. Two incomparable states _s_ 1 and _s_ 2 are pooled iff 


![](assets/065/paper-0003-11.png)


Equal prior odds decide whether one shared next-step law is better supported than two, without a similarity threshold, state count, or edit cost. Merging is greedy over pairs that share an observed next step, largest ∆ first with rescoring, until no pair has ∆ _>_ 0; ties break by state index, and ancestor and descendant states are never merged, so repeats and order-flexible behavior stay representable. 

The resulting automaton _G_ = ( _S, U, ρG_ ) consists of procedure states _s ∈S_ , admissible next steps _u ∈U_ ( _s_ ), and a posterior-predictive joint law _ρG_ ( _u, s_<sup>_′_</sup> _| s_ ). A continuation absent from the _n_<sup>ref</sup> correct executions keeps the Jeffreys posterior-predictive probability _ε_ = <u>12</u><sup>_/_(</sup><sup>_n_ref+1).</sup> The demonstrations also say what each step changes. Let **o** _i_ = _ve_<sup>(</sup><sup>_k_</sup> _i_<sup>_i_)</sup> _−vb_<sup>(</sup><sup>_k_</sup> _i_<sup>_i_)</sup> be the change of the actor’s descriptor over segment _i_ , standardized on the demonstrations. A diagonal Gaussian random-effects model, with within- and betweenstep variances estimated by moments, gives step _u_ a posterior mean **_µ_** _u_ shrunk toward the task mean and a predictive variance **Σ** _u_ , and the step effect of segment _i_ is 


![](assets/065/paper-0003-14.png)


with log densities averaged over coordinates, _ωu_ the Jeffreys frequency of _u_ among the demonstrated steps, and _βi_ ( _u_ ) = 0 before completion. The automaton and the step effects use no annotated boundary or label and no validation or test video.

> Original page for checking 2 unresolved font glyphs.

![Original page 3](assets/065/verify-page-003.png)

<!-- Page 4 -->

![](assets/065/paper-0004-00.png)


Fig. 1. PROVIA tracks a procedure carried out by _K_ actors. Left: correct executions are decoded into actor-tagged step sequences and merged into one automaton by Bayesian state merging; on the query stream, the factual state records the steps each actor performed and an exact filter over procedure state and per-actor execution status, _Bi_ ( _s,_ **m** ), records the progress accepted. Right: the segmentation module, shared across actors. 

_D. Bayesian Filtering over Procedure State_ 

Segment _i_ owns a bounded recurrent state, and the factual state is updated when the segment completes: 


![](assets/065/paper-0004-04.png)


where LN is layer normalization, GRU a gated recurrent unit, _ϕ_ c a causal window encoder trained with the classifier, _ψ_ a map of the hazard, _Ef_ the embedding of step factor _f_ , _W_ a linear map, and _gi,t_ runs over the frames of segment _i_ only. _Hi_ is updated after every segment, whatever its execution status, so it records what was observed. Each actor owns a factual state; the query of a segment on actor _k_ adds the factual state of _k_ , a linear map of those of the other actors, and an actor embedding, which with _K_ = 1 reduces to _Hi−_ 1. 

Given a procedure state _s_ , the classifier produces a status energy for each _m ∈M_ from a key **k** _s_ that embeds three automaton statistics of _s_ (successor support, termination probability, continuation entropy), and the observation potential of the segment under state _s_ and status _m_ is the log-softmax 


![](assets/065/paper-0004-07.png)


with a bias _bm_ and a projection _Wm_ per status and _d_ the state dimension. 

Let **m** = ( _m_<sup>(1)</sup> _, . . . , m_<sup>(</sup><sup>_K_)</sup> ) _∈M_<sup>_K_</sup> collect the execution status of the current segment of every actor, and let _Bi−_ 1( _s,_ **m** ) be the posterior over procedure state and 

status vector at the boundary of segment _i_ . _Hi_ records what was observed; _Bi_ records which progress was accepted. Under the mistake and correction branches _B_ keeps its state while _H_ carries the segment, so the next segment, and a correction in particular, is read against what was performed and not against a state the mistake would have created. The automaton defines the reference transition 


![](assets/065/paper-0004-11.png)


where _pG_ ( **_π_** _i,t | u_ ) =<sup>�</sup> _f_<sup>_|Yf| ⟨_</sup><sup>**_π_**</sup> _i,t_<sup>_f,_</sup><sup>**_α_**</sup> _u_<sup>_f⟩_isthelikelihood</sup> ratio of the observed step factors under the label law **_α_**<sup>_f_</sup> _u_ of step _u_ against a uniform law over the labels _Yf_ ; it equals one when the segmentation model is uninformative. A step the segmentation model misses, independently with the training-fold miss rate _κ <_ 1, is absorbed by the closure Γ = ( _I − κρ_ ¯ _G_ )<sup>_−_1</sup> diag( **1** _− κρ_ ¯ _G_ **1** ), whose rows sum to one, where _ρ_ ¯ _G_ ( _s_<sup>_′_</sup> _| s_ ) =<sup>�</sup> _u_<sup>_ρG_(</sup><sup>_u, s′|s_);acontinuationabsent</sup> from the demonstrations enters with probability _ε_ and leaves the state unchanged. The correct-status operator is 


![](assets/065/paper-0004-13.png)


Mistake, correction and insertion explain the observation without advancing the procedure state: Λ<sup>_m_</sup> _i,t_<sup>(</sup><sup>_s, s′_)=</sup><sup>**1**[</sup><sup>_s′_=</sup> _s_ ] exp _ℓ_<sup>_m_</sup> _θ,i,t_<sup>(</sup><sup>_s_)for</sup><sup>_m̸_=C.Atthepredictedcompletionof</sup>

> Original page for checking 2 unresolved font glyphs.

![Original page 4](assets/065/verify-page-004.png)

<!-- Page 5 -->

segment _i_ on actor _k_ = _ki_ , the exact filtering update acts on the procedure state and on the status coordinate of that actor alone, 


![](assets/065/paper-0005-01.png)



![](assets/065/paper-0005-02.png)


and _Bi ∝ B_<sup>�</sup> _i_ , where **m**<sup>_′_</sup> [ _k←m_ ]<sup>replacesthe</sup><sup>_k_-thcoordinate</sup> of **m**<sup>_′_</sup> by _m_ , the admissible steps in Λ are those tagged with actor _k_ , and _P_ tr and the initial status law are the Jeffreys posterior-predictive estimates (counts plus one half) from the status sequences of the training fold. With _K_ = 2 the recursion runs for whichever hand completes; when both complete on the same frame the two orders of application are averaged. With _K_ = 1, Eq. (7) is applied once, at _ei_ ; before _ei_ the segment likelihood changes the reported posterior but not the procedure state. With _K_ = 2 the belief also carries, for each open segment, the status mass that the clock of Sec. IV-E has not yet decided: the fraction decided at a frame passes through Eq. (7) with the evidence of that frame, so a fraction decided as correct advances the procedure state at its decision frame, every decided branch keeps receiving the later evidence of the segment, and at _ei_ the remaining mass is decided and the branches are merged into _Bi_ . In both cases each unit of status mass passes through the update once, and the procedure state advances only along the correct-status branch. 

## _E. Sequential Detection Rule_ 

The status of an open segment starts unresolved, and a clock moves its mass to decided frame by frame; the completion gate _ci,t_ is the decided mass, and at the predicted completion the remaining unresolved mass is decided, so _ci,ei_ = 1 under either annotation. When steps describe the performer, the clock is the completion posterior induced by the hazard, _ci,t_ = 1 _−_<sup>�</sup><sup>_t_</sup> _ν_ = _bi_<sup>(1</sup><sup>_−hi,ν_).Whenthey</sup> describe a hand, the segmentation model supplies the causal posterior that the hand’s interaction has begun, which fixes the segment’s identity, and the clock is a two-state head on _qi,t_ , learned with the observation model, whose input includes that posterior. The mistake probability reported at frame _t_ is _ai,t_ = _ci,t p_ ( _mi_ = M _| x≤t, Bi−_ 1): it rises with the evidence that the step is complete and with the evidence that it was wrong. No latency loss or time threshold enters it. 

Let _γi_ =<sup>�</sup> _s,_ **m**<sup>_Bi−_1(</sup><sup>_s,_</sup><sup>**m**)</sup><sup>_P_tr(M</sup><sup>_|m_(</sup><sup>_ki_))betheproba-</sup> bility that the filter assigns to a mistake in segment _i_ before the segment is observed, and _ai_ = _p_ ( _mi_ = M _| x≤ei, Bi−_ 1) the posterior at its completion. The ratio of the posterior odds to the prior odds 


![](assets/065/paper-0005-07.png)


is the evidence score of segment _i_ ; the division normalizes the score by the status prior that _P_ tr has already propagated. The Shiryaev–Roberts statistic [24], [25] _Si_ = (1+ _Si−_ 1) _ξi_ , 

_S_ 0 = 0, accumulates these scores and equals<sup>�</sup> _r≤i_ � _ij_ = _r_<sup>_ξj_,</sup> the sum over onsets _r_ of the products of the scores from _r_ to _i_ . An alarm is raised when _Si ≥ τ_ and resets _S_ only; the filter and the factual state are unchanged. The threshold _τ_ is set for a stated false-alarm budget (Sec. III). 

## _F. Learning Objective_ 

The segmentation model is trained first and frozen, the automaton and the step effects are extracted from its decodes by Eqs. (1)–(2), and the observation model is optimized on the frozen segments, so mistake supervision can neither move segment boundaries nor rewrite the automaton. Each predicted segment inherits the status of the annotated step it is matched to. With _K_ = 1, the predicted segment nearest to an annotated completion inside its completion cell inherits that step’s status, one-to-one, and the other segments are correct context. With _K_ = 2, the segments of each hand are matched to that hand’s annotated steps by a maximumcardinality monotone matching of overlapping intervals, and an unmatched segment is an insertion. 

Let _pi,m_ be the end-of-segment posterior for execution status _m_ , � _ωm_ = ( _nm_ +<sup><u>1</u></sup> 2<sup>)</sup><sup>_/_(�</sup> _m_<sup>_′ nm′_+</sup><sup>_<u>|M</u>_</sup> 2<sup>_<u>|</u>_) the fold-training</sup> Jeffreys status law, and _wm ∝ ω_ � _m_<sup>_−_1itsinverse-priorweight.</sup> We use the prior-preserving case-control log score 


![](assets/065/paper-0005-13.png)


With _K_ = 2 the same score trains the clock: the end-ofsegment posterior is a mixture over the frames at which the clock decided the status mass (Sec. IV-D), and _L_ reaches the clock through this mixture; no separate loss or latency term is used. When a benchmark does not annotate corrections, the likelihood marginalizes C and Cr, so a correction is never relabeled as a mistake. 


![](assets/065/paper-0005-15.png)


## _A. Setup_ 

_a) Datasets.:_ We use four public egocentric benchmarks with complementary kinds of mistakes: CaptainCook4D [5], IndustReal [6], HoloAssist [7], and the egocentric view of IMPACT v1.1 [9]. CaptainCook4D and IndustReal use their official participant-disjoint splits; for HoloAssist, whose test labels are not released, a video-groupdisjoint validation subset is carved from the official training partition and the official validation partition is the outer test (1,204/262/207 recordings); IMPACT’s official splits are not participant-disjoint, so we use a deterministic participantdisjoint fold (57/15/21 executions from 8/2/3 participants). The outer test sets contain 442/1,391, 17/194, 931/17,705, and 177/1,760 mistakes/step segments (prevalence .318, .088, .053, .101). Every method is trained with three seeds, and results are means over them. 

_b) Shared feature streams.:_ Each benchmark has one feature setting shared by every method. On the three singleactor benchmarks it is the frozen DINOv2 ViT-S/14 encoder [26] on 224 _×_ 224 RGB frames, sampled at 8 Hz. On IMPACT-ego it is an in-domain hand-object stream per

> Original page for checking 8 unresolved font glyphs.

![Original page 5](assets/065/verify-page-005.png)

<!-- Page 6 -->

TABLE I 

CLASSES ARE COUNTED OVER THE WHOLE CORPUS, GRANULARITY IS THE MEDIAN INTERVAL BETWEEN THE STEP COMPLETIONS OF ONE ACTOR, STEPS/EXEC IS THE MEDIAN NUMBER OF STEPS PER EXECUTION, AND DEMOS/TASK IS THE MEAN NUMBER OF ERROR-FREE TRAINING EXECUTIONS PER TASK. 

|Benchmark|Domain|h|Steps|Classes|Steps/exec<br>D|emos/task|Granularity<br>_K_|
|---|---|---|---|---|---|---|---|
|CaptainCook4D [5]|cooking|94|5,394|360|14|3.9|43.3 s<br>1|
|IndustReal [6]|assembly|6|501|39|6|12.0|38.3 s<br>1|
|HoloAssist [7]|mixed tasks|122|141,212|2,197|63|10.8|1.9 s<br>1|
|IMPACT-ego [9]|disassembly|6|8,015|134|79|15.0|2.7 s<br>2|



hand, since frozen features leave every controlled system at chance there (AUROC .45–.49): a YOLOv9-c detector (640 px, confidence .25) finds each hand at 15 Hz, a crop enlarged 1.6 times around it is encoded by a DINOv2-S finetuned on training-fold step labels only, and the stream is that descriptor and its rate of change. The segmentation model of Sec. IV-B runs on these streams, so every method receives the same segments, hazard, and step factors. 

## _B. Implementation Details_ 

_a) Segmentation model.:_ On the three single-actor benchmarks ( _K_ = 1) the event is step completion; frame _t_ enters at 8 Hz as [ _vt, vt−_ 1 _, v_ ˙ _t_ ], and each branch is a stack of dilated causal depthwise convolutions (width 192, kernel 3, dilations 1 _, . . . ,_ 2<sup>_L−_1</sup> ), with _L_ the smallest value whose causal support covers the longest gap between consecutive training completions (4.3–17 min); 9.4–11.2M parameters. On IMPACT-ego ( _K_ = 2) the phase changes are fitted with an exact interval-censored likelihood, and the mark is read from the start of the approach to the onset of the interaction. IMPACT annotates no contact onset, so the interaction onset of a training step is taken at the midpoint of its annotated interval; the network is a frame-wise two-layer map (1.5M parameters), unmarked intervals become segments with the prior step distribution, and the insertion status of Sec. IVA is used. The segmentation model is trained with AdamW (weight decay 10<sup>_−_2</sup> , gradient clipping 1.0) and early stopping on the validation likelihood, with the learning rate of each branch selected from _{_ 10<sup>_−_4</sup> _,_ 3 _×_ 10<sup>_−_4</sup> _,_ 10<sup>_−_3</sup> _}_ by the same criterion. 

_b) Filter.:_ The causal window encoder _ϕ_ c of Eq. (3) is a linear map followed by six dilated causal convolutions with a 16 s support, and _ψ_ is a single linear layer. PROVIA uses a 192-dimensional segment and factual state and one optimization rule on all datasets (AdamW, 3 _×_ 10<sup>_−_4</sup> , weight decay 10<sup>_−_2</sup> , at most 80 epochs, early stopping on the validation log score); AP, AUROC, thresholds, and latency never enter checkpoint selection. It has 0.71–0.78M trainable parameters and no per-dataset head, task embedding, or language model. One NVIDIA A100 at batch one takes 13.4– 16.1 ms per RGB frame for encoder and segmentation model, and the exact update adds at most 0.9 ms, so the pipeline runs at 58–70 frames per second. On the same stream the scoring heads of the baselines below add 1.0 ms (Causal-TCN), 1.1– 1.3 ms (MistSense-RGB-style) and 0.6–12.5 ms (Controlled PREGO, whose window is re-read at every frame) per frame. 

_c) Baselines.:_ As released, PREGO queries a language model at every step and MistSense reads hand pose, both were scored on recordings cut at the first mistake, and neither returns a score with a stated false-alarm rate. We therefore compare with three online alternatives that receive the same stream and differ in how they carry the procedure: _Causal-TCN_ , a supervised visual control of six leftpadded temporal blocks; _Controlled PREGO_ , the official MiniROAD [27] recognizer of PREGO [1] with its languagemodel call replaced by a deterministic anticipator learned from correct training prefixes; and _MistSense-RGB-style_ , the RGB Video-Q-Former path of MistSense [17] without pose or its explanation-only language model. All use the seeds of PROVIA, are trained with their published objective and selected on validation loss, derive temporal windows once from correct training durations, and read the same predicted segments and past frames only. Controlled PREGO is scored by one minus the posterior mass of the anticipated successor, a continuous score in place of its binary mismatch decision. 

## _C. Comparison with Controlled Baselines_ 

**Step-level results.** PROVIA has the highest AP and AUROC among the evaluated controlled baselines on every benchmark (Table II). The margin over the best baseline is largest on HoloAssist, the single-actor benchmark with the most steps per execution, where resetting the record of what was performed costs the largest share of the AP, a seventh (Sec. V-D). 

**IMPACT-ego.** Step identity limits every method there: its steps last one to two seconds and the two hands interleave. With segments only where the model decodes an event, 57% of the annotated steps hold a decision; keeping an open step on every hand raises this to 86% and lifts PROVIA from .129 to .147 AP. 

## _D. Ablation Studies_ 

Table III removes one component at a time from the frozen model at inference. _w/o factual state_ resets _Hi_ to its initial value before every segment, _w/o status transition_ replaces _P_ tr by the training-fold initial law, _w/o procedure-state belief_ replaces the posterior by a uniform law over the states with an admissible successor, and _w/o completion gate_ reports the marginal prefix mistake probability. 

**Factual state and status transition.** Resetting the factual state before every segment costs AP on all three benchmarks, a seventh of it on HoloAssist and a tenth on IndustReal and CaptainCook4D, and AUROC moves with it (.670 to .653 on HoloAssist, .554 to .516 on CaptainCook4D). Retrained from scratch without _Hi_ at the same parameter count, the model stays below the full one on HoloAssist and CaptainCook4D and above it on IndustReal, so on the two larger benchmarks the parameter count does not account for the gain. The status transition is the second dependence on the past, a prior on how the next execution status follows the last; removing it costs AP everywhere and most on IndustReal and CaptainCook4D.

<!-- Page 7 -->

TABLE II 

STEP-LEVEL RESULTS OF ALL METHODS, AS MEAN _±_ SD OVER THREE TRAINING SEEDS; BOLD MARKS THE BEST VALUE. ON IMPACT-EGO (<sup>_†_</sup> ) ALL METHODS SHARE AN IN-DOMAIN HAND-OBJECT STREAM. 

||Captain|Cook4D|Indus|tReal|HoloA|ssist|IMPAC|T-ego<sup>_†_</sup>|
|---|---|---|---|---|---|---|---|---|
|Method|AP _↑_|AUROC _↑_|AP _↑_|AUROC _↑_|AP _↑_|AUROC _↑_|AP _↑_|AUROC _↑_|
|Causal-TCN|.336_±_.007|.527_±_.014|.148_±_.040|.616_±_.055|.111_±_.012|.633_±_.002|.127_±_.009|.546_±_.008|
|Controlled PREGO [1]|.330_±_.003|.496_±_.007|.133_±_.010|.612_±_.008|.057_±_.002|.540_±_.007|.086_±_.002|.442_±_.006|
|MistSense-RGB-style [17]|.346_±_.006|.522_±_.018|.101_±_.007|.567_±_.028|.105_±_.009|.625_±_.008|.134_±_.009|.548_±_.010|
|PROVIA|**.364**_±_**.024**|**.554**_±_**.018**|**.153**_±_**.029**|**.625**_±_**.022**|**.131**_±_**.011**|**.670**_±_**.009**|**.147**_±_**.008**|**.567**_±_**.007**|



TABLE III 

ABLATION OF THE FROZEN MODEL AT INFERENCE: TEST AP AS MEANS OVER THREE TRAINING SEEDS. THE RETRAINED VARIANT IS A MATCHED ARCHITECTURE TRAINED FROM SCRATCH WITHOUT THE FACTUAL STATE. 

|||AP _↑_||
|---|---|---|---|
|Variant|HoloAssist|IndustReal|CaptainCook4D|
|PROVIA (full)|.131|.153|.364|
|w/o factual state _Hi_|.113|.138|.328|
|w/o factual state _Hi_ (retrained)|.121|.159|.333|
|w/o status transition _P_tr|.127|.135|.337|
|w/o procedure-state belief|.127|.147|.371|
|w/o completion gate|.123|.119|.370|



**Belief over procedure states.** The belief contributes little at the step level. The induced automata are nearly linear: after merging, a state admits 1.01 to 1.18 next steps on average and the merge compresses the prefix tree of the demonstrations by 1% to 14%, and a belief over a nearly linear automaton carries little beyond position. 

**Completion gate and CaptainCook4D.** The gate ties the reported probability to the evidence that the step has ended and is worth most on IndustReal. On CaptainCook4D the gate and the belief do not help and the status transition carries the benchmark. With .318 of its steps mistaken, the highest prevalence of the four, only 3.9 executions of a recipe are error-free from end to end, so the automaton is a prefix tree of about four traces over a 27.6-step sequence, whereas the status transition is estimated from every training execution. 

## _E. Qualitative Results_ 

Fig. 2 follows one execution through the detector. The six alarms all fall inside mistake cells, two in the same cell; five credit the mistake of their own cell and three of these also the preceding mistake, whose cell held decisions but no alarm, so eight of the nine mistakes are credited; the first, at 23 s, has no decision in its cell, since the first segment completes at 48 s. 

## _F. Detection under a False-Alarm Budget_ 

An assistant is operated at a false-alarm budget, and Table IV scores every method’s alarms on the three singleactor benchmarks under the protocol of Sec. III. 

**Alarm-level results across benchmarks.** At 1 alarm per minute the position controls already recover most of what 


![](assets/065/paper-0007-13.png)


<!-- Start of picture text -->
step 5 step 8 step 10<br>step 3 order error step 6 measurement error step 9 measurement error<br>order error technique error timing error technique error correct technique error<br>1 2 3 4 5 6 7 8 9 10<br>0.2<br>0.1<br>0.0<br>τ<br>1<br>0<br>0 100 200 300 400 500 600<br>time (s)<br>steps<br>ai t ,<br>Si<br><!-- End of picture text -->

Fig. 2. One CaptainCook4D test execution (Zoodles, 656 s) with the seed0 model. Top: frames from six of the steps, three seconds before their completion, with the step index and the annotated error types above each frame and a line to the frame time. Second row: the twelve annotated steps as their completion cells, red for mistakes and green for correct steps, with the eighteen predicted completions as ticks. Third row: the reported mistake probability _ai,t_ at every frame. Bottom: the Shiryaev–Roberts statistic _Si_ at each completion against the threshold _τ_ frozen on validation at 0.5 false alarms per minute; the shaded regions above _τ_ are the alarms. 

any method recovers on CaptainCook4D; the methods separate at the strict budgets. On HoloAssist PROVIA leads at every budget and does so at the lowest measured false-alarm rate of the four methods; on CaptainCook4D it leads at 0.1 per minute at the lowest measured rate of any row, and at 0.5 per minute it reaches the recall of Causal-TCN with fewer false alarms. The lead at 0.1 rests on the factual state: with _Hi_ reset before every segment, the CaptainCook4D recall falls from .154 to .112. The order does not depend on the grace of one decision: with one-to-one crediting, where an alarm credits only the mistake of its own cell, every recall falls, and PROVIA still leads on HoloAssist at every budget (.023, .090 and .151 against at most .010, .040 and .087 for any other row) and on CaptainCook4D at 0.1 per minute (.094 against .081). On IndustReal no method exceeds all three perceptionfree controls at any budget. The order follows what the sequential test has to accumulate: an execution offers about 63 segments on HoloAssist, 14 on CaptainCook4D and 6 on IndustReal (Table I), and the IndustReal thresholds are set on four validation mistakes. 

**First and later mistakes.** On HoloAssist at 0.5 per minute

<!-- Page 8 -->

TABLE IV 

ALARM-LEVEL RESULTS WITH THRESHOLDS FROZEN ON VALIDATION, AS MEANS OVER THREE TRAINING SEEDS. COLUMNS 0.1, 0.5 AND 1.0 GIVE THE RECALL OF ALL MISTAKES AT VALIDATION BUDGETS OF THAT MANY FALSE ALARMS PER MINUTE OF CORRECT OPERATION, FA THE FALSE-ALARM RATE PER MINUTE REACHED AT THE 0.1 THRESHOLD, AND LATER THE RECALL AT 0.5 OF THE DECODED MISTAKES THAT FOLLOW ANOTHER DECODED MISTAKE. 

|Method|0.1_↑_|Ca<br>FA_↓_|ptainCoo<br>0.5_↑_|k4D<br>1.0_↑_|Later_↑_|0.1_↑_|FA_↓_|IndustRe<br>0.5_↑_|al<br>1.0_↑_|Later_↑_|0.1_↑_|FA_↓_|HoloAss<br>0.5_↑_|ist<br>1.0_↑_|Later_↑_|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|Causal-TCN|.100|.094|.600|**.845**|**.709**|**.255**|.126|**.529**|**.882**|**1.00**|.015|.094|.044|.099|.058|
|Controlled PREGO [1]|.101|.105|**.605**|.825|.694|.137|.103|.392|.863|.667|.009|.095|.044|.087|.058|
|MistSense-RGB-style [17]|.128|.103|.604|.805|.698|.118|.112|**.529**|.745|**1.00**|.008|.102|.048|.095|.063|
|PROVIA|**.154**|.075|.600|.839|.701|.098|.126|.392|.667|.444|**.034**|.093|**.124**|**.210**|**.126**|
|Position control (index)|.090|.099|.473|.826|.599|.176|.129|.529|.882|1.00|.000|.000|.041|.078|.054|
|Position control (time)|.102|.117|.532|.765|.676|.294|.129|.588|.765|1.00|.014|.061|.055|.071|.071|
|Position control (training)|.100|.108|.430|.656|.507|.176|.138|.529|.765|1.00|.018|.103|.058|.139|.068|



PROVIA recalls twice the share of later mistakes of any baseline and 1.8 times that of any position control (Later in Table IV), and .180 of the first mistakes of an execution against at most .048 for any other row, so its lead there is not confined to the mistakes that follow a corrupted state. **Timing of alarms.** At 0.5 per minute .82 of PROVIA’s detections on CaptainCook4D and .89 on HoloAssist precede the next step, with a median delay after the end of the mistake of 9.3 s on CaptainCook4D and 0.5 s on HoloAssist, where the baselines take 1.0 to 1.6 s and at most .85 of their detections precede the next step. 

## VI. CONCLUSION 

PROVIA reads each step of a procedure against the execution as it actually happened. It keeps the steps each actor performed apart from the progress it accepts, and raises alarms at a stated false-alarm budget faster than the video arrives. Scored on complete trials and against controls that use no perception, it ranks mistakes best among the evaluated controlled baselines on four benchmarks spanning cooking, industrial assembly and disassembly, and everyday tasks, over a 23-fold range of step granularity, and removing the record of what was performed at inference costs accuracy on each single-actor benchmark. As an alarm it recalls the most mistakes at 0.1 false alarms per minute on CaptainCook4D and at every budget on HoloAssist, where its alarms follow the end of the mistake within half a second, earlier than those of any baseline. 

## ACKNOWLEDGMENT 

The project is funded by the Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – SFB1574 – 471687386. This work was supported in part by the SmartAge project sponsored by the Carl Zeiss Stiftung (P2019-01-003; 2021-2026). The authors gratefully acknowledge the computing time provided on the high-performance computer HoreKa by the National HighPerformance Computing Center at KIT (NHR@KIT). This center is jointly supported by the Federal Ministry of Education and Research and the Ministry of Science, Research and the Arts of Baden-W¨urttemberg, as part of the National High-Performance Computing (NHR) 

joint funding program (https://www.nhr-verein. de/en/our-partners). HoreKa is partly funded by the German Research Foundation (DFG). 

## REFERENCES 

- [1] A. Flaborea _et al._ , “PREGO: Online mistake detection in procedural egocentric videos,” in _Proc. CVPR_ , 2024, pp. 18 483–18 492. 

- [2] L. Seminara, G. M. Farinella, and A. Furnari, “Differentiable task graph learning: Procedural activity representation and online mistake detection from egocentric videos,” in _Proc. NeurIPS_ , vol. 37, 2024, pp. 59 373–59 407. 

- [3] F. Sener _et al._ , “Assembly101: A large-scale multi-view video dataset for understanding procedural activities,” in _Proc. CVPR_ , 2022, pp. 21 096–21 106. 

- [4] G. Ding, F. Sener, S. Ma, and A. Yao, “Every mistake counts in assembly,” _arXiv preprint arXiv:2307.16453_ , 2023. 

- [5] R. Peddi _et al._ , “CaptainCook4D: A dataset for understanding errors in procedural activities,” in _Proc. NeurIPS_ , vol. 37, 2024, pp. 135 626– 135 679. 

- [6] T. J. Schoonbeek, T. Houben, H. Onvlee, P. H. N. de With, and F. van der Sommen, “IndustReal: A dataset for procedure step recognition handling execution errors in egocentric videos in an industrial-like setting,” in _Proc. WACV_ , 2024, pp. 4353–4362. 

- [7] X. Wang _et al._ , “HoloAssist: an egocentric human interaction dataset for interactive AI assistants in the real world,” in _Proc. ICCV_ , 2023, pp. 20 270–20 281. 

- [8] S.-P. Lee, Z. Lu, Z. Zhang, M. Hoai, and E. Elhamifar, “Error detection in egocentric procedural task videos,” in _Proc. CVPR_ , 2024, pp. 18 655–18 666. 

- [9] D. Wen _et al._ , “IMPACT: A dataset for multi-granularity human procedural action understanding in industrial assembly,” in _Proc. MM_ , 2026. 

- [10] H. Zhang _et al._ , “IMPACT-HOI: Supervisory control for onset-anchored partial HOI event construction,” _arXiv preprint arXiv:2605.01666_ , 2026. 

- [11] W.-J. Huang _et al._ , “Modeling multiple normal action representations for error detection in procedural tasks,” in _Proc. CVPR_ , 2025, pp. 27 794–27 804. 

- [12] W. Guo, Y. Pu, and Y. Kong, “Procedural mistake detection via action effect modeling,” in _Proc. ICLR_ , 2026. 

- [13] S.-P. Lee and E. Elhamifar, “Error recognition in procedural videos using generalized task graph,” in _Proc. ICCV_ , 2025, pp. 10 009–10 021. 

- [14] ——, “AXG-Reasoner: Error detection and explanation in long task videos with vision–language models,” in _Proc. CVPR_ , 2026, pp. 3421– 3431. 

- [15] S. Ozsoy, L. Doorenbos, F. Spurio, G. Francesca, and J. Gall, “The unreasonable effectiveness of VLMs for zero-shot procedural mistake detection,” _arXiv preprint arXiv:2606.21579_ , 2026. 

- [16] L. Plini _et al._ , “TI-PREGO: Chain of thought and in-context learning for online mistake detection in procedural egocentric videos,” _Computer Vision and Image Understanding_ , vol. 264, p. 104613, 2026. 

- [17] C. Patsch, Y. Wu, M. Zakour, D. Salihu, and E. Steinbach, “MistSense: Versatile online detection of procedural and execution mistakes,” in _Proc. ICCV_ , 2025, pp. 14 528–14 537.

<!-- Page 9 -->

- [18] T. J. Schoonbeek _et al._ , “Learning to recognize correctly completed procedure steps in egocentric assembly videos through spatio-temporal modeling,” _Computer Vision and Image Understanding_ , vol. 262, p. 104528, 2025. 

- [19] S. Majumder, A. Nethi, Z. Al-Halah, and K. Grauman, “MistExit: Learning to exit for early mistake detection in procedural videos,” _arXiv preprint arXiv:2603.14252_ , 2026. 

- [20] K. Peng _et al._ , “Navigating open set scenarios for skeleton-based action recognition,” in _Proc. AAAI_ , 2024, pp. 4487–4496. 

- [21] F. Liu _et al._ , “GuideMe: Multi-domain task guidance and intervention in streaming video,” in _Proc. ECCV_ , 2026. 

- [22] K. Kundu _et al._ , “Plan, watch, recover: A benchmark and architectures for proactive procedural assistance,” _arXiv preprint arXiv:2606.04970_ , 2026. 

- [23] A. Stolcke and S. Omohundro, “Hidden Markov model induction by Bayesian model merging,” in _Proc. NeurIPS_ , vol. 5, 1992, pp. 11–18. 

- [24] A. N. Shiryaev, “On optimum methods in quickest detection problems,” _Theory of Probability & Its Applications_ , vol. 8, no. 1, pp. 22–46, 1963. 

- [25] S. W. Roberts, “A comparison of some control chart procedures,” _Technometrics_ , vol. 8, no. 3, pp. 411–430, 1966. 

- [26] M. Oquab _et al._ , “DINOv2: Learning robust visual features without supervision,” _Transactions on Machine Learning Research_ , 2024. 

- [27] J. An, H. Kang, S. H. Han, M.-H. Yang, and S. J. Kim, “MiniROAD: Minimal RNN framework for online action detection,” in _Proc. ICCV_ , 2023, pp. 10 341–10 350.
