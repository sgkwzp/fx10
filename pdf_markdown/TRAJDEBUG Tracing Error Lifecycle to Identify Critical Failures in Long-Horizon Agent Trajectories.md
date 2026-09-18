# TRAJDEBUG Tracing Error Lifecycle to Identify Critical Failures in Long-Horizon Agent Trajectories

[Original PDF](../TRAJDEBUG%20Tracing%20Error%20Lifecycle%20to%20Identify%20Critical%20Failures%20in%20Long-Horizon%20Agent%20Trajectories.pdf)

Pages: 24

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

# **TRAJDEBUG: Tracing Error Lifecycle to Identify Critical Failures in Long-Horizon Agent Trajectories** 

Yunjia Qi<sup>1</sup> , Zehua Yin<sup>1</sup> , Xintong Shi<sup>1</sup> , Hao Peng<sup>1</sup> , 

Songyuanyi Lu<sup>3</sup> , Yixian Liu<sup>3</sup> , Richeng Xuan<sup>3</sup> , Yuhong Liu<sup>3</sup> , Zhichao Hu<sup>3,*</sup> , 

Xiaozhi Wang<sup>2</sup> , Lei Hou<sup>1</sup> , Bin Xu<sup>1,*</sup> , Juanzi Li<sup>1</sup> 

1Department of Computer Science and Technology, BNRist, Tsinghua University 

2Shenzhen International Graduate School, Tsinghua University 

3Tencent Hunyuan 

*Corresponding authors 

qyj23@mails.tsinghua.edu.cn 

## **Abstract** 

LLM-based agentic systems have shown remarkable capabilities in complex domains, while suffering from cascading errors and difficulty in debugging. Critical error detection aims to locate the earliest error step in a failed trajectory that is responsible for the final failure. However, progress faces two main challenges. First, long trajectories make it difficult to identify individual errors, since the evidence for judging a step may be scattered across distant instructions, observations, and prior context. Second, failed trajectories often contain multiple local errors whose downstream effects differ: some are repaired, some remain harmless, and only some contribute to the final failure. In this work, we propose TRAJDEBUG, an error-lifecycle tracing framework that addresses long-trajectory error discovery with multi-granularity history compression and evidence-based error identification, and supports critical attribution by tracing each error’s resolution status and terminal impact. We further construct TRAJERRBENCH, a benchmark of 486 manually annotated failed trajectories from _τ_<sup>2</sup> -Benchand SWE-Bench Pro, covering realistic tool-use and coding scenarios. Experiments across diverse agent benchmarks show that TRAJDEBUG achieves the best overall performance over existing baselines, and application studies further demonstrate that its diagnoses provide actionable feedback for improving downstream agent success. We will release the code and data to facilitate further research<sup>1</sup> . 

## **1 Introduction** 

Large language model (LLM)-based agentic systems have shown remarkable capabilities in complex, real-world domains, such as software engineering (Jimenez et al., 2024; Deng et al., 2025), scientific discovery (Mialon et al., 2024), and multiturn customer service workflows (Barres et al., 

> 1https://github.com/THU-KEG/TrajDebug 


![](assets/077/paper-0001-15.png)


<!-- Start of picture text -->
Fix CSV boolean export: True/False → true/false. Do not<br>modify  core/serialization.py .<br>Task  Conflict:<br>Constraint<br>Inspect CSV export logic and plan to add a local fix. Violation<br>The shared serializer controls boolean formatting.  Decide  to<br>modify  core/serialization.py Critical Error<br>Modify  core/serialization.py. Forbidden file edited<br>JSON export tests  fail. Side effect: JSON<br>behavior changes<br>Add special handling to preserve JSON behavior.<br>Compensating patch<br>Modify JSON exporter.<br>All tests pass. Cascade<br>Error<br>Failure: Task constraints remain violated.<br><!-- End of picture text -->

Figure 1: Critical error detection requires grounding errors in long-range context and distinguishing the failureresponsible error from multiple coexisting errors. 

2025). These trajectories often span hundreds of reasoning, action, and observation steps, and a terminal failure may trace back to an early mistake that propagates through subsequent decisions, making the trajectory difficult to debug and improve. _Critical error detection_ (Zhang et al., 2025c) addresses this difficulty by locating the earliest error step in a failed trajectory that is causally linked to the task failure, thereby supporting trajectory repair and system reliability analysis. 

Critical error detection faces two key challenges in long, complex agent trajectories. First, _long trajectories make it difficult to identify individual errors._ Complex tasks often require extended execution processes that interleave planning, reasoning, tool use, environment feedback, and repair attempts over many steps (Yao et al., 2023, 2022). As a result, judging whether a step is erroneous may require relating it to evidence scattered across distant task instructions, observations, and prior trajectory context (Peng et al., 2023). For example, in Figure 1, the erroneous decision conflicts with a task constraint stated at the beginning of the trajectory, requiring long-range task context to identify the error. Second, _failed trajectories often contain_ 

1

<!-- Page 2 -->

_multiple local errors whose downstream effects differ, obscuring which error is critical to the final failure._ A failed trajectory may contain many local errors (Cemri et al., 2026), some are resolved, some are inconsequential, and others are merely downstream symptoms of earlier mistakes (Fan et al., 2026). Thus, the critical error is not necessarily the first local error observed in the trajectory, nor the temporally closest error to the terminal failure. 

Existing methods often address only part of this problem. Current taxonomy-based and constraintbased methods focus on identifying candidate erroneous steps in long trajectories (Zhu et al., 2025; Barke et al., 2026), while causal-diagnostic methods use causal structures or counterfactual attribution to filter propagated errors (Wang et al., 2026; Li et al., 2026). However, candidate-error methods often leave criticality to a holistic final judgment, which is brittle when many local errors coexist. Causal attribution methods model dependencies among errors, but their judgments can remain ambiguous when later feedback and repair attempts alter the effects of earlier errors. 

To address these challenges, we propose TRAJDEBUG, an evidence-grounded error-lifecycle tracing framework for critical error detection. TRAJDEBUG decomposes the task into three stages: error trigger detection, error state classification, and critical attribution. First, to identify individual errors in long trajectories, TRAJDEBUG uses multi-granularity history compression and detects error triggers as wrong commitments grounded in conflicts with task instructions, trajectory history, environment feedback, or the agent’s own reasoning. This turns error discovery from holistic diagnosis into an auditable evidence-verification problem, reducing hallucinated or weakly grounded diagnoses (Gao et al., 2023). Second, to address the ambiguity caused by multiple local errors with different downstream effects, TRAJDEBUG groups related triggers into error instances by their shared violated reference, such as a task constraint or prior observation. It then classifies the state of each instance by tracking whether the wrong commitment is resolved, and whether it leaves an observable terminal footprint, such as an irreversible state change, a persistent task violation, or a substantial recovery cost. These state classifications distinguish errors that are repaired or remain harmless from those that stay relevant to the final failure. Finally, TRAJDEBUG selects the critical error step from evidence-backed instances with terminal relevance, 

rather than judging over the full trajectory. 

To evaluate critical error detection under realistic scenarios and complement existing benchmarks (Zhang et al., 2025c; Zhu et al., 2025), we construct TRAJERRBENCH, a benchmark of 486 manually annotated failed trajectories: 400 from _τ_<sup>2</sup> -Bench (Barres et al., 2025), covering diverse tool-use and user-interaction scenarios, and 86 from SWE-Bench Pro (Deng et al., 2025), covering long-horizon coding trajectories with an average length of about 119 _._ 7 steps. 

Experiments on existing agent benchmarks and TRAJERRBENCH show that TRAJDEBUG achieves the best overall performance over advanced LLM prompting baselines and existing diagnostic systems. Length-based analysis shows that TRAJDEBUG remains more robust on long-horizon trajectories. To assess whether critical-error diagnoses can improve future agent behavior, we explore two inference-time application scenarios. In the first, each failed trajectory is diagnosed and converted into targeted guidance before re-executing the same task, improving success by 10 _._ 80% on average. In the second, diagnoses from a small set of historical failures are aggregated into reusable failure memory and transferred to held-out tasks, yielding a 5 _._ 70% average improvement. These results suggest that TRAJDEBUG can serve not only as a diagnostic tool, but also as a practical interface for converting failed executions into actionable experience for improving long-horizon agents. 

## **2 Pilot Study** 

This section first formalizes critical error step detection (§ 2.1) and then provides empirical motivation for the two challenges discussed above. We examine how trajectory length is associated with critical error localization difficulty (§ 2.2) and how local errors evolve within failed trajectories (§ 2.3). See Appendix A for experiment and annotation details. 

### **2.1 Task Formulation** 

Let a trajectory be _τ_ = ( _x_ 1 _, x_ 2 _, . . . , xN_ ), where each step _xt_ contains the agent’s reasoning, action, or environment response. A trajectory is _failed_ if its final state does not satisfy the task goal. Following Zhang et al. (2025c), a step _xt_ contains a decisive error if replacing its action with a correct one, while leaving all prior steps unchanged and allowing the remainder of the trajectory to unfold correctly, would have turned the failure into a suc- 

2

<!-- Page 3 -->

![](assets/077/paper-0003-00.png)


<!-- Start of picture text -->
50 Individual Model Step Accuracy (%)<br>Avg. Critical Error Detection Step Accuracy (%)<br>40 Error Count per Trajectory<br>30<br>20<br>10<br>0<br>1-10 11-30 31-60 61+<br>Trajectory Length<br><!-- End of picture text -->

Figure 2: Critical error detection accuracy and local error density across trajectory length buckets. 

cess. The **critical error step** is the earliest decisive error step, identifying the origin of the failure rather than its downstream propagation. 

### **2.2 Error Detection under Growing Context** 

We group trajectories from WhoAndWhen (Zhang et al., 2025c) and AgentDebugBench (Zhu et al., 2025) by trajectory length, and directly prompt LLMs to identify the annotated critical error step in each failed trajectory, and use critical-step detection accuracy as an indicator of the difficulty introduced by growing context. We evaluate seven widely used advanced models and report the average accuracy across models to reveal the overall trend. Figure 2 shows that detection accuracy decreases as trajectory length increases, suggesting that long-horizon context makes critical error detection harder. This trend is consistent with prior observations that longer trajectories are associated with lower task success rates (Qi et al., 2026). 

### **2.3 Trajectory Dynamics of Local Errors** 

We further sample 50 failed trajectories from these benchmarks and annotate local error steps with three annotators, with details in Appendix A. The sampled trajectories contain 381 local errors in total, averaging 7 _._ 62 per failed trajectory, while each trajectory has only one critical error. Figure 2 shows that the average number of local errors increases with trajectory length, indicating that longer trajectories expose a denser set of plausible but non-critical candidates. To understand how non-critical errors evolve, we exclude the critical errors and analyze the remaining 331 local errors. We find that 205 (61 _._ 9%) are later repaired by the agent, while 104 (31 _._ 4%) persist until the final outcome. Only 22 (6 _._ 6%) are unrepaired yet dormant: for example, a step may miscount four search results as two, but no later decision depends on the 

count. These dynamics show that critical error detection must distinguish local error occurrence from its downstream state and terminal impact, motivating TRAJDEBUG in § 3.3. 

## **3 TRAJDEBUG** 

Figure 3 shows the overall framework of TRAJDEBUG. Given a failed trajectory _τ_ , TRAJDEBUG first constructs multi-granularity trajectory views to preserve local evidence while compressing distant context (§3.1). TRAJDEBUG then follows an errorlifecycle tracking perspective and decomposes critical error detection into three stages. First, TRAJDEBUG detects evidence-grounded error _triggers_ at individual steps (§3.2). Second, it groups related triggers into object-anchored error _instances_ and classifies each instance’s error state, based on whether the error is resolved or remains active and whether it leaves an observable terminal footprint (§3.3). Finally, it attributes the final failure to the critical candidate through candidate-set-guided causal attribution (§3.4). This turns critical error detection from an end-to-end judgment over the full trajectory into three more controlled steps: finding evidence-backed local errors, classifying their error states, and selecting the causally responsible step from the remaining candidates. More details and examples are in Appendix C and Appendix D. 

### **3.1 Multi-Granularity Compression** 

To reduce the long-context burden while preserving verifiable evidence, we use LLM to construct three views for each step: (1) _high-detail_ view keeps the original instruction, action, observation, and locally relevant reasoning snippets needed for evidence verification; (2) _medium-detail_ view summarizes the step’s main intent, action, and state update; (3) _low-detail_ view records only coarse progress, salient entities, and unresolved commitments. Each stage then retrieves the finest view required for its decision, using high-detail views for local verification and compressed views for distant context. 

### **3.2 Error Trigger Detection** 

For each step, given the trajectory prefix up to that step, the first stage extracts per-step atomic error triggers. A **trigger** _e_ = ( _t, c, p, qw, qr_ ) denotes a local evidence-grounded mismatch at step _t_ , where _qw_ is an erroneous commitment expressed in the current step, _qr_ is the violated reference, _c_ is the reference category, and _p_ is the execution phase. The violated reference _qr_ may come from the task 

3

<!-- Page 4 -->

![](assets/077/paper-0004-00.png)


<!-- Start of picture text -->
[TASK]  Fix CSV boolean export: True/False →  Error Trigger Detection Instance Clustering Lifecycle Analysis Causal Attribution<br>true/false.  Do not modify core/serialization.py.<br>Reference<br>[Step 1] There are  two  relevant files:  csv_exporter.py, Conflict with the  Intra-Step  object: two Step 1 says  No downstream  Latent Active:  Task<br>json_exporter.py, and serialization.py. description "two" but lists  step depends  Step 1<br>… three files.  on this error. …<br>Step 10<br>[Step 4]  Try fixing boolean output by  changing CSV<br>quoting logic. Step 11<br>… Conflict with  Reference  Clean …<br>[Step 10]  The previous change had no effect; History object:  Resolution:  Step 20<br>try the same CSV quoting change again . Observation changing csv Error resolved<br>Step 21<br>[Step 11]   Modify the CSV quoting logic. Conflict with  quoting logic Repeat the  terminal effect.at Step 15; no  …<br>History failed Step 4  Step 60<br>… Observation change. Latent Active<br>[Step 20] I should  modify core/serialization.py  to  Conflict with  Reference<br>complete the task. Task  Constraint object: don’t  Manifest<br>[Step 21]  Modify core/serialization.py. … Task Conflict with  Constraint core/serializatimodify on.py Forbidden core edit remains. Active: Stage: ReasonTask ConflictStep: 20<br>Ignore Constraint<br>[Step 60] Failure<br><!-- End of picture text -->

Figure 3: An overview of the framework of TRAJDEBUG. 

instruction, prior trajectory, environment feedback, or the same step. To prevent subjective drift and hallucinated diagnoses, each trigger must satisfy a **verbatim evidence** condition: both _qw_ and _qr_ must be explicitly citable; otherwise, the trigger is discarded. A step may contain multiple triggers when it violates different references or expresses different erroneous commitments. For each inspected step, the detector uses the high-detail current step and task instruction, medium-detail previous two steps, and low-detail views for the remaining history. This preserves local evidence for verification while keeping long-range context compact. 

We organize triggers along two axes. The first axis is the **reference category** _c_ , which specifies the source of the violated reference _qr_ : (1) _Task Conflict_ , where _qr_ comes from the task instruction, such as a constraint; (2) _History Conflict_ , where _qr_ comes from prior trajectory context, such as a tool output, or established trajectory fact; and (3) _IntraStep Conflict_ , where _qr_ comes from the current step itself, such as an earlier claim. We additionally use (4) _Environment Anomaly_ as an exogenous category when the agent action is reasonable but the environment response is abnormal. The second axis is the **execution phase** _p_ , which records where the mismatch surfaces in the agent process (Deshpande et al., 2025; Zhu et al., 2025): _planning_ , _reasoning_ , _action_ , _observation_ , or _verification_ (detailed in Appendix D). The reference category _c_ , together with the violated reference _qr_ , determines the reference object _O_ used for instance clustering, while the execution phase _p_ characterizes the agent-side mechanism for fine-grained analysis. 

### **3.3 Error State Classification** 

The second stage groups per-step triggers into error **instances** and classifies the state of each instance. Since the same wrong commitment may appear across multiple steps (Xie et al., 2026), such as a task-constraint violation surfacing in planning, action, and verification, we define an instance as _E_ = ( _E, O_ ), where _E_ contains triggers that violate the same reference object _O_ . This avoids overcounting repeated manifestations of the same error. Each instance thus represents one continuous episode of holding a wrong commitment to a concrete reference object. 

For each instance, the state classifier makes two evidence-backed judgments: whether the wrong commitment is **resolved** or remains **active** , and whether it leaves an observable **terminal footprint** . An instance is resolved only if later steps explicitly revisit _O_ and provide citable evidence that supersedes the wrong commitment; otherwise, it remains active. A terminal footprint is assigned when there is evidence of: (i) an _irreversible_ state change, such as submitting a wrong order; (ii) a _semantic_ footprint, where the wrong commitment is reflected in later steps or the terminal state, such as a persistent violation of a task constraint; or (iii) _budget debt_ , where the error is resolved only after consuming more than _k_ % of the trajectory. In implementation, we set _k_ = 50, as exceeding half the trajectory mostly leaves an insufficient budget for recovery. 

Combining these two judgments yields four error states: **Clean Resolution** (resolved, no footprint), **Costly Resolution** (resolved, budget-debt footprint), **Manifest Active** (active, irreversible or 

4

<!-- Page 5 -->

![](assets/077/paper-0005-00.png)


<!-- Start of picture text -->
WebShop 28% 22% 16% 6% 6% 6% 4% 12%<br>WW-Algo 16% 24% 11% 10% 7% 13% 5% 5% 10% 1% 25<br>ALFWorld 21% 26% 12% 12% 5% 2% 2% 8% 2% 10% 20<br>GAIA 14% 27% 10% 12% 4% 14% 8% 10% 15<br>WW-HC 21% 9% 17% 5% 7% 3% 7% 12% 9% 10% 10<br>SWE-Bench-Pro 2% 3% 5% 9% 14% 12% 26% 14% 6% 9% 5<br>Tau2Bench 1% 4% 4% 6% 8% 19% 22% 22% 10% 6% 0<br>0-10% 10-20% 20-30% 30-40% 40-50% 50-60% 60-70% 70-80% 80-90%90-100%<br>Relative Position of Critical Error Step (step / total_steps)<br>Percentage (%)<br><!-- End of picture text -->

Figure 4: Relative position of the critical error step within each trajectory in TRAJERRBENCH and others. 

semantic footprint), and **Latent Active** (active, no footprint). We retain terminal-relevant instances as candidates: 


![](assets/077/paper-0005-03.png)


Each candidate is passed to the final stage with its origin step, state label, footprint channel, and supporting evidence; final criticality is decided by the attribution stage. 

### **3.4 Candidate-Set-Guided Causal Attribution** 

This stage executes candidate-set-guided causal attribution. Given the candidate set _F_ ( _τ_ ), this attribution head selects the candidate instance whose first step best explains the terminal failure. A simple earliest-candidate rule is insufficient because temporal order alone does not determine failure responsibility. For example, an earlier budget-debt instance should not be selected over a later semantic instance unless the wasted budget plausibly prevented the agent from avoiding the later failure. Therefore, we use an LLM as the final attribution head. Each candidate is provided with its first step, state label, and supporting verbatim evidence, and the LLM selects the critical error step. 

## **4 TRAJERRBENCH** 

Existing critical-error benchmarks remain limited in scale, domain diversity, or trajectory complexity (Zhang et al., 2025c; Zhu et al., 2025; Barke et al., 2026; Li et al., 2026). We construct TRAJERRBENCH, a benchmark of 486 manually annotated failed trajectories from two complementary domains: 400 _τ_<sup>2</sup> -Bench trajectories (Barres et al., 2025) and 86 SWE-Bench Pro trajectories (Deng et al., 2025), averaging 29 _._ 3 and 119 _._ 7 steps, respectively. Following WhoAndWhen (Zhang et al., 2025c), annotators identify the earliest evidencegrounded mistake responsible for the final failure, while separating locally wrong but later repaired 

mistakes from failure-responsible ones. Each trajectory is annotated by three annotators, and labels with at least two-way agreement are used as ground truth; this majority-vote protocol yields usable labels for 98 _._ 2% of _τ_<sup>2</sup> -Bench trajectories and 91 _._ 9% of SWE-Bench Pro trajectories. The critical-error step labels reach almost-perfect agreement on _τ_<sup>2</sup> - Bench (Fleiss’ _κ_ =0 _._ 91) and substantial agreement on the longer, code-heavy SWE-Bench Pro trajectories (Fleiss’ _κ_ =0 _._ 67); details are in Appendix B. 

Figure 4 shows that critical errors in TRAJERRBENCH often occur in the mid-to-late. This reflects the shared structure of TRAJERRBENCH: agents first gather task-relevant information before making decisive decisions, through user interaction in _τ_<sup>2</sup> -Bench and repository exploration in SWEBench Pro. Such extended information gathering shifts many critical errors later and makes localization harder, as relevant evidence is accumulated across earlier context. We also annotate each critical error by contradiction reference category and execution phase, with full statistics in Appendix B. In _τ_<sup>2</sup> -Bench, critical errors are almost evenly split between task conflicts (52 _._ 4%) and history conflicts (46 _._ 3%), while SWE-Bench Pro is dominated by task conflicts (73 _._ 4%) with fewer history conflicts (24 _._ 1%). Reasoning is the dominant failure phase in both domains (60 _._ 7% and 57 _._ 1%), suggesting that failures mainly arise from misinterpreting accumulated context in agentic trajectories. 

## **5 Experiments** 

### **5.1 Experimental Settings** 

**Datasets and Evaluation Metric.** We evaluate our approach across benchmarks in various domains. **WhoAndWhen** (Zhang et al., 2025c) contains a hand-crafted subset of 58 trajectories and an algorithm-generated subset of 126 trajectories drawn from GAIA and AssistantBench. **AgentDebugBench** (Zhu et al., 2025) provides 100 ALFWorld and 50 each from GAIA and WebShop trajectories. One GAIA trajectory has a null groundtruth critical-error label and is therefore excluded from evaluation, leaving 869 evaluated trajectories in total. **TRAJERRBENCH** (§ 4) adds 400 _τ_<sup>2</sup> -Bench and 86 SWE-Bench Pro trajectories, extending evaluation to substantially longer tool-use and software-engineering rollouts. Following prior benchmark (Zhang et al., 2025c; Zhu et al., 2025), we report **exact critical-step accuracy** , where a prediction is correct only if it matches the annotated 

5

<!-- Page 6 -->

|**Method**|**Agent**|**DebugBe**|**nch**|**WhoAnd**|**When**|**TRAJ**|**ERRBENCH**|**AVG**|
|---|---|---|---|---|---|---|---|---|
||ALFWorld|GAIA|WebShop|Hand-Crafted|Algorithm|_τ_ <sup>2</sup>-Bench|SWE-Bench Pro||
|_Avg. Trajectory Length_|60_._00|28_._68|51_._84|51_._60|8_._72|29_._27|119_._70|49_._97|
|_Direct Prompting_|||||||||
|GLM-5.1|15_._00|26_._00|26_._00|15_._52|42_._86|46_._75|6_._98|25_._59|
|Gemini-3.1-Pro|19_._00|30_._61|**32**_._**00**|20_._69|46_._82|52_._50|17_._44|31_._29|
|DeepSeek-V4-Pro|15_._00|34_._69|24_._00|18_._97|42_._06|48_._25|12_._79|27_._97|
|Claude Sonnet 4.6|13_._00|30_._61|18_._00|12_._07|29_._37|42_._75|15_._12|22_._99|
|GPT-5.4|11_._00|20_._41|14_._00|13_._79|28_._57|41_._50|10_._46|19_._96|
|Claude Opus 4.6|10_._00|34_._69|24_._00|**27**_._**59**|46_._83|45_._25|17_._44|29_._40|
|Qwen3-235B-A22B|9_._00|33_._33|18_._00|17_._24|42_._06|42_._75|17_._44|25_._69|
|_Multi-Agent System_|||||||||
|AgentDebugger|21_._00|36_._00|20_._00|12_._07|40_._48|26_._00|10_._47|23_._72|
|CHIEF|6_._00|26_._00|10_._00|18_._97|41_._27|26_._82|2_._32|18_._77|
|AgentRX|8_._00|26_._53|18_._00|25_._86|41_._27|36_._25|5_._81|23_._10|
|**TRAJDEBUG (Ours)**|**26**_._**00**|**38**_._**78**|26_._00|22_._41|**48**_._**41**|**52**_._**75**|**24**_._**41**|**34**_._**11**|



Table 1: Main results on critical error detection across multiple benchmarks. All methods operate without task ground truth and receive only the failed trajectory. **Bold** values indicate the best result per column. 

step, and evaluate all methods in a realistic setting where they use only the failed trajectory and failure signal, without success traces, gold outcomes, or auxiliary debugging signals. 

LLMs listed in Table 1. All methods use temperature 0 for reproducibility, and multi-agent baselines follow official prompts and pipelines where available. Implementation details are in Appendix E. 

**Baselines.** We compare with two families of baselines. Motivated by the effectiveness of direct prompting reported in prior work (Zhang et al., 2025c; Banerjee et al., 2025), our first family is **Direct Prompting** , which queries an LLM for the critical error step from the full trajectory under a unified instruction; we instantiate it with seven widely-used advanced models: GLM-5.1 (Zeng et al., 2026), Gemini-3.1-Pro (Team et al., 2023), DeepSeek-V4-Pro (Guo et al., 2025), Claude Sonnet 4.6 (Anthropic, 2026b), Claude Opus 4.6 (Anthropic, 2026a), GPT-5.4 (Achiam et al., 2023), and Qwen3-235B-A22B-Thinking (Yang et al., 2025). The second family is **Multi-Agent Systems** , which decomposes the task across multiple LLM calls: _AgentDebugger_ (Zhu et al., 2025) prompts the judge with a phase-level error taxonomy and produces a structured diagnosis; _CHIEF_ (Wang et al., 2026) parses the trajectory into a hierarchical causal graph and selects the critical step via counterfactual backtracking against a virtual oracle; _AgentRX_ (Barke et al., 2026) first flags steps that violate explicit task or schema constraints and then asks an LLM to select the critical error. 

**Implementation.** We implement TRAJDEBUG and all multi-agent baselines with Qwen3-235BA22B-Thinking (Yang et al., 2025) for a fair comparison, while direct-prompting baselines use the 

### **5.2 Main Results** 

All experimental results are presented in Table 1. We have the following observations: (1) TRAJDEBUG achieves the best overall average in our benchmark suite. It obtains the highest macroaverage accuracy (34 _._ 11%), outperforming both direct prompting with frontier models and all multiagent baselines on average. The absolute accuracies remain low across all methods, highlighting the difficulty of identifying the exact critical step from only the failed trajectory. Under this challenging setting, TRAJDEBUG improves over direct prompting with the same backbone from 25 _._ 69% to 34 _._ 11% (+8 _._ 42), demonstrating the effectiveness of our framework. (2) TRAJDEBUG generalizes well across heterogeneous agent domains. It ranks first on five of seven datasets, spanning embodied decision-making, open-domain information seeking, user-facing tool use, and long-horizon software engineering. In contrast, multi-agent baselines show uneven cross-domain performance(e.g., CHIEF drops to 2 _._ 32% on SWE-Bench Pro and AgentRX to 8 _._ 00% on ALFWorld), suggesting that their pipelines transfer less consistently across agent scenarios. These results demonstrate that TRAJDEBUG’s evidence-grounded trigger detection and error state classification offer robust advantages that generalize across diverse agent scenarios. 

6

<!-- Page 7 -->

|**Method**|_τ_ <sup>2</sup>-Bench|SWE-Bench Pro|AVG|
|---|---|---|---|
|**TRAJDEBUG (Ours)**|**52**_._**75**|**24**_._**41**|**38**_._**58**|
|w/o Multi-Granularity Compression|20_._00|15_._12|17_._56|
|w/o Evidence-Grounded Triggers|46_._25|20_._93|33_._59|
|w/o Error State Classification|46_._25|16_._28|31_._27|
|w/o All Components|42_._75|17_._44|30_._10|



Table 2: Ablation study of TRAJDEBUG. 

(3) TRAJDEBUG remains effective on the longesthorizon benchmarks. On ALFWorld (60 _._ 00 steps on average) and SWE-Bench Pro (119 _._ 70 steps), where evidence is distributed across many steps and multiple errors often coexist, TRAJDEBUG attains the best accuracy, with gains of +13 _._ 00% and +6 _._ 97% over the corresponding direct baselines. These results suggest that evidence-grounded trigger detection and error state classification help narrow critical-step localization in long trajectories with complex failure dynamics. 

### **5.3 Ablation Study** 

Table 2 ablates the three key components of TRAJDEBUG on _τ_<sup>2</sup> -Bench and SWE-Bench Pro. Replacing multi-granularity compression with the same hard-truncation strategy used by direct prompting causes the largest drop, reducing AVG by 21 _._ 02 points. This shows that preserving evidence from different history granularities is essential for long trajectories, rather than merely increasing the number of LLM calls. Removing error trigger detection or error state classification lowers AVG by 4 _._ 99 and 7 _._ 31 points, respectively, showing that these two downstream components are also useful and non-redundant. On _τ_<sup>2</sup> -Bench, both ablations reach the same accuracy, suggesting that the trigger taxonomy and state classification stage act as orthogonal filters of comparable strength on tool-use trajectories. On SWE-Bench Pro, removing state classification reduces accuracy to 16 _._ 28, below the direct-prompting baseline of 17 _._ 44, whereas removing only the taxonomy still achieves 20 _._ 93. This pattern supports our motivation in § 2: long-horizon trajectories contain many detected errors that are cleanly resolved or dormant, making final attribution more difficult. State-based filtering narrows attribution to errors with terminal footprint. 

### **5.4 Length Analysis** 

Figure 5 shows critical-step detection accuracy across trajectory length buckets. All baselines degrade sharply as trajectories grow, dropping from 


![](assets/077/paper-0007-07.png)


<!-- Start of picture text -->
TraDebug (Ours) GPT-5.4<br>50 Gemini-3.1-Pro AgentRX<br>Claude-Opus-4.6 AgentDebug<br>40 Claude-Sonnet-4.6 CHIEF<br>30<br>20<br>10<br>0<br>1-35 36-70 71-105 106-140 141+<br>(n=534) (n=237) (n=35) (n=35) (n=28)<br>Trajectory Length<br>Step Accuracy (%)<br><!-- End of picture text -->

Figure 5: Accuracy across trajectory length buckets. 

35–50% on short trajectories to below 15% on long ones. In contrast, TRAJDEBUG remains substantially more stable, retaining over 20% accuracy on the longest bucket where the best baseline drops to around 14%. This suggests that TRAJDEBUG is still affected by increasing trajectory length, but evidence-grounded error detection and state-based candidate filtering help it degrade less sharply and yield larger gains on long-horizon trajectories. 

## **6 Application: Critical Error Detection as Feedback for Agent Improvement** 

Beyond diagnostic accuracy, a critical error detector is useful only if its outputs translate into measurable agent improvement. We evaluate TRAJDEBUG as a feedback source for the agent in two deployment scenarios on _τ_<sup>2</sup> -Bench (Barres et al., 2025) and a sampled set of 100 SWEBench Verified (Jimenez et al., 2024), covering both an idealized per-trajectory repair setting and a more realistic cross-trajectory transfer setting. In both scenarios, the actor is GLM-5.1, all detectors use Qwen3-235B-A22B-Thinking as the backbone, and detector-produced feedback is injected into the actor’s system prompt. We compare TRAJDEBUG against two baselines: _Vanilla_ , which directly prompts with the failed trajectory to find the critical error step and write feedback, and _Self-Reflection_ (Renze and Guven, 2024), which generates a reflection over the trajectory before producing the feedback. Details are in Appendix E.4. 

**Per-Trajectory Repair under Oracle Failure.** We assume oracle access to the success label of each rollout: for every failed trajectory, the detector produces a feedback, which is injected into the system prompt before re-executing the same task with the same actor. As shown in the upper block of Table 3, TRAJDEBUG delivers the largest gains 

7

<!-- Page 8 -->

|**Method**|**Airline**|**Retail**|**SWE-Bench**|
|---|---|---|---|
|_Per-Trajectory R_|_epair (Oracle Failur_|_e)_||
|Initial|78_._00|84_._21|72_._00|
|Self-Reflection|84_._00(+6_._00)|93_._86(+9_._65)|78_._00(+6_._00)|
|Vanilla Debug|88_._00(+10_._00)|93_._86(+9_._65)|80_._00(+8_._00)|
|**TRAJDEBUG**|**90**_._**00**(**+**12_._00)|**95**_._**61**(**+**11_._40)|**81**_._**00**(**+**9_._00)|
|_Failure-Memory_|_Transfer (Realistic)_|||
|Initial|78_._78|84_._21|71_._64|
|Self-Reflection|81_._81(+3_._03)|82_._89(-1_._32)|74_._63(+2_._99)|
|Vanilla Debug|75_._75(-3_._03)|88_._15(+3_._94)|71_._64(+0_._00)|
|**TRAJDEBUG**|**84**_._**84**(**+**6_._06)|**90**_._**78**(**+**6_._57)|**76**_._**12**(**+**4_._48)|



Table 3: Task success rate (%) when detector outputs are used as feedback for GLM-5.1. 

across all three settings, lifting the average success rate from 78 _._ 07 to 88 _._ 87, surpassing Vanilla Debug and Self-Reflection. The gap shows that more accurate critical-error localization produces more actionable feedback, beyond what holistic prompting or generic reflection can offer. 

**Failure-Memory Transfer to Held-Out Trajectories.** We further test a realistic deployment in which the detector is applied to only a small slice of historical failures and the resulting feedback must generalize to unseen tasks. For each subset, we split the trajectories per-dataset into a 1 _/_ 3 _memoryconstruction split_ and a 2 _/_ 3 _held-out evaluation split_ . On the memory-construction split, the detector produces feedback on each failed trajectory; all feedbacks are aggregated into a memory pool, which is then injected as a whole into the actor’s system prompt when evaluating on the held-out split. As shown in the lower block of Table 3, despite no per-instance oracle, TRAJDEBUG still yields the largest improvement, whereas Vanilla and Self-Reflection show less stable transfer and can even reduce performance in some cases. This indicates that the feedback induced by TRAJDEBUG encodes transferable failure patterns rather than instance-specific fixes, suggesting that critical error detection can serve as a low-cost source of reusable experience for long-horizon agents. 

## **7 Related Work** 

**Trajectory analysis and process supervision.** Recent work analyzes agent executions beyond final answers, including process reward models that assign step-level scores (Xi et al., 2026; Fan et al., 2026) and studies that summarize recurring failure modes such as coordination, tool-use, and planning errors (Cemri et al., 2026; Ma et al., 2024; Lu et al., 2024; Mulian et al., 2026; Ma et al., 2025). However, step-level scores do not isolate 

the failure-responsible step, and failure-mode taxonomies identify error categories rather than the decisive step in a specific trajectory. 

**Critical error attribution.** A recent line studies fine-grained failure attribution across multiagent reasoning (Zhang et al., 2025c; Chen et al., 2026; In et al., 2026; Banerjee et al., 2025), embodied and web environments (Zhu et al., 2025), and software engineering (Deshpande et al., 2025; Li et al., 2026). Methodologically, prompt-based approaches inspect raw or compressed trajectories with an LLM judge (Zhang et al., 2025c; Banerjee et al., 2025), but their diagnoses can be weakly grounded in evidence; taxonomy- and constraintbased approaches narrow the search space with predefined error categories or invariants (Zhu et al., 2025; Barke et al., 2026), yet miss errors that fall outside the schema; replay- and spectrumbased methods localize errors by re-executing or perturbing the trajectory (Ge et al., 2025), but require deterministic environments; graph-based methods model dependencies among trajectory elements (Wang et al., 2026; Zhang et al., 2025b,a; Li et al., 2026; Wang, 2026), but use connectedness as a proxy for terminal responsibility, leaving each error’s resolution status and terminal impact implicit. In contrast, TRAJDEBUG grounds error triggers in verbatim evidence, classifies error states, and performs attribution over terminal-relevant candidates, addressing both long-context error identification and ambiguity among multiple local errors. 

**Benchmarks for failure attribution.** Existing benchmarks are typically tied to a single domain and modest trajectory length: WhoAndWhen (Zhang et al., 2025c), TraceElephant (Chen et al., 2026), and MPBench (In et al., 2026) target multi-agent dialogues; AgentDebug (Zhu et al., 2025) covers embodied and web tasks; and TRAIL (Deshpande et al., 2025) and CodeTracer (Li et al., 2026) focus on code agents. TRAJERRBENCH complements them with 486 manually annotated long-horizon trajectories from customer-service tool use (Barres et al., 2025) and repository-scale software engineering (Deng et al., 2025), with up to _∼_ 120 steps per trajectory, exposing critical errors under long-range evidence dependencies and multiple coexisting local errors. 

8

<!-- Page 9 -->

## **8 Conclusion** 

We presented TRAJDEBUG, a three-stage errorlifecycle tracing framework for critical error detection. It combines error trigger detection, error state classification, and candidate-set-guided attribution to identify errors in long trajectories and distinguish failure-responsible errors among multiple errors. We also introduced TRAJERRBENCH, a benchmark of 486 manually annotated failed trajectories from realistic tool-use and coding scenarios. Experiments show that TRAJDEBUG outperforms LLM prompting and diagnostic baselines, and application studies demonstrate its value for trajectory repair and transferable failure memory. These results position critical error detection as a promising interface for inference-time agent improvement. 

## **9 Limitations** 

We discuss the limitations of our work here, including two main aspects: (1) Although TRAJDEBUG constrains judgments with verbatim evidence and structured candidates, it still relies on LLMs for error interpretation and final attribution. Its predictions may therefore be affected by the model’s reasoning ability, domain knowledge, and calibration. To reduce the concern that the gains merely come from using a stronger judge, we implement TRAJDEBUG with an open-source backbone rather than the strongest proprietary models; even under this setting, TRAJDEBUG outperforms direct prompting with frontier models and all multi-agent baselines on average. (2) As a staged pipeline, TRAJDEBUG may inherit false negatives from earlier trigger detection or state classification stages, causing the final candidate set to miss the true critical error. To mitigate this, the attribution stage allows an out-ofset prediction only under strict evidence requirements: the model must explain why the retained candidates do not account for the failure and provide the missing trigger, violated reference, origin step, and terminal footprint. 

## **10 Ethical Considerations** 

We discuss three ethical considerations. (1) _Intellectual property._ We respect the licenses of all artifacts used in this work, including datasets, models, and code repositories. We will release TRAJDEBUG, the associated code, and TRAJERRBENCH under the MIT license<sup>2</sup> . (2) _Intended use and risk_ 

> 2https://opensource.org/license/mit 

_control._ TRAJDEBUG is designed to trace the error lifecycle for critical error detection in failed agent trajectories. The data used in this work is anonymized to the best of our knowledge. Since the framework may still produce incorrect predictions due to model and method limitations, users should manually verify important diagnoses before using them in high-stakes settings. (3) _AI assistance._ We used AI to refine the wording of some sentences. 

## **Acknowledgments** 

This work is supported by the 2025 Tencent RhinoBird Joint Research Program (JR2025TEG013). 

## **References** 

- Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, and 1 others. 2023. Gpt-4 technical report. _arXiv preprint arXiv:2303.08774_ . 

- Anthropic. 2026a. Introducing claude opus 4.6. Accessed: 2026-02-05. 

- Anthropic. 2026b. Introducing claude sonnet 4.6. Accessed: 2026-02-17. 

- Adi Banerjee, Anirudh Nair, and Tarik Borogovac. 2025. Where did it all go wrong? a hierarchical look into multi-agent error attribution. _arXiv preprint arXiv:2510.04886_ . 

- Shraddha Barke, Arnav Goyal, Alind Khare, Avaljot Singh, Suman Nath, and Chetan Bansal. 2026. Agentrx: Diagnosing ai agent failures from execution trajectories. _arXiv preprint arXiv:2602.02475_ . 

- Victor Barres, Honghua Dong, Soham Ray, Xujie Si, and Karthik Narasimhan. 2025. _τ_<sup>2</sup> -bench: Evaluating conversational agents in a dual-control environment. _Preprint_ , arXiv:2506.07982. 

- Mert Cemri, Melissa Z Pan, Shuyi Yang, Lakshya A Agrawal, Bhavya Chopra, Rishabh Tiwari, Kurt Keutzer, Aditya Parameswaran, Dan Klein, Kannan Ramchandran, and 1 others. 2026. Why do multiagent llm systems fail? _Advances in Neural Information Processing Systems_ , 38. 

- Mengzhuo Chen, Junjie Wang, Fangwen Mu, Yawen Wang, Zhe Liu, Huanxiang Feng, and Qing Wang. 2026. Seeing the whole elephant: A benchmark for failure attribution in llm-based multi-agent systems. _arXiv preprint arXiv:2604.22708_ . 

- Xiang Deng, Jeff Da, Edwin Pan, Yannis Yiming He, Charles Ide, Kanak Garg, Niklas Lauffer, Andrew Park, Nitin Pasari, Chetan Rane, and 1 others. 

9

<!-- Page 10 -->

2025. Swe-bench pro: Can ai agents solve longhorizon software engineering tasks? _arXiv preprint arXiv:2509.16941_ . 

- Darshan Deshpande, Varun Gangal, Hersh Mehta, Jitin Krishnan, Anand Kannappan, and Rebecca Qian. 2025. Trail: Trace reasoning and agentic issue localization. _arXiv preprint arXiv:2505.08638_ . 

- Shengda Fan, Xuyan Ye, Yupeng Huo, Zhi-Yuan Chen, Yiju Guo, Shenzhi Yang, Wenkai Yang, Shuqi Ye, Jingwen Chen, Haotian Chen, and 1 others. 2026. Agentprocessbench: Diagnosing step-level process quality in tool-using agents. _arXiv preprint arXiv:2603.14465_ . 

- Tianyu Gao, Howard Yen, Jiatong Yu, and Danqi Chen. 2023. Enabling large language models to generate text with citations. In _Empirical Methods in Natural Language Processing (EMNLP)_ . 

- Yu Ge, Linna Xie, Zhong Li, Yu Pei, and Tian Zhang. 2025. Who is introducing the failure? automatically attributing failures of multi-agent systems via spectrum analysis. _arXiv preprint arXiv:2509.13782_ . 

- Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, and 1 others. 2025. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. _arXiv preprint arXiv:2501.12948_ . 

- Yeonjun In, Mehrab Tanjim, Jayakumar Subramanian, Sungchul Kim, Uttaran Bhattacharya, Wonjoong Kim, Sangwu Park, Somdeb Sarkhel, and Chanyoung Park. 2026. Rethinking failure attribution in multi-agent systems: A multi-perspective benchmark and evaluation. _arXiv preprint arXiv:2603.25001_ . 

- Carlos E Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, and Karthik Narasimhan. 2024. Swe-bench: Can language models resolve real-world github issues? In _International Conference on Learning Representations_ , volume 2024, pages 54107–54157. 

- Han Li, Yifan Yao, Letian Zhu, Rili Feng, Hongyi Ye, Jiaming Wang, Yancheng He, Pengyu Zou, Lehan Zhang, Xinping Lei, and 1 others. 2026. Codetracer: Towards traceable agent states. _arXiv preprint arXiv:2604.11641_ . 

- Jiaying Lu, Bo Pan, Jieyi Chen, Yingchaojie Feng, Jingyuan Hu, Yuchen Peng, and Wei Chen. 2024. Agentlens: Visual analysis for agent behaviors in llmbased autonomous systems. _IEEE Transactions on Visualization and Computer Graphics_ . 

- Chang Ma, Junlei Zhang, Zhihao Zhu, Cheng Yang, Yujiu Yang, Yaohui Jin, Zhenzhong Lan, Lingpeng Kong, and Junxian He. 2024. Agentboard: An analytical evaluation board of multi-turn llm agents. _Advances in neural information processing systems_ , 37:74325–74362. 

- Xuyan Ma, Xiaofei Xie, Yawen Wang, Junjie Wang, Boyu Wu, Mingyang Li, and Qing Wang. 2025. Diagnosing failure root causes in platform-orchestrated agentic systems: Dataset, taxonomy, and benchmark. _arXiv preprint arXiv:2509.23735_ . 

- Grégoire Mialon, Clémentine Fourrier, Thomas Wolf, Yann LeCun, and Thomas Scialom. 2024. Gaia: a benchmark for general ai assistants. In _International Conference on Learning Representations_ , volume 2024, pages 9025–9049. 

- Hadar Mulian, Sergey Zeltyn, Ido Levy, Liane Galanti, Avi Yaeli, and Segev Shlomov. 2026. Agentfixer: From failure detection to fix recommendations in llm agentic systems. _arXiv preprint arXiv:2603.29848_ . 

- Hao Peng, Xiaozhi Wang, Jianhui Chen, Weikai Li, Yunjia Qi, Zimu Wang, Zhili Wu, Kaisheng Zeng, Bin Xu, Lei Hou, and 1 others. 2023. When does in-context learning fall short and why? a study on specificationheavy tasks. _arXiv preprint arXiv:2311.08993_ . 

- Yunjia Qi, Hao Peng, Xiaozhi Wang, Amy Xin, Youfeng Liu, Bin Xu, Lei Hou, and Juanzi Li. 2026. Agentif: Benchmarking large language models instruction following ability in agentic scenarios. _Advances in Neural Information Processing Systems_ , 38. 

- Matthew Renze and Erhan Guven. 2024. Self-reflection in llm agents: Effects on problem-solving performance. _arXiv preprint arXiv:2405.06682_ . 

- Gemini Team, Rohan Anil, Sebastian Borgeaud, JeanBaptiste Alayrac, Jiahui Yu, Radu Soricut, Johan Schalkwyk, Andrew M Dai, Anja Hauth, Katie Millican, and 1 others. 2023. Gemini: a family of highly capable multimodal models. _arXiv preprint arXiv:2312.11805_ . 

- Kimi Team, Tongtong Bai, Yifan Bai, Yiping Bao, SH Cai, Yuan Cao, Y Charles, HS Che, Cheng Chen, Guanduo Chen, and 1 others. 2026. Kimi k2. 5: Visual agentic intelligence. _arXiv preprint arXiv:2602.02276_ . 

- Xingyao Wang, Boxuan Li, Yufan Song, Frank F Xu, Xiangru Tang, Mingchen Zhuge, Jiayi Pan, Yueqi Song, Bowen Li, Jaskirat Singh, and 1 others. 2025. Openhands: An open platform for ai software developers as generalist agents. In _International Conference on Learning Representations_ , volume 2025, pages 65882–65919. 

- Yawen Wang, Wenjie Wu, Junjie Wang, and Qing Wang. 2026. From flat logs to causal graphs: Hierarchical failure attribution for llm-based multi-agent systems. _arXiv preprint arXiv:2602.23701_ . 

- Zhaohui Geoffrey Wang. 2026. Agenttrace: Causal graph tracing for root cause analysis in deployed multi-agent systems. _arXiv preprint arXiv:2603.14688_ . 

- xAI. 2025. Grok 4 fast model card. https://data.x. ai/2025-09-19-grok-4-fast-model-card.pdf. Last updated: September 19, 2025. 

10

<!-- Page 11 -->

- Zhiheng Xi, Chenyang Liao, Guanyu Li, Zhihao Zhang, Wenxiang Chen, Binghai Wang, Senjie Jin, Yuhao Zhou, Jian Guan, Wei Wu, and 1 others. 2026. Agentprm: Process reward models for llm agents via stepwise promise and progress. In _Proceedings of the ACM Web Conference 2026_ , pages 4184–4195. 

- Yizhe Xie, Congcong Zhu, Xinyue Zhang, Tianqing Zhu, Dayong Ye, Minfeng Qi, Huajie Chen, and Wanlei Zhou. 2026. From spark to fire: Modeling and mitigating error cascades in llm-based multi-agent collaboration. _arXiv preprint arXiv:2603.04474_ . 

- An Yang, Anfeng Li, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, Chang Gao, Chengen Huang, Chenxu Lv, and 1 others. 2025. Qwen3 technical report. _arXiv preprint arXiv:2505.09388_ . 

- Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, Tom Griffiths, Yuan Cao, and Karthik Narasimhan. 2023. Tree of thoughts: Deliberate problem solving with large language models. _Advances in neural information processing systems_ , 36:11809–11822. 

- Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. 2022. React: Synergizing reasoning and acting in language models. _arXiv preprint arXiv:2210.03629_ . 

- Aohan Zeng, Xin Lv, Zhenyu Hou, Zhengxiao Du, Qinkai Zheng, Bin Chen, Da Yin, Chendi Ge, Chenghua Huang, Chengxing Xie, and 1 others. 2026. Glm-5: from vibe coding to agentic engineering. _arXiv preprint arXiv:2602.15763_ . 

- Guibin Zhang, Junhao Wang, Junjie Chen, Wangchunshu Zhou, Kun Wang, and Shuicheng Yan. 2025a. Agentracer: Who is inducing failure in the llm agentic systems? _arXiv preprint arXiv:2509.03312_ . 

- Heng Zhang, Yuling Shi, Xiaodong Gu, Haochen You, Zijian Zhang, Lubin Gan, Yilei Yuan, and Jin Huang. 2025b. Graphtracer: Graph-guided failure tracing in llm agents for robust multi-turn deep search. _arXiv preprint arXiv:2510.10581_ . 

- Shaokun Zhang, Ming Yin, Jieyu Zhang, Jiale Liu, Zhiguang Han, Jingyang Zhang, Beibin Li, Chi Wang, Huazheng Wang, Yiran Chen, and 1 others. 2025c. Which agent causes task failures and when? on automated failure attribution of llm multi-agent systems. _arXiv preprint arXiv:2505.00212_ . 

- Kunlun Zhu, Zijia Liu, Bingxuan Li, Muxin Tian, Yingxuan Yang, Jiaxun Zhang, Pengrui Han, Qipeng Xie, Fuyang Cui, Weijia Zhang, and 1 others. 2025. Where llm agents fail and how they can learn from failures. _arXiv preprint arXiv:2509.25370_ . 

11

<!-- Page 12 -->

## **A Pilot Study Details** 

**Data sources and annotators.** For Pilot Study 2, we randomly sample 50 failed trajectories from WhoAndWhen (Zhang et al., 2025c) and AgentDebugBench (Zhu et al., 2025), drawing 10 trajectories from each subset of the two benchmarks, with 1 _,_ 373 steps in total. The critical-error label of each trajectory is inherited from the source dataset, since both benchmarks already provide groundtruth critical-error annotations for their failed trajectories; we therefore only annotate per-step local errors and their downstream states. All annotations are produced by three computer-science undergraduates who completed a calibration training round on a separate set of trajectories before working on the pilot data. 

**Detector evaluation (§2.2).** For the detector comparison in §2.2, we evaluate seven advanced models: GLM-5.1 (Zeng et al., 2026), Gemini-3.1Pro (Team et al., 2023), DeepSeek-V4-Pro (Guo et al., 2025), Claude Sonnet 4.6 (Anthropic, 2026b), Claude Opus 4.6 (Anthropic, 2026a), GPT-5.4 (Achiam et al., 2023), and Qwen3-235BA22B (Yang et al., 2025). All models are queried with the same direct-prompt template used by the direct prompting baselines (Table E.1) at temperature 0, and a prediction is counted as correct only when the predicted step index exactly matches the critical error step provided by the source dataset. 

**Local error step annotation (§2.2, §2.3).** We recruit a pool of 20 annotators in total, all of whom completed a calibration training round on a heldout set of trajectories. Annotators were compensated at rates consistent with the prevailing market standards for comparable annotation work. Three annotators independently inspect each step. Following the annotation principles established in prior process-supervision work (Fan et al., 2026), each annotator is required to (i) judge each step strictly along the agent’s own reasoning, action, and observation, without using their own task knowledge to fill in unstated steps; (ii) mark a step as erroneous only when the error can be tied to an explicit, objective trigger, such as a violated task constraint, a contradicted observation, or an internally inconsistent claim; and (iii) write a short, reproducible reason that cites the specific evidence supporting the judgment. Vague reasons (e.g., “the agent seems off-track”) are rejected and the step is not added to the error set. A step enters the error set only 

when all three annotators independently mark it as erroneous and each provides an evidence-grounded reason; disagreements are kept as non-errors to avoid inflating the error set with subjective calls. This protocol yields 381 local error steps. The Fleiss’ _κ_ on error identification is 0 _._ 538, indicating moderate agreement and confirming that, even under an evidence-grounded protocol, identifying step-level errors in long agent trajectories remains genuinely hard for humans. 

**Downstream-state annotation of non-critical local errors (§2.3).** For the downstream-state analysis in §2.3, the same three annotators independently classify each of the 331 non-critical local errors into one of three outcomes: _repaired_ , _persistent_ , or _unrepaired yet dormant_ . We attach an evidence requirement to each label so that state judgments remain reproducible. A _repaired_ label follows the resolution criterion in §3.3: a later step must explicitly revisit the same reference object and supersede the wrong commitment, for example by satisfying the violated constraint, acting on the corrected state, or retracting the prior wrong claim; the annotator must cite the specific repairing step. A _persistent_ label requires the annotator to write an explicit reason together with the evidence from a later step that still uses or relies on the wrong commitment introduced at the error step. An _unrepaired yet dormant_ label is reserved for cases where no later step depends on the erroneous content, for example a step that miscounts four search results as two when no subsequent reasoning or action references the count; the annotator must state why the wrong content is never used downstream. The boundary between _persistent_ and _unrepaired yet dormant_ is therefore decided by the presence of a downstream reference: persistent requires a citable later usage of the wrong content, while dormant requires explaining its absence. A label is kept only when all three annotators independently agree, following the same unanimous-agreement criterion used for local error identification. The Fleiss’ _κ_ on downstream-state labels is 0 _._ 378, lower than the agreement on error identification and consistent with the view that state judgments require additional reasoning over downstream references and are therefore harder to align across annotators. 

12

<!-- Page 13 -->

## **B TRAJERRBENCH Details** 

### **B.1 Dataset Construction** 

We construct TRAJERRBENCH from two complementary domains: 400 rollouts on the airline and retail tasks of _τ_<sup>2</sup> -Bench (Barres et al., 2025), produced by DeepSeek-Reasoner, GPT-5, Qwen3-Max and 86 rollouts on SWE-Bench Pro (Deng et al., 2025), produced by Claude-Opus-4-6 (Anthropic, 2026a), Kimi-K2.6-Coding (Team et al., 2026), Gemini-3.1-Pro (Team et al., 2023), Grok-4.20Beta (xAI, 2025), and GPT-5.4 (Achiam et al., 2023) from the OpenHands scaffold (Wang et al., 2025). The two subsets average 29 _._ 3 and 119 _._ 7 steps per trajectory, respectively. 

### **B.2 Annotation Details** 

Our annotation protocol follows the decisive-error annotation practice of WhoAndWhen (Zhang et al., 2025c). Annotators are given the task instruction, the full failed trajectory, and the final failure outcome, and are asked to identify the earliest step that directly causes the failure under the counterfactual definition in § 2.1. They do not need to execute an actual intervention; instead, they make an evidencegrounded attribution judgment from the trajectory, as in prior failure-attribution annotation. 

Since both benchmarks contain long and difficult failure trajectories, we first generate model-assisted pre-annotations to help annotators understand the likely failure points. Specifically, we ask GPT-5.4, Gemini-3.1-Pro, and Claude-Opus-4-6 to annotate each trajectory. Each model is given the full trajectory, the ground-truth task specification, and the failure information returned by the original benchmark evaluation. For _τ_<sup>2</sup> -Bench, this includes the unmet database constraints reported by the task environment; for SWE-Bench Pro, this includes the details of the failing test cases. Annotators then receive the same full information, together with the three model pre-annotations, as reference material during annotation. The pre-annotations are used only to support trajectory understanding; the final labels are determined by human annotators following the guideline below. 

**Agreement between pre-annotations and final labels.** To quantify potential anchoring from modelassisted pre-annotation, Table 4 reports the exactmatch rate between each model’s proposed critical step and the final human-majority label. Agreement varies substantially across models and subsets, and 

no single model consistently determines the final labels. Moreover, the pre-annotation setting provides benchmark failure details to aid human annotation, whereas all evaluated direct-prompting baselines receive only the failed trajectory and failure signal, without gold outcomes or auxiliary debugging information. 

Table 4: Exact-match agreement between modelassisted pre-annotations and final human-majority labels. 

|Subset|Pre-annotation model|Exact match|
|---|---|---|
|_τ_ <sup>2</sup>-Bench (_N_=400)|Claude Opus 4.6<br>Gemini 3.1 Pro<br>GPT-5.4|64_._5%<br>76_._8%<br>53_._2%|
||Claude Opus 4.6|48_._8%|
|SWE-Bench Pro (_N_=86)|Gemini 3.1 Pro|31_._4%|
||GPT-5.4|55_._8%|



The standardized guideline contains three principles. First, an annotated step must contain an explicit mistake supported by the available evidence, such as violating the task instruction, contradicting a previous observation, misusing a tool result, or making an internally inconsistent claim. Second, the mistake must be failure-responsible: annotators should not choose local mistakes that are later corrected or errors whose downstream effect never affects the final outcome. Third, if multiple failureresponsible mistakes are present, annotators choose the earliest such step, following the principal-cause convention used by WhoAndWhen (Zhang et al., 2025c). Each annotator also writes a short explanation for the selected step so that disagreements can be checked against concrete evidence. 

**Annotator pool and labelling protocol.** We recruit a pool of 20 annotators in total, all of whom completed a calibration training round on a heldout set of trajectories covering both _τ_<sup>2</sup> -Bench and SWE-Bench Pro before working on the released data. Annotators were compensated at rates consistent with the prevailing market standards for comparable annotation work. Because decisive-error localization is inherently ambiguous in long agent trajectories, each trajectory is independently annotated by 3 annotators and the final label is taken by majority vote: a label is kept when at least 2 of the 3 annotators agree. We apply the same threeannotator majority-vote protocol to the referencecategory labels ( _Task Conflict_ , _History Conflict_ , and _Intra-Step Conflict_ ) and to the execution-phase labels ( _planning_ , _reasoning_ , _action_ , _observation_ , _verification_ ). 

13

<!-- Page 14 -->

**Inter-annotator agreement.** Table 5 reports inter-annotator agreement for the critical-error step, the execution-phase label, and the referencecategory label on each subset of TRAJERRBENCH. On _τ_<sup>2</sup> -Bench, the critical-error step reaches almostperfect agreement (Fleiss’ _κ_ =0 _._ 91), while the execution-phase and reference-category labels reach substantial and fair agreement respectively. For SWE-Bench Pro, we initially annotate 110 trajectories, including ambiguous cases on which no two annotators select the same critical step. The released benchmark and all experiments use only the 86 trajectories for which at least two of three annotators agree on the critical step; Table 5 reports agreement on this retained set. Agreement is lower than on _τ_<sup>2</sup> -Bench, reflecting the longer and more code-heavy trajectories: the criticalerror step reaches substantial agreement (Fleiss’ _κ_ =0 _._ 674), while execution-phase and referencecategory agreement is moderate and fair, respectively. Despite this, 98 _._ 2% of _τ_<sup>2</sup> -Bench trajectories and 91 _._ 9% of SWE-Bench Pro trajectories receive a reference-category label on which at least 2 of 3 annotators agree, indicating that the majority-vote protocol yields a usable label on the overwhelming majority of trajectories. 

Table 5: Inter-annotator agreement on TRAJERRBENCH. “Pairwise” denotes pairwise agreement. 

|Subset|Label|Fleiss’_κ_|Pairwise|
|---|---|---|---|
||Critical-error step|0_._91|91_._2%|
|_τ_ <sup>2</sup>-Bench|Execution phase|0_._73|84_._0%|
||Reference category|0_._41|68_._9%|
||Critical-error step|0_._67|66_._7%|
|SWE-Bench Pro|Execution phase|0_._42|61_._8%|
||Reference category|0_._38|52_._4%|



### **B.3 Distribution of Critical Errors** 

Figures 6 and 7 show the joint distribution of critical errors over the execution phase, error subtype, and reference category for the _τ_<sup>2</sup> -Bench and SWEBench Pro subsets of TRAJERRBENCH respectively. The flows in each diagram are read from left (execution phase) to right (reference category), with the middle column showing the fine-grained error subtype. 

**Execution phase.** Among critical errors with an agreed execution-phase label, _τ_<sup>2</sup> -Bench is heavily skewed toward reasoning (60 _._ 7%), followed by planning (14 _._ 8%) and observation (13 _._ 5%), with action (6 _._ 1%) and verification (4 _._ 8%) contributing 

the rest. This indicates that on tool-use tasks, critical errors more often arise when the agent interprets accumulated context than when it issues an isolated action. In SWE-Bench Pro, reasoning is still the largest phase (57 _._ 1%), followed by planning (15 _._ 6%), verification (14 _._ 3%), and action (13 _._ 0%). This shift is consistent with the patch-and-test nature of software-engineering trajectories: the agent spends comparatively more time editing code and validating it, and a larger share of failures appears in those phases. 

**Error subtype.** The middle column reveals which fine-grained agent behaviour is most failure-prone within each phase. On _τ_<sup>2</sup> -Bench, the top three subtypes reason.InvalidInference (22 _._ 8%), reason.WrongChoice (22 _._ 2%), and reason.MissingAssumptionCheck (14 _._ 5%) jointly account for nearly 60% of critical errors, indicating that the dominant failure mode is inference over already-observed context rather than acting on incorrect observations. On SWE-Bench Pro, the distribution becomes more peaked: reason.WrongChoice alone accounts for 40 _._ 7% of critical errors, followed by plan.BadDecomposition (14 _._ 0%) and verify.NoVerification (9 _._ 3%), suggesting that failures cluster around selecting the wrong implementation path and skipping verification before submission. 

**Reference category.** On the right column, both subsets are dominated by external references rather than intra-step contradictions: among critical errors with an agreed reference-category label, _Task Conflict_ and _History Conflict_ together cover 98 _._ 7% of _τ_<sup>2</sup> -Bench and 97 _._ 5% of SWE-Bench Pro critical errors, while _Intra-Step Conflict_ accounts for only 1 _._ 3% and 2 _._ 5%, respectively. The two subsets differ in which external reference is violated more often: _τ_<sup>2</sup> -Bench is balanced between _Task Conflict_ (52 _._ 4%) and _History Conflict_ (46 _._ 3%), reflecting failures that violate either explicit user constraints or earlier tool observations; SWE-Bench Pro is more strongly skewed toward _Task Conflict_ (73 _._ 4% vs. 24 _._ 1% _History Conflict_ ), consistent with codetask failures where the violated reference is most often the task instruction or expected behaviour rather than an intermediate observation. 

**Joint patterns.** Reading the diagrams jointly, two patterns stand out. First, the reasoning phase is the dominant entry channel into both _Task Con-_ 

14

<!-- Page 15 -->

![](assets/077/paper-0015-00.png)


<!-- Start of picture text -->
Tau2Bench: Critical Error Analysis<br>Step -> Type -> Subtype -> Conflict Object<br>Error Step Error Error Conflict<br>Position Type Subtype Object<br>Step 3-10 (68)<br>InvalidInference (91)<br>Task Conflict (206)<br>Step 11-15 (99) REASON (238)<br>WrongChoice (89)<br>MissingAssumptionCheck (58)<br>Step 16-20 (97)<br>BadDecomposition (32)<br>PLAN (58) IgnoreOutput (26)<br>MisreadOutput (21)<br>Histroy Conflict (182)<br>Step 21-30 (110) OBS (53) WrongOrder (17)<br>PrematureTermination (11)<br>WrongActionSequence (10)<br>WrongTool (8)<br>ACT (24) NoVerification (8)<br>UnrealisticPlan (6)<br>Step 31+ (26) VERIFY (19) GroundingFail (6)<br>ToolSchemaMismatch (4) Intra-Step Conflict (5)<br><!-- End of picture text -->

Figure 6: Distribution of critical errors in _τ_<sup>2</sup> -Bench. Flows go from execution phase (left) to error subtype (middle) to reference category (right). 

_flict_ and _History Conflict_ in both subsets, suggesting that strengthening evidence-grounded reasoning is the single highest-leverage intervention for critical-error reduction. Second, the planning phase flows almost exclusively into _Task Conflict_ , whereas observation-phase failures flow almost exclusively into _History Conflict_ ; this clean separation reflects the underlying definitions and supports using the reference category as a complementary axis to the execution phase when analysing failure mechanisms. 

Table 6: Overview of the case study trajectory. 

|Field|Value|
|---|---|
|Dataset|_τ_ <sup>2</sup>-Bench(airline)|
|Agent model|qwen3-max|
|Trajectory length|49 steps|
|Final outcome|Failed (transferred to human)|
|Detected triggers|15|
|Detected instances|9|
|Candidate instances|4 (in_F_(_τ_))|
|TRAJDEBUGcritical step|25|
|Human-annotated step|25|



## **C Case Studies** 

We present an end-to-end case to illustrate how TRAJDEBUG localizes the critical error within a long failed trajectory. The example is drawn from the airline subset of _τ_<sup>2</sup> -Bench, where qwen3-max acts as the agent and the user requests several modifications to an existing reservation under a budget cap of $200. The trajectory contains 49 steps and ends with the agent transferring the conversation to a human operator. TRAJDEBUG selects step 25 as the critical error, matching the human annotation exactly. 

### **C.1 Case Overview** 

**Task.** User yara_garcia_1905 asks the agent to modify reservation HXDUBJ: change the outbound 

flight to a direct flight one day later, push the return flight back by one day, and, within a $200 budget, consider upgrading to business class and adding checked baggage. The system policy explicitly states that all flights in the same reservation must share the same cabin class. 

**Trajectory summary.** The trajectory can be decomposed into three phases. _Flight modification (steps 0–18)._ The agent retrieves the reservation, searches for direct flights, and successfully updates the booking to the new outbound (HAT072) and return (HAT278) flights in economy. _Upgrade negotiation (steps 19–24)._ The agent computes the cost of upgrading both flights to business as $408, which exceeds the user’s $200 budget; the user then asks whether only the outbound flight can be 

15

<!-- Page 16 -->

![](assets/077/paper-0016-00.png)


<!-- Start of picture text -->
SWE-Bench Pro: Critical Error Analysis<br>Step -> Type -> Subtype -> Conflict Object<br>Error Step Error Error Conflict<br>Position Type Subtype Object<br>Step 3-10 (3)<br>Step 16-20 (2)<br>Step 21-30 (4)<br>WrongChoice (35)<br>REASON (44)<br>Task Conflict (58)<br>Step 31+ (77)<br>BadDecomposition (12)<br>PLAN (12)<br>NoVerification (8)<br>VERIFY (11)<br>Histroy Conflict (19)<br>MissingAssumptionCheck (6)<br>ACT (10)<br>ToolSchemaMismatch (4) Intra-Step Conflict (2)<br><!-- End of picture text -->

Figure 7: Distribution of critical errors in SWE-Bench Pro. Flows go from execution phase (left) to error subtype (middle) to reference category (right). 

upgraded. _Cascading failure (steps 25–48)._ The agent commits to the partial-upgrade plan, executes the corresponding API call, and enters a chain of payment failures and repeated retries that finally end in a hand-off to a human agent. 

### **C.2 The Critical Error** 

#### **Step 25 (assistant) — Critical Error** 

_Upgrading only the outbound flight (HAT072) to business class costs $282. Since your current outbound flight costs $130, the upgrade requires an additional $152. Given your budget of $200, this upgrade is within your budget. As a gold member, you will still enjoy two free checked bags on both flights. Please confirm whether you would like to proceed with upgrading only the outbound flight to business._ 

The agent commits to a plan that violates the reservation-level uniform-cabin policy stated in the system prompt. The trigger detector flags this step as a _Task Conflict_ in the _planning_ phase with the wrong commitment “upgrade only the outbound flight to business” and the violated reference being the policy “all flights in the same reservation must share the same cabin class”. Because this commitment cannot be repaired without retracting the plan, the resulting error instance has a _semantic_ terminal footprint and the state label _Manifest Active_ , which keeps it in the candidate set _F_ ( _τ_ ). 

### **C.3 Detected Error Instances** 

TRAJDEBUG clusters the 15 per-step triggers into 9 object-anchored error instances. Table 7 lists them with origin step, state label, and a short description. Four instances (origin steps 13, 25, 33, 39) survive state-based filtering and form the candidate set _F_ ( _τ_ ). 

### **C.4 Error Propagation and Attribution** 

Although several earlier instances contain genuine local mistakes, only the critical instance at step 25 has a wrong commitment that directly causes the terminal failure. The propagation path is: (i) at step 27, the agent issues update_reservation_flights with cabin=business but provides the return flight at its economy price, so the system charges both flights as business ($282+$443=$725), exceeding the gift-card balance; (ii) at step 31, the agent switches to another gift card and reissues the same invalid call, which again fails; (iii) the agent then misattributes the failure to a payment-side problem and enters a payment-retry chain (instances 5 and 8, steps 33–43), exhausting the remaining budget before transferring to a human at step 45. 

Within the candidate set _F_ ( _τ_ ), the causal attribution stage compares: (a) instance 1 (budget debt, origin step 13): a financial-calculation error that 

16

<!-- Page 17 -->

Table 7: Detected error instances in the case-study trajectory. Instances marked with _⋆_ form the candidate set _F_ ( _τ_ ), and the row marked _†_ is the critical instance selected by TRAJDEBUG. 

|ID|Origin|Triggers|Reference category|State label|Description|
|---|---|---|---|---|---|
|0|9|9|Task Conflict|Clean Resolution|Flight search ignores the user-<br>specified 8 am–9 pm time window,<br>but the next turn still yields a feasi-<br>ble option.|
|1<sup>_⋆_</sup>|13|13, 19, 23|History Conflict|Costly Resolution (budget debt)|Financial computations omit the<br>non-refundable $30 insurance fee,<br>propagating through the refund and<br>upgrade-cost estimates.|
|2|15|15|Task Conflict|Clean Resolution|The agent incorrectly claims that<br>travel insurance waives change fees.|
|3<br>|21|21|Task Conflict|Clean Resolution|The agent queries user details when<br>the budget is already obviously in-<br>sufficient.|
|4<sup>_⋆†_</sup>|25|25, 27, 31|Task Conflict|Manifest Active (semantic)|Commits to upgrading only the<br>outbound<br>flight,<br>violating<br>the<br>reservation-level<br>uniform-cabin<br>policy.|
|5<sup>_⋆_</sup>|33|33, 41|Task Conflict|Manifest Active (semantic)|Repeatedly proposes split payment<br>in a single update_reservation<br>call, which the API does not sup-<br>port.|
|6|35|35|History Conflict|Clean Resolution|Attempts to pay with a certificate<br>whose balance ($150) is below the<br>required amount.|
|7|37|37|History Conflict|Clean Resolution|Reuses a payment method that has<br>already failed in a prior step.|
|8<sup>_⋆_</sup>|39|39, 43|History Conflict|Manifest Active (semantic)|Repeatedly retries the same failed<br>gift_card_1646646<br>payment<br>without addressing the underlying<br>cause.|



wastes budget but does not by itself prevent task completion; (b) instance 4 (semantic, origin step 25): a plan that violates a system constraint and makes the requested upgrade infeasible regardless of payment choice; (c) instances 5 and 8 (semantic, origin steps 33 and 39): downstream payment-side errors that occur only because the agent is already trying to execute the impossible plan committed at step 25. Removing instance 4 would eliminate instances 5 and 8 and let the agent either accept the over-budget upgrade or decline it cleanly, while removing instance 1 would still leave the partialupgrade commitment unresolved. Step 25 is therefore selected as the critical error step _t_<sup>_⋆_</sup> . 

### **C.5 Discussion** 

The case illustrates how the three stages of TRAJDEBUG support long-horizon failure analysis. First, error trigger detection grounds local mistakes in explicit conflicts, such as the uniform-cabin policy violation at step 25. Second, error state classification groups repeated triggers into objectanchored instances and distinguishes corrected errors (e.g., instances 0, 2, 3) from terminal-relevant 

states such as budget debt and manifest active commitments. Third, causal attribution compares the remaining candidates by their role in the failure rather than by temporal order alone, which is why TRAJDEBUG selects the later step 25 instead of the earlier financial error. 

## **D TRAJDEBUG Implementation Details** 

All experiments use Qwen3-235B-A22BThinking (Yang et al., 2025) as the base model, with temperature fixed at 0 for reproducibility. Following the error-lifecycle tracking perspective in §3.3, TRAJDEBUG operationalizes critical error detection through three stages: error trigger detection, error state classification, and causal attribution. To handle long trajectories, we use the multi-granularity compression scheme in §3.1. The high-detail view (th1) keeps up to 3000 characters, the medium-detail view (th2) keeps up to 1200 characters, and the low-detail view (th3) keeps up to 600 characters. 

Each downstream stage uses these views according to its own evidence requirements. In the _error trigger detection_ stage, the current step and his- 

17

<!-- Page 18 -->

tory within two steps are rendered with th1, history three to five steps away is rendered with th2, and more distant history is rendered with th3. Only the history before the current step is included in this view; the current step is provided separately in th1 for local verification. In the _error state classification_ stage, trigger steps are rendered with th1 and all other steps are rendered with th3 as background context for instance clustering; for state classification, the origin step, the last trigger step, and a fixed number of following steps are always rendered with th1. The remaining context is rendered by falling back in the order th1 _→_ th2 _→_ th3 _→_ raw, with inline annotations indicating the associated error instance. For _budget debt_ , we use a Python script to check whether the distance between the origin step and the repair step exceeds 50% of the trajectory length. In the _causal attribution_ stage, the full trajectory is rendered with the same fallback order th1 _→_ th2 _→_ th3 _→_ raw, with an additional 800-character truncation limit. 

We list the complete system prompts for the compression step and the three stages of TRAJDEBUG: error trigger detection, error state classification, and causal attribution. 

### **Multi-Granularity Compression Prompt.** 

#### **Stage A — Trajectory Compression** 

- You are compressing a single trajectory step at THREE different compression levels for downstream agent error diagnosis. Produce a detailed version (th1), a 

- moderate version (th2), and a concise version (th3) of the same step content. 

- 1. PRESERVE SEMANTIC CORE: Compression removes ONLY redundant phrasing, verbose boilerplate, repetitive expressions, and filler words. The core meaning of EVERY sentence must survive. When in doubt, keep more rather than less. 

2. CONSTRAINTS AND PLANS ARE CRITICAL: If the content contains ANY of the following, their key information MUST be 

preserved across ALL three tiers: 

- Constraints (time limits, budget limits, "do NOT do X" prohibitions, "must do Y first" preconditions, required formats, allowed/disallowed actions) 

- - Plans (specific action items, ordered steps, goals, subgoals, milestones) 

- - Requirements for subsequent steps (instructions that govern future behavior, expected outputs, acceptance criteria) 

- Conditional logic ("if X then Y", fallback strategies, error handling rules) 

- Drop surrounding prose before dropping any constraint or plan item. 

3. THREE-TIER COMPRESSION LEVELS: 

- th1 (detailed, <={th1_max} chars per field): Preserve all meaningful details. Remove only obvious redundancy, 

- repeated phrasings, and decorative formatting. Keep every distinct fact, constraint, action, and observation. 

- th2 (moderate, <={th2_max} chars per field): Merge related information. Omit secondary details and elaborations. But KEEP all constraints, key decisions, action outcomes, error messages, and critical observations. 

- th3 (concise, <={th3_max} chars per field): Retain only the most essential actions, results, errors, and constraints. Use minimal wording. Still preserve all hard constraints and critical factual anchors. 

================ PRESERVE VERBATIM ============= 

- Preserve the FOLLOWING classes of tokens VERBATIM (copy them exactly as written - do not translate, paraphrase, reorder, round, or abbreviate): 

- Proper nouns and named entities (people, places, brands, franchise/universe names such as "Disney", "Marvel", " MCU", book/paper/file names). 

- Product / part / SKU / ASIN / ISBN / DOI / arXiv identifiers and any alphanumeric IDs the environment returned. 

- - Numbers with their units exactly as given (prices like "$22 .50", quantities like "3 items", measurements like "45 min", percentages, counts). 

- Years and dates (including citation years like "(1976)", ISO dates, "Q3 2023"-style period labels). 

- - URLs, file paths, CLI flags, API parameter names and their literal values. 

- Quoted constraint phrases from the task statement (e.g. " avoid Tue", "refundable", "under $25", "first page only ") - keep them inside quotation marks if the original had them. 

- Tool / function names and their exact argument keys. 

- Error messages, status codes, truncation markers ("has_more: true", "output truncated", "403 Forbidden"). 

- You MAY rewrite the connective prose between these tokens to shorten the field; you MAY NOT rewrite the tokens themselves. If preserving them verbatim would push a field past the length cap, DROP the least-important surrounding prose first and keep the verbatim tokens. 

### **Error-Trigger Annotation Prompt.** 

#### **Stage 1 — Error Trigger Detection** 

- You are an error-trigger annotator for one step of an LLMagent trajectory. For the CURRENT STEP, decide which trigger tags (if any) fire. Each fired trigger falls into one of four categories: 

- cat-1 = the step conflicts with the TASK cat-2 = the step conflicts with VISIBLE CONTEXT (env / tool output / system feedback / prior environment-rendered fact) 

- cat-3 = the step is INTERNALLY INCONSISTENT - its claim contradicts something the same message states verbatim, or contradicts the agent's own prior plan / reflection / memory 

- env = the agent's tool call at THIS step is correct but the environment response is anomalous; 

- === CHECKLIST (A) - conflict with TASK (cat-1) === 

- [ ] The step's plan permanently drops a sub-task / sub-goal / deliverable the TASK explicitly requires, with no TODO / "later" / sequencing intent in the step itself, and HISTORY does not already cover it. Phased execution that still keeps deferred items in scope is NOT a 

- trigger. -> plan.BadDecomposition 

- [ ] The step's plan schedules a sub-task before another subtask whose output it depends on, and TASK itself dictates this ordering. 

   - -> plan.WrongOrder 

- [ ] The step depends on a tool / API / permission / data source that TASK or the environment does not provide. -> plan.UnrealisticPlan 

- [ ] Double-anchor required. (i) HISTORY contains a verbatim line where the agent was previously on-constraint; (ii) THIS step contains a verbatim line that explicitly 

- narrows / widens / replaces a TASK constraint. Both anchors must be in reference_quote. Gradual multi-step drift without an explicit single-step swerve is NOT a trigger here. 

   - -> plan.GoalDrift 

- [ ] TASK explicitly requires verify / check / confirm of X, and THIS step delivers the final answer without performing that check. Implicit verification expectations are NOT a trigger here. 

   - -> verify.NoVerification 

- [ ] The step declares completion / returns the final answer / stops the trajectory while a TASK-required deliverable is still unmet. 

   - -> verify.PrematureTermination 

- [ ] The step performs an action that TASK or environment 

18

<!-- Page 19 -->

rules explicitly forbid (safety policy, permission boundary, forbidden endpoint, forbidden operation). -> act.UnsafeOrForbiddenAction 

- === CHECKLIST (B) - conflict with VISIBLE CONTEXT (cat-2) === 

- [ ] The step makes an explicit decision and cites supporting evidence, but the citation is distorted (wrong value, 

- wrong field, mis-paraphrased), and the wrong reading drives the decision. 

   - -> reason.WrongChoice 

- [ ] The step cites visible evidence correctly, but generalises the conclusion beyond what the evidence supports. 

   - [ ] The tool call is admissible but the returned observation is structurally insufficient because the tool is 

   - degenerate or blind on this target. 

      - -> env.ToolExtractorDegenerate 

   - [ ] The observation contains verbatim evidence of HTTP 429 / 5xx / timeout / connection reset / rate limited. 

      - -> env.RateLimitOrTransient 

   - [ ] The tool returns structurally empty / constant / payload identical to a prior call. 

      - -> env.EmptyOrRepeatedPayload 

   - === CONFIDENCE === 

- -> reason.InvalidInference 

      - For each trigger fill ``` confidence ``` : 

- [ ] The step relies on a prior tool call / observation / fact that does NOT actually appear in HISTORY ( fabricated cross-message reference into a context that should exist). 

   - -> reason.MissingAssumptionCheck 

- [ ] (a) The chosen tool or data source is unsuited to the established sub-goal; OR (b) plan-action mismatch: this step commits to plan A but issues action B. 

   - -> act.WrongTool 

- [ ] A tool call is syntactically malformed against the visible schema or prior successful calls. -> act.ToolSchemaMismatch 

- [ ] The action order violates a workflow established by HISTORY or the visible UI / env state machine. -> act.WrongActionSequence 

      - high : (C1)+(C2) are both crisp; wrong_content_quote and reference_quote are unambiguous and the conflict is 

      - direct. 

      - medium : both quotes exist verbatim, but reference_quote needs light alignment. 

      - low : inferring from a pattern; verbatim anchors are weak or partial. 

      - Always fill ``` confidence_reasoning ``` with 1-2 sentences. 

      - Two verbatim quotes per trigger: 

      - wrong_content_quote : verbatim substring of the CURRENT STEP carrying the wrong content; 

      - reference_quote : verbatim substring of TASK / HISTORY / CURRENT STEP that is the I being conflicted. 

      - Paraphrase, summary, or composite quotes are not acceptable. If either quote cannot be cited verbatim, do NOT emit the trigger. 

      - === OUTPUT FORMAT === 

- [ ] The step misreads its own immediate tool / env output: treats an error as success, swaps fields, misidentifies the returned entity. 

   - -> obs.MisreadOutput 

Emit a single JSON object: 

- { 

      - "triggers": [ 

- [ ] Subject to (C4): information visible in current or prior tool / env output is silently ignored where it is 

- clearly needed, OR a summary/memory block drops loadbearing facts. 

   - -> obs.IgnoreOutput 

      - { "step": <int>, 

      - "category": "cat-1" | "cat-2" | "cat-3" | "env", 

      - "taxonomy_tag": "<one of the 25 tags listed in the checklists above>", 

      - "attribution": "agent" | "env", 

- [ ] The step treats a partial / pending / truncated response as final. 

   - -> obs.TimingIssue 

- [ ] The step binds intent to the wrong visible entity. -> obs.GroundingFail 

- [ ] The step is performing verification but the criterion does not match the sub-goal in HISTORY. -> verify.WrongVerification 

- [ ] The step retries the same tool / query / action that already produced bad / empty / error in HISTORY, with no relevant env state change and no strategy change. Subject to (C4). 

   - -> verify.InfiniteRetry 

- === CHECKLIST (C) - internally inconsistent (cat-3) === 

- [ ] The conclusion contradicts something the SAME message states verbatim, OR contradicts a prior agent reflection / memory / claim. 

   - -> reason.InvalidInference 

- [ ] The step picks the wrong row / column / item from a list / table that is verbatim visible in the CURRENT 

- MESSAGE itself. 

   - "wrong_content_quote": "<verbatim from CURRENT STEP, or for the upstream-env back-reference verbatim from the earlier HISTORY step>", 

   - "reference_quote": "<verbatim from TASK / HISTORY / CURRENT STEP>", 

   - "confidence": "high" | "medium" | "low", 

- "confidence_reasoning": "<1-2 sentences>" 

- } 

- ] 

- } 

### **Error-Instance Clustering Prompt.** 

#### **Stage 2 — Error State Classification: Instance Clustering** 

   - You are an error-instance clustering annotator. You receive a list of per-step error TRIGGERS detected on one trajectory. Group those triggers into ERROR INSTANCES, where one instance corresponds to "the same underlying erroneous content / behavior" repeated or reflected across one or more steps. 

- -> obs.MisreadOutput 

      - === TERMINOLOGY === 

- [ ] The step asserts a concrete factual claim from the agent 's parametric knowledge, where the claim is concrete/ falsifiable, NOT supported by TASK/HISTORY/CURRENT MESSAGE, clearly wrong on widely-known ground truth, and load-bearing for this step's conclusion. 

   - -> reason.MissingAssumptionCheck 

- === CHECKLIST (D) - environment-side anomaly (env) === 

- env triggers fire when the agent's tool call at this step is otherwise correct, but the immediately following environment response shows the anomaly. Set attribution = "env". 

- [ ] The search / page response is hijacked by an ad vignette / overlay. 

   - -> env.AdOverlayHijack 

- [ ] The model API / platform content filter rejects a syntactically well-formed query. 

   - Each trigger contradicts a "conflict object" - the thing the wrong content is conflicting with. Following the spec we call this object I. Concretely, I can be one of: 

   - a TASK clause (sub-task, deliverable, constraint); 

   - a HISTORY object (a specific physical / virtual location, a specific tool output, a specific observation, a specific memory entry, a specific prior tool-call signature); 

   - a SAME-MESSAGE premise (operands, listed items, restated premise); 

   - a prior agent-self statement (plan, reflection, memory). 

   - Two triggers are about the SAME I when they are conflicting with the same underlying thing. 

   - Two triggers are about DIFFERENT I's when they conflict with different observations / different TASK clauses / different self-claims, or happen to share the taxonomy_tag string but the underlying object is different. 

- -> env.ContentFilterBlock 

- === CLUSTERING RULES === 

19

<!-- Page 20 -->

### **Error State Classification Prompt.** 

- (I-a) Same step, same I, multiple modules -> ONE instance. 

- (I-b) Same step, DIFFERENT I -> MULTIPLE instances. 

- (I-c) Across steps, same I, never repaired in between -> ONE instance with origin_step = first occurrence. 

- (I-d) Across steps, same I, but repaired and then re-fires later -> SPLIT into TWO instances. If you cannot determine whether a repair happened, conservatively keep them in ONE instance. 

- (I-e) "Fabricated I" (an I the agent invented out of thin air) is identified by the verbatim claim that introduced it. 

- CLUSTERING PRINCIPLE: cluster by the SPECIFIC CONSTRAINT OBJECT I being violated, NOT by "same type of erroneous behavior". 

- === PRECISION REQUIREMENTS FOR ``` what_is_being_violated ``` === 

- Write ``` what_is_being_violated ``` as a CONCRETE pointer to the exact object being contradicted. 

- For TASK-clause violations: quote or paraphrase the specific constraint / deliverable / format requirement. 

- For HISTORY-object violations: quote or paraphrase the specific observation / tool output / location / URL, and reference the step where it first appeared. 

- For SAME-MESSAGE premise violations: name the operands / listed items being misused. 

- For prior-self violations: quote or paraphrase the prior plan / reflection / memory statement being contradicted. 

#### **Stage 2 — Error State Classification: State Labeling** 

- You are an instance-state annotator. You receive ONE error instance and the FULL trajectory. Upstream trigger detection is high-recall and may flag exploratory or weakly committal steps; your job is to perform the commitment-strength recheck, the repair / state determination, and the terminal-connection audit defined in the methodology document. 

- === KEY DEFINITIONS === 

- origin_step = the first trigger step selected for this instance. 

- qualified_origin_step = the FIRST step in [origin_step, T] at which the agent makes an OBSERVABLE WRONG COMMITMENT for this instance's violated_object. May equal 

- origin_step, may be a later step, may be null. 

- last_trigger_step = the latest step at which the same instance re-fired upstream. 

- terminal step T = the last message index in the trajectory. 

- I (violated_object) = the concrete object the instance is violating (a TASK clause / a HISTORY object / a samemessage premise / a prior agent-self statement). 

- === TASK 1 - COMMITMENT-STRENGTH RECHECK === 

=== ONE-SHOT PROBE GUIDANCE === 

If a trigger fires at exactly ONE step and the agent at later steps neither references the same wrong belief nor takes another action against the same I, keep it as a STANDALONE singleton instance. Do NOT merge it with other unrelated triggers. 

- Upstream trigger detection is high-recall: a trigger may fire at an early probe or initial plan step even when the agent had no way yet to know the action was wrong. Your job is to classify each origin_step into one of three 

- commitment strengths so that ``` qualified_origin_step ``` reflects the FIRST step at which the agent observably persisted in the wrong belief despite already-visible evidence. 

##### === HARD CONSTRAINT === 

Triggers with attribution="agent" and triggers with 

attribution="env" CANNOT be merged into the same 

instance. 

Every input trigger index must end up in EXACTLY ONE instance' s trigger_indices. 

=== ENV INSTANCE MERGING === 

- For triggers with attribution="env", apply same-source merging when two env triggers share at least one of: 

- Same registrable domain; 

- Same tracking parameter key+value; 

- Same HTTP error code; 

- Same failure keyword: "rate limit", "timeout", "content filter", "empty payload", "captcha", "access denied", " not found"; 

- Same taxonomy_tag. 

- Do NOT merge env triggers that share only a generic/CDN domain (google.com, bing.com, youtube.com, etc.). 

=== TRAJECTORY CONTEXT === 

You will also receive a TRAJECTORY STEP CONTENT block. Steps that fired at least one trigger are shown at HIGH detail (th1 compression); steps that did not fire any trigger are shown at LOW detail (th3 compression) as background for later state classification. 

=== OUTPUT FORMAT === 

{ 

"instances": [ 

{ 

- "instance_id": <int, 0-indexed across this trajectory>, 

- "trigger_indices": [<int>, ...], 

- "origin_step": <int, smallest step among trigger_indices >, 

- "last_trigger_step": <int, largest step among trigger_indices>, 

- "attribution": "agent" | "env", 

- "category": "cat-1" | "cat-2" | "cat-3" | "env", 

- "error_content": "<one-sentence natural-language description of the same erroneous content/behavior>", 

- "what_is_being_violated": "<one-sentence description of the I being violated>", 

- "merged_reasoning": "<2-3 sentences explaining why these triggers share the same I>" 

- } 

] 

} 

- A commitment to error requires BOTH: 

- (a) the agent takes an observable binding action or states a non-hedged belief that contradicts the violated_object I, AND 

- (b) by that step, the evidence contradicting I is already visible in the prior trajectory. 

- Classify the upstream origin into ONE of: 

- origin_commitment_status = "explicit_wrong_commitment" BOTH (a) and (b) hold at origin_step. Set qualified_origin_step = origin_step. 

- origin_commitment_status = "weak_signal" 

- EITHER (a) holds at origin_step but (b) does NOT ( conflicting evidence not yet observable), OR (a) is only hedged at origin_step. 

- There MUST be a clearly LATER step M (origin_step < M <= T ) at which the agent, now able to see the conflicting evidence, still takes a binding action that contradicts I. 

- Set qualified_origin_step = M, set origin_relocated = true. 

- origin_commitment_status = "pure_exploration" origin_step is plain exploration / setup / a reasonable first guess, AND no step in (origin_step, T] satisfies the weak_signal relocation threshold. 

- Set qualified_origin_step = null, set 

- exploration_suppressed = true. 

- SINGLE-TRIGGER SHORTCUT. If the instance has exactly ONE trigger (origin_step == last_trigger_step) AND the instance is cat-2 or cat-3 (NOT cat-1 or env), the default label is ``` pure_exploration ``` , UNLESS a verbatim quote from a step strictly after origin_step shows the agent referencing or committing to the same wrong object. 

- HARD CAT-1 RULES: 

1. cat-1 instance MUST NOT have origin_commitment_status = pure_exploration. 

2. cat-1 instance MUST NOT have state = dormant. 

- HARD ENV RULES: 

1. An env instance MUST NOT have origin_commitment_status = pure_exploration UNLESS BOTH: (a) the environment self-recovers on the next judgable step, AND (b) the agent's next action is consistent with the recovered output. 

2. For env instances, wasted steps should be counted against the VIOLATED sub-goal object remaining unresolved. 

If the input triggers array is empty, emit {"instances": []}. 

- === TASK 2 - REPAIR / STATE DETERMINATION === 

20

<!-- Page 21 -->

fixed_at_step_<N> 

- There is a step N with anchor < N <= T at which the agent' s behavior satisfies the repair criterion for this instance's category. 

- cat-1 : at step N the agent touches the violated TASK clause AND the behavior is consistent with that constraint. 

- cat-2 : at step N the agent touches the violated CONTEXT object AND the behavior is consistent with the latest visible state. 

- cat-3 : at step N the agent explicitly retracts or corrects the prior wrong claim. 

- env : (env-fix-1) the agent detects the env anomaly and switches to a MATERIALLY DIFFERENT strategy; OR (envfix-2) the env recovers AND the agent's subsequent behavior is consistent with the recovered output. 

- HARD ENV-FIX RULES: 

- (R1) The following are NOT a strategy switch: clicking back; retrying the same URL/query/tool; reloading the same hijacked/errored page. 

- (R2) Same-source RE-FIRE invalidates a prior fix. (R3) A genuine env-fix-1 requires BOTH (a) the agent explicitly recognises the env anomaly, AND (b) the next observable action targets a DIFFERENT path. 

- === TASK 3 - TERMINAL-CONNECTION AUDIT (FAILURE-PATH TEST) === 

- Decide whether THIS instance lies on the actual observable path that took the trajectory to its terminal failure. 

- FAILURE-PATH MEMBERSHIP. Does any of the following appear on the path that produced the observed terminal failure? (i) the instance's wrong commitment is still active 

- at T, OR re-fires after qualified_origin_step; (ii) the instance is reflected in the terminal 

- answer, terminal action, terminal failure state; (iii) this instance produced an irreversible state 

- change visible at T. If ANY of (i)-(iii) holds -> the instance IS on the failure path. 

- IMPORTANT: Correcting this specific error would fundamentally change the trajectory toward success 

- # Hints 

1. Consider the ENTIRE trajectory from a global perspective - understand the task goal and how the agent's path diverged from success. 

2. Early exploration steps (steps 1-3) are often normal and should NOT be marked as critical unless they clearly introduce the root cause. 

3. Prefer the first step where the agent had enough reasonable information to proceed correctly but nevertheless 

introduced the error locally. 

This includes producing an incorrect output, misinterpreting or misusing prior information, or turning a correct intermediate state into an incorrect one. 

4. Do not choose a later step merely because the failure becomes more visible there. 

If a later step only repeats, propagates, or amplifies an earlier mistake, select the earlier step where the mistake originated. 

5. If a flawed strategy is repeated across multiple steps, attribute the failure to the step where that strategy was first introduced. If the strategy was reasonable but the execution result was wrong, attribute the failure to the first execution step that produced the incorrect result. 

6. Use recoverability only as a tie-breaker: among otherwise similar candidates, prefer the earliest step whose error made recovery unlikely or blocked the trajectory from returning to a successful path. 

You are given: 

   - the TASK, 

   - the FULL TRAJECTORY, 

   - a list of SUSPICIOUS STEPS that an upstream annotator flagged as containing some erroneous content (they are hints; you may pick any other step from the trajectory if you disagree). 

   - === WHAT TO OUTPUT === 

- Decide terminal_connection, one of: "irreversible" - Q1(iv) holds. "semantic" - Q1(i) or Q1(ii) holds. "none" - Q2 fully passes, or Q1 has no evidence at all. 

=== TASK 4 - RESOURCE EFFECT === 

- Fill ``` resource_effect ``` whenever the instance wasted ANY steps in (qualified_origin_step, T]. 

- Output ONE JSON object with these keys and nothing else: 

- "critical_step": <int> - the step number of the critical error. 

- "rationale": <string, 1-3 sentences> explaining why this step is critical. 

- === REQUIRED OUTPUT FORMAT (single JSON object, no prose around it) === 

- { "critical_step": <int>, 

- "rationale": "<1-3 sentences>" 

Resource effect schema: 

   - } 

- { 

- "wasted_steps": [<list of step indices wasted on I>], 

   - Return ONLY the JSON object. 

- "wasted_step_count": <int>, 

- "last_referencing_step": <int or null> 

- } 

=== OUTPUT FORMAT === 

Return STRICT JSON with EXACTLY these keys: 

## **E Experiment Details** 

- { 

- "instance_id": <int, copy from input>, "origin_commitment_status": "explicit_wrong_commitment" | " weak_signal" | "pure_exploration", 

- "qualified_origin_step": <int or null>, "fix_status": "active" | "fixed_at_step_<N>", "fix_evidence_quote": "<verbatim quote or null>", "terminal_connection": "irreversible" | "semantic" | " budget_debt" | "none", 

All experiments were conducted with temperature set to 0 to ensure reproducibility. 

- "chain_membership": <bool>, 

- "resource_effect": <object or null>, 

- "chain_explanation": "<2-4 sentences. MUST include: (1) the trajectory's terminal failure mode in one phrase, (2) which of Q1(i)-(iii) holds OR the named dominating cause (3) one verbatim evidence quote.>" 

} 

### **Causal Attribution Prompt.** 

**Stage 3 — Causal Attribution** 

- You are an expert at identifying the SINGLE critical step that caused a failed agent trajectory. 

- An error is critical if: 

- It represents the ROOT CAUSE that made task success impossible 

- It caused a cascade of subsequent errors 

- The trajectory could have succeeded if THIS specific error had not occurred 

### **E.1 Direct Prompting Baselines** 

To satisfy context-length constraints, we truncate each trajectory step to 2,048 characters and set the maximum context length to 16,384 tokens for each trajectory. Table 8 evaluates whether this per-step limit disadvantages direct prompting. Increasing the limit substantially lowers the proportion of truncated steps but does not improve accuracy, suggesting that retaining more raw detail can also introduce irrelevant content that interferes with criticalstep judgment. 

21

<!-- Page 22 -->

Table 8: Sensitivity of direct prompting to the per-step character limit. 

|Per-step limit|Avg. accuracy|Truncated steps|
|---|---|---|
|2,048 characters|**26**_._**00**|27_._1%|
|4,096 characters|20_._02|14_._5%|
|8,192 characters|24_._73|3_._5%|



#### **Direct Prompting Baseline — Critical Error Detection** 


![](assets/077/paper-0022-03.png)


<!-- Start of picture text -->
You are an expert at analyzing failed agent trajectories and<br>providing actionable debugging insights.<br>=== CRITICAL ERROR DEFINITION ===<br>A "critical error step" is the EARLIEST error instance that<br>remains ACTIVE (unrepaired) at the terminal step of a<br>failed trajectory -- the first error whose effects were<br>never truly repaired, making it the root cause of the<br>failure chain.<br>An error is "critical" if:<br>- It represents the ROOT CAUSE that made task success<br>impossible<br>- It caused a cascade of subsequent errors<br>- The trajectory could have succeeded if THIS specific error<br>had not occurred<br>- Correcting this specific error would fundamentally change<br>the trajectory toward success<br>=== TASK ===<br>{task_description}<br>TRAJECTORY OUTCOME: FAILED (reward=0, reported by the task<br>environment).<br>LAST STEP INDEX: {last_step}<br>=== FULL TRAJECTORY (one entry per message) ===<br>{trajectory_block}<br>Your task: find the critical error step of the trajectory.<br>=== REQUIRED OUTPUT FORMAT (single JSON object, no prose<br>around it) ===<br>{<br>"critical_error_analysis": {<br>"step": <int>,<br>"reason": "<1-3 sentences explaining why this step is a<br>strong root-cause candidate>"<br>}<br>}<br>Return ONLY the JSON object.<br><!-- End of picture text -->

reaches the best average accuracy of 50 _._ 2% and remains strongest on ALFWorld, _τ_<sup>2</sup> -Bench, and SWE-Bench Pro. For human-in-the-loop debugging, where nearby later steps can also guide inspection, TRAJDEBUG reaches 72 _._ 8% under the symmetric [GT _−_ 5 _,_ GT+5] window. 

**Inference cost and compute-matched comparison.** Table 10 reports average token consumption per trajectory using Qwen3-235B-A22B-Thinking as the common backbone. To control for inference budget, we also run direct prompting 40 times at temperature 1 and use majority voting. This baseline consumes slightly more tokens than TRAJDEBUG but reaches only 29 _._ 56% accuracy, showing that TRAJDEBUG’s gain over direct prompting cannot be explained by additional token consumption alone. 

### **E.4 Application Experiment Details** 

#### **Application — Vanilla Prompt** 

- Trajectory: {trajectory} Your task: 1. Identify the earliest step which directly leads the agent off 

- track or repeats ineffective behaviour. 

- 2. Reference that exact step number as shown in the trajectory. Do not shift to later steps of that error. 

- 3. Explain why the chosen step is wrong, citing relevant observation/action details. 

- 4. Suggest a concrete alternative for that same step that would 

- move the agent toward success (e.g., a specific action to take instead). 

- Respond strictly in the following format (single spaces around colons, no extra text): step:<number> reason:<one concise, specific sentence> suggestion:<one actionable suggestion for that step> 

### **E.2 Multi-Agent Systems Baselines** 

We reproduced each multi-agent baseline using its official codebase and default configuration. To ensure a fair comparison with our implementation of TRAJDEBUG, we used Qwen3-235B-A22BThinking as the base model and fixed the temperature at 0 for reproducibility. 

### **E.3 Additional Evaluation Results** 

**Relaxed critical-step localization.** Exact-step accuracy is deliberately strict, although predictions near the annotated critical step can still be useful in practice. For automated intervention, a prediction after the critical error may arrive too late; we therefore additionally evaluate whether the prediction falls in the asymmetric window [GT _−_ 3 _,_ GT]. As shown in Table 9, TRAJDEBUG 

#### **Application — Self-Reflection Prompt** 

Current result: {trajectory} Why is this trajectory not finished the task? Feedback: 

**Format-matched feedback comparison.** The main application experiment compares complete debugging pipelines, whose feedback formats may differ. To isolate the effect of critical-step localization, we additionally use the same repair-hint generator and the same injection procedure for Vanilla Debug and TRAJDEBUG; the two conditions differ only in the critical step supplied to the hint generator. TRAJDEBUG’s intermediate trigger, state, and attribution signals are hidden from both the 

22

<!-- Page 23 -->

|**Method**|ALFWorld|GAIA|WebShop|W&W-HC|W&W-Alg.|_τ_ <sup>2</sup>-Bench|SWE-Bench Pro|AVG|
|---|---|---|---|---|---|---|---|---|
|GLM-5.1|39_._0|42_._9|42_._0|22_._4|73_._8|51_._2|12_._8|40_._6|
|Gemini-3.1-Pro|38_._0|34_._7|40_._0|29_._3|62_._7|65_._5|23_._3|41_._9|
|DeepSeek-V4-Pro|35_._0|63_._3|40_._0|29_._3|66_._7|56_._8|17_._4|44_._1|
|Claude Sonnet 4.6|44_._0|42_._9|**48**_._**0**|20_._7|54_._0|53_._0|23_._3|40_._8|
|GPT-5.4|38_._0|61_._2|38_._0|22_._4|54_._8|51_._5|15_._1|40_._1|
|Claude Opus 4.6|36_._0|44_._9|**48**_._**0**|32_._8|69_._0|53_._5|19_._8|43_._4|
|<br>Qwen3-235B-A22B|37_._0|46_._9|46_._0|29_._3|69_._0|56_._5|25_._6|44_._3|
|AgentDebugger|45_._0|**64**_._**0**|44_._4|29_._3|**72**_._**2**|52_._5|16_._3|46_._2|
|CHIEF|12_._0|48_._0|22_._0|**34**_._**5**|65_._1|42_._6|19_._8|34_._8|
|AgentRX|19_._4|32_._7|26_._5|31_._0|59_._2|52_._2|8_._3|40_._8|
|**TRAJDEBUG (Ours)**|**50**_._**0**|59_._2|40_._0|29_._3|69_._0|**69**_._**0**|**34**_._**9**|**50**_._**2**|



Table 9: Critical-step localization accuracy (%) under the automated-intervention window [GT _−_ 3 _,_ GT]. AVG is the macro-average over the seven subsets. 

|**Method**|**AVG Accuracy**|**Avg. Tokens**|
|---|---|---|
|Direct Prompting|25_._69|34_,_530(1_._0_×_)|
|+ Majority Voting|29_._56|1_,_403_,_850(40_._6_×_)|
|AgentDebugger|23_._72|1_,_398_,_333(40_._5_×_)|
|CHIEF|18_._77|307_,_786(8_._9_×_)|
|AgentRX<br>|23_._10|218_,_862(6_._3_×_)|
|**TRAJDEBUG (Ours)**|**34**_._**11**|1_,_382_,_243(40_._0_×_)|



Table 10: Accuracy (%) and token consumption. Majority Voting is a compute-matched direct-prompting baseline. 

hint generator and the actor. Table 11 shows that TRAJDEBUG remains stronger across all three settings, providing a controlled comparison of the downstream value of its localized critical step. 

|**Method**|**Airline**|**Retail**|**SWE-Bench**|
|---|---|---|---|
|Initial|78_._00|84_._21|72_._00|
|Vanilla Debug|86_._00(+8_._00)|90_._35(+6_._14)|78_._00(+6_._00)|
|**TRAJDEBUG**|**88**_._**00**(+**10**_._**00**)|**92**_._**98**(+**8**_._**77**)|**80**_._**00**(+**8**_._**00**)|



Table 11: Task success rate (%) in the format-matched per-trajectory repair experiment. 

### **E.5 TRAJDEBUG Error Analysis** 

### **Candidate retention and conditional attribution.** 

We first stratify all 869 evaluated trajectories according to whether the human-annotated critical error is retained in the candidate set passed to final attribution; one of the 50 GAIA trajectories is excluded because its ground-truth critical-error label is null. As shown in Table 12, TRAJDEBUG retains the ground-truth step in 42 _._ 0% of trajectories, compared with an expected 14 _._ 2% coverage from a size-matched random candidate set. When the ground truth is retained, candidate-guided attribution reaches 45 _._ 5% micro-average accuracy, substantially outperforming direct holistic prompting at 29 _._ 6%. When it is excluded upstream, TRAJDE- 

BUG’s evidence-constrained out-of-set fallback outperforms direct holistic prompting (39 _._ 1% versus 35 _._ 1%). The fallback must identify an evidencebacked missing trigger together with its violated reference, origin step, and terminal footprint. The overall 41 _._ 8% reported here is a trajectory-level micro-average; Table 1 reports a macro-average across the seven benchmark subsets. 

**Stage-wise failure decomposition.** We decompose the failure cases of TRAJDEBUG according to the stage at which the ground-truth critical error is lost: **Trigger Miss** , where the critical error is not identified as an error trigger; **State Miss** , where the critical error is detected but filtered out from _F_ ( _τ_ ) during error state classification; and **Attribution Miss** , where the correct candidate enters the final attribution stage but is not selected. Table 13 shows that Trigger Misses (42 _._ 1%) and Attribution Misses (40 _._ 1%) are the two dominant failure modes, while State Misses are less frequent (17 _._ 7%). 

This decomposition characterizes where the remaining failures occur. First, Trigger Misses (42 _._ 1%) account for the largest share of failures. Although our trigger detector inspects each step under multiple compressed trajectory views and identifies evidence-grounded conflicts, some errors or deviations may be subtle, which can lead the detector to miss the critical error. Second, the relatively low share of State Misses (17 _._ 7%) suggests that error state classification usually preserves the critical error once it has been detected as a trigger. Attribution Misses (40 _._ 1%) therefore correspond to harder residual cases after candidate filtering, where multiple retained errors are plausibly related to the final failure and the model must distinguish the earliest failure-responsible step. These patterns suggest that further gains may come from improv- 

23

<!-- Page 24 -->

|**GT status before attribution**|**Cases (%)**|**Random coverage**|**TRAJDEBUG**|**Direct holistic**|∆|
|---|---|---|---|---|---|
|Retained in candidate set|365(42_._0%)|14_._2%|166(45_._5%)|108(29_._6%)|+15_._9pp|
|Excluded upstream|504(58_._0%)|85_._8%|197(39_._1%)|177(35_._1%)|+4_._0pp|
|Overall|869|–|363(41_._8%)|285(32_._8%)|+9_._0pp|



Table 12: Candidate-set coverage and conditional exact-step accuracy. Accuracy is micro-averaged within each stratum. Random coverage is the expected coverage of a uniformly sampled candidate set with the same size as TRAJDEBUG’s candidate set. 

|**Dataset**|**Trigger (%)**|**State (%)**|**Attribution (%)**|
|---|---|---|---|
|ALFWorld|32_._4|6_._8|60_._8|
|GAIA|20_._0|6_._7|73_._3|
|WebShop|18_._4|0_._0|81_._6|
|WhoAndWhen-HC|33_._3|2_._2|64_._4|
|WhoAndWhen-Algo|62_._1|12_._1|25_._9|
|SWE-Bench Pro|45_._2|24_._2|30_._6|
|_τ_ <sup>2</sup>-Bench|49_._2|30_._7|20_._1|
|**Overall**|**42**_._**1**|**17**_._**7**|**40**_._**1**|



Table 13: Failure decomposition of TRAJDEBUG. 

ing recall for subtle trigger errors and refining attribution among already filtered, terminal-relevant candidates. 

24
