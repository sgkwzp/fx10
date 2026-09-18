# CausalTrace A Neurosymbolic Causal Analysis Agent for Smart Manufacturing

[Original PDF](../CausalTrace%20A%20Neurosymbolic%20Causal%20Analysis%20Agent%20for%20Smart%20Manufacturing.pdf)

Pages: 8

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

# **CausalTrace: A Neurosymbolic Causal Analysis Agent for Smart Manufacturing Chathurangi Shyalika**<sup>1</sup> **, Aryaman Sharma**<sup>1</sup> **, Fadi El Kalach**<sup>2</sup> **, Utkarshani Jaimini**<sup>3*</sup> **, Cory Henson**<sup>4</sup> **, Ramy Harik**<sup>2</sup> **, Amit Sheth**<sup>1</sup> 

1Artificial Intelligence Institute, University of South Carolina 

2Department of Automotive Engineering, Clemson University 

3Stride Lab, University of Michigan, Dearborn 

4Bosch Center for Artificial Intelligence, Pittsburgh 

#### **Abstract** 

Modern manufacturing environments demand not only accurate predictions but also interpretable insights to process anomalies, root causes, and potential interventions. Existing AI systems often function as isolated black boxes, lacking the seamless integration of prediction, explanation, and causal reasoning required for a unified decision-support solution. This fragmentation limits their trustworthiness and practical utility in high-stakes industrial environments. In this work, we present CausalTrace, a neurosymbolic causal analysis module integrated into the SmartPilot industrial CoPilot. CausalTrace performs data-driven causal analysis enriched by industrial ontologies and knowledge graphs, including advanced functions such as causal discovery, counterfactual reasoning, and root cause analysis (RCA). It supports real-time operator interaction and is designed to complement existing agents by offering transparent, explainable decision support. We conducted a comprehensive evaluation of CausalTrace using multiple causal assessment methods and the C3AN framework (i.e. Custom, Compact, Composite AI with Neurosymbolic Integration), which spans principles of robustness, intelligence, and trustworthiness. In an academic rocket assembly testbed, CausalTrace achieved substantial agreement with domain experts (ROUGE-1: 0.91 in ontology QA) and strong RCA performance (MAP@3: 94%, PR@2: 97%, MRR: 0.92, Jaccard: 0.92). It also attained 4.59/5 in the C3AN evaluation, demonstrating precision and reliability for live deployment. 

## **Introduction** 

Manufacturing is entering an era of hyperautonomous operations, powered by advances in AI-enabled sensing, control, and decision support (Hasan et al. 2026). As production systems grow in complexity, there is an urgent need for solutions that integrate causal reasoning with humaninterpretable decision support to ensure adaptive and trustworthy operation in safety-critical environments. 

While machine learning models have demonstrated impressive results in demand forecasting and anomaly detection, their lack of interpretability remains a significant barrier to adoption in high-stakes industrial settings. These black-box models often fail to meet the practical needs 

*Work done while at University of South Carolina Copyright © 2026, Association for the Advancement of Artificial Intelligence (www.aaai.org). All rights reserved. 

of shop-floor operators and subject matter experts (SMEs), who require not only accurate predictions but also actionable and understandable insights into system behavior (Singh, Goyat, and Panwar 2024). This has fueled the demand for AI systems that can explain why events occur, identify underlying causes, and offer counterfactual reasoning to support ’what if’ analysis. These capabilities are essential for real-time decision-making, proactive maintenance, and effective human-machine collaboration in production workflows (Acharya, Kuppan, and Divya 2025; Boskabadi et al. 2025). Yet, existing AI solutions rarely integrate these functionalities into a unified, deployable framework, limiting their utility in live industrial environments. 

To address this gap, we present **CausalTrace** , a neurosymbolic causal analysis agent embedded in our prior work, _SmartPilot_<sup>1</sup> industrial CoPilot (Shyalika et al. 2025a,b). SmartPilot builds on the vision of **C3AN** — _Custom, Compact, Composite AI with Neurosymbolic Integration_ (Sheth et al. 2025)— an AI paradigm emphasizing robustness, intelligence, and trust of AI systems. _Custom_ in C3AN refers to domain-specific data and workflows and _Compact_ refers to efficient models deployable across infrastructures, including edge devices. _Composite_ refers to the modular orchestration of specialized AI components- neural, symbolic, and decision modules- into a unified system. _Neurosymbolic_ denotes the integration of neural learning and symbolic reasoning within each module, enabling transparent, knowledge-aligned, and explainable decision-making. Key contributions of this work are: 

- Design and implement CausalTrace, a neurosymbolic causal analysis agent capable of real-time causal discovery, root cause analysis (RCA), causal effect estimation, and counterfactual reasoning. 

- Integrate data-driven causal methods with structured knowledge (ontologies, knowledge graphs), semantic user interfaces, and evaluation pipelines into neurosymbolic agent workflows, enabling human-interpretable reasoning and a deployable decision-support system. 

- Develop a comprehensive evaluation methodology grounded in the C3AN framework, incorporating a suite of techniques to ensure robustness, intelligence, and 

1Code: https://github.com/ChathurangiShyalika/SmartPilot, Demo: https://smartpilot.my.canva.site

<!-- Page 2 -->

trustworthiness. Conduct causal assessments including counterfactual effect estimation, RCA validation, and comparisons with baseline and ablation variants. 

- Demonstrate the deployment and practical utility of CausalTrace on an academic rocket assembly testbed, highlighting its readiness for real-world manufacturing environments. 

## **Related Work** 

**Causal Reasoning in Industrial AI** Research on causal reasoning in industrial settings spans both symbolic and data-driven approaches. Early systems employ causal models rooted in qualitative physics and control theory to support fault localization and diagnostic reasoning (Bandekar 1989). Other efforts introduce planning-based frameworks that embed causal reasoning into multi-robot coordination and factory automation, enabling optimal plan reuse and failure diagnosis in dynamic production environments (Erdem et al. 2012). More recently, causal discovery techniques such as nonparametric entropy methods and informationgeometric inference have been used to reconstruct causal networks directly from process data, guiding performance prediction and process optimization in complex industrial workflows (Sun et al. 2024). 

**Neurosymbolic and Knowledge-Infused Systems** In safety-critical domains like manufacturing and cybersecurity, neurosymbolic systems have shown promise in improving explainability and behavior under uncertainty by combining neural networks with explicit knowledge graphs (Piplai et al. 2023). In scientific domains such as geochemistry, symbolic rules extracted from expert literature via LLMs have been integrated with learning models to guide predictions and improve domain alignment (Chen et al. 2025). 

**Agentic AI and Multiagent Architectures in Industry** Agentic AI represents a paradigm shift toward autonomous systems capable of goal-driven, adaptive decision-making. Surveys of Agentic AI emphasize its core attributes: autonomy, proactivity, learning, and reactivity as enablers for complex real-world applications (Acharya, Kuppan, and Divya 2025). Agentic systems have been integrated with digital twins to support real-time monitoring and control of nonlinear systems (Kusiak 2025; Boskabadi et al. 2025). Recent frameworks such as Intelligent Design 4.0 (Jiang et al. 2025), intent-based industrial automation (Romero and Suyama 2025), and multi-agent coordination architectures (Panigrahy 2025) propose layered systems where LLMpowered agents decompose high-level goals and orchestrate downstream execution across various functions. 

**Summary and Motivation** While prior work in causal reasoning, neurosymbolic AI, and agentic systems has made meaningful strides, current solutions often fall short in integration, interactivity, and operational readiness. Symbolic methods struggle to scale; neural models lack transparency; and agentic systems lack semantic grounding and are not designed for operator-in-the-loop decision support. These gaps hinder adoption in complex industrial environments where explainability, adaptability, and human collaboration are critical. SmartPilot is built to address these limitations 


![](assets/036/paper-0002-07.png)


<!-- Start of picture text -->
seriesTime  Images  Manuf. series Time         Text<br>process<br>ontologies<br>AutoencoderLSTM  EfficientNET knowledgeStructured sources LSTM RAG Manufacturing manuals<br>Fusion        Knowledgeinfusion Retrieve relevant<br>model information<br>questionsUser  (Conversational query interface)InfoGuide Causal AnalysisCause Root<br>Response Trace DiscoveryCasual  seriesTime<br><!-- End of picture text -->

Figure 1: Multi-agent architecture of SmartPilot holistically. By fusing causality, neurosymbolic methods, and agentic AI, it lays a practical and extensible foundation for intelligent manufacturing. 

## **System Design** 

### **SmartPilot Architecture** 

The earlier version of the SmartPilot system adopts a multiagent architecture, comprising three specialized agents that collectively support predictive analytics and operator assistance. The algorithmic details of these agents are available at (Shyalika et al. 2025c,a,b). PredictX agent specializes in anomaly prediction using multimodal sensor data (time series and images). It leverages decision-level fusion enhanced by transfer learning and knowledge-infused learning (via process ontologies) in predicting anomalies. ForeSight agent employs a Knowledge-Infused LSTM (KIL-LSTM) model to predict throughput across production cycles. It integrates time series data with domain priors to improve longterm forecasting. InfoGuide is a question-answering agent that provides real-time responses to operational, safety, maintenance, and troubleshooting queries. It uses retrievalaugmented generation over curated manufacturing manuals and integrates with other agents to address questions related to anomaly detection, production forecasting, and causal reasoning. SmartPilot’s natural language understanding and explanation are powered by LLaMA3-70B-8192 model. 

### **Integrating the CausalTrace Agent** 

The CausalTrace agent extends SmartPilot’s capabilities beyond prediction to include explanation, attribution, and simulation needed for efficient RCA. This agent is tightly coupled into SmartPilot (Figure 1) and supports real-time and historical data analysis through an interactive interface. The causal analysis pipeline (Figure 2) includes the following components and features. 

**Data Loader and Feature Selector.** SmartPilot’s Data Loader supports two modes of data ingestion: direct connection to Programmable Logic Controllers (PLCs) for realtime streaming, or batch upload of historical sensor data for offline analysis. Once data is ingested, the Feature Selector enables the selection of data-driven feature selection methods or manual selection based on domain expertise, allowing operators to prioritize variables most relevant to the analysis. 

**Causal Discovery Engine.** The engine supports Independent Component Analysis–based Linear Non-Gaussian Acyclic Model (ICA-based LiNGAM) (Shimizu et al. 2006)

<!-- Page 3 -->

![](assets/036/paper-0003-00.png)


<!-- Start of picture text -->
InfoGuide Data  Feature  Causal b)<br>a) (Conversational query interface) Loader Selector Trace<br>Predicted<br>anomalies<br>Causal  Semantic Feature Interpretation<br>Discovery<br>Edge Stability Scoring<br>Engine<br>Interactive Graph Modification<br>Forecasted Neurosymbolic integration<br>demand<br>Smart Manufacturing  Root<br>Knowledge Graph Cause<br>Analysis<br>Dynamic Process<br>Ontology Counterfactual Evaluation<br>Causal Graph  Causal  RCA Evaluation<br>Prompt Injection Evaluator Baseline and Ablation<br>Comparison<br>C3AN Evaluation<br>Memory<br>Module<br><!-- End of picture text -->

Figure 2: (a) _Architecture of CausalTrace agent_ : PredictX provides predicted anomalies, ForeSight offers forecasted demand, both feeding into InfoGuide. Data flows through Data Loader and Feature Selector before entering the Causal Discovery Engine. Discovered causal graphs support Root Cause Analysis. Causal graphs and RCA results are validated in the Causal Evaluator. InfoGuide responses are enhanced via neurosymbolic integration, combining a manufacturing knowledge graph, process ontology, and causal graph prompts. Final results are stored in the Memory Module. (b) _Interactive User Interface_ : Causal graph visualization and allows causal graph editing. Enhances graphs with ontology-derived descriptions, types, and units. Tooltip metadata is enriched using a smart manufacturing knowledge graph. 

and Differentiable Causal Discovery with Attention (DiffAN) (Sanchez et al. 2022) to construct Directed Acyclic Graphs (DAGs) from multivariate sensor data. To enhance reliability, we integrate bootstrap-based edge stability analysis (Algorithm 1) directly into the discovery workflow. Causal graphs are repeatedly estimated on bootstrapresampled datasets, and edge stability scores computed from their occurrence frequency are used to down-weight or remove low-confidence edges (Algorithm 1). This yields more trustworthy graphs while preserving meaningful causal structure. For each retained edge, the total causal effect is computed (Algorithm 2) to quantify both direct and indirect influences between variables, and results are visualized in the user interface for interactive exploration. 

**Root Cause Analysis.** For each anomaly, the RCA module combines expert-defined, cycle-aware sensor tolerance ranges with the learned causal topology to generate a ranked list of candidate root causes, based on causal path effect strengths and sensor deviation analysis. 

**Neurosymbolic Integration.** SmartPilot adopts a multilayered neurosymbolic integration framework that tightly couples structured knowledge with data-driven reasoning. The system leverages a _smart manufacturing knowledge graph_ encoded in RDF to represent entities such as sensors, machines, parts, and anomalies. This knowledge is injected into the reasoning layer using rdflib, enriching InfoGuide’s responses with semantic context. A _dynamic process ontology_<sup>2</sup> , implemented in Neo4j, encodes process semantics, variable relationships, and operational constraints. Real-time Cypher queries enable on-demand retrieval of explanations, tolerance ranges, and sensor-function mappings. The _causal graph prompt injection_ mechanism serial- 

2https://github.com/revathyramanan/Dynamic-ProcessOntology 

**Algorithm 1: Bootstrap-Based Edge Stability Analysis** 

**Input:** Dataset _D_ , number of bootstrap samples _N_ , causal discovery method _M_ 

**Output:** Stability score _s_ for each edge _A → B_ 

- 1: Initialize list _WA → B_ = [] for each _A → B_ 

- 2: **for** _i_ = 1 to _N_ **do** 

- 3: Resample dataset _D_<sup>(</sup><sup>_i_)</sup> with replacement from _D_ 

- 4: Run _M_ on _D_<sup>(</sup><sup>_i_)</sup> to estimate causal graph _G_<sup>(</sup><sup>_i_)</sup> 

- 5: **for** each directed edge _A → B_ in _G_<sup>(</sup><sup>_i_)</sup> **do** 

- 6: Record causal strength _wi_ of _A → B_ 

- 7: Append _wi_ to _WA → B_ 

- 8: **end for** 

- 9: **end for** 

- 10: **for** each edge _A → B_ with samples _WA → B_ = _w_ 1 _, . . . , wN_ **do** 

- 11: Compute mean strength: _w_ ¯ = _N_<sup><u>1</u></sup> � _i_ = 1 _N wi_ 

- 12: Compute standard deviation: 

   - <u>1</u> 

   - _σ_ = ~~�~~ _N_ <u>�</u> _Ni_ =1<sup>(</sup><sup>_wi −w_¯)2</sup> 

- 13: Compute stability score: _s_ = 1+1 _σ_ 

- 14: **end for** 

- 15: **Edge Interpretation:** 

   - _s ≥_ 0 _._ 9: Very strong and stable 

   - 0 _._ 8 _≤ s <_ 0 _._ 9: Reliable 

   - 0 _._ 6 _≤ s <_ 0 _._ 8: Moderately stable (use with caution) 

   - _s <_ 0 _._ 6: Unstable (typically excluded) 

- 16: Retain edges with _s_ _<u>≥</u>_ 0 _._ 6 for the final causal graph 

izes the total causal effect matrix from the causal discovery step and passes it into LLM prompts. This allows the system to generate explanations and reasoning that are grounded in the structure of the causal graph.

> Original page for checking 3 unresolved font glyphs.

![Original page 3](assets/036/verify-page-003.png)

<!-- Page 4 -->

#### **Algorithm 2: Total Causal Effect Computation** 

**Input:** Causal effect matrix **B** , identity matrix **I Output:** Total causal effect matrix **T** = ( **I** _−_ **B** )<sup>_−_1</sup> 

- 1: Start with a structural equation model (SEM): **X** = **BX** + **_ε_** , where **X** is a vector of observed variables and **_ε_** is noise. 

- 2: Rearranged to: ( **I** _−_ **B** ) **X** = **_ε_** 

- 3: Solve for **X** using: **X** = ( **I** _−_ **B** )<sup>_−_1</sup> **_ε_** . 

- 4: Therefore, the total effect matrix is: **T** = ( **I** _−_ **B** )<sup>_−_1</sup> . 

- 5: Each entry _Tij_ captures total effect of variable _j_ on variable _i_ 

- 6: This can be decomposed as **T** = **I** + **B** + **B**<sup>2</sup> + **B**<sup>3</sup> + _· · ·_ . 

- 7: Interpretation: 

   - **I** : Self influence (identity effect), 

   - **B** : Direct effects (1-hop causal influence), 

   - **B**<sup>_k_</sup> : Indirect effects through _k_ -hop paths. 

- 8: Series expansion valid when graph is acyclic or spectral radius of **B** _<_ 1 

- 9: _⇒_ Total causal effect aggregates all direct and mediated <u>influences</u> 

**Interactive User Interface.** The interface visualizes causal graphs with rich semantic metadata derived from the process ontology and the knowledge graph. Each node is annotated with descriptions, types, units, and anomaly relevance, and tool tips display this semantic information for interactive exploration. CausalTrace is integrated with InfoGuide’s conversational query interface, enabling operators to ask natural language questions about graph structure, causal reasoning, and root cause analysis. Example queries are shown in Figure 3, with a complete set of competency questions provided in Appendix A. Users can also interactively modify the discovered causal graph by adding or removing nodes and edges; all edits are validated against the ontology to ensure semantic consistency, allowing domain experts to refine and adapt the graph in real time. 

**Memory Module.** This enables persistent, context-aware reasoning by storing and retrieving information across sessions. It consists of three components: _episodic memory_ , which logs time-stamped interactions such as causal discovery and RCA runs for longitudinal tracking; _semantic memory_ , which stores structured annotations of sensors and entities to support enriched, context-aware explanations; and _procedural memory_ , which retains user preferences (e.g., chosen algorithms or display settings) to enable personalized interactions. These memory traces are stored in JSON format and are injected into InfoGuide’s natural language responses to ensure continuity and context-aware dialogue. 

## **Evaluation and Results** 

**Dataset Description.** We use the publicly available manufacturing dataset generated by the Future Factories (FF) Lab at the McNair Aerospace Research Center, University of South Carolina (Harik et al. 2024). This dataset captures synchronized sensor and image data from a prototype rocket assembly pipeline designed to emulate industrialgrade manufacturing processes. It contains 166K records 

- **Causal Graph Structure** 

- C – Is there a causal relation between A and B? – What are the causal parents of C? **Causal Reasoning** – If the value of A is set to value _x_ , what would be its effect on B? 

- B – What is the strength of the causal relation between B and C? 

- D **Root Cause Analysis** – What is the strongest cause of the anomalous value of variable B? 

- A – Why is D not likely a root cause of B? 

Figure 3: Illustration of a structured causal graph with categorized query types: structure, reasoning, and RCA. 

sampled at 1.95 Hz over 30 hours, covering 285 complete rocket assembly–disassembly cycles. Each cycle is segmented into 21 distinct operational states. The dataset includes time-series measurements from potentiometers, load cells, drive temperatures, and robot kinematics. The annotated version used in this work (Shyalika et al. 2025c)<sup>3</sup> includes cycle state labels along with ground-truth anomaly types. These anomalies indicate missing rocket components and include six types, such as NoNose, NoBody2, and combined cases like NoBody2,NoBody1. In the evaluation, causal discovery was performed using ICA-based LiNGAM and DiffAN on eight key variables identified through XGBoost feature selection and validated by domain experts. LiNGAM produced 20 directed causal edges, while DiffAN yielded 15. The subsections below detail the evaluation methods conducted on these causal graphs. 

**Counterfactual Effect Computation.** CausalTrace provides an interactive module for validating causal links via counterfactual effect computation. From the user interface, users can select an edge _A → B_ , apply an intervention on _A_ , and compare the predicted change in _B_ (from the learned total effect; Algorithm 3) with observed changes in held-out data. This enables direct plausibility checks and graph refinement based on domain knowledge. 

**Root Cause Analysis Evaluation.** We evaluated the RCA module on anomaly events from the FF dataset with known fault cases. For each anomaly, CausalTrace produced a ranked list of candidate root causes using causal path significance and sensor deviation analysis. Here, _K_ denotes the cut-off rank that is, the number of top predictions considered when computing the metrics. Results showed close agreement with expert-defined causes, achieving Mean Average Precision@K (MAP@3) of 94%, Precision@K (PR@2) of 97%, Mean Reciprocal Rank (MRR) of 0.92 and a Jaccard index of 0.92. 

**Comparison with Baseline and Ablation Variants** To assess CausalTrace, we compared it against: (1) a **correlation-based root cause ranking** , which identifies candidate causes based on Pearson correlation with the anomalies, and (2) a **CausalTrace variant without KG and ontology grounding** , which omits 

3https://github.com/ChathurangiShyalika/NSF-MAP

<!-- Page 5 -->

#### **Algorithm 3:Counterfactual Validation of Causal Effects** 

**Input:** Dataset _D_ , total effect matrix _τ_ , tolerance _ϵ_ , effect threshold _δ_ 

**Output:** Validation table with 

( _A, B, τA→B,_ ∆ _B_ pred _,_ ∆ _B_ obs _,_ Error) for each valid causal pair _A → B_ 

- 1: **for** each variable pair ( _A, B_ ) where _A_ = _B_ and _|τA→B| > δ_ **do** 

- 2: Estimate baseline ( _a_ 1) and intervention ( _a_ 2) values. If unspecified, compute: 

   - _a_ 1 = _Q_ 1( _A_ ) (1st quartile) _, a_ 2 = _Q_ 3( _A_ ) (3rd quartile) 

- 3: Compute predicted change using total effect: 

         - ∆ _B_ pred = ( _a_ 2 _− a_ 1) _· τA→B_ 

- 4: Extract subsets of _D_ : 

   - Baseline group: rows where _A ≈ a_ 1 within _ϵ_ 

   - Counterfactual group: rows where _A ≈ a_ 2 within _ϵ_ 

- 5: Compute observed change in _B_ : 

      - ∆ _B_ obs = E[ _B | A ≈ a_ 2] _−_ E[ _B | A ≈ a_ 1] 

- 6: Compute absolute error: Error = _|_ ∆ _B_ pred _−_ ∆ _B_ obs _|_ 

- 7: Record result: ( _A, B, τA→B,_ ∆ _B_ pred _,_ ∆ _B_ obs _,_ Error) 

- 8: **end for** 

- 9: Compile results into a table for global causal graph assessment 

- 10: **Interpretation:** 

   - Small error _⇒_ Causal effect from _A_ to _B_ is wellsupported by data 

   - Large error _⇒_ Possible misspecification or unobserved confounding 

|Method|ROUGE-1|Jaccard|MAP@3|PR@2|MRR|
|---|---|---|---|---|---|
|RCA baseline|–|0.33|44%|51%|0.5|
|CausalTrace|0.56|–|–|–|–|
|(no KG ontology)||||||
|**CausalTrace (full)**|**0.91**|**0.92**|**94%**|**97%**|**0.92**|



Table 1: Comparison of CausalTrace and baselines 

semantic tool tips, concept filtering, and knowledgeinformed edge validation. Results show that the correlation baseline yields high false positives due to spurious associations and fails to capture causal directionality (Jaccard:0.33,MAP@3:44%,PR@2:51%,MRR:0.50). The ontology-ablated variant degrades interpretability and occasionally yields invalid causal paths. In contrast, full CausalTrace achieves higher agreement with expert annotations and generates explanations rated as more trustworthy by domain evaluators, with a ROUGE-1 score of 0.91 compared to 0.56 for the variant without ontology (Table 1). 

**C3AN Principles Evaluation.** We assessed CausalTrace using the C3AN framework, which defines 14 principles for robust, intelligent, and trustworthy AI systems. A subset of 10 principles was selected based on operational relevance, assessability, and alignment with CausalTrace’s capabilities, as in Table 2. To evaluate the system against the C3AN principles, we manually crafted 10 targeted questions 

per principle using expert guidelines and industry best practices. The ground truth answers were obtained from two sources: (1) domain experts familiar with the manufacturing processes, and (2) official manufacturing manuals and documentation. The ground truth answer was also modeled keeping the C3AN principle in focus<sup>4</sup> . 

To evaluate the system based on the questionnaire, we implemented an **LLM-as-a-Judge pipeline** . The pipeline consists of state-of-the-art LLMs (GPT-4o-mini and LLaMA3-70B-8192), each provided with three inputs: the question, ground truth, and the CausalTrace-generated answer. Using these inputs as the context, the LLM is prompted to evaluate the generated answer based on the ground truth and provide an integer score from 1 to 5, where 1 signifies complete misalignment with the ground truth and 5 denotes maximum alignment. The LLM is also prompted to explain its score. This enables the model to use more tokens, improving judgment accuracy and reducing bias. The LLMas-a-Judge framework enabled efficient, low-bias evaluation of system responses. However, since it lacks special domain knowledge, CausalTrace was also assessed by six human evaluators-three experts in the manufacturing sector and three computer scientists. These evaluators scored responses on a scale of 1–5 based on alignment with the ground truth, following the same rubric. (Table 2). 

The results in Table 3, indicate that GPT-4o-mini was slightly more conservative in its scoring ( _Weighted Cohen’s Kappa_ ( _κ_ ) mean = 4.19) than LLaMA3-70B-8192 (mean = 4.32). In contrast, human evaluators rated more favorably, with an average score of 4.59. The _κ_ values further validated the consistency and reliability of these evaluations. Agreement was generally higher within evaluator groups than across them. Specifically, GPT-4o-mini and LLaMA3-70B-8192 demonstrated substantial inter-model agreement ( _κ_ = 0 _._ 56), whereas their agreement with human evaluators was notably lower ( _κ_ = 0 _._ 52 for GPT-4o-mini and _κ_ = 0 _._ 58 for LLaMA3-70B-8192). Human evaluators exhibited moderate internal agreement ( _κ_ = 0 _._ 58). These findings suggest that both LLMs and humans tend to align more closely with members of their own group when assessing responses against the ground truth. 

## **Pathway To Deployment** 

CausalTrace is integrated as a core agent in SmartPilot, which is currently under deployment in the FF Lab. The full deployment pipeline proceeds through two primary phases: virtual and real-world deployment (Figure 4). In the initial phase, SmartPilot is virtually deployed using the Testbed as a Service (TaaS) framework (McCormick and Wuest 2025), which emulates the robotic assembly line operations. TaaS functions as a data replay mechanism, publishing data from a pre-existing dataset one timestamp at a time, mimicking the behavior of live data streams. In this setting, SmartPilot subscribes to specific MQTT (Message Queuing Telemetry Transport) topics defined by TaaS and processes the incoming data streams as if operating in a live production environment. This virtual prototyping setup offers a controlled 

4Questions and results available at: https://shorturl.at/pKWr2

<!-- Page 6 -->

|C3AN Principle, Category and<br>Evaluation Description|LLM1<br>Avg.<br>Sc.|LLM2<br>Avg.<br>Sc.|Human<br>Avg.<br>Sc.||<br>|InfoGuide<br>Conversational<br>Query Interface||
|---|---|---|---|---|---|---|---|
|**Reliability[R]:**Tested for hallucinations in responses.|4|4.5|4.2|**Causal**<br>**Trace**||||
|**Consistency [R]**:Assessed stability using paraphrased|3.5|4.5|4.4|||||
|queries and comparing output similarity.<br>**Abstraction[I]**:Evaluated how low-level data are mapped|4|3.3|4.6|Causal||<br>Knowledge Sources|API<br>Endpoints|
|to high-level concepts in knowledge graph and ontology||||<br>Graphs||Dynamic Process<br>Ontolo<br>Smart<br>Manufacturing||
|**Causality[I]**:Tested via causal discovery, total|4.9|4.4|4.7|||gy<br> <br>Knowledge Graph|Local Data<br>Propagation|
|effects, root cause analysis, and counterfactuals.|||||Internal D|ata Processing||
|**Reasoning[I]**: Measured the system’s ability to|3.8|4.5|4.6|||||
|logically infer conclusions.|||||MQTT Client|OPC UA Client|USB|
|**Planning[I]**: Evaluated multi-agent workflows from<br>data inut to final outut|4|5|4.6||Data Flo|w<br>Data Flow||
|p  i p.<br>**Grounding[T]:**Checked if answers used context|4.4|4.6|4.6|TaaS|MQTT Broker|Assembly Li<br>OPC UA Server|ne<br>Cameras|
|from knowledge graph and ontology.||||Virtual D|eployment|Physical Deployment||
|**Attribution[T]**:Verified traceability of decisions<br>using agent logs and contextual sources.<br>**Interpretability[T]**:Users could inspect model<br>settings, selected features, and causal graphs.<br>**Explainability[T]:**Judged clarity of explanations<br>for and causal outputs.|4.5<br>4<br>5|4.5<br>3.3<br>5|4.2<br>4.5<br>5|Figure 4: <br>with virtual<br>erate in re<br>tion foreca<br>The curren<br>|End-to-end <br>and real-w<br>al time to <br>sting, ques<br>t deployme<br>|deployment pipeline of S<br>orld integration<br>perform anomaly detection<br>tion answering, and causal <br>nt architecture is optimized <br>|martPilot<br>, produc-<br> analysis.<br> for min-<br>|



Figure 4: End-to-end deployment pipeline of SmartPilot with virtual and real-world integration 

erate in real time to perform anomaly detection, production forecasting, question answering, and causal analysis. The current deployment architecture is optimized for minimal latency in data acquisition and processing, as demonstrated in (El Kalach et al. 2025). However, its centralized nature presents scalability limitations as system complexity increases. To address this, future iterations of the system will transition to a decentralized processing model. Furthermore, the direct connection to cameras imposes spatial constraints, as the system responsible for image ingestion must remain within the physical range of the camera cabling. 

Table 2: Average performance on selected C3AN principles, evaluated by two LLMs (GPT-4o-mini and LLaMA3-70B-8192) and six human evaluators. Categories: R= Robustness, I= Intelligence, T= Trustworthiness. 


![](assets/036/paper-0006-04.png)


<!-- Start of picture text -->
LLM1 LLM2 E1 E2 E3 E4 E5 E6<br>LLM1 1<br>LLM2 0.61 1<br>E1 0.68 0.68 1<br>E2 0.48 0.56 0.56 1<br>E3 0.50 0.45 0.61 0.53 1<br>E4 0.61 0.59 0.64 0.86 0.58 1<br>E5 0.33 0.66 0.52 0.57 0.54 0.52 1<br>E6 0.52 0.46 0.51 0.57 0.86 0.49 0.37 1<br><!-- End of picture text -->

In the second iteration of the deployment, the OPC UA Server and direct camera connections are to be replaced by a public MQTT broker, enabling SmartPilot to be hosted in a publicly accessible environment. This revised architecture introduces an additional layer beneath the data processing stage: a data publishing module that streams data from the local servers and cameras to the MQTT broker. SmartPilot is also publicly hosted<sup>5</sup> to enable community access, leveraging both in-house and community-driven abstractions for interfacing with its back-end services. This setup enables global real-time access, improving scalability and accessibility, but it introduces latency, which we plan to address with edge computing and asynchronous communication. 

Table 3: Inter-annotator agreements ( _κ_ ) (range: –1 to 1). Green: perfect agreement, yellow: moderate, red: low. LLM1: GPT-4o-mini, LLM2: LLaMA3-70B-8192, E1–E6: Human evaluators. 

and repeatable environment for evaluating system behavior under a range of operational conditions. 

## **Conclusion and Further Work** 

We introduced CausalTrace, a neurosymbolic causal analysis agent for intelligent manufacturing. Integrated with knowledge sources, it supports interpretable and trustworthy reasoning over complex industrial data. Evaluated via the C3AN framework, CausalTrace demonstrates strong alignment with robustness, intelligence, and trustworthiness. Its phased deployment from controlled virtual prototyping to ongoing live integration shows practical viability and scalability potential. Future work will extend capabilities such as intervention planning, continual causal graph learning, and safety-aware, instruction-following features. These enhancements aim to further optimize performance and adaptability in diverse operational environments. 

Following successful virtual validation, SmartPilot progresses to real-world deployment. The process begins with configuring the OPC UA Server at the assembly line level. Subsequently, analog sensor data is streamed via the OPC UA Server, while image data is acquired directly from cameras positioned in the lab. This phase encompasses internal data processing tasks, including structuring raw inputs and developing a robust data ingestion pipeline. Next, the knowledge graph, dynamic process ontology, and previously generated in-memory causal graphs are instantiated via Neo4j, RDF, and HTTP SSE, respectively, and integrated with the data infrastructure. Finally, leveraging the ingested timeseries signals, visual data, and semantic insights from knowledge sources, SmartPilot’s four specialized agents op- 

5https://aiisc.ai/smartpilot/

<!-- Page 7 -->

## **Acknowledgment** 

This work was supported in part by NSF grant #2119654, “RII Track 2 FEC: Enabling Factory to Factory (F2F) Networking for Future Manufacturing”. 

## **References** 

Acharya, D. B.; Kuppan, K.; and Divya, B. 2025. Agentic AI: Autonomous Intelligence for Complex Goals–A Comprehensive Survey. _IEEE Access_ , 18912 – 18936. 

Bandekar, V. R. 1989. Causal models for diagnostic reasoning. _Artificial Intelligence in Engineering_ , 4(2): 79–91. Boskabadi, M. R.; Cao, Y.; Khadem, B.; Clements, W.; Gerek, Z. N.; Reuthe, E.; Sivaram, A.; Savoie, C. J.; and Mansouri, S. S. 2025. Industrial Agentic AI and generative modeling in complex systems. _Current Opinion in Chemical Engineering_ , 48: 101150. 

Chen, W.; Zhang, J.; Li, W.; Que, X.; Li, C.; and Ma, X. 2025. Integrating Neuro-Symbolic AI and Knowledge Graph for Enhanced Geochemical Prediction in Copper Deposits. _Applied Computing and Geosciences_ , 100259. 

El Kalach, F.; Farahani, M.; Wuest, T.; and Harik, R. 2025. Real-time defect detection and classification in robotic assembly lines: a machine learning framework. _Robotics and Computer-Integrated Manufacturing_ , 95: 103011. 

Erdem, E.; Haspalamutgil, K.; Patoglu, V.; and Uras, T. 2012. Causality-based planning and diagnostic reasoning for cognitive factories. In _Proceedings of 2012 IEEE 17th International Conference on Emerging Technologies & Factory Automation (ETFA 2012)_ , 1–8. IEEE. 

Harik, R.; Kalach, F. E.; Samaha, J.; Clark, D.; Sander, D.; Samaha, P.; Burns, L.; Yousif, I.; Gadow, V.; Tarekegne, T.; et al. 2024. Analog and Multi-modal Manufacturing Datasets Acquired on the Future Factories Platform. _arXiv preprint arXiv:2401.15544_ . 

Hasan, M. K.; Latif, Z.; Hlali, A.; Xunping, L.; and Aka, S. A. B. 2026. Hyperautomation: The Next Frontier in Supply Chain (SC) and Manufacturing. In _Emerging Trends in Smart Logistics Technologies_ , 1–44. IGI Global Scientific Publishing. 

Romero, M. L.; and Suyama, R. 2025. Agentic AI for Intent-Based Industrial Automation. _arXiv preprint arXiv:2506.04980_ . 

Sanchez, P.; Liu, X.; O’Neil, A. Q.; and Tsaftaris, S. A. 2022. Diffusion models for causal discovery via topological ordering. _arXiv preprint arXiv:2210.06201_ . 

Sheth, A. P.; Roy, K.; Venkataramanan, R.; Nadimuthu, V.; and Shyalika, C. 2025. Composite AI With Custom, Compact, Neurosymbolic Models: The Emergent Enterprise Artificial Intelligence Paradigm. _IEEE Internet Computing_ , 29(2): 37–49. 

Shimizu, S.; Hoyer, P. O.; Hyv¨arinen, A.; Kerminen, A.; and Jordan, M. 2006. A linear non-Gaussian acyclic model for causal discovery. _Journal of Machine Learning Research_ , 7(10). 

Shyalika, C.; Prasad, R.; Al Ghazo, A.; Eswaramoorthi, D. L.; Shree Muthuselvam, S.; and Sheth, A. 2025a. SmartPilot: Agent-Based CoPilot for Intelligent Manufacturing. In _Proc. of the 24th International Conference on Autonomous Agents and Multiagent Systems_ , 3053–3055. 

Shyalika, C.; Prasad, R.; Ghazo, A. A.; Eswaramoorthi, D.; Kaur, H.; Muthuselvam, S. S.; and Sheth, A. 2025b. SmartPilot: A Multiagent CoPilot for Adaptive and Intelligent Manufacturing. In _Proc. of the IEEE Conference on Artificial Intelligence_ . 

Shyalika, C.; Prasad, R.; Kalach, F. E.; Venkataramanan, R.; Zand, R.; Harik, R.; and Sheth, A. 2025c. NSF-MAP: Neurosymbolic Multimodal Fusion for Robust and Interpretable Anomaly Prediction in Assembly Pipelines. _arXiv preprint arXiv:2505.06333_ . 

Singh, M.; Goyat, R.; and Panwar, R. 2024. Fundamental pillars for industry 4.0 development: implementation framework and challenges in manufacturing environment. _The TQM Journal_ , 36(1): 288–309. 

Sun, Y.-N.; Pan, Y.-J.; Liu, L.-L.; Gao, Z.-G.; and Qin, W. 2024. Reconstructing causal networks from data for the analysis, prediction, and optimization of complex industrial processes. _Engineering Applications of Artificial Intelligence_ , 138: 109494. 

Jiang, S.; Xie, M.; Chen, F. Y.; Ma, J.; and Luo, J. 2025. Intelligent Design 4.0: Paradigm Evolution Toward the Agentic AI Era. _arXiv preprint arXiv:2506.09755_ . 

Kusiak, A. 2025. Agentic Manufacturing System = Digital Twin + Manufacturing. _Journal of Intelligent Manufacturing_ , 36: 2221–2222. 

McCormick, M.; and Wuest, T. 2025. Testbed as a Service (TaaS): A Scalable Ecosystem for Smart Manufacturing and Industry 4.0 Collaboration. 

Panigrahy, S. 2025. Multi-Agentic AI Systems: A Comprehensive Framework for Enterprise Digital Transformation. _Journal of Computer Science and Technology Studies_ , 7(6): 86–96. 

Piplai, A.; Kotal, A.; Mohseni, S.; Gaur, M.; Mittal, S.; and Joshi, A. 2023. Knowledge-enhanced NeuroSymbolic AI for Cybersecurity and Privacy. _arXiv preprint arXiv:2308.02031_ .

<!-- Page 8 -->

## **Appendix** 

## **Appendix A: CausalTrace Competency Questions** 

This section presents a structured set of competency questions designed to evaluate the capabilities of the CausalTrace across key reasoning dimensions. These questions are grounded in the example causal graph _G_ = _{A → B, B → C, D → B}_ , which is assumed to be generated by the CausalTrace and span four core categories: (1) Causal Graph Structure, (2) Causal Reasoning, (3) Root Cause Analysis, and (4) Causal Discovery. The goal is to assess the agent’s ability to interpret, reason over, and explain causal relationships in response to natural language queries. 

#### **Questions about Causal Graph Structure** 

1. Does A cause B? 

2. Does B cause A? 

3. Does A cause C? 

4. Is there a causal relation between A and B (or between B and A)? 

5. Is there a causal relation between A and D? 

6. What variables have a direct causal effect on B (i.e., causal parents of B)? 

7. Is there a causal relation between A and Z? 

#### **Questions about Causal Reasoning** 

1. What is the strength of the causal relation between A and B? 

2. Which variable has the strongest causal effect on B? 

3. If the value of A were set to _x_ , what would be the effect on B? 

#### **Questions about Root Cause Analysis** 

1. What is the most likely root cause of the anomalous value of variable B? 

2. What are the three most likely root causes of the anomalous value of variable B, ranked in descending order? 

3. Is A a likely root cause of the anomalous value of variable B? 

4. Which is more likely to be the root cause: A or D? 

5. Why is D not considered a likely root cause of the anomalous value of variable B? 

#### **Questions about Causal Discovery** 

1. What algorithm was used to learn the causal graph? 

2. What is the stability score of the edge _A → B_ ? 

3. Which edges in the graph are considered the least reliable? 

4. How many bootstrap iterations were used during causal discovery?
