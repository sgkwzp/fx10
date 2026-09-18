# Vinci2 Providing Proactive Assistance in Continuous Egocentric Videos

[Original PDF](../Vinci2%20Providing%20Proactive%20Assistance%20in%20Continuous%20Egocentric%20Videos.pdf)

Pages: 36

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

# **Vinci2: Providing Proactive Assistance in Continuous Egocentric Videos** 

Sitong Gong<sup>1</sup><sup>_,_2</sup><sup>_,_3</sup> , Tianyu Yan<sup>_⋆_1</sup><sup>_,_2</sup><sup>_,_3</sup> , Caixin Kang<sup>_⋆_2</sup><sup>_,_3</sup> , Bo Zheng<sup>2</sup> , Xiang Ruan<sup>1</sup> , Huchuan Lu<sup>1</sup> , Kaipeng Zhang<sup>2</sup> , Yoichi Sato<sup>3</sup> , and Yifei Huang<sup>_†_2</sup><sup>_,_3</sup> 

- 1Dalian University of Technology 2Alaya Lab 3The University of Tokyo `stgong@mail.dlut.edu.cn, {tianyu.yan, caixin.kang, bo.zheng, kaipeng.zhang}@shanda.com, {ruanxiang, lhchuan}@dlut.edu.cn, ysato@iis.u-tokyo.ac.jp, hyf015@gmail.com` 

**Abstract.** When should an intelligent assistant speak up without being asked? Continuous egocentric video offers rich, evolving context that enables a new form of assistance: one that is proactive rather than merely reactive. Yet existing approaches either wait passively for user queries or treat every detected event as requiring a response, without considering the user’s history, current activity, or whether assistance would actually be welcome. We reframe proactive assistance as a context-dependent decision problem: the agent must not only perceive what is happening, but reason over accumulated temporal context to determine when and whether to intervene. To this end, we present Vinci2, a proactive egocentric assistance system that advances the on-device assistant Vinci from reactive response toward proactivity. On the evaluation side, we present EgoServe, the first large-scale benchmark for proactive assistance in continuous egocentric video. EgoServe comprises over 3,000 service instances organized along 4 temporal memory horizons, ranging from immediate safety alerts to long-term habit coaching, across 10 service categories. On the modeling side, we propose EgoMemo, a training-free, memory-augmented agent that maintains three complementary memory representations: multi-scale temporal summaries, a semantic knowledge graph, and visual embedding archives. At each timestep, EgoMemo performs retrieval-augmented reasoning to determine whether assistance is warranted and, if so, produces contextually grounded responses. Experiments demonstrate that EgoMemo establishes strong baselines on EgoServe while remaining competitive on existing egocentric benchmarks. Our benchmark and code are publicly available at Vinci2. 

**Keywords:** Egocentric Vision · Proactive VLM · LLM Agent 

> _⋆_ Equal contribution. 

> _†_ Corresponding author.

<!-- Page 2 -->

2 Sitong Gong et al. 


![](assets/081/paper-0002-01.png)


<!-- Start of picture text -->
What is outside on the balcony? What's on the on the door with title "Dear Residents" Can you walk me through how to prepare onions? Egocentric Video Stream ...<br>…<br>A cannondale. off your waste bags inside the bins"It reads “Please step in and dispose  onion to prepare it for chopping.First, cut off the ends of the  Discard the onion ends to keep your workspace clean.<br>(a) Reactive Paradigm (b) Semi-proactive Paradigm<br>phone. Please use the side volume Reaching that high may shake the button for a steadier shot. MemoryConstruction You left a file transfer running on your laptop downstairs a few minutes ago. Since you're free now, do you want to check its status? You’re looking for salt. You put it on the kitchen table after buying it the day before yesterday.<br>Reasoner<br>Long-Term Messages Retriever<br>Call Memory<br>Multimodal Context Knowledge Graph MessagesEpisodic  (c) Proactive Paradigm (Ours) Egocentric Video Stream ...<br><!-- End of picture text -->

**Fig. 1: Three paradigms of egocentric assistants.** (a) Reactive: responds only to explicit user queries. (b) Semi-proactive: monitors the video stream for predefined taskrelevant events. (c) Proactive (ours): autonomously decides when and how to intervene without any user prompt. 

## **1 Introduction** 

The promise of proactive egocentric intelligence is an assistant that sees what you see, understands your context as it evolves, and offers help at the right moment without being asked. Recent progress in Video-LLMs [30, 33, 51, 53, 54], streaming visual perception [27, 46, 70], and egocentric foundation models [22, 64, 69] has brought this vision within reach, enabling continuous comprehension and reasoning over first-person video. Yet while the perception capabilities are maturing rapidly, the question of how and when an assistant should proactively intervene remains largely unaddressed. 

Existing egocentric assistants operate under two limiting paradigms, as illustrated in Fig. 1. Most current Video-LLMs [30,47,77] follow a _reactive_ paradigm, responding only when explicitly prompted. Recent event-triggered systems [58, 73, 74] adopt a _semi-proactive_ paradigm: given a task instruction provided by the user in advance, they monitor the video stream for predefined events and generate responses upon detection. However, these methods are constrained by the scope of the initial instruction and the immediate visual context, lacking the ability to reason over long-horizon historical observations, and offering no mechanism to assess whether the current situation genuinely warrants interrupting the user. We argue for a third paradigm, _proactive_ assistance, that has not yet been explored: the agent reasons over the user’s accumulated context, including their history, habits, current activity, and goals, to make a deliberate decision about whether, when, and how to intervene. We instantiate this paradigm in Vinci2, a successor to the egocentric assistant Vinci [22] that advances from reactive response to genuine proactivity. Vinci2 comprises two complementary components: a benchmark **EgoServe** , and a training-free agent **EgoMemo** , which we detail below.

<!-- Page 3 -->

Vinci2 3 

On the evaluation side, no existing benchmark addresses this need. Offline video QA benchmarks [10,14,31,38] evaluate comprehension over pre-segmented clips without any notion of proactive intervention. Streaming comprehension benchmarks [39] assess temporal understanding but do not evaluate proactive behavior. Existing proactive dialogue benchmarks [58, 73] operate under a taskcompletion setting where the user provides an explicit instruction upfront, and do not model the decision of whether to intervene or remain silent. To fill this gap, we present **EgoServe** , the first large-scale benchmark for proactive assistance in continuous egocentric video. Built upon EgoLife [64], HoloAssist [61], and CaptainCook4D [42], EgoServe spans diverse daily activities, multiple users, and extended temporal contexts ranging from minutes to hours, with proactive services organized into 4 temporal memory horizons and 10 service categories. 

On the modeling side, current streaming Video-LLMs lack explicit memory mechanisms for long-horizon retrieval, while retrieval-augmented generation methods [37] have not been applied to the proactive setting where the system must autonomously decide whether a response is warranted. We take a first step with **EgoMemo** , a training-free, memory-augmented agent that maintains three complementary memory representations: (1) multi-scale temporal summaries that hierarchically organize observations from fine-grained clip-level descriptions to coarse activity and session summaries; (2) a semantic knowledge graph encoding entity relationships and activity patterns; and (3) visual embedding archives for similarity-based retrieval. At each timestep, the agent determines whether proactive assistance is warranted and, when deeper context is needed, retrieves and synthesizes information across all three memory stores. 

Our contributions are as follows: 

- We formalize proactive assistance in continuous video experiences as a decisiondriven reasoning task over streaming egocentric perception, and situate it within a taxonomy of three paradigms: reactive, semi-proactive, and proactive. 

- We present EgoServe, the first benchmark for evaluating proactive assistance under 4 temporal horizons, comprising over 3,000 service instances across 10 service categories. 

- We develop EgoMemo, a training-free, memory-augmented agent that demonstrates the feasibility of proactive assistance through retrieval-augmented reasoning, establishing strong baselines on EgoServe and competitive results on existing egocentric benchmarks. 

## **2 Related Works** 

**Egocentric Video Understanding.** Egocentric video understanding has been studied primarily in offline settings where complete recordings are available [12, 13, 18, 19, 21, 23, 24, 32, 44, 45, 48, 50, 59, 66, 72]. Benchmarks such as EgoSchema [38], EgoThink [7] and EgoExoLearn [20], EgoExoBench [17] evaluate episodic memory, cognitive capabilities, and cross-view understanding over pre-recorded footage, while EgoVLP [47] and LaViLa [75] advance video-language pre-training

<!-- Page 4 -->

#### 4 Sitong Gong et al. 

for egocentric retrieval. A parallel line targets the streaming setting: VideoLLMonline [5], Flash-VStream [70], and StreamChat [35] enable real-time video conversation, Dispider [46] disentangles perception and reasoning for low-latency interaction, and OVO-Bench [39] benchmarks online video comprehension. However, both lines focus on answering questions about observed content, without modeling the decision of whether and when to proactively intervene. Our EgoServe fills this gap by evaluating proactive assistance across multiple temporal memory horizons. 

**Proactive Large Language Models.** Proactive behavior has been explored in language-only settings, where ProAgent [69] enables agents to anticipate teammates’ needs in multi-agent cooperation and proactive dialogue systems [8] investigate model-initiated interactions. In the vision-language domain, StreamBridge [58], EWO [74], and ProAssist [73] explore event-triggered proactive generation from streaming video, while Vinci [22] deploys an on-device multimodal proactive assistant. These methods generally conflate event detection with the decision to intervene. In contrast, EgoMemo treats intervention as an explicit reasoning outcome conditioned on retrieved multi-scale historical context. **Proactive Assistive Systems.** The vision of context-aware proactive assistance has deep roots in wearable computing. Early work on context-aware applications [49] and contextual awareness in wearable devices [9, 55] established the foundational paradigm of systems that adapt behavior based on sensed user context. Recent advances in foundation models have revived this vision: ContextAgent [63] builds proactive LLM agents on wearable perceptions from smart glasses and earphones, SensibleAgent [28] introduces unobtrusive proactive interaction for AR glasses, and ProAgentBench [56] provides a benchmark for evaluating proactive LLM agents with real-world data. These efforts focus primarily on language-only or short-horizon sensory contexts. In contrast, our work targets proactive assistance over continuous egocentric video streams, requiring long-horizon memory and temporal reasoning across extended activity contexts. **Memory-Based Video Agents.** Processing long video within limited context windows has motivated memory-augmented architectures such as MovieChat [54], MA-LMM [16], and VideoAgent [11]. Recent RAG-based approaches [25, 36, 37], VideoRAG [37], Vgent [52], and WorldMM [67], further introduce graph-driven indexing and multi-type memory with adaptive retrieval, but assume offline access to the complete video. EgoMemo departs from these methods in two ways: both memory construction and retrieval are fully streaming, and a VLM-based caption reconstruction step bridges the information gap between structured retrieval results and the contextual descriptions needed for reasoning. 

## **3 EgoServe Benchmark** 

### **3.1 Task Formulation** 

We formulate proactive assistance as a joint decision-and-generation task over continuous video. Let _V_ = _{v_ 1 _, v_ 2 _, . . .}_ denote an egocentric video stream segmented into sequential clips. At each timestep _t_ , the agent observes _vt_ and must

<!-- Page 5 -->

![](assets/081/paper-0005-00.png)


<!-- Start of picture text -->
Vinci2 5<br>Input 1h Human  <Service-specific Prompt><br>Annotations Gemini Annotator Trigger Instant/Short-Term/Episodic<br>Dense Captions Proactive Services<br>Extract<br>Manual Verification<br>Hour 2 Human  Cross-Segment<br>Annotations Long-Term Events Final Proactive Services<br>Carry to Next Turn Manual Verification<br>Hour N Human Annotations Gemini Annotator Trigger Long-Term Proactive Services<br>(a) EgoServe Annotation Pipeline (b) Response Word Frequency<br>Episodic<br>TR<br>EgoServe<br>(c) Video Duration Distribution (d) Service Category Distribution across Data Source (e) Service Category Distribution<br>Streaming Input …<br><!-- End of picture text -->

**Fig. 2: Overview of the EgoServe benchmark.** (a) Annotation pipeline: human annotations from each source dataset are processed through category-specific prompts via a foundation model, followed by manual verification. (b) Response word frequency. (c) Video duration distribution. (d) Per-dataset service counts. (e) Service instance distribution across 10 subcategories and 4 temporal horizons. 

produce a binary intervention decision _dt ∈{_ 0 _,_ 1 _}_ along with a service response _rt_ when _dt_ = 1. A correct proactive response requires three conditions to be met: (1) the intervention occurs within a reasonable temporal window of the ground-truth trigger point; (2) the predicted service type matches the groundtruth category; and (3) the generated response is relevant to the identified service need and grounded in the observed context, as assessed by LLM-based evaluation against reference responses. 

### **3.2 Data Source** 

EgoServe is built upon three egocentric video datasets that together span diverse scenarios and temporal scales. EgoLife [64] provides multi-day continuous daily life recordings, from which we select three participants (A1, A4, A5) across their first five days, enabling evaluation of long-horizon services that require reasoning across temporally distant events, such as connecting observations from different days. HoloAssist [61] captures task-oriented interactions with procedural annotations (step boundaries, error flags, instructor interventions), and we select its 191 validation videos for instant and short-term service evaluation. CaptainCook4D [42] offers structured cooking recordings with both correct and erroneous executions across 24 recipes, from which we select 87 videos with explicit step-error annotations from the validation and test splits, providing a controlled setting for evaluating error detection and corrective guidance.

<!-- Page 6 -->

- 6 Sitong Gong et al. 

### **3.3 Service Taxonomy** 

A key design principle of EgoServe is that proactive services are organized along two orthogonal dimensions: the temporal memory horizon required to provide the service, and the application context of the service itself. We define 4 temporal memory horizons based on the scope of context the agent must reason over: 

- **Instant services** require only the current observation and immediate context, including Safety Alerts (SA: warning about a hazard in the scene) and Tool Use guidance (TU: suggesting a more appropriate tool). 

- **Short-Term services** require context spanning the recent minutes of activity, including Error Recovery (ER: detecting and correcting a procedural mistake), Resource Reminder (RR: reminding the user about a recently used resource), and Next-Step Guidance (NSG: suggesting the next action in an ongoing task). 

- **Episodic services** require reasoning over the current task, potentially spanning tens of minutes to hours, including Task Reminder (TR: reminding the user of an unfinished task) and Memory Recall (MR: retrieving earlier information that becomes relevant). 

- **Long-Term services** require cross-session or multi-day context, including Habit Coaching (HC: suggesting behavioral improvements based on recurring patterns), Routine Optimization (RO: suggesting adjustments to recurring routines), and Memory Link (ML: connecting the current situation to events from previous sessions). 

This taxonomy yields 4 major categories and 10 subcategories, as summarized in Table 1. The design reflects a core insight: the difficulty of proactive assistance scales with the temporal horizon of the required context, and a comprehensive benchmark must evaluate across all horizons. 

### **3.4 Annotation Pipeline** 

Annotating proactive services at scale requires identifying not only what happened in the video, but when assistance would have been appropriate and what the agent should say. We design a semi-automated pipeline that leverages foundation models guided by service category-specific prompts, grounded in existing human annotations from each source dataset. 

The annotation pipeline of different datasets is presented in Fig. 2. We leverage the existing human annotations and apply different techniques to different data sources. For HoloAssist, we preprocess the full set of human annotations in chronological order and design tailored prompts that map structured annotations into proactive service instances. For example, instructor corrections map to Error Recovery, and step transitions map to Next-Step Guidance. Due to the task-oriented nature of HoloAssist, annotations primarily cover Instant and Short-Term categories. For EgoLife, we segment annotations into 1-hour intervals and stream them into Gemini together with category-specific prompts. For Instant, Short-Term, and Episodic categories, service dialogues are generated

<!-- Page 7 -->

Vinci2 7 

directly from each interval. For Long-Term services, we adopt a streaming cuecapturing strategy: the model incrementally accumulates events across intervals that may trigger specific long-term service types and continuously generates candidate dialogues. These accumulated cues are then combined with future timeline annotations and re-input into the model, simulating the cross-session reasoning that long-term services require. For CaptainCook4D, we leverage the procedural step annotations and error labels to generate service instances focused on task guidance and error correction. All generated annotations undergo manual verification to ensure temporal accuracy, category correctness, and response quality. 

### **3.5 Evaluation Protocol** 

EgoServe evaluates proactive assistance along two complementary dimensions: _Temporal precision._ For each service category, we match predicted interventions against ground-truth trigger points using a temporal tolerance window _δ_ adapted to the characteristic timescale of each source dataset. A prediction is considered a true positive if its trigger timestamp falls within (start_time _−δ,_ end_time+ _δ_ ) of a ground-truth service instance _of the same category_ . We compute Precision, Recall, and F1 independently for each of the 10 service subcategories. _Response quality._ For all successfully matched prediction–ground-truth pairs, we evaluate the quality of the generated response using GPT [41] as an automatic judge, which scores each response on a 1–5 scale across contextual grounding and effectiveness. The LLM-score reports the average over all matched pairs. 

## **4 Methodology** 

We present EgoMemo, a training-free, memory-augmented agent for proactive assistance in continuous egocentric video. As illustrated in Fig. 3, EgoMemo continuously processes incoming video, maintains structured long-term memory, and performs context-aware reasoning at each timestep. In _proactive_ mode, it monitors the evolving scene and autonomously decides when to provide helpful interventions by retrieving relevant historical context. In _reactive_ mode, a user query triggers the same retrieval pipeline. Both modes share a unified architecture consisting of two core stages: (1) _streaming memory construction_ (Sec. 4.1), which incrementally builds three complementary memory representations, and (2) _streaming retrieval-augmented reasoning_ (Sec. 4.2), which retrieves and reconstructs relevant context for decision-making. Both construction and reasoning are conducted incrementally, never requiring access to the complete video. 

### **4.1 Streaming Memory Construction** 

Given a continuous egocentric video stream _V_ = _{v_ 1 _, v_ 2 _, . . .}_ , we segment it into non-overlapping short clips. For each clip _vt_ arriving at timestep _t_ , we generate a dense textual caption _ct_ using a vision-language model, annotated with its corresponding timestamp, and extract sampled keyframes _{ft_<sup>1</sup><sup>_, . . . , f_</sup> _t_<sup>_K}_.These</sup>

<!-- Page 8 -->

8 Sitong Gong et al. 


![](assets/081/paper-0008-01.png)


<!-- Start of picture text -->
Ego-centric  Clip-level Captions<br>Video Stream … 𝑐𝑡 Reasoner 𝑞 User Question 𝑟𝑡<br>Session-level Reactive Mode<br>𝑀𝑆 Streaming Input 𝑑𝑡 = 1 𝑑𝑡 = 0<br>𝑣1<br>Need Retrieval?<br>Activity-level<br>Caption  𝑀𝐴 𝑞𝑟<br>Generator … Clip-level𝑀𝐶 Multimodal Encoder 𝑞𝑣 𝑡𝑒𝑥𝑡 Retrieval QuerySemantic Search 𝑇𝐸𝑛𝑐 Temporal Search Reasonerመ𝐶<br>𝑣3 … Visual Search𝑒 𝑞𝑣 Matched Entities<br>Merge<br>Evolving Knowledge Graph<br>Top-k Embeddings 1-hop Neighbors<br>𝑓𝑡𝑘 Multimodal Encoder 𝑒𝑡,𝑘𝑣 Extract Caption & Visual Feature<br>𝑣𝑡 𝐼𝑔𝑟𝑎𝑝ℎ Revised Captions<br>Visual Embedding Archive Filtered by Timeline 𝐼𝑣𝑖𝑠 Caption Reconstruction<br>(a) Streaming Memory Construction (b) Streaming Retrieval-Augmented Reasoning<br>…<br>…<br>Filtered by Timeline Retrieved Context<br><!-- End of picture text -->

**Fig. 3: Architecture of EgoMemo.** (a) clip-level captions are incrementally organized into three-level temporal summaries ( _MC_ , _MA_ , _MS_ ), an evolving knowledge graph _G_ , and a visual embedding archive _A_ . (b) Streaming retrieval-augmented reasoning: three parallel retrieval pathways (temporal, semantic, and visual) gather evidence, which is unified via VLM-based caption reconstruction before the reasoner produces an intervention decision _dt_ and response _rt_ . 

captions and keyframes are the atomic inputs from which three complementary memory representations are incrementally constructed. 

**Multi-Scale Temporal Memory.** We organize captions into a three-level hierarchy: **Clip-level** captions _MC_ = _{_ ( _ct, t_ ) _| t_ = 1 _, . . . , T }_ preserve fine-grained perceptual detail; **Activity-level** summaries _MA_ periodically aggregate consecutive clip captions to capture activity context; and **Session-level** summaries _MS_ further aggregate activity entries to encode long-horizon routines. Formally: 


![](assets/081/paper-0008-05.png)


where _Wj_ and _Wk_ denote temporal windows at the Activity and Session levels, respectively. The roll-up is fully incremental: only newly accumulated segments trigger summarization at the next level. To support retrieval, we encode captions at all three levels into dense embeddings _{e_<sup>_c_</sup> _i_<sup>_, ea_</sup> _j_<sup>_, e_</sup> _k_<sup>_s}_usingatextencoder</sup><sup>`TEnc`</sup> and index them for similarity search. 

**Evolving Knowledge Graph.** To capture semantic relationships between entities across different time segments, we maintain a knowledge graph _G_ = ( _N , E_ ) that evolves as new observations arrive. For each caption _ct_ , we prompt an LLM to extract entities and relations _Rt_ = **Extract** ( _ct_ ), which are merged into the global graph through name-based entity resolution: _Gt_ = **Merge** ( _Gt−_ 1 _, Rt_ ) _._ Each node in _G_ maintains links to its source captions, enabling the graph to serve as a structured index over the temporal memory. 

**Visual Embedding Archive.** To complement text-based memories with visual details that are difficult to verbalize (object appearances, spatial layouts), we

<!-- Page 9 -->

Vinci2 9 

encode sampled keyframes using a multimodal encoder and store the resulting embeddings alongside their source caption index and timestamp: 


![](assets/081/paper-0009-02.png)


This enables similarity-based retrieval of visually relevant moments that may lack lexical overlap with the query. 

### **4.2 Streaming Retrieval-Augmented Reasoning** 

At each timestep _t_ , the LLM reasoning agent receives the current clip-level caption _ct_ and the most recent short-term context. For proactive assistance, it assesses whether the current observation warrants an active intervention; for reactive QA, a user query _q_ serves as an external trigger with _dt_ = 1 by default. In both cases, when deeper context is needed, the agent generates a retrieval query _qr_ and invokes three parallel retrieval pathways, followed by a caption reconstruction step that synthesizes the retrieved evidence into a coherent context for final reasoning. 

**Multi-Scale Temporal Retrieval.** We search the multi-scale temporal memory by encoding _qr_ into a dense embedding and retrieving the top- _k_ similar captions: 


![](assets/081/paper-0009-07.png)


The constraint _t_<sup>_′_</sup> _≤ t_ enforces the streaming setting. Clip-level entries provide fine-grained evidence, while activity- and session-level summaries offer broader context for queries involving extended activities or recurring patterns. **Graph-Based Semantic Retrieval.** We extract key entities from _qr_ , match them against nodes in _G_ , and expand to their 1-hop neighbors to capture semantically associated events: 


![](assets/081/paper-0009-09.png)


where _I_ graph collects caption indices linked to the matched nodes and their neighbors. This captures events described with different wording or occurring at distant timesteps. 

**Visual Similarity Retrieval.** Since _qr_ is in text form, we first rewrite it into a visual-centric description _qv_<sup>text</sup> emphasizing visual attributes, encode it via the multimodal encoder to obtain **e**<sup>_qv_</sup> = **MEnc** ( _qv_<sup>text</sup> ), and retrieve the top- _k_ matching keyframe embeddings: 


![](assets/081/paper-0009-12.png)


Each retrieved visual embedding is linked to its source clip-level caption, yielding a set of caption indices _I_ vis. 

**Caption Reconstruction and Reasoning.** Both graph-based and visual retrieval return sets of caption indices rather than self-contained descriptions. To

<!-- Page 10 -->

10 Sitong Gong et al. 

bridge this gap, we apply a unified _VLM-based caption reconstruction_ step: for each set of retrieved indices _I ∈{I_ graph _, I_ vis _}_ , we gather the corresponding cliplevel captions and keyframes, and prompt a VLM to generate a reconstructed caption conditioned on the retrieval query: 


![](assets/081/paper-0010-02.png)


This reconstruction resolves co-references, recovers visual details absent from the original captions, and produces a query-focused narrative. The outputs from the temporally retrieved captions _{ct′}t′∈I_ temp, graph-reconstructed context _c_ ˆgraph, and visually reconstructed context _c_ ˆvis, are aggregated into a unified retrieved context _C_<sup>ˆ</sup> and provided to the LLM reasoning agent: 


![](assets/081/paper-0010-04.png)


where _dt ∈{_ 0 _,_ 1 _}_ is the intervention decision and _rt_ is the generated response. For reactive QA, the same pipeline is invoked with the user query as _qr_ and _dt_ = 1. This unified formulation requires no architectural modification between the two modes. 

### **4.3 Adaptation to Other Benchmarks** 

While EgoMemo is designed for streaming scenarios, its architecture naturally accommodates offline video understanding tasks where the full video is available at inference time. In this setting, we first process the entire video sequentially to construct the complete memory representations ( _MC_ , _MA_ , _MS_ , _G_ , and _A_ ) in a single forward pass. Given a query _q_ , the agent adopts a coarse-to-fine perception strategy: it first receives all activity-level and session-level summaries ( _MA_ and _MS_ ) to form a global understanding of the video, and attempts to answer the question based on this high-level context alone. If the agent determines that the available information is insufficient, it invokes the same retrieval pipeline described in Sec. 4.2 to retrieve fine-grained clip-level evidence from _MC_ , _G_ , and _A_ . This coarse-to-fine strategy avoids unnecessary retrieval for questions answerable from high-level summaries, while preserving access to detailed evidence when needed. The adaptation requires no modification to the model architecture, demonstrating that the streaming-first design of EgoMemo generalizes gracefully to offline settings. We evaluate both streaming and offline performance in Sec. 5. 

## **5 Experiments** 

### **5.1 Experimental Setup** 

**Evaluation Datasets** We evaluate EgoMemo across three benchmark categories. (1) **Proactive assistance** : our EgoServe benchmark, which evaluates proactive service triggering over streaming egocentric video. (2) **Online video understanding** : ESTP-Bench [74], which assesses ego-proactive video understanding through temporally grounded questions at opportune moments; and

<!-- Page 11 -->

Vinci2 11 

**Table 1:** Evaluation results on EgoServe benchmark. 

|**Model**|**Inst**<br>|**ant**|**Sho**|**rt-ter**|**m**|**Epis**|**odic**|**Lo**|**ng-te**|**rm**|**Overall**|**LLM-score**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|
||_SA_|_TU_|_NSG_|_ER_|_RR_|_MR_|_TR_|_HC_|_ML_|_RO_|||
|Qwen3-VL-Plus [2]|5.2|1.5|8.6|**10.4**|3.4|0.0|1.8|4.4|0.0|0.0|3.5|2.8|
|GPT-5-mini [41]|**12.5**|3.6|9.5|1.0|5.2|0.0|**9.4**|**5.7**|0.0|0.0|4.7|**3.0**|
|w/o MS|11.2|8.0|24.2|1.9|4.9|**4.8**|2.9|4.6|1.9|5.7|7.0|2.8|
|w/o Recons.|10.5|7.6|**26.1**|0.4|**5.8**|0.0|4.8|5.4|0.0|5.7|6.6|2.8|
|w/o VSR|11.7|6.0|24.8|1.2|3.9|1.2|6.6|4.2|3.2|6.4|6.9|2.8|
|w/o GSR|**12.5**|5.6|24.4|1.9|4.9|2.6|4.8|2.4|0.0|5.4|6.5|2.8|
|w/o MTR|9.7|**8.8**|24.6|1.2|4.0|4.0|4.5|1.9|2.1|7.5|6.8|2.7|
|**EgoMemo (Ours)**|11.4|7.5|24.7|1.7|4.7|3.8|5.7|3.7|**4.9**|**11.8**|**8.0**|2.8|



OVO-Bench [39], which evaluates online video comprehension across backward tracing, real-time perception over 858 videos. (3) **Offline egocentric QA** : EgoSchema [38], a long-form temporal reasoning benchmark with over 5,000 multiple-choice questions spanning 250+ hours of Ego4D video; EgoTaskQA [26], which tests understanding of task-oriented egocentric activities, converted to multiple-choice format following [11]; and QAEgo4D [4], which evaluates episodic memory querying over Ego4D recordings. 

**Implementation Details** For streaming memory construction, we use Qwen3VL-8B-Instruct as the VLM to generate clip-level captions _ML_ from each video segment. Activity-level summaries _MA_ and Session-level summaries _MS_ are produced via LLM-based summarization. The temporal windows _Wj_ and _Wk_ are adapted to the video duration: for ultra-long recordings such as EgoLife, we use 30s/5min/1h for clip/activity/session levels, while for shorter online benchmarks we use 10s/1min/5min. Entity and relation extraction for the evolving knowledge graph is performed using GPT-4o-mini. For retrieval, we encode textual captions with OpenAI’s text-embedding-3-small as the text encoder `TEnc` , and encode keyframes with ImageBind as the multimodal encoder `MEnc` . The reasoning agent uses GPT-5-mini for online streaming benchmarks and GPT-5.2 for offline benchmarks. For EgoServe evaluation, the temporal tolerance window _δ_ is set per dataset according to its characteristic timescale: _δ_ = 60s for EgoLife, _δ_ = 25s for CaptainCook4D, and _δ_ = 10s for HoloAssist. Further details on hyperparameters and prompt designs are provided in the supplementary material. 

### **5.2 Results on EgoServe** 

**Main Comparison** Table 1 reports per-category F1 scores on the EgoServe benchmark, where a prediction counts as a true positive only if it falls within the dataset-specific temporal window of a ground-truth instance of the _same_ service category. We compare EgoMemo against two strong proprietary models: GPT-5-mini and Qwen3-VL-Plus. Both models struggle substantially: Qwen fails almost entirely on episodic and long-term services where historical context is essential. GPT-5-mini performs better (4.7 overall), particularly on instant

<!-- Page 12 -->

12 Sitong Gong et al. 

**Table 2:** Experimental results of various models evaluated on the ESTP-Bench. 

|**Model**|||**Ex**|**plicit **|**Proac**|**tive **|**Task**|||**Imp**|**licit **|**Proac**|**tive T**|**ask**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
||_OR_|_AP_|_TRU_|_OL_|_OSC_|_EOL_|_EOSC_|_AR_|_All_|_OFR_|_IFR_|_NAR_|_TU_|_All_|
|EyeWO*|26.6|26.6|25.1|26.8|19.8|22.3|20.8|20.7|23.6|24.8|31.0|75.3|78.7|52.5|
|LLaVA-OneVision [29]|8.3|8.8|22.8|25.4|13.5|9.8|9.6|10.3|13.6|20.3|20.9|35.9|49.9|31.8|
|Qwen2-VL [1]|13.7|13.5|15.4|**29.5**|8.0|15.4|16.6|10.9|15.4|17.8|19.8|**56.4**|63.1|**39.3**|
|MiniCPM-V [65]|14.9|16.8|17.1|26.8|7.7|12.9|12.5|13.1|15.2|15.9|21.0|46.8|62.2|36.5|
|LLaVA-NeXT-Video [29]|15.6|14.6|21.9|26.8|12.8|14.2|13.5|12.3|16.5|18.6|23.2|44.9|51.6|34.6|
|InternVL-V2 [6]|11.3|5.9|7.0|10.1|0.7|2.7|5.2|2.2|5.6|8.3|2.9|4.3|11.2|6.7|
|LIVE [5]|11.2|13.9|7.9|13.2|5.6|9.4|6.0|8.9|9.5|5.8|8.9|41.0|46.7|25.6|
|MMDuet [62]|7.2|10.3|17.6|10.2|4.2|6.1|8.8|8.5|9.1|10.0|7.7|50.1|**69.1**|34.2|
|**EgoMemo (Ours)**|**25.4**|**30.5**|**32.4**|22.9|**26.6**|**26.1**|**35.8**|**21.1**|**27.6**|**23.8**|**29.9**|36.7|48.4|34.7|



Safety alerts (12.5) and short-term Next-Step Guidance (9.5), but still scores zero on all long-term categories except Habit Coaching (5.7), confirming that even powerful VLMs cannot provide meaningful proactive assistance without access to accumulated context. 

EgoMemo achieves 8.0 overall F1, nearly doubling GPT-5-mini’s performance. The gains are most pronounced on long-term services: Memory Link reaches 4.9 (vs. 0.0 for both baselines) and Routine Optimization reaches 11.8 (vs. 0.0), demonstrating that our structured memory and retrieval mechanisms successfully enable cross-session reasoning. On episodic services, EgoMemo attains non-zero scores on both Memory Recall (3.8) and Task Reminder (5.7), whereas the baselines fail on at least one. Short-term services show strong performance across Next-Step Guidance (24.7) and Resource Reminder (4.7). For matched predictions, the LLM-score reaches 2.8. We note that GPT-5-mini matches far fewer service instances overall (4.7 vs. 8.0), indicating that the primary bottleneck for baselines lies in temporal precision rather than response quality. 

The absolute scores remain moderate across all methods, reflecting the genuine difficulty of proactive assistance: the agent must simultaneously decide _when_ to intervene within the correct temporal window, identify the appropriate service type, and produce a helpful response. EgoServe is designed to expose these challenges and serve as a diagnostic tool for future progress. 

**Ablation Study** We ablate each component of EgoMemo on EgoServe to understand its individual contribution. Results are reported in Table 1. 

Replacing the three-level temporal hierarchy with a single-scale caption store ( _w/o MS_ ) reduces the overall F1 from 8.0 to 7.0, with Memory Link dropping from 4.9 to 1.9 and Routine Optimization from 11.8 to 5.7, confirming that the hierarchical organization of clip-, activity-, and session-level summaries is essential for capturing patterns across extended temporal spans. Removing the VLM-based caption reconstruction step ( _w/o Recons._ ) causes a large overall drop (8.0 _→_ 6.6). Both Memory Recall and Memory Link fall to 0.0, indicating that raw retrieved snippets are insufficient for the reasoner to synthesize coherent cross-temporal evidence. Disabling the visual embedding archive ( _w/o VSR_ )

<!-- Page 13 -->

Vinci2 13 

**Table 3:** Evaluation results on OVO-Bench. 

|**Model**||**Real-**<br>|**Time **<br>|**Visual **<br>|**Perce**<br>|**ption**<br>||**Ba**<br>|**ckwar**<br>|**d Trac**<br>|**ing**<br>|
|---|---|---|---|---|---|---|---|---|---|---|---|
||_OCR_|_ACR_|_ATR_|_STU_|_FPD_|_OJR_|_Avg._|_EPM_|_ASI_|_HLD_|_Avg._|
|GPT-4o [40]|69.8|64.22|71.55|51.12|70.3|59.78|64.46|**57.91 **|**75.68**|48.66|**60.75**|
|Qwen2-VL-72B [1]|65.77|60.55|69.83|51.69|69.31|54.35|61.92|52.53|60.81|**57.53**|56.95|
|LLaVA-Video-7B [29]|69.13|58.72|68.83|49.44|**74.26**|59.78|63.52|56.23|57.43|7.53|40.4|
|LLaVA-OneVision-7B [29]|66.44|57.80|73.28|53.37|71.29|61.96|64.02|54.21|55.41|21.51|43.71|
|InternVL-V2-8B [6]|67.11|60.55|63.79|46.07|68.32|56.52|60.39|48.15|57.43|24.73|43.44|
|LongVU-7B [51]|53.69|53.21|62.93|47.75|68.32|59.78|57.61|40.74|59.46|4.84|35.01|
|VideoLLM-online-8B [5]|8.05|23.85|12.07|14.04|45.54|21.20|20.79|22.22|18.80|12.18|17.73|
|EyeWO [74]|24.16|27.52|31.89|32.58|44.55|35.87|32.76|39.06|38.51|6.45|28.00|
|Dispider [46]|57.72|49.54|62.07|44.94|61.39|51.63|54.55|48.48|55.41|4.3|36.06|
|**EgoMemo (Ours)**|**91.28**|**75.23**|**77.59**|**62.92**|69.31|**75.54**|**75.15**|52.53|50.00|44.62|49.60|



yields a modest reduction (8.0 _→_ 6.9), with the impact concentrated on Memory Link (4.9 _→_ 3.2) and Routine Optimization (11.8 _→_ 6.4), where visual cues help identify recurring objects or scenes that textual descriptions alone may miss. Removing the knowledge graph pathway ( _w/o GSR_ ) reduces F1 to 6.5, with Memory Link dropping sharply to 0.0, highlighting the graph’s role in linking semantically related entities across time. Without multi-scale temporal retrieval ( _w/o MTR_ ), F1 drops to 6.8, and Memory Link falls to 2.1, as the system loses its primary mechanism for locating temporally relevant context at the appropriate granularity. 

Taken together, caption reconstruction and graph semantic retrieval have the largest individual impact, while all three retrieval pathways (temporal, semantic, and visual) contribute complementary evidence. No single pathway subsumes another, validating the design of parallel heterogeneous retrieval for proactive assistance. 


![](assets/081/paper-0013-05.png)


**Fig. 4: Qualitative examples of EgoMemo’s proactive assistance.** Left: an instant Safety Alert service triggered by observing the user scrubbing a knife barehanded. Right: a long-term Routine Optimization service triggered on Day 2 by detecting a recurring pattern of prolonged phone recording across multiple sessions and days.

<!-- Page 14 -->

14 Sitong Gong et al. 

**Qualitative Analysis** Fig. 4 shows two representative examples of EgoMemo’s proactive behavior on EgoServe. In the left example, the agent observes the user scrubbing a knife and immediately triggers a Safety Alert based solely on the current clip-level caption. In the right example, the agent detects on Day 2 that the user has been holding a phone with a timer on screen; it retrieves crosssession memory confirming a recurring pattern of prolonged recording across multiple days, and triggers a Routine Optimization service suggesting ways to streamline this behavior. 

### **5.3 Generalization to Existing Benchmarks** 

We further evaluate EgoMemo on five established benchmarks to verify that its architecture generalizes beyond proactive assistance. **ESTP-Bench** (Table 2). EgoMemo achieves the best overall score of 27.6 **Table 4: Results on offline ego-** on explicit proactive tasks, surpass- **centric video benchmarks.** For Egoing EyeWO (23.6), with particularly TaskQA, we convert the dataset into MCQ format following [71].71].]. strong gains on context-dependent sub- **Method** _<mark>EgoQAEgo-</mark>_ tasks such as TRU (32.4 vs. 25.1) and _TaskQA Ego4D Schema_ EOSC (35.8 vs. 20.8). On implicit proacLLaVA-OneVision-7B [29] 55.8 65.7 60.1 tive tasks, EgoMemo scores 34.7 comVideoLLaMA3VideoChat2-HD[68[31] ] 56.645.5 62.452.0 61.155.8 pared to EyeWO’s 52.5. Notably, EyeWO Exo2Ego-7B [71] 48.1 62.1 61.3 is the only trained model in this comparQwen2-VL-7B [1] 57.9 60.3 63.3 EgoThinker <u>[43]</u> **64.4** <u>66.2 67.6</u> ison; all others, including EgoMemo, are **<mark>EgoMemo</mark>** **<u><mark>(Ours)</mark></u>** <u><mark>60.9</mark></u> **<mark>68.0 74.8</mark>** entirely training-free. 

**Table 4: Results on offline egocentric video benchmarks.** For EgoTaskQA, we convert the dataset into MCQ format following [71].71].]. 

**OVO-Bench** (Table 3). EgoMemo achieves the best real-time perception score of 75.15, outperforming GPT-4o (64.46) and LLaVA-OneVision (64.02). On backward tracing, EgoMemo scores 49.60, competitive with GPT-4o (60.75); the gap is expected given the substantially larger capacity and context windows of proprietary models. 

**Offline egocentric QA** (Table 4). EgoMemo achieves the best scores on two of the three egocentric QA datasets: EgoSchema (74.8, +7.2 over EgoThinker) and QAEgo4D (68.0 vs. 66.2), demonstrating that structured memory access is particularly effective for long-form temporal reasoning. On EgoTaskQA, EgoMemo scores 60.9, competitive with EgoThinker (64.4), where fine-grained action-state reasoning within short procedural segments favors direct visual perception over memory retrieval. 

These results confirm that EgoMemo’s streaming-first design generalizes across both streaming and offline settings without architectural modification. 

## **6 Conclusion** 

We presented EgoServe, the first large-scale benchmark for proactive assistance in continuous egocentric video, comprising over 3,000 service instances across 10 categories and 4 temporal memory horizons. Alongside the benchmark, we

<!-- Page 15 -->

Vinci2 15 

introduced EgoMemo, a training-free, memory-augmented agent that maintains multi-scale temporal summaries, an evolving knowledge graph, and a visual embedding archive to perform retrieval-augmented reasoning over streaming video. Experiments show that EgoMemo establishes strong baselines on EgoServe and achieves competitive or state-of-the-art results on 5 existing benchmarks. **Limitations and future work.** EgoMemo’s text-based memory loses finegrained visual details during captioning, and the name-based entity resolution may fail for visually ambiguous entities. The semi-automated annotation pipeline may also introduce biases toward service types that are easier for foundation models to generate. Future directions include learning intervention timing from human preferences, incorporating audio context, and extending EgoServe to multi-turn proactive dialogues and multi-user settings. 

## **7 Acknowledgement** 

The paper is supported in part by the National Natural Science Foundation of China under grant No.62441231, 62293542, Liao Ning Province Science and Technology Plan No.2023JH26/10200016, Dalian City Science and Technology Innovation Fund No.2023JJ11CG001, and Ningbo Key R&D project under Grant No.2025Z039. 

## **A. EgoServe Benchmark** 

We first compare EgoServe with existing video understanding benchmarks in Table 5. EgoServe is the first benchmark that simultaneously covers egocentric perspective, multi-day temporal span, proactive service evaluation, and streaming inference protocol, comprising 3.4k service instances across _∼_ 128h of video from three complementary source datasets. 

**Table 5:** Comparison between EgoServe and existing video understanding benchmarks. 

|**Benchmark**|**#Pairs**|**Total Len**|**Ego**|**Multi-Day**|**Proactive**|**Streaming**|
|---|---|---|---|---|---|---|
|OVO-Bench [39]|2.8k|-|✗|✗|✗|✓|
|StreamingBench [34]|4.5k|-|✗|✗|✗|✓|
|EgoSchema [38]|5k|_∼_250h|✓|✗|✗|✗|
|EgoLife [64]|3k|_∼_266h|✓|✓|✗|✗|
|ProAssist [73]|30.1k|_∼_478h|✓|✗|✓|✓|
|**EgoServe (Ours)**|3.4k|_∼_128h|✓|✓|✓|✓|



### **A.1 Annotation Details** 

We describe the annotation procedure for each source dataset in detail. As illustrated in Fig. 2 of the main paper, the annotation pipeline follows a semiautomated approach: category-specific prompts guide Gemini-2.5-Pro [57] to

<!-- Page 16 -->

16 Sitong Gong et al. 

generate candidate proactive service instances from existing human annotations, and all generated candidates undergo manual verification before inclusion in the final benchmark. The complete prompt templates for all service categories are provided at the end of this supplementary material. 

**EgoLife Subset** EgoLife provides multi-day continuous egocentric recordings with dense captions spanning the first five days of three participants (A1, A4, A5). As shown in Fig. 2 (a) of the main paper, the annotation pipeline follows two distinct processing paths depending on the temporal horizon of the target service: the upper path handles Instant, Short-Term, and Episodic services, while the lower path handles Long-Term services. 

**Stage 1: Preparing 1-hour human annotations.** Initially, we segment each participant’s daily recording into non-overlapping 1-hour intervals. For each interval, we collect all available human annotations—including dense captions, action descriptions, speaker transcripts, and interaction logs—and organize them in chronological order as a structured JSON document. This document, together with a summarization prompt, is streamed into the Gemini Annotator to produce a condensed activity record for the interval, capturing key events, objects, locations, and social interactions. These interval-level summaries serve as the input to the second stage. 

**Stage 2: Proactive service generation.** For **Instant, Short-Term, and Episodic** services (the upper path in Fig. 2(a)), each 1-hour interval is processed independently. The interval’s structured annotations are streamed into the Gemini Annotator together with a service-specific prompt (e.g., Safety Alert, Error Recovery, Task Reminder). The model directly triggers candidate service instances from the observations within that interval, producing structured JSON output conforming to a predefined schema that enforces fields such as temporal trigger window, service category, observation context, and proactive response. 

For **Long-Term** services (Habit Coaching, Memory Link, Routine Optimization, Personal Feedback), we follow the lower path in Fig. 2 (a) and adopt the streaming cue-capturing strategy described in Sec. 3.4 of the main paper. Rather than processing each interval independently, the Gemini Annotator first extracts cross-segment long-term events from each group of intervals, then carries the accumulated events to the next turn as additional context. Concretely, for each participant, the pipeline proceeds as follows: 

1. The first group of intervals (e.g., Day 1) is processed with the categoryspecific prompt. The Gemini Annotator identifies potential long-term events (e.g., recurring behaviors, unfinished plans) and outputs both cross-segment long-term events (new observations relevant to the service type) and candidate triggers (proactive service instances where sufficient evidence has accumulated). 

2. The extracted cross-segment long-term events are carried to the next turn: they are prepended to the prompt for the next group of intervals. This allows the model to reason over cross-session patterns—for example, a Habit

<!-- Page 17 -->

Vinci2 17 

Coaching trigger on Day 3 may reference behavioral patterns first observed on Day 1. 

3. This process repeats until all days have been processed, progressively building a richer context for long-term service detection. 

This streaming design ensures that long-term services are grounded in genuine multi-day patterns rather than being fabricated from single-interval observations. 

**HoloAssist Subset** HoloAssist captures task-oriented interactions where an instructor guides a user through procedural activities (e.g., assembling furniture, configuring devices). The dataset provides structured human annotations including step boundaries, instructor corrections, and error flags. 

Unlike EgoLife, HoloAssist annotations are processed in a single stage, as the task-oriented nature of the videos and the availability of fine-grained procedural annotations make direct service generation feasible. For each of the selected videos, we preprocess the full set of human annotations in chronological order and construct a structured JSON document containing the complete interaction timeline—step descriptions, instructor utterances, error labels, and step transitions. 

This document is then paired with a category-specific prompt and passed to Gemini. Due to the task-oriented nature of HoloAssist, annotations primarily cover **Instant** and **Short-Term** service categories: 

- **Safety Alerts (SA):** triggered when the user handles potentially dangerous tools or materials in an unsafe manner. 

- **Tool Use (TU):** triggered when the user could benefit from using a more appropriate tool or technique. 

- **Next-Step Guidance (NSG):** generated from step transition points, where the model produces guidance for the upcoming procedural step. 

- **Error Recovery (ER):** derived from instructor correction annotations, where the model generates corrective guidance when a procedural mistake is detected. 

- **Resource Reminder (RR):** triggered when the user is about to leave a resource unattended or a closure task incomplete, such as leaving a door open or walking away from an unsaved document. 

Each service category is annotated in a separate pass with its own prompt template and structured output schema, ensuring category-specific detection criteria and mutual exclusion rules are enforced. 

**CaptainCook4D Subset** CaptainCook4D provides structured cooking recordings with both correct and erroneous recipe executions across 24 recipes. We select 87 videos from the validation and test splits that contain explicit step-error annotations.

<!-- Page 18 -->

18 Sitong Gong et al. 

The annotation process leverages the procedural step annotations and error labels to generate proactive service instances focused on three categories: **Tool Use (TU)** , **Next-Step Guidance (NSG)** and **Error Recovery (ER)** . A single unified prompt instructs Gemini to map procedural step transitions to next-step guidance and error labels to corrective feedback. The structured recipe context (correct step sequences and annotated deviations) provides strong supervision for generating temporally precise and factually grounded service instances. 

**Output Schema and Quality Control** All annotation prompts enforce structured JSON output, where each service instance includes a temporal trigger window, service category label, observation context, and a proactive response. Long-Term service outputs additionally contain linked past events and crosssession reasoning chains. Category-level mutual exclusion rules are embedded in the prompts to prevent overlapping annotations, complementing the manual verification process described in Sec. 7. 

We provide visualization examples of the generated annotations for all 11 service subcategories in Fig. 8–11, organized by temporal horizon: Instant services (Safety Alert, Tool Use), Short-Term services (Error Recovery, Next-Step Guidance, Resource Reminder), Episodic services (Memory Recall, Task Reminder), and Long-Term services (Habit Coaching, Memory Link, Routine Optimization). 

These visualizations illustrate two key properties of our annotations. First, **contextual grounding** : every generated response is directly anchored in the observed video content. For Instant and Short-Term services, the responses reference specific objects, actions, or states visible in the current frames (e.g., a Safety Alert identifying an exposed hazard, or an Error Recovery correcting a procedural mistake observed in the clip). For Episodic and Long-Term services, the responses additionally draw on evidence from temporally distant past events— the “Past Linked Messages” and “Trigger Reason” fields in each visualization explicitly show what earlier observations support the current intervention and how they are connected across time gaps ranging from minutes to days. Second, **response effectiveness** : the generated proactive dialogues are phrased as natural, actionable suggestions rather than generic warnings. Each response addresses a specific user need at the moment of intervention: Episodic services such as Memory Recall and Task Reminder help the user recover forgotten context or resume interrupted activities, while Long-Term services such as Habit Coaching and Routine Optimization synthesize multi-day behavioral patterns into concrete improvement suggestions. This combination of temporal grounding and natural phrasing ensures that the annotations reflect realistic proactive assistance scenarios. 

### **A.2 Manual Verification** 

As described in Sec. 3.4 of the main paper, all generated annotation candidates undergo a manual verification process before inclusion in the final EgoServe benchmark.

<!-- Page 19 -->

Vinci2 19 

**Table 6:** Manual verification statistics for EgoServe annotations across all service categories. MV represents Manual Verification while Acc. Rate refers to acceptance rate. 

|**Metrics**|**Inst**<br>_SA_|**ant**<br>_TU_|**Sho**<br>_NSG_|**rt-ter**<br>_ER_|**m**<br>_RR_|**Epis**<br>_MR_|**odic**<br>_TR_|**Lo**<br>_HC_|**ng-ter**<br>_ML_|**m**<br>_RO_|**Overall**|
|---|---|---|---|---|---|---|---|---|---|---|---|
|Before MV|195|549|1392|1236|182|67|112|76|80|149|4038|
|After MV|241|510|1214|925|127|63|88|61|80|128|3437|
|Acc. Rate (%)|100|92.9|87.2|74.8|69.8|94.0|78.6|80.3|100.0|85.9|85.1|



**Verification procedure.** Two trained annotators jointly review each candidate annotation. For every service instance, both annotators watch the corresponding source video segment together and discuss whether the candidate should be accepted. A candidate is accepted only when both annotators reach consensus; otherwise it is discarded. The primary rejection criteria are: 

- **Lack of practical utility:** the generated response does not provide genuinely useful assistance to the user. For example, a service that repeats information the user has already obtained (e.g., “Based on the dance video you selected earlier, it is one minute and fifty-two seconds” when the user is already reading the duration on screen) is rejected, as it offers no additional value. 

- **Temporal misalignment:** the proposed trigger time window does not correspond to the actual video content—the triggering context described in the annotation is not present in the frames at the specified timestamps. 

- **Insufficient visual grounding:** the service content is generated purely from speech transcripts or dialogue context without incorporating visual observations. Since proactive assistance in egocentric video should be grounded in what the user _sees and does_ , annotations that rely solely on audio information are excluded. 

**Verification statistics.** Table 6 reports the manual verification results for each service category. Out of 4,038 candidates generated by the annotation pipeline, 3,437 remain after manual verification, yielding an overall acceptance rate of 85.1%. Among Instant services, Safety Alert (SA) is a special case: its count increases after verification (195 _→_ 241) rather than shrinking, because we found that Gemini had misclassified a number of genuine safety events into other categories and reassigned them back to SA during manual review; we therefore report its acceptance rate as 100%. Tool Use (TU) likewise attains a high rate of 92.9%, as both are triggered by immediately observable events that are straightforward to verify. Short-Term services show progressively lower rates: Next-Step Guidance (NSG) reaches 87.2%, whereas Error Recovery (ER: 74.8%) and especially Resource Reminder (RR: 69.8%, the lowest overall) are harder to confirm, reflecting the difficulty of precisely identifying procedural mistakes and recently-used resources from visual context alone. Episodic services remain fairly reliable, with Memory Recall (MR) at 94.0% and Task Reminder (TR) at 78.6%, indicating that the temporal linking between past and current events is generally sound.

<!-- Page 20 -->

20 Sitong Gong et al. 

Among Long-Term services, Memory Link (ML) is fully retained (100.0%) and Routine Optimization (RO) reaches 85.9%, while Habit Coaching (HC) has the lowest rate at 80.3%, as cross-session behavioral patterns are more susceptible to generating responses with insufficient practical utility. Overall, these results confirm that our semi-automated pipeline produces high-quality candidates, and that manual verification not only filters unreliable instances but also corrects category misassignments, ensuring the quality of the final EgoServe benchmark. 

## **B. Methods** 


![](assets/081/paper-0020-03.png)


<!-- Start of picture text -->
𝑓11 𝑓12 𝑓13 𝑓14 𝑓15 … … 𝑓𝑡1 𝑓𝑡2 𝑓𝑡3 𝑓𝑡4 𝑓𝑡5 … IncomingFrames<br>𝑣1 𝑣𝑡<br>𝑐 1 𝑐𝑡<br>{"dense_caption": {"DAY1-11:09:43-11:09:48": " I hold my phone  {"dense_caption": {"DAY1-11:13:50-11:13:55": " I place my<br>in my right hand  …", "DAY1-11:09:48-11:09:53": " I use both  hand on the screen of a laptop on the top shelf of my desk<br>hands to interact with my phone  ...", "DAY1-11:09:53-11:09:58":  tower  ...", "DAY1-11:13:55-11:14:00": " I extend my arm  𝑅𝑡<br>" app icons I hold my phone with both hands, displaying the home screen with  …", "DAY1-11:09:58-11:10:00": " I hold my phone with  … … upward and away from the desk, reaching toward the wall  "DAY1-11:14:00-11:14:05": " I reach forward with my left hand  ...",<br>both hands, displaying a timer at  "description": " I hold my phone and navigate its interface while  ...", …},  toward a laptop on the middle shelf of the desk tower  "description": " I repeatedly reach toward and interact with  ...", …},  Extract Entities<br>seated at a table with others …"} multiple laptops and monitors on my desk setup  ..."} Merge<br>Clip-level Captions 𝑀𝐶<br>𝐺𝑡<br>"1-11:09:45-11:14:47": " I remain seated at a table with four<br>Activity-level Captions 𝑀𝐴 others, interacting with devices and materials throughout the  …<br>session. I repeatedly hold and gesture with my phone  …"<br>"1-11:09:45-12:12:12":  " I remain seated at the checkered  Text Embedding<br>Session-level Captions 𝑀𝑆 table for the full hour, hands mostly clasped or resting on<br>my lap, observing others without initiating action  ... "<br><!-- End of picture text -->

**Fig. 5:** Illustration of the multi-scale temporal memory construction. Clip-level captions _MC_ preserve fine-grained timestamped action descriptions, which are progressively summarized into activity-level ( _MA_ ) and session-level ( _MS_ ) captions covering broader temporal spans. 

### **B.1 Details on Multi-Scale Temporal Memory Construction** 

We provide additional details on the multi-scale temporal memory described in Sec. 4.1 of the main paper, with the concrete caption formats illustrated in Fig. 5. 

**Clip-level Captions** _MC_ **.** For each incoming video clip _vt_ , a vision-language model produces a structured JSON object containing two fields: (1) `dense_caption` , a dictionary mapping fine-grained timestamp intervals (e.g., "DAY1-11:09:4311:09:48") to per-interval action descriptions, and (2) `description` , a brief summary that captures the overall activity of the clip. Each timestamp follows the format `DAY{d}-HH:MM:SS-HH:MM:SS` , which jointly encodes the day index and the absolute start/end time, enabling precise temporal localization across multiday recordings. Fig. 5 illustrates a concrete example from the EgoLife subset, where the clip-level captions effectively preserve fine-grained perceptual details such as object interactions and hand poses.

<!-- Page 21 -->

Vinci2 21 

**Activity-level Captions** _MA_ **.** As the clip-level caption stream grows, we periodically aggregate consecutive clip captions within a temporal window _Wj_ into an activity-level summary _MA_<sup>(</sup><sup>_j_)via an LLM-based summarize operation (Eq. 1 in</sup> the main paper). Each activity-level caption is stored with a merged timestamp (e.g., "1-11:09:45-11:14:47") spanning the full window duration, and condenses the fine-grained clip-level details into a coherent activity narrative—for example, _“I remain seated at a table with four others, interacting with devices and materials throughout the session.”_ This level captures medium-range behavioral context while significantly reducing memory size. 

**Session-level Captions** _MS_ **.** Similarly, activity-level summaries are further aggregated into session-level summaries _MS_<sup>(</sup><sup>_k_)</sup> over a larger window _Wk_ . Sessionlevel captions cover a broader temporal span (e.g., "1-11:09:45-12:12:12" in the EgoLife subset) and distill the activity patterns into high-level descriptions of the user’s overall routine and behavioral state. This coarsest granularity allows the system to maintain a compact representation of long-horizon context spanning hours to days. In addition to the temporal hierarchy, we extract named entities (people, objects, locations) from each clip caption _ct_ to form the entity set _Rt_ (right side of Fig. 5), which are incrementally merged into the evolving knowledge graph _G_ to support structure-aware semantic retrieval. All captions at each level are encoded into dense embeddings _{e_<sup>_c_</sup> _i_<sup>_, ea_</sup> _j_<sup>_, e_</sup> _k_<sup>_s}_usingatextencoder</sup><sup>`TEnc`and</sup> indexed for similarity search during retrieval. The entire memory construction process—including caption generation, multi-scale summarization, entity extraction, and embedding indexing—operates in a fully streaming fashion: only newly accumulated segments trigger summarization at the next level, rather than reprocessing the entire history, ensuring that both computational cost and latency remain bounded as the video stream extends over multiple days. 

### **B.2 More Details on Different Benchmarks** 

We provide detailed configurations for adapting EgoMemo to each evaluation benchmark, covering the proactive EgoServe benchmark, the online OVO-Bench, and all offline egocentric benchmarks. As shown in Fig. 3 (b) of the main paper, at each reasoning step, the agent first decides whether retrieval is needed. This decision is made by the reasoning LLM itself through a structured prompt that instructs it to assess whether the available streaming context is sufficient to respond, or whether additional historical evidence must be retrieved. If retrieval is triggered, the agent generates a retrieval query and invokes the multi-pathway retrieval pipeline described in Sec. 4.2. 

**EgoServe (EgoLife Subset)** The EgoLife subset of EgoServe consists of multiday, multi-hour egocentric recordings. The memory construction and retrieval process follows the pipeline described in Sec. 4 of the main paper almost exactly, with all three levels of temporal memory ( _MC_ , _MA_ , _MS_ ) constructed and maintained in a streaming fashion.

<!-- Page 22 -->

22 Sitong Gong et al. 

**Table 7:** Detailed evaluation results of Precision (P) and Recall (R) on EgoServe benchmark. **w/o MS** replaces the three-level temporal memory hierarchy with a single clip-level caption store while **w/o Recons.** removes the VLM-based caption reconstruction step. 

|**Mdl**|_S_|_A_|_TU_||_NS_|_G_|_ER_||||_R_|_R_|_MR_|_T_|_R_|_H_|_C_|_ML_||_RO_|**AV**|**G**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|**oe**|P|R|P|R|P|R|P|R||P||R|P<br>R|P|R|P|R|P<br>R|P|R|P|R|
|Qwen3-VL-Plus|**8.8**|3.7|12.9|0.8|9.0|8.2|17.2|**7.5**||1.|7|**86.6**|0.0<br>0.0|3.9|1.1|**6.7**|3.3|0.0<br>0.0|0.0|0.0|6.0<br>|11.1|
|GPT-5-mini|7.0|**59.8**|7.7|2.4|8.5|10.9|10.6|0.5||2.|7|59.8|0.0<br>0.0|**11.5**|8.0|5.0|6.6|0.0<br>0.0|0.0|0.0|5.3<br>|14.8|
|w/o MS|6.3<br>|46.9|18.3|5.1|18.3|35.8|21.4|1.0||2.|6|35.4|3.8 **6.3**|1.8|6.8|2.8|**13.1**|3.7<br>1.2|4.4|7.8|8.3<br>|15.9|
|w/o Recons.|6.0<br>|43.1|20.2|4.7|**19.9 **|**38.0**|6.9|0.2||**3.**|**1**|40.9|0.0<br>0.0|3.3|9.1|3.8|9.8|0.0<br>0.0|5.3|6.2|6.8<br>|15.2|
|w/o VSR|6.7<br>|45.2|15.1|3.7|18.9|36.2|14.3|0.7||2.|1|27.6|1.0<br>1.6|4.1|**17.1**|2.5|**13.1**|4.4<br>2.5|4.6|10.2|7.4<br>|15.8|
|w/o GSR|7.2<br>|49.0|14.0|3.5|18.4|36.3|**30.0**|1.0||2.|6|36.2|2.3<br>3.2|3.0|11.4|1.5|6.6|0.0<br>0.0|4.1|7.8|8.3<br>|15.5|
|w/o MTR|5.5<br>|40.3|**21.9 **|**5.5**|18.6|36.2|15.0|0.7||2.|2|29.1|**5.4** 3.2|3.1|8.0|1.4|3.3|5.9<br>1.3|7.3|7.8|8.6<br>|13.5|
|**EgoMemo (Ours)**|6.5<br>|48.6|19.1|4.7|18.7|36.3|22.2|0.9||2.|5|33.9|3.1<br>4.8|3.5|14.8|2.2|11.5|**7.1**<br>**3.8**|**8.7**|**18.8**|**9.4**<br>|**17.8**|



At each reasoning step, the streaming input to the reasoning agent consists of the current clip-level caption _ct_ together with the most recent activity-level caption _MA_<sup>(</sup><sup>_j_), which provides broader situational context (e.g., what the user has</sup> been doing over the past several minutes) beyond the fine-grained details of the current clip alone. This combination allows the reasoner to make more informed intervention decisions and to generate temporally scoped retrieval queries when additional historical context is needed. 

Specifically, for **time-aware retrieval query generation** : when the reasoning agent determines that retrieval is necessary, it is additionally prompted to include a temporal scope descriptor (e.g., “last one hour”, “last day”) within the query. A separate LLM call then resolves this relative temporal reference against the known start and end times of each day’s recording, producing an absolute time range (e.g., DAY1-11:30:00 to DAY3-14:15:00). The subsequent retrieval is then restricted to captions falling within this resolved time window, which substantially reduces the search space for long multi-day recordings while preserving the ability to recall distant episodic events. 

**OVO-Bench** OVO-Bench evaluates online video understanding across two main question categories: realtime perception and backward tracing. 

**Realtime perception.** For realtime questions, the model must answer based on what is currently happening in the video. We directly provide the **clip-level captions from the last 10 seconds** together with **all available activitylevel and session-level summaries** to the reasoning agent, which outputs the answer without any retrieval step. This design reflects the nature of realtime queries: the answer lies in the most recent observations, while the global summaries supply sufficient contextual grounding. 

**Backward tracing.** For backward tracing questions, the model must reason about events that occurred earlier in the video. We adopt a coarse-to-fine inference strategy: all activity-level and session-level summaries are provided as global context, and the agent first attempts to answer from this high-level information. If the agent judges the context insufficient, it generates a retrieval query and invokes the retrieval pipeline to fetch fine-grained clip-level evidence, following the same iterative retrieve-and-reason process.

<!-- Page 23 -->

Vinci2 23 

**Offline Egocentric Benchmarks** We provide the detailed configuration for each offline benchmark as follows. 

**EgoSchema.** Each video in EgoSchema is approximately 3 minutes long. Given this moderate duration, we construct only two levels of temporal memory: **cliplevel** captions _MC_ with a window size of 15 seconds, and **activity-level** summaries _MA_ with a window size of 1 minute, yielding roughly 12 clip-level captions and 3 activity-level summaries per video. Session-level summaries _MS_ are omitted as the video length does not warrant a third level of abstraction. 

During the caption generation phase, we provide the VLM with not only the sampled video frames of each clip but also the question and its candidate answer options. This encourages the VLM to attend to visual details that are relevant to the downstream question, producing more informative and targeted clip-level descriptions than generic captions would offer. 

At inference time, the agent first receives all three activity-level summaries as global context and attempts to answer the question based on this high-level information alone. If the agent determines that the available context is insufficient, it generates a retrieval query and invokes the retrieval pipeline (Sec. 4.2) to retrieve fine-grained clip-level evidence. This retrieve-and-reason cycle is repeated for up to 3 rounds, allowing the agent to progressively gather more specific evidence until a confident answer is reached. 

**EgoTaskQA and QAEgo4D.** EgoTaskQA and QAEgo4D are short-duration egocentric video understanding benchmarks, where video lengths range from a few seconds to several minutes. We construct temporal memory using a **cliplevel** window of 10 seconds and an **activity-level** window of 1 minute, with session-level summaries again omitted due to the limited video duration. The question-aware captioning strategy described above is applied identically. 

Since many videos in these benchmarks are very short (under 10 seconds), a fixed coarse-to-fine strategy would be unnecessarily complex. We therefore adopt an adaptive approach: the agent first checks whether any activity-level summaries exist for the given video. If no activity-level summary is available— indicating that the video is too short for even a single activity-level aggregation window—all clip-level captions are directly provided to the reasoning agent, which is prompted to output an answer without invoking retrieval. If activitylevel summaries do exist, the inference procedure follows the same coarse-tofine retrieval process as EgoSchema: the agent first attempts to answer from activity-level context, and resorts to iterative retrieval over clip-level captions when needed. 

## **C. Experiments** 

### **C.1 Detailed Results on EgoServe Benchmark** 

**Precision and Recall breakdown (Table 7).** Table 7 reports per-category Precision (P) and Recall (R) on the full EgoServe benchmark. Across all models, average Recall consistently exceeds Precision, indicating that the primary bottleneck lies in generating precisely timed and relevant interventions rather than

<!-- Page 24 -->

24 Sitong Gong et al. 

**Table 8:** Evaluation results on EgoLife subset. 

|**Model**|**Inst**<br>_SA_|**ant**<br>_TU_|**Sho**<br>_NSG_|**rt-te**<br>_ER_|**rm**<br>_RR_|**Epis**<br>_MR_|**odic**<br>_TR_|**Lo**<br>_HC_|**ng-t**<br>_ML_|**erm**<br>_RO_|**Overall**|
|---|---|---|---|---|---|---|---|---|---|---|---|
|Qwen3-VL-Plus|6.2|5.0|9.4|**4.4**|3.7|0.0|1.8|4.4|0.0|0.0|3.5|
|GPT-5-mini|10.3|0.0|8.6|0.0|6.7|0.0|**9.4**|**5.7**|0.0|0.0|4.1|
|w/o MS|14.3|8.0|7.6|0.0|9.6|**4.8**|2.9|4.6|1.9|5.7|5.9|
|w/o Recons.|13.0|**9.1**|9.5|0.0|**11.9**|0.0|4.8|5.4|0.0|5.7|5.9|
|w/o VSR|14.9|4.9|5.7|0.0|7.5|1.2|6.6|4.2|3.2|6.4|5.5|
|w/o GSR|**18.5**|0.0|7.3|0.0|9.7|2.6|4.8|2.4|0.0|5.4|5.1|
|w/o MTR|12.1|0.0|**12.3**|0.0|7.5|4.0|4.5|2.0|2.1|7.6|5.2|
|**EgoMemo (Ours)**|18.2|4.4|8.8|0.0|8.8|3.8|5.7|3.7|**4.9**|**11.9**|**7.0**|



missing service opportunities. Our full model (EgoMemo) achieves the highest average Precision (9.4) and Recall (17.8), confirming that the complete pipeline strikes a reasonable balance between proactive coverage and intervention quality. Among the baselines, GPT-5-mini exhibits a strong Recall bias (14.8) with very low Precision (5.3), suggesting frequent but poorly targeted interventions. 

Comparing ablation variants, remov- 

ing the multi-scale temporal retrieval **Table 9:** Evaluation results on Captain(w/o MTR) causes the largest Recall cook4d subset. **<mark>Instant Short-term</mark>** drop in Long-Term categories (e.g., RO: **Model** _<mark>SA TU NSG ER RR</mark>_ **Overall** 7.8 vs. 18.8), while removing caption reQwen3-VL-Plus 3.9 2.4 **12.2 10.0 2.3** 6.2 construction (w/o Recons.) yields the GPT-5-miniw/o MS **22.8** 12.9 9.98.3 7.79.5 1.52.0 2.01.8 **8.4** 7.2 largest drop in average Precision (6.8 vs. w/o Recons. 12.1 11.3 9.6 0.5 1.8 7.1 9.4) and collapses Memory Recall and w/ow/o VSRGSR 12.513.7 8.88.5 10.39.4 1.50.5 1.62.0 6.87.0 Memory Link to zero (MR: 0.0 vs. 4.8; w/o MTR 11.5 **14.5** 10.0 0.5 2.1 7.7 ML: 0.0 vs. 3.8 in Recall), reflecting the **<mark>EgoMemo</mark>** **<u><mark>(Ours)</mark></u>** <mark>12.2 11.0 9.3 1.5 2.1 7.2</mark> importance of caption reconstruction for grounding episodic and long-term retrieval. 

**Table 9:** Evaluation results on Captaincook4d subset. 

**Per-subset results (Tables 8–10).** Tables 8–10 break down the F1 scores across the three source datasets. On the EgoLife subset (Table 8), EgoMemo achieves the best overall score (7.0), with notable advantages in Routine Optimization (11.9) and Memory Link (4.9); the multi-scale temporal retrieval (w/o MTR) and graph-based semantic retrieval (w/o GSR) ablations show the largest 

drops, underscoring the importance of hierarchical context and entity semantics for multi-day recordings. On CaptainCook4D (Table 9), the scores are generally higher due to the structured procedural nature of cooking tasks, with EgoMemo reaching 7.2 overall. Here GPT-5-mini yields the best overall score (8.4), demonstrating its strength in detecting safety-related events in cooking 

**Table 10:** Evaluation results on HoloAssist subset. 

|**Mdl**|**Inst**|**ant**|**Sho**|**rt-ter**|**m**|**Oll**|
|---|---|---|---|---|---|---|
|**oe**|_SA_|_TU_|_NSG_|_ER_|_RR_|**vera**|
|Qwen3-VL-Plus|0.0|0.0|7.1|**11.7**|0.0|3.8|
|GPT-5-mini|0.0|0.0|11.0|0.8|**0.6**|2.5|
|w/o MS|1.1|**6.0**|36.1|1.9|0.0|**9.0**|
|w/o Recons.|1.2|3.5|**38.0**|0.4|0.0|8.6|
|w/o VSR|**3.2**|3.3|37.0|1.2|0.0|8.9|
|w/o GSR|2.2|3.4|36.2|3.2|0.0|**9.0**|
|w/o MTR|1.6|4.2|35.5|1.9|0.0|8.6|
|**EgoMemo (Ours)**|1.2|4.7|36.3|2.0|0.0|8.8|

<!-- Page 25 -->

Vinci2 25 

**Table 12:** Detailed results of LLM evaluation on EgoServe benchmark. R represents the rationality and E refers to effectiveness. 

|Eval LLM|Metrics|Qwen3-VL-Plu|s<br>GPT-5-mini|w/o MS<br>w|/o Recons|w/o VSR<br>|w/o GSR<br>|w/o MTR|EgoMemo|
|---|---|---|---|---|---|---|---|---|---|
||R|2.5|**2.7**|2.5|2.5|2.5|2.5|2.5|2.5|
|GPT-4o [40]|E|3.0|**3.3**|3.0|3.0|3.0|3.0|2.9|3.0|
||Overall|2.8|**3.0**|2.8|2.8|2.8|2.8|2.7|2.8|
||R|2.3|**2.5**|2.2|2.2|2.2|2.2|2.2|2.2|
|Deepseek-R1 [15]|E|2.5|**2.9**|2.6|2.4|2.4|2.5|2.3|2.5|
||Overall|2.4|**2.7**|2.4|2.3|2.3|2.4|2.2|2.3|



scenarios. On HoloAssist (Table 10), Next-Step Guidance dominates all models (36.3 for ours), while Instant and other Short-Term categories remain challenging. Notably, w/o GSR and w/o MS achieves the highest overall score (9.0) on this subset, suggesting that graph-based semantic retrieval and high-level captions provide limited benefit for short, self-contained procedural videos where the relevant context is mostly local. 

### **C.2 Retrieval Time Analysis** 

To compare retrieval efficiency across methods, we randomly sample 30 videos from the EgoSchema test set and measure the average time (in seconds) each method requires to process one minute of video under a single-retrieval setting, where the model decides whether retrieval is needed and performs at most one retrieval pass. As shown in Table 11, VideoAgent [60] requires 67.25 seconds per minute of video due to its iterative multi-round agent reasoning process. The base Qwen2.5VL-7B [3] model, which processes video frames directly without retrieval, achieves the lowest latency at 2.95 seconds, but lacks the ability to access historical context. Augmenting it with Video-RAG [37] increases the retrieval time to 20.81 seconds owing to the additional retrieval and context integration overhead. EgoMemo achieves a retrieval time of 13.11 seconds per minute of video, which is 5 _._ 1 _×_ faster than VideoAgent and 1 _._ 6 _×_ faster than Video-RAG, while supporting richer retrieval pathways (temporal, semantic, and visual). 

We note that EgoMemo’s memory construction phase takes 77.33 seconds per minute of video on average; however, since memory construction and downstream reasoning operate asynchronously in our streaming pipeline, this cost does not add to the per-query retrieval latency. 

**Table 11:** Retrieval time comparison across different methods, measured in seconds per minute of video. 

|**Method**|**Retrieval Time (Sec)**|
|---|---|
|VideoAgent|67.25|
|Qwen2.5VL-7B|2.95|
|Qwen2.5VL-7B + Video-RAG|20.81|
|**EgoMemo (Ours)**|13.11|



### **C.3 Evaluation Protocol** 

**Temporal matching.** Each predicted service event is characterized by a trigger time window ( _t_<sup>start</sup> _p , t_<sup>end</sup> _p_ ) and a service sub-type _sp_ ; ground-truth (GT) events are similarly defined as ( _t_<sup>start</sup> _g , t_<sup>end</sup> _g , sg_ ). To handle inherent temporal ambiguity in proactive service triggers, we introduce a dataset-specific tolerance _δ_ that

<!-- Page 26 -->

#### 26 Sitong Gong et al. 

reflects the annotation granularity and typical action duration of each dataset: _δ_ = 60 s for EgoLife (long-form daily activities with coarse temporal boundaries), _δ_ = 10 s for HoloAssist (short procedural tasks), and _δ_ = 25 s for CaptainCook4D (medium-length cooking sessions). Matching is performed **per sub-type in isolation** : for each service sub-type _s_ , we collect all predictions and GT events of type _s_ and apply greedy nearest-neighbor matching. Concretely, for each GT event _g_ , we compute the temporal center of every unmatched prediction _p_ and check whether it falls within the expanded window [ _t_<sup>start</sup> _g − δ, t_<sup>end</sup> _g_ + _δ_ ]. Among all qualifying candidates, the prediction with the smallest distance to the GT interval is selected as the match, where the distance is zero if the prediction center lies within [ _t_<sup>start</sup> _g , t_<sup>end</sup> _g_ ] and equals the gap to the nearest boundary otherwise. Each prediction can be matched to at most one GT event, enforcing a one-to-one assignment. 


![](assets/081/paper-0026-02.png)


<!-- Start of picture text -->
You are an expert evaluator of proactive assistant systems.<br>You are an expert evaluator of proactive assistant systems.<br>Your task: evaluate the EFFECTIVENESS of a predicted proactive service.<br>Your task: evaluate the RATIONALITY of a predicted proactive service by Focus on whether the message logically and helpfully assists the user.<br>comparing it against the ground truth (GT). Focus on semantic similarity<br>between the GT and predicted text. ------------------------------------------------------------<br>------------------------------------------------------------Input Input------------------------------------------------------------<br>------------------------------------------------------------ GT Service Type : {gt_service_type}<br>GT Message : {gt_user_prompt}<br>GT Service Type : {gt_service_type}<br>GT Message : {gt_user_prompt} Predicted Service Type : {pred_service_type}<br>Predicted Message : {pred_user_prompt}<br>Predicted Service Type : {pred_service_type}<br>Predicted Message : {pred_user_prompt} ------------------------------------------------------------<br>------------------------------------------------------------Evaluation Criteria — Rationality (1-5) Evaluation Criteria — Effectiveness (1-5)------------------------------------------------------------<br>------------------------------------------------------------ Assess whether the predicted message provides logical, helpful assistance:<br>- Does it logically address the user's situation?<br>Assess the semantic similarity between the predicted message and the GT: - Is the advice or information actionable and useful?<br>- Do both messages address the same underlying situation or need? - Is the reasoning behind the service sound?<br>- Is the predicted content semantically consistent with the GT? - Does it proactively help the user in a meaningful way?<br>- Are the key information elements preserved? - Is the tone and framing appropriate for a proactive assistant?<br>1 = Completely irrelevant or contradicts GT 1 = Illogical or unhelpful; provides no meaningful assistance<br>2 = Major semantic mismatch; addresses a different need 2 = Poorly reasoned; the help offered is confusing or misguided<br>3 = Partially aligned; captures some aspects but misses key points 3 = Somewhat helpful but lacks clear logic or actionability<br>4 = Mostly aligned; minor semantic differences 4 = Logically sound and helpful, minor issues<br>5 = Fully semantically equivalent to GT 5 = Excellent — clearly reasoned, actionable, and genuinely helpful<br>------------------------------------------------------------Output Format (STRICT — nothing else)------------------------------------------------------------ ------------------------------------------------------------Output Format (STRICT — nothing else)------------------------------------------------------------<br>Rationality: <1-5> Effectiveness: <1-5><br>Justification: <1-3 sentences> Justification: <1-3 sentences><br>(a) LLM Evaluation Prompt for Rationality (b) LLM Evaluation Prompt for Effectiveness<br><!-- End of picture text -->

**Fig. 6:** LLM Evaluation Prompts. 

**Detection metrics.** For each service sub-type _s_ , we aggregate matched, predicted, and GT counts _globally across all videos_ in the dataset and compute Precision, Recall, and F1: 


![](assets/081/paper-0026-05.png)

<!-- Page 27 -->

Vinci2 27 

We report the **macro-averaged F1** over all active sub-types (those with at least one GT or prediction) as the primary metric, which prevents dominant sub-types from overshadowing rare ones. 

**LLM-as-judge scoring.** Beyond detection accuracy, we evaluate the quality of generated service dialogues for successfully matched prediction–GT pairs. Following recent practices in open-ended generation evaluation [76], we employ an LLM as an automatic judge to assess two complementary dimensions on a 1– 5 scale, as shown in Fig. 6: (1) **Rationality** measures the semantic alignment between the predicted dialogue and the GT, considering whether both address the same underlying situation and preserve key informational elements; (2) **Effectiveness** evaluates whether the predicted dialogue provides logically sound, actionable, and genuinely helpful proactive assistance. Each dimension is scored independently with temperature 0 to ensure reproducibility, and we report the average score across all matched pairs. 

To further verify the robustness of our evaluation, we employ two independent LLM judges—GPT-4o [40] and DeepSeek-R1 [15]—and report the detailed Rationality (R) and Effectiveness (E) scores in Table 12. Although DeepSeekR1 is systematically stricter, assigning lower absolute scores than GPT-4o (mean overall 2.38 vs. 2.81), the two judges produce highly consistent _relative_ rankings across all models and ablation variants: both identify the same best-performing configuration (the GPT-5-mini baseline) and the same weakest one (w/o MTR). The per-model overall scores of the two judges are strongly correlated (Pearson r _≈_ 0.95), confirming that our conclusions are not sensitive to the choice of judge model. We further observe that, under both judges, Effectiveness scores are consistently higher than Rationality scores for all models, suggesting that the generated responses are generally helpful in tone and framing even when they do not precisely match the ground-truth semantics. 

### **C.3 More Qualitative Results** 

Fig. 7 presents qualitative examples of EgoMemo’s proactive assistance across four representative service categories on the EgoLife subset. Each example illustrates both the streaming decision process (Trigger vs. Keep Silent) and the generated service content. 

The top-left example shows a **Resource Reminder** triggered on Day 1: the system observes the user turning on the faucet at the sink and proactively reminds them to check that the water is not left running before walking away. The top-right example demonstrates a **Task Reminder** on Day 4: after the user moves away from a table with unfinished flower-arranging materials, the system reminds them to complete or tidy up the activity. Both cases rely solely on recent clip-level observations to detect closure failures or interrupted tasks within a short temporal window. 

The bottom two examples highlight services that require broader context. The **Next-Step Guidance** (bottom-left) is triggered on Day 2 when the user places a green box on the table during a meal, and the system suggests a natural follow-up action. The **Habit Coaching** example (bottom-right) demonstrates

<!-- Page 28 -->

- 28 Sitong Gong et al. 


![](assets/081/paper-0028-01.png)


<!-- Start of picture text -->
…<br>… …<br>Trigger Trigger Trigger Keep Silent Keep Silent Trigger Trigger Trigger<br>Observation :  I hold my phone in my left hand and use my right  Observation :  I hold the green hanger with both hands, standing near the washing<br>hand to turn on the faucet at the sink, while dishes and cleaning  machine with the hanger dangling in front of me (DAY2-13:55:10-13:55:15);<br>supplies are visible on the counter around the sink. retrieved memory shows the washer was left open earlier with clothes visible,<br>indicating a laundry load started earlier may remain unfinished .<br>Triggered Service:  Resource Reminder Triggered Service:  Task Reminder<br>Timestamp: DAY1 21:38:45-21:38:50 Timestamp: DAY2 13:55:10-13:55:15<br>Service Content:  It looks like you just turned on the faucet — Service Content:  It looks like a laundry load may still be unfinished—<br>would you like to check the sink to make sure it's not left running? would you like a quick reminder to check the washer now?<br>… …<br>Trigger Trigger Trigger Keep Silent Keep Silent Trigger Trigger Trigger<br>Observation + Retrieval:  I hold my phone in front of me and look at its screen<br>Observation :  I hold the green box steady on the table with my left  (DAY5-18:51:10-18:51:15); retrieved memory shows repeated, prolonged phone use<br>hand while looking toward the other people at the table. during social gatherings across multiple earlier days, indicating a recurring habit.<br>Triggered Service:  Next Step Guidance Triggered Service:  Habit Coaching<br>Timestamp: DAY2 11:41:45-11:41:50 Timestamp: DAY5 18:51:10-18:51:15<br>Service Content:  You just placed the green box and are holding it— Service Content:  You've been frequently holding and checking your phone<br>would you like a quick suggestion for what to do next, such as  during social gatherings over several days; would you like a quick tip to<br>putting it away or setting it aside so you can continue with the meal? help reduce phone use and be more present with others?<br><!-- End of picture text -->

**Fig. 7:** Qualitative examples of EgoMemo’s proactive assistance. 

the value of long-term memory retrieval: on Day 5, the system detects the user checking their phone and retrieves evidence of repeated phone use during social gatherings across multiple earlier days, synthesizing this cross-day pattern into a coaching suggestion to reduce screen time. Notably, the streaming timeline shows that EgoMemo appropriately remains silent during intervals where no actionable service opportunity is detected, avoiding unnecessary interruptions. 

## **References** 

1. Bai, J., Bai, S., Chu, Y., Cui, Z., Dang, K., Deng, X., Fan, Y., Ge, W., Han, Y., Huang, F., et al.: Qwen technical report. arXiv preprint arXiv:2309.16609 (2023) 12, 13, 14 

2. Bai, S., Cai, Y., Chen, R., Chen, K., Chen, X., Cheng, Z., Deng, L., Ding, W., Gao, C., Ge, C., et al.: Qwen3-vl technical report. arXiv preprint arXiv:2511.21631 (2025) 11 

3. Bai, S., Chen, K., Liu, X., Wang, J., Ge, W., Song, S., Dang, K., Wang, P., Wang, S., Tang, J., Zhong, H., Zhu, Y., Yang, M., Li, Z., Wan, J., Wang, P., Ding, W., Fu, Z., Xu, Y., Ye, J., Zhang, X., Xie, T., Cheng, Z., Zhang, H., Yang, Z., Xu, H., Lin, J.: Qwen2.5-vl technical report (2025), `https://arxiv.org/abs/2502.13923` 25 

4. Bärmann, L., Waibel, A.: Where did i leave my keys?-episodic-memory-based question answering on egocentric videos. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 1560–1568 (2022) 11 

5. Chen, J., Lv, Z., Wu, S., Lin, K.Q., Song, C., Gao, D., Liu, J.W., Gao, Z., Mao, D., Shou, M.Z.: Videollm-online: Online video large language model for streaming

<!-- Page 29 -->

Vinci2 29 


![](assets/081/paper-0029-01.png)


<!-- Start of picture text -->
Instant Proactive Services<br>Annotation Content Annotation Content<br>T i me Window: DAY1 13:11:19-13:11:20 Time Window :  DAY1 00:00 : 16-00:00:17<br>Observation : The user is manipulating a rack part which suddenly falls, indicating instability  Observation : The user attempts to open the front panel door while the circuit breaker lever<br>and risk of impact injury. is still in the 'on' position, neglecting to isolate power first.<br>Response:  Watch out, that rack part looks loose and might fall on your feet. Response :  Stop immediately! Do not open the panel door while the power is on.<br>(a) Safety Alert<br>Annotation Content Time Window: DAY1 00:11:56-00:15:44Annotation Content<br>Time Window: DAY1 00:04:14 - 00:04:55 Observation :  Mi c row ave- Microwave fo r  1 m i nute 20 secon ds, or until it rises  and the<br>Observation:  Stir-Stir the contents in the mug well toppings are bubbling<br>Response:  When you stir, keep the spoon mostly in the center and use small circles, then scrape  Response:  For this mug cake, aim for about 1 minute 20 seconds, and you can stop as soon as it<br>around the sides and bottom so everything gets fully combined without splashing over the rim. rises and the toppings are bubbling. If it looks like it’s climbing up the mug, pause early and let it<br>settle for a moment before deciding if it needs a few more seconds.<br>(b) Tool Use<br><!-- End of picture text -->

**Fig. 8:** Annotation examples of Instant proactive assistance. 


![](assets/081/paper-0029-03.png)


<!-- Start of picture text -->
Short-Term Proactive Services<br>Annotation Content Time Window: DAY1 00:03:05-00:04:14Annotation Content<br>Time Wi n dow: DAY1 00:00:16-00:00:19 Ob s erv a tion : Top-Top cup with 1 t a bles p oon of s a lsa.<br>Observation : The user withdraws the lens cover, but the instruction was to detach the lens;  Response:  It’ll work best if you add the salsa once the egg is almost set, and keep it to about 1<br>the explanation notes the student should withdraw the lens. tablespoon so it doesn’t get too wet. If you’ve already added more or added it early, you can spoon<br>Response:  Hold on, you have removed the lens cover, but the task is to detach the entire lens . a little back out and let it cook a bit longer to set up.<br>(a) Error Recovery<br>Annotation Content Annotation Content<br>Time Window: DAY1 00:00:29-00:00:31 Time W i ndow: DAY1 00:02:25-00:02:39<br>Observation : User has removed the GoPro from the packaging. Observation : Place the dripper on top of a coffee mug.<br>Response:  You have the GoPro ready. The next step is to swap out the battery. Response:  Before you start pouring, go ahead and set the dripper on top of your mug so it sits flat<br>and stable.<br>(b) Next-Step Guidance<br>Annotation Content Annotation Content<br>Time Window :  DAY1 00:08 : 26-00:08:45 Time Window: DAY1 12:46:54-12:46:5 8<br>Observation:  Put-Put all the Vegetables in a microwave-safe bowl Observation:  I was working on my laptop in the bedroom but got distracted by my phone<br>Response:  A few pieces of vegetable look like they’ve fallen onto the counter—would you like to  and walked out to the kitchen, leaving the laptop open.<br>scoop them back into the microwave-safe bowl (or discard them) before continuing? Response:  I noticed you headed to the kitchen, but your laptop is still open in the bedroom.<br>(c) Resource Reminder<br><!-- End of picture text -->

**Fig. 9:** Annotation examples of Short-term proactive assistance.

<!-- Page 30 -->

30 Sitong Gong et al. 


![](assets/081/paper-0030-01.png)


<!-- Start of picture text -->
Episodic Proactive Services<br>… …<br>Past Linked Messages 25 - mi n  Gap Time Wind ow: DAY5 1Annotation Content 5:20:53-15:21:01<br>Time Window: DAY5 14:55:11-14:55:13 Current Observation:  I am walking around the living room asking<br>Observation : I put the power bank down in the  Trigger Reason : I am currently searching for a power bank, but I placed  Alice, Tasha, and Lucia if there is a power bank available.<br>second-floor living room before heading downstairs. one on the table about 25 minutes ago which I may have forgotten. Response :  Are you looking for a power bank? You placed one on the table<br>when you first arrived about twenty minutes ago.<br>… …<br>Annotation Content<br>Past Linked Messages 9-min Ga p Time W indow:  DAY 2 1 1:05 : 14 -11:0 5:16<br>Current Observation:  I finish washing items, wipe my hands, and<br>iodine on Meituan since Jake didn't have anyTime Window: Observation : I confirmed I would order DAY2 10:56:54-10:56:56 Trigger Reason:  and has been busy washing dishes; recalling the order prompts a volume check to ensure the delivery is heard.The user ordered an urgent item (iodine) shortly ago  pick up my phone in the living room. Response been busy washing up, do you want to unmute your phone so you hear the delivery? : You ordered the iodine about ten minutes ago. Since you've<br>(a) Memory Recall<br>… …<br>Past Linked Messages 12- min Gap Time W ind ow: DAY4 16:28:31 Annotation Content- 16:2 8:33<br>Time Window: DAY4 16:16:06-16:16:07 Current Observation:  I walk away from the craft table towards the<br>Observation : I finished wrapping the strap  Trigger Reason : User is leaving the workspace and moving to the  refrigerator, effectively ending the crafting session.<br>around the iron ring for the wind chime but did not  kitchen to eat/chat, leaving the partially assembled wind chime on the  Response:  Since you're packing up and heading to the kitchen, I noticed<br>attach any hanging decorations. table.  you left your wind chime on the table. You finished wrapping the ring, but<br>haven't attached the butterflies or bells yet. Do you want to assemble it now?<br>… …<br>Annotation Content<br>Past Linked Messages 2-min  Ga p Time W ind ow: DAY4 17:23:34-17:23:36<br>Time Window: DAY4 17:21:03-17:21:05 Current Observation:  I put down the mobile phone after recording<br>Observation : I stated the intention to 'Record it and send it to your  Trigger Reason:  User puts the phone down and  and switch to relaxing and singing.<br>girlfriend' before starting to film Nicous. disengages from the device without performing  Response :  Since you're putting your phone down, I noticed you didn't send<br>the 'send' action mentioned earlier. that video of Nicous yet. Do you want to share it before you relax?<br>(b) Task Reminder<br><!-- End of picture text -->

**Fig. 10:** Annotation examples of Episodic proactive assistance.

<!-- Page 31 -->

Vinci2 

31 


![](assets/081/paper-0031-02.png)


<!-- Start of picture text -->
Long-Term Proactive Services<br>… …<br>Annotation Content<br>Time Window: DAY5 20:16:08-20:16:12Observation: User is drinking Coke Trigger Reason: Time since last drink exceeds 120 minutes while 2 -ho ur  Gap gathering. It has been over 2 hours (since 20:16) without a recorded drink.Ti Current Observation: me  Win dow :  DA Y5  22:19:13  User is eating pizza (salty food) during a social - 22:19:16<br>consuming salty food, increasing dehydration risk Response :  I see you're having some pizza. It's been about two hours since your<br>last water break—maybe grab a drink to go with it?<br>… …<br>Annotation Content Annotation Content<br>Time Window: Current Observation:  DA Y3 2 1:50:19-21:50:20 User is checking the  Cross-day Gap Time Window: DAY3 22:30:15-22:30:28<br>weather on their phone while sitting with friends,  Current Observation:  User is sitting at the outdoor table browsing<br>continuing a period of screen use that has crossed the 21:50 late-night threshold Response:  scrolling on your phone, just like last night. Staying on screens this late can delay your wind-down.It's past 9:50 PM and I notice you're still  Trigger Reason:  recreational scrolling (Day 3), mirroring the late-night screen habit from Day 1 and Day 2, which is concerning given the user's earlier mention of not feeling well.It is past 22:30 and the user is engaging in  Xiaohongshu posts instead of interacting or winding down.  Response again, similar to previous nights. Since you mentioned not feeling well earlier, it might be better to rest your eyes. : It's past 10:30 PM and I notice you're scrolling on your phone<br>(a) Habit-Coaching<br>… …<br>disposable tableware)Time Window: DAY1 Observation : Compile shopping list for afternoon trip (salt, sugar, Past Linked Messages13:29:18-13:29:22 Trigger Reason tableware (chopsticks) that were likely purchased as part of the shopping list made on Day 1. Cross-day Gap: I am retrieving the extra  kitchen cabinet. Response disposable tableware pack you bought yesterday? Ti Current Observation me Wind:  You're heading upstairs for chopsticks. Are these from the  ow: DAY3 22:24:40-22:24:41 Annotation Content: I go upstairs to search for chopsticks in the<br>… …<br>Time Window: DAY1 13:00:11-13:00:15Past Linked Messages Cro ss- day  Ga p Time Window: DAY2 11:50:54-11:50:58 Current Observation Annotation Content: I watch Jake take out a ruler and Alice<br>Observation : Plan to scan the house with  measure the table, engaging in manual measurement.<br>iPhone for 3D model Trigger Reason:  The group is measuring the room/furniture manually,  Response : I see they are measuring the table manually. Does Jake still<br>which relates to Jake's earlier plan to scan the house for a 3D model. plan to do the 3D iPhone scan he mentioned?<br>(b)Memory Link<br>… …<br>Time Observation Past Linked Messages Window: DAY3 : I take a photo of the strawberry 22:10:16-22 : 10:18 Time Observation Past Linked Messages Window: DAY4 : Taking Photos with a phone.  1 3:22 :17 - 13:22:20 arrangement and the plush toy in a social setting.  Ti Current Observation me  Window: DAY5 20:38:20-20:38:22 Annotation Content: The user is taking photos of the food<br>Cross-day Gap Response spread. Would you like me to sort these into your 'Collectibles' and 'Social  :  You're capturing some nice shots of the collection and the food<br>Events' albums automatically?<br>… …<br>Past Linked Messages Cross-day Gap Time Window: DAY5 20:50:Annotation Content 50 - 2 0:50 :52<br>Observation Time Window:: Searching charge cablesDAY4 21:33:59-21:34:01 Trigger Reason:  tech issues (Day 4 cable hunt, Day 2 power supply search). Recurring issues with specific devices suggest a need for maintenance tracking or logging faulty equipment.The user frequently acts as the troubleshooter for group  that isn't charging, testing cables and power banks. Response:  again. Since this keeps happening, would you like me to log a 'Service Request' for this specific pair so you remember to check them later? Current Observation You're troubleshooting the charging connection for those glasses  : The user is troubleshooting a pair of glasses<br>(c) Routine Optimization<br><!-- End of picture text -->

**Fig. 11:** Annotation examples of Long-term proactive assistance.

<!-- Page 32 -->

32 Sitong Gong et al. 

- video. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 18407–18418 (2024) 4, 12, 13 

- 6. Chen, Z., Wang, W., Cao, Y., Liu, Y., Gao, Z., Cui, E., Zhu, J., Ye, S., Tian, H., Liu, Z., et al.: Expanding performance boundaries of open-source multimodal models with model, data, and test-time scaling. arXiv preprint arXiv:2412.05271 (2024) 12, 13 

- 7. Cheng, S., Guo, Z., Wu, J., Fang, K., Li, P., Liu, H., Liu, Y.: Egothink: Evaluating first-person perspective thinking capability of vision-language models. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 14291–14302 (2024) 3 

- 8. Deng, Y., Lei, W., Lam, W., Chua, T.S.: A survey on proactive dialogue systems: Problems, methods, and prospects. arXiv preprint arXiv:2305.02750 (2023) 4 

- 9. Dey, A.K.: Understanding and using context. Personal and ubiquitous computing **5** (1), 4–7 (2001) 4 

- 10. Dong, Y., Kang, C., Zhang, J., Zhu, Z., Wang, Y., Yang, X., Su, H., Wei, X., Zhu, J.: Benchmarking robustness of 3d object detection to common corruptions. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 1022–1032 (2023) 3 

- 11. Fan, Y., Ma, X., Wu, R., Du, Y., Li, J., Gao, Z., Li, Q.: Videoagent: A memoryaugmented multimodal agent for video understanding. In: European Conference on Computer Vision. pp. 75–92. Springer (2024) 4, 11 

- 12. Girdhar, R., Grauman, K.: Anticipative video transformer. In: ICCV (2021) 3 13. Goyal, M., Modi, S., Goyal, R., Gupta, S.: Human hands as probes for interactive object understanding. In: CVPR (2022) 3 

- 14. Grauman, K., Westbury, A., Byrne, E., Chavis, Z., Furnari, A., Girdhar, R., Hamburger, J., Jiang, H., Liu, M., Liu, X., et al.: Ego4d: Around the world in 3,000 hours of egocentric video. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 18995–19012 (2022) 3 

- 15. Guo, D., Yang, D., Zhang, H., Song, J., Wang, P., Zhu, Q., Xu, R., Zhang, R., Ma, S., Bi, X., et al.: Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948 (2025) 25, 27 

16. He, B., Li, H., Jang, Y.K., Jia, M., Cao, X., Shah, A., Shrivastava, A., Lim, S.N.: Ma-lmm: Memory-augmented large multimodal model for long-term video understanding. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 13504–13514 (2024) 4 

17. He, Y., Huang, Y., Chen, G., Pei, B., Xu, J., Lu, T., Pang, J.: Egoexobench: A benchmark for first-and third-person view video understanding in mllms. arXiv preprint arXiv:2507.18342 (2025) 3 

18. Huang, Y., Cai, M., Li, Z., Lu, F., Sato, Y.: Mutual context network for jointly estimating egocentric gaze and action. IEEE Transactions on Image Processing **29** , 7795–7806 (2020) 3 

19. Huang, Y., Cai, M., Li, Z., Sato, Y.: Predicting gaze in egocentric video by learning task-dependent attention transition. In: ECCV (2018) 3 

20. Huang, Y., Chen, G., Xu, J., Zhang, M., Yang, L., Pei, B., Zhang, H., Dong, L., Wang, Y., Wang, L., et al.: Egoexolearn: A dataset for bridging asynchronous egoand exo-centric view of procedural activities in real world. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 22072– 22086 (2024) 3 

21. Huang, Y., Sugano, Y., Sato, Y.: Improving action segmentation via graph-based temporal reasoning. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 14024–14034 (2020) 3

<!-- Page 33 -->

Vinci2 33 

22. Huang, Y., Xu, J., Pei, B., He, Y., Chen, G., Yang, L., Chen, X., Wang, Y., Nie, Z., Liu, J., et al.: Vinci: A real-time embodied smart assistant based on egocentric vision-language model. arXiv preprint arXiv:2412.21080 (2024) 2, 4 

23. Huang, Y., Yang, L., Chen, G., Zhang, H., Lu, F., Sato, Y.: Matching compound prototypes for few-shot action recognition. International Journal of Computer Vision **132** (9), 3977–4002 (2024) 3 

24. Huang, Y., Yang, L., Sato, Y.: Weakly supervised temporal sentence grounding with uncertainty-guided self-training. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 18908–18918 (2023) 3 

25. Jeong, S., Kim, K., Baek, J., Hwang, S.J.: Videorag: Retrieval-augmented generation over video corpus. In: Findings of the Association for Computational Linguistics: ACL 2025. pp. 21278–21298 (2025) 4 

26. Jia, B., Lei, T., Zhu, S.C., Huang, S.: Egotaskqa: Understanding human tasks in egocentric videos. Advances in Neural Information Processing Systems **35** , 3343– 3360 (2022) 11 

27. Kang, C., Huang, Y., Ouyang, L., Zhang, M., Liu, R., Sato, Y.: Can mllms read the room? a multimodal benchmark for assessing deception in multi-party social interactions. arXiv preprint arXiv:2511.16221 (2025) 2 

28. Lee, G., Xia, M., Numan, N., Qian, X., Li, D., Chen, Y., Kulshrestha, A., Chatterjee, I., Zhang, Y., Manocha, D., et al.: Sensible agent: A framework for unobtrusive interaction with proactive ar agents. In: Proceedings of the 38th Annual ACM Symposium on User Interface Software and Technology. pp. 1–22 (2025) 4 

29. Li, B., Zhang, Y., Guo, D., Zhang, R., Li, F., Zhang, H., Zhang, K., Zhang, P., Li, Y., Liu, Z., et al.: Llava-onevision: Easy visual task transfer. arXiv preprint arXiv:2408.03326 (2024) 12, 13, 14 

30. Li, K., He, Y., Wang, Y., Li, Y., Wang, W., Luo, P., Wang, Y., Wang, L., Qiao, Y.: Videochat: Chat-centric video understanding. Science China Information Sciences **68** (10), 200102 (2025) 2 

31. Li, K., Wang, Y., He, Y., Li, Y., Wang, Y., Liu, Y., Wang, Z., Xu, J., Chen, G., Luo, P., et al.: Mvbench: A comprehensive multi-modal video understanding benchmark. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 22195–22206 (2024) 3, 14 

32. Li, Y.M., Huang, W.J., Wang, A.L., Zeng, L.A., Meng, J.K., Zheng, W.S.: Egoexofitness: Towards egocentric and exocentric full-body action understanding. In: European conference on computer vision. pp. 363–382. Springer (2024) 3 

33. Lin, B., Ye, Y., Zhu, B., Cui, J., Ning, M., Jin, P., Yuan, L.: Video-llava: Learning united visual representation by alignment before projection. In: Proceedings of the 2024 conference on empirical methods in natural language processing. pp. 5971– 5984 (2024) 2 

34. Lin, J., Fang, Z., Chen, C., Wan, Z., Luo, F., Li, P., Liu, Y., Sun, M.: Streamingbench: Assessing the gap for mllms to achieve streaming video understanding. arXiv preprint arXiv:2411.03628 (2024) 15 

35. Liu, J., Yu, Z., Lan, S., Wang, S., Fang, R., Kautz, J., Li, H., Alvare, J.M.: Streamchat: Chatting with streaming video. arXiv preprint arXiv:2412.08646 (2024) 4 

36. Long, L., He, Y., Ye, W., Pan, Y., Lin, Y., Li, H., Zhao, J., Li, W.: Seeing, listening, remembering, and reasoning: A multimodal agent with long-term memory. arXiv preprint arXiv:2508.09736 (2025) 4 

37. Luo, Y., Zheng, X., Li, G., Yin, S., Lin, H., Fu, C., Huang, J., Ji, J., Chao, F., Luo, J., et al.: Video-rag: Visually-aligned retrieval-augmented long video comprehension. arXiv preprint arXiv:2411.13093 (2024) 3, 4, 25

<!-- Page 34 -->

- 34 Sitong Gong et al. 

38. Mangalam, K., Akshulakov, R., Malik, J.: Egoschema: A diagnostic benchmark for very long-form video language understanding. Advances in Neural Information Processing Systems **36** , 46212–46244 (2023) 3, 11, 15 

39. Niu, J., Li, Y., Miao, Z., Ge, C., Zhou, Y., He, Q., Dong, X., Duan, H., Ding, S., Qian, R., et al.: Ovo-bench: How far is your video-llms from real-world online video understanding? In: Proceedings of the Computer Vision and Pattern Recognition Conference. pp. 18902–18913 (2025) 3, 4, 11, 15 

40. OpenAI: Introducing GPT-4o and More Tools to ChatGPT Free Users. `https: //openai.com` (2024), accessed: 2026-03-06 13, 25, 27 

41. OpenAI: GPT-5.1 (2025), `https://openai.com` , large language model 7, 11 42. Peddi, R., Arya, S., Challa, B., Pallapothula, L., Vyas, A., Gouripeddi, B., Zhang, Q., Wang, J., Komaragiri, V., Ragan, E., et al.: Captaincook4d: A dataset for understanding errors in procedural activities. Advances in Neural Information Processing Systems **37** , 135626–135679 (2024) 3, 5 

43. Pei, B., Huang, Y., Xu, J., He, Y., Chen, G., Wu, F., Qiao, Y., Pang, J.: Egothinker: Unveiling egocentric reasoning with spatio-temporal cot. arXiv preprint arXiv:2510.23569 (2025) 14 

44. Plizzari, C., Goletto, G., Furnari, A., Bansal, S., Ragusa, F., Farinella, G.M., Damen, D., Tommasi, T.: An outlook into the future of egocentric vision. arXiv preprint arXiv:2308.07123 (2023) 3 

45. Plizzari, C., Planamente, M., Goletto, G., Cannici, M., Gusso, E., Matteucci, M., Caputo, B.: E2 (go) motion: Motion augmented event stream for egocentric action recognition. In: CVPR (2022) 3 

46. Qian, R., Ding, S., Dong, X., Zhang, P., Zang, Y., Cao, Y., Lin, D., Wang, J.: Dispider: Enabling video llms with active real-time interaction via disentangled perception, decision, and reaction. In: Proceedings of the Computer Vision and Pattern Recognition Conference. pp. 24045–24055 (2025) 2, 4, 13 

47. Qinghong Lin, K., Jinpeng Wang, A., Soldan, M., Wray, M., Yan, R., Zhongcong Xu, E., Gao, D., Tu, R., Zhao, W., Kong, W., et al.: Egocentric video-language pretraining. arXiv e-prints pp. arXiv–2206 (2022) 2, 3 

48. Radevski, G., Grujicic, D., Blaschko, M., Moens, M.F., Tuytelaars, T.: Multimodal distillation for egocentric action recognition. In: ICCV (2023) 3 

49. Schilit, B., Adams, N., Want, R.: Context-aware computing applications. In: 1994 first workshop on mobile computing systems and applications. pp. 85–90. IEEE (1994) 4 

50. Shan, D., Geng, J., Shu, M., Fouhey, D.: Understanding human hands in contact at internet scale. In: CVPR (2020) 3 

51. Shen, X., Xiong, Y., Zhao, C., Wu, L., Chen, J., Zhu, C., Liu, Z., Xiao, F., Varadarajan, B., Bordes, F., et al.: Longvu: Spatiotemporal adaptive compression for long video-language understanding. arXiv preprint arXiv:2410.17434 (2024) 2, 13 

52. Shen, X., Zhang, W., Chen, J., Elhoseiny, M.: Vgent: Graph-based retrievalreasoning-augmented generation for long video understanding. arXiv preprint arXiv:2510.14032 (2025) 4 

53. Shu, Y., Liu, Z., Zhang, P., Qin, M., Zhou, J., Liang, Z., Huang, T., Zhao, B.: Video-xl: Extra-long vision language model for hour-scale video understanding. In: Proceedings of the Computer Vision and Pattern Recognition Conference. pp. 26160–26169 (2025) 2 

54. Song, E., Chai, W., Wang, G., Zhang, Y., Zhou, H., Wu, F., Chi, H., Guo, X., Ye, T., Zhang, Y., et al.: Moviechat: From dense token to sparse memory for long

<!-- Page 35 -->

Vinci2 35 

- video understanding. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 18221–18232 (2024) 2, 4 

- 55. Starner, T.: Wearable computing and contextual awareness. Ph.D. thesis, Massachusetts Institute of Technology (1999) 4 

- 56. Tang, Y., Tang, H., Cao, T., Nguyen, L., Zhang, A., Cao, X., Liu, C., Ding, W., Li, Y.: Proagentbench: Evaluating llm agents for proactive assistance with real-world data. arXiv e-prints pp. arXiv–2602 (2026) 4 

- 57. Team, G., Anil, R., Borgeaud, S., Alayrac, J.B., Yu, J., Soricut, R., Schalkwyk, J., Dai, A.M., Hauth, A., Millican, K., et al.: Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805 (2023) 15 

- 58. Wang, H., Feng, B., Lai, Z., Xu, M., Li, S., Ge, W., Dehghan, A., Cao, M., Huang, P.: Streambridge: Turning your offline video large language model into a proactive streaming assistant. arXiv preprint arXiv:2505.05467 (2025) 2, 3, 4 

- 59. Wang, H., Singh, M.K., Torresani, L.: Ego-only: Egocentric action detection without exocentric transferring. In: ICCV (2023) 3 

- 60. Wang, X., Zhang, Y., Zohar, O., Yeung-Levy, S.: Videoagent: Long-form video understanding with large language model as agent. In: European Conference on Computer Vision. pp. 58–76. Springer (2024) 25 

61. Wang, X., Kwon, T., Rad, M., Pan, B., Chakraborty, I., Andrist, S., Bohus, D., Feniello, A., Tekin, B., Frujeri, F.V., et al.: Holoassist: an egocentric human interaction dataset for interactive ai assistants in the real world. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp. 20270–20281 (2023) 3, 5 

62. Wang, Y., Meng, X., Wang, Y., Liang, J., Wei, J., Zhang, H., Zhao, D.: Videollm knows when to speak: Enhancing time-sensitive video comprehension with videotext duet interaction format. arXiv preprint arXiv:2411.17991 **1** (3), 5 (2024) 12 

63. Yang, B., Xu, L., Zeng, L., Liu, K., Jiang, S., Lu, W., Chen, H., Jiang, X., Xing, G., Yan, Z.: Contextagent: Context-aware proactive llm agents with open-world sensory perceptions. arXiv preprint arXiv:2505.14668 (2025) 4 

64. Yang, J., Liu, S., Guo, H., Dong, Y., Zhang, X., Zhang, S., Wang, P., Zhou, Z., Xie, B., Wang, Z., et al.: Egolife: Towards egocentric life assistant. In: Proceedings of the Computer Vision and Pattern Recognition Conference. pp. 28885–28900 (2025) 2, 3, 5, 15 

65. Yao, Y., Yu, T., Zhang, A., Wang, C., Cui, J., Zhu, H., Cai, T., Li, H., Zhao, W., He, Z., et al.: Minicpm-v: A gpt-4v level mllm on your phone. arXiv preprint arXiv:2408.01800 (2024) 12 

66. Ye, H., Zhang, H., Daxberger, E., Chen, L., Lin, Z., Li, Y., Zhang, B., You, H., Xu, D., Gan, Z., et al.: MM-Ego: Towards building egocentric multimodal llms for video qa. In: International Conference on Learning Representations (ICLR) (2025) 3 

67. Yeo, W., Kim, K., Yoon, J., Hwang, S.J.: Worldmm: Dynamic multimodal memory agent for long video reasoning. arXiv preprint arXiv:2512.02425 (2025) 4 

68. Zhang, B., Li, K., Cheng, Z., Hu, Z., Yuan, Y., Chen, G., Leng, S., Jiang, Y., Zhang, H., Li, X., et al.: Videollama 3: Frontier multimodal foundation models for image and video understanding. arXiv preprint arXiv:2501.13106 (2025) 14 

69. Zhang, C., Yang, K., Hu, S., Wang, Z., Li, G., Sun, Y., Zhang, C., Zhang, Z., Liu, A., Zhu, S.C., et al.: Proagent: building proactive cooperative agents with large language models. In: Proceedings of the AAAI Conference on Artificial Intelligence. vol. 38, pp. 17591–17599 (2024) 2, 4

<!-- Page 36 -->

36 Sitong Gong et al. 

70. Zhang, H., Wang, Y., Tang, Y., Liu, Y., Feng, J., Dai, J., Jin, X.: Flash-vstream: Memory-based real-time understanding for long video streams. arXiv preprint arXiv:2406.08085 (2024) 2, 4 

71. Zhang, H., Chu, Q., Liu, M., Shi, H., Wang, Y., Nie, L.: Exo2ego: Exocentric knowledge guided mllm for egocentric video understanding. arXiv preprint arXiv:2503.09143 (2025) 14 

72. Zhang, L., Zhou, S., Stent, S., Shi, J.: Fine-grained egocentric hand-object segmentation: Dataset, model, and applications. In: ECCV (2022) 3 

73. Zhang, Y., Dong, X.L., Lin, Z., Madotto, A., Kumar, A., Damavandi, B., Chai, J., Moon, S.: Proactive assistant dialogue generation from streaming egocentric videos. In: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing. pp. 12055–12079 (2025) 2, 3, 4, 15 

74. Zhang, Y., Shi, C., Wang, Y., Yang, S.: Eyes wide open: Ego proactive video-llm for streaming video. arXiv preprint arXiv:2510.14560 (2025) 2, 4, 10, 13 

75. Zhao, Y., Misra, I., Krähenbühl, P., Girdhar, R.: Learning video representations from large language models. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 6586–6597 (2023) 3 

76. Zheng, L., Chiang, W.L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E., et al.: Judging llm-as-a-judge with mt-bench and chatbot arena. Advances in neural information processing systems **36** , 46595–46623 (2023) 27 

77. Zohar, O., Wang, X., Dubois, Y., Mehta, N., Xiao, T., Hansen-Estruch, P., Yu, L., Wang, X., Juefei-Xu, F., Zhang, N., et al.: Apollo: An exploration of video understanding in large multimodal models. In: Proceedings of the Computer Vision and Pattern Recognition Conference. pp. 18891–18901 (2025) 2
