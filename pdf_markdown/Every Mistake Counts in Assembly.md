# Every Mistake Counts in Assembly

[Original PDF](../Every%20Mistake%20Counts%20in%20Assembly.pdf)

Pages: 11

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

**Every Mistake Counts in Assembly** 

**Guodong Ding**<sup>1</sup> **Fadime Sener**<sup>2</sup> **Shugao Ma**<sup>2</sup> **Angela Yao**<sup>1</sup> 1National University of Singapore 2Meta Reality Labs Research {dinggd, ayao}@comp.nus.edu.sg {famesener, shugao}@meta.com 

# **Abstract** 

One promising use case of AI assistants is to help with complex procedures like cooking, home repair, and assembly tasks. Can we teach the assistant to interject after the user makes a mistake? This paper targets the problem of identifying ordering mistakes in assembly procedures. We propose a system that can detect ordering mistakes by utilizing a learned knowledge base. Our framework constructs a knowledge base with spatial and temporal beliefs based on observed mistakes. Spatial beliefs depict the topological relationship of the assembling components, while temporal beliefs aggregate prerequisite actions as ordering constraints. With an episodic memory design, our algorithm can dynamically update and construct the belief sets as more actions are observed, all in an online fashion. We demonstrate experimentally that our inferred spatial and temporal beliefs are capable of identifying incorrect orderings in real-world action sequences. To construct the spatial beliefs, we collect a new set of coarse-level action annotations for Assembly101 based on the positioning of the toy parts. Finally, we demonstrate the superior performance of our belief inference algorithm in detecting ordering mistakes on the Assembly101 dataset. 

# **1 Introduction** 

We all know the pains of assembling furniture<sup>1</sup> , not to mention making mistakes during the procedure. Imagine now an AI assistant to support complex procedural activities like furniture assembly, cooking, or home repair. An intelligent assistant should be able to learn from the mistakes and detect them in the future. Mistake detection can be considered a procedural activity understanding task. Procedural activities are well explored in video understanding, and typical tasks include temporal action segmentation [5, 7], action anticipation [1, 17, 15]. Making mistakes is a natural and common part of performing procedures in real-world settings. In the video dataset Assembly101 [14], adult participants were asked to assemble and disassemble a children’s toy vehicle designed for 4- to 6-year-olds, however, nearly 60% of the sequences contained at least one mistake. 27 _._ 4% of these were action ordered incorrectly. For example, as shown in Fig. 3(a), if the roof is placed on the cabin before the speaker and the light, it will be impossible to position them afterwards. In developing an AI assistant, it is natural to consider support in the form of assessment and mistake detection. 

As a procedural activity, toy assembly distinguishes itself from similar activities in a number of ways. Firstly, assembling a toy involves a fixed set of steps based on the predetermined structure of the parts. Secondly, toy assembly is a sequential process, where each step builds upon the previous one. It is therefore necessary to follow some ordering of actions to complete the toy. Lastly, assemblers may encounter situations requiring problem-solving skills, such as identifying mistakes, locating alternative solutions, and resolving problems. The closest related tasks to the notion of mistakes in the video domain are anomaly detection [19] and unintentional action detection [6]. These tasks 

1A quick online search leads to dozens of articles with titles like “31 Pieces of Furniture You Won’t Have a Hard Time Assembling” and “The Secret to Assembling IKEA Furniture Without Losing Your Sanity” 

Preprint. Under review.

<!-- Page 2 -->

![](assets/041/paper-0002-00.png)



![](assets/041/paper-0002-01.png)



![](assets/041/paper-0002-02.png)



![](assets/041/paper-0002-03.png)



![](assets/041/paper-0002-04.png)



![](assets/041/paper-0002-05.png)



![](assets/041/paper-0002-06.png)


<!-- Start of picture text -->
ASSEMBLY EPISODE<br>... ...<br>...<br>SPATIAL TEMPORAL<br>INFERENCER KNOWLEDGE BASE<br>... ...<br>STEP LABELS<br><!-- End of picture text -->

Figure 1: Overview of our mistake detection system. Each colored circle denotes a toy part to be assembled. The INFERENCER takes as input an assembly sequence incrementally, consults the Knowledge base at each step to make predictions on the action of interest. Faces in the sequence they appear denote ‘correct’,‘order mistake’,‘correction’ and ‘unnecessary detach’. The knowledge base summarizes two type of belief sets, spatial and temporal. Spatial beliefs reveals the topology of objects while temporal beliefs denotes the ordering constraints. 

share the same spirit of detecting deviations from expected behaviour. For example, a car accident is an anomaly, whereas knocking over a vase is unintentional. However, it is important to note that anomalies or unintentional actions are inherently defined by their semantics, _i.e._ , observing the acts stand-alone is sufficient to determine that they are atypical. The same cannot be said for ordering mistake actions in assembly sequences because a given action can be correct or incorrect depending on the temporal context in which it is being performed, _e.g._ , it is physically possible to attach the cabin before or after attaching the seats. However, ‘attaching cabin’ will only be a correct action when seats are already placed. 

Knowledge representation and reasoning (KRR) is a fundamental area of study in artificial intelligence (AI). Knowledge representation models explicit and implicit knowledge in a domain, ranging from factual data to complex relationships and rules. Reasoning, on the other hand, refers to the ability of AI systems to derive new information or make intelligent inferences based on available knowledge. In this paper, our goal is to develop an intelligent system that can detect ordering mistakes in assembly sequences in the presence of a knowledge base, as depicted in Fig. 1. Specifically, two types of beliefs are formed in the knowledge base, _i.e._ , spatial beliefs and temporal beliefs. We define spatial beliefs to accumulate the topological relationships of the toy parts. For example, the ‘wheel’ attaches to the ‘chassis’; attaching ‘wheel’ to ‘cabin’ is not allowed and should therefore be identified as a mistake. Spatial beliefs are agnostic of the action order, _e.g._ , ‘wheel’ and ‘cabin’ are both attached to the ‘chassis, but the order in which they are attached is not implied. We therefore introduce temporal beliefs to keep track of the ordering constraints in the action sequences. 

To the best of our knowledge, Sener _et. al_ [14] are the first to advocate for the mistake detection task and their Assembly101 is the only real-world dataset with mistake annotations in action orderings. However, the annotated actions are ambiguous, as they reference only a single component. An assembly action, however, involves at least two working objects, and the other object must be provided to reveal the structural information. To this end, we provide a new annotations set that includes both interacting parts. 

To summarize, our main contributions are threefold: **1)** We formulate the ordering mistake detection problem as a knowledge representation and reasoning problem. To this end, we propose a novel mistake detection framework consisting of a BELIEFBUILDER and an INFERENCER to work with an assembly knowledge base. The BELIEFBUILDER constructs the knowledge base in an online fashion 

2

<!-- Page 3 -->

and the INFERENCER consults the knowledge base when making predictions. **2)** We design two types of beliefs in the knowledge base, _i.e._ , spatial and temporal beliefs, both in the format of logic rules. Spatial beliefs define the toy topology, while temporal beliefs encompass the ordering constraints. Additionally, we offer a graph interpretation for each type of belief. **3)** We enrich the Assembly101 dataset with information about the mistake type and the explicit part-to-part connection details to facilitate the mistake detection task. We evaluate our method on Assembly101 and demonstrate its superior capability for mistake detection. 

# **2 Related Work** 

**Procedural Activity Understanding.** Procedural knowledge is an important aspect of cognitive psychology and educational research. It has been studied in computer vision under the context of procedural planning [3], step forecasting [17, 10] and temporal action segmentation [5]. Common investigated procedural activities by the research community are from the cooking [4, 11, 20, 21] or assembly [14, 12, 2]. Procedural knowledge can be classified according to how they are sourced, i.e., explicit and implicit knowledge. Explicit knowledge assumes external providers, e.g., in the form of recipes [13] or instruction manuals [9], while implicit knowledge indicates learning from data with no supervision [17, 15] or distant supervision [10]. Our approach falls into the second category as we learn to construct our beliefs from the training data. 

**Mistake Detection.** Our approach is the first to study ordering mistakes in procedural activities that can handle the flexibility of action order and the variation in approaches of the participants. [18] tried to detect missing actions for making lattes. In their dataset, 18 of the 41 videos has a purposefully omitted action, _e.g.‘steaming milk’_ . [18] model the dependencies of latte-making actions with a directed graph and learn the graph from the complete sequences. Missing actions, however, are not identified until the entire sequence is completed. This method is not generalizable to detect the assembly ordering mistakes in Assembly101 since it can only identify the missing steps in a fixed order. 

**Anomaly Detection.** Detecting anomalies, especially in temporal sequences and unintentional actions [6, 19] are tasks similar to ours in spirit. These differ from procedural mistakes because the unintended actions are identifiable by their inherent semantics. An example would be a person walking suddenly falling to the ground. The unintionality is defined by the semantics of falling to the ground. On the contrary, the mistakes in an assembly task are usually irrelevant to semantics and more dependent on the temporal context it locates. This makes mistake detection in assembly tasks a suitable case for modeling the temporal logic of action sequences. 

# **3 The Approach** 

## **3.1 Preliminaries** 

**Study on mistakes.** We first survey all the mistakes made by participants in Assembly101 and list them in Table 1. Coarsely speaking, there are three classes for the mistake detection task: _‘correct’_ , _‘mistake’_ and _‘correction’_ , where the latter is a step made to rectify the mistake. The mistakes can be further classified into four types according to their root cause. The most straightforward type is the generic ordering mistake. Accumulated mistakes happen after generic order mistakes. Misorientation mistakes occur to the placement of a part in an incorrect orientation, _e.g._ , a reversed cabin. The last type of mistake is the unnecessary detachment of correctly assembled parts. Detecting misorientation mistakes requires 3D perception and a model of the toy parts, which extends beyond the scope of this work. We aim to build a system to identify assembly sequences’ ordering mistakes. 

**Definitions.** Consider a collection of _N_ assembly sequences **S** = _{_ **s** _n}_<sup>_N_</sup> _n_ =1<sup>and its corresponding</sup> label set _Y_ . Each sequence **s** = _{_ ( _v, i, j_ ) _t}_<sup>_T_</sup> _t_ =1<sup>has</sup><sup>_T_steps, where</sup><sup>_v∈{_attach</sup><sup>_,_detach</sup><sup>_}_denotes the</sup> ‘verb’, while ( _i, j_ ) are toy part indices. The step-wise mistake label is denoted as _yt_ . The ( _i, j_ ) part notations are generally considered commutable in our work, _i.e._ , ( _i, j_ ) _≡_ ( _j, i_ ). 

The objective of the mistake detection system is to learn from the existing mistakes in action sequences such that it can be used to detect mistakes in future unseen sequences. To do so, we build a knowledge base _K_ = _{S, T }_ that maintains spatial beliefs _S_ and temporal beliefs _T_ . We 

3

<!-- Page 4 -->

Table 1: Six types of mistakes in Assembly101. Misorientation shown in grey as it is beyond the scope of our work. 

|Verb|Coarse|# of samples|Remark|Fine|# of samples|
|---|---|---|---|---|---|
||correct|2914|correct step|A|2914|
|attach|||generic order|B|153|
||mistake|355|accumulated|C|46|
||||misorientation|D|156|
|detach|mistake|371|unnecessary|F|371|
||correction|348|correction|E|348|



propose a BELIEFBUILDER and an INFERENCER to interact with the knowledge base accordingly. OurBELIEFBUILDER algorithm are carefully designed to deal with streaming action sequences. As mentioned, the ordering mistake actions are context-dependent. Temporal context is important in both belief building and inference stages. To that end, we define an episodic memory _M_ to form a collective temporal context for the algorithms. 

## **3.2 Spatial Beliefs** _S_ **.** 

In the context of toys, the spatial topology is pre-defined, _e.g._ , the ‘roof’ is attached to the ‘cabin’ and the ‘wheels’ to the ‘chassis’. Following this logic, we define a spatial belief set, _S_ , which encompasses pairs of connecting toy parts, see Fig. 2 ( _i, j_ ) pairs. The spatial beliefs serve two purposes. To start with, they can be employed to confirm the feasibility of attaching the parts, _i_ and _j_ , with the following rule: 

SPATIAL( _i, j_ ) _�→ y_ ˆ : 


![](assets/041/paper-0004-06.png)


In practice, if any pair is incompatible with the spatial beliefs, attempting to attach them would be a mistake, as they would not fit geometrically. In addition, the belief set, _S_ , can verify the completion of the assembly sequence and indicate any unperformed or missing actions. 


![](assets/041/paper-0004-08.png)



![](assets/041/paper-0004-09.png)



![](assets/041/paper-0004-10.png)


**Graph Interpretation.** One can represent the spatial belief set as a graph, where each toy part 

is depicted as a node, and the edges denote the feasibility of attaching them. An edge between two nodes indicates feasibility, and completion is achieved when the graph has been fully traversed by the episodic memory _M_ . Fig. 2 visualizes the graph representation of spatial beliefs. 

## **3.3 Temporal Beliefs** _T_ **.** 

Spatial beliefs do not imply any ordering constraints in attaching the toy parts. The ordering mistakes are determined by the temporal context in which the action is being observed. We determine ordering constraints from the mistake instances during training to establish the temporal beliefs _T_ . A temporal belief _Tij_ for its anchor pair ( _i, j_ ) provides the following rule: 

TEMPORAL( _M, i, j_ ) _�→ y_ ˆ : 


![](assets/041/paper-0004-16.png)


4

> Original page for checking 2 unresolved font glyphs.

![Original page 4](assets/041/verify-page-004.png)

<!-- Page 5 -->

![](assets/041/paper-0005-00.png)


<!-- Start of picture text -->
PART GEOMETRY: RULE GRAPH: PART GEOMETRY: RULE GRAPH:<br>ROOF CABIN<br>r = 1 r = 2<br>LIGHT SPEAKER INTERIOR BASE<br>CABIN CHASSIS<br>(a) Transitive (b) Intransitive<br><!-- End of picture text -->

Figure 3: Transitivity of temporal beliefs. Part geometry implies the ordering constraints (left) and its graph representation (right). Anchor action (the red edge) is reliant on the completion of the rest (back edges in grey group). Transitive and intransitive rules differ in the radius _r_ of their graphs. For transitive rules ( _r_ = 1), any actions from the dependency set (black edges) will be mistakes after anchor action is performed. While, for intransitive rules ( _r >_ 1), only the last action in black edges that completes the rule graph will be considered mistake. 

where _Dij ⊂Tij_ corresponds to a list of part pairs ( _i_<sup>_′_</sup> _, j_<sup>_′_</sup> ), which we refer to as dependent for the correct execution of _Aij_ . In Fig. 3(a), with anchor (roof,cabin), _Dij_ consists of (light,cabin) and (speaker,cabin). The above rule indicates that the anchor action is only possible when all its dependents have been correctly assembled. 

**Error Accumulation.** The TEMPORAL rule considers and predicts only for the anchor action. However, it is necessary to consider the dependents because an error anchor action in context ( _¬Aij ∈ M_ ) would turn its dependent actions from _Dij_ that are yet to happen into accumulated errors. To that end, we define the transitivity on _Tij_ to correspond to two different cases of error accumulation, _i.e._ , _transitive_ (written as _Tij_ ) and _intransitive_ (written as _¬Tij_ ). A transitive (Fig. 3(a)) rule indicates that executing any dependent after the anchor is a mistake. With a slight abuse of notation, we define the following inference rule _Tij_ ( _M_ ): 

_Tij_ ( _M_ ) _�→ y_ ˆ : 


![](assets/041/paper-0005-05.png)


which indicates that with (roof,cabin) attached, attaching (light,cabin) and (speaker,cabin) will be mistakes. In contrast, an intransitive (Fig. 3(b)) rule would consider executing any dependent to be correct except for the last dependent pair. Consider (base,chassis) attached as the wrong anchor action in context, attaching (cabin,interior) is correct, while further attachment of (interior,chassis) is considered a mistake. The predictions will be the opposite if one first attaches (interior, chassis) and then (cabin,interior), which is implied by the following rule: 

_¬Tij_ ( _M_ ) _�→ y_ ˆ : 


![](assets/041/paper-0005-08.png)


We define _Tij_<sup>_′_:=</sup><sup>_Tkl|_(</sup><sup>_i, j_)</sup><sup>_∈Dkl_the temporal rule that has (</sup><sup>_i, j_) in its dependent set.Combining</sup> both transitive and intransitive rule, we have the following to make inference: 


![](assets/041/paper-0005-10.png)


**Graph Interpretation.** Similar to the spatial rule, we show that our temporal rules can be represented as graphs. In its graph form, the transitivity of the rule is determined by its radius. Conventionally, the radius of a graph is defined as: 


![](assets/041/paper-0005-12.png)


where _d_ ( _u, v_ ) is the geodesic distance or shortest-path distance between two nodes _u_ and _v_ in graph _V_ . _Transitive_ rule graphs have the precise radius with _r_ = 1 while _intransitive_ rule graphs are those with larger radius ( _r >_ 1). An illustration is shown in Fig. 3. The anchor action (edge in red) is only correct when the dark edges are traversed. It is possible to consider a hybrid version of these two cases; more details on this case are left to the Supplementary. 

5

> Original page for checking 2 unresolved font glyphs.

![Original page 5](assets/041/verify-page-005.png)

<!-- Page 6 -->

## **3.4 Belief Building and Inference** 

We next focus on the construction and inference procedures of the above belief sets by introducing BELIEFBUILDER and INFERENCER. BELIEFBUILDER illustrates the process of managing the knowledge base _K_ to take into account of a new piece of information that is observed incrementally. As the name suggests, the INFERENECER, consults the knowledge base _K_ , and makes prediction on the action being observed. 

## **Algorithm 1** Belief building Step 

1: **procedure** BELIEFBUILDER( _M, i, j, y, C_ ) 2: **switch** _y_ **do** 3: **case** _Aij_ 4: _S ←S ∪_ ( _i, j_ ) 5: _Cij ←_ [ _Cij_ ] _∩_ PRECEDES( _M, i, j_ ) _▷_ Eq. 9 6: **if** _Dij ∈ M_ **then** 7: _Dij ←_ [ _Dij_ ] _∩_ [CONTEXT( _M, i, j_ )] _∩_ [ _Cij_ ] _▷_ Eq. 10 8: _Tij ←_ CONNECT( _Tij, M, S_ ) _▷_ Eq. 11 9: POP( _M, ¬Aij_ ), POP( _M, Dij_ ) 10: **end if** 11: PUSH( _M, y_ ) 12: **case** _¬Aij_ 13: **if** ACCUMULATED( _¬Aij_ ) **then** 14: **for** _¬Ai′j′ ∈ M, S_ **do** 15: _Di′j′ ←Di′j′ ∪_ ( _i, j_ ) _▷_ Eq. 12 16: **end for** 17: **end if** 18: PUSH( _M, y_ ) 19: **case** _¬Dij_ 20: POP( _M, Aij_ ) 21: **case** _Dij_ 22: PUSH( _M, y_ ) 23: **end procedure** 

**BELIEFBUILDER.** The knowledge base of spatial beliefs (see Sec. 3.2) and temporal beliefs (see Sec. 3.3) is initialized as empty at the beginning, _i.e._ , _S_ = ∅ _, T_ = ∅. This indicates that the knowledge base is completely agnostic of the toy being assembled. The BELIEFBUILDER is aimed to build and update both of them as more assembly sequences are provided in an incremental manner. Every mistake counts in assembly sequences, and any ordering mistake always reveals a temporal belief. For the mistakes ( _¬Aij_ ), the mistake context CONTEXT( _M, i, j_ ) invariably contains its dependents. The mistake context is the set of correct actions between the mistake fix ( _Dij_ ) and its correct execution ( _Aij_ ), _i.e._ , CONTEXT( _M, i, j_ ) = _{_ ( _i_<sup>_′_</sup> _, j_<sup>_′_</sup> ) _|tDij < tAi′j′ < tAij , Ai′j′ ∈ M }_ . _Dij_ is updated with the following: 


![](assets/041/paper-0006-05.png)


where [ _·_ ] will only be a valid term if ( _·_ ) is not an empty set. Although observing the ordering mistakes in the sequences is an obvious and strong cue for the builder to update the temporal beliefs, there is also implicit temporal logic hidden behind a fully correct assembly. For example, an action _Aij_ is not temporally dependent on its subsequent actions. In reverse, its preceding actions PRECEDES( _M, i, j_ ) = _{_ ( _i_<sup>_′_</sup> _, j_<sup>_′_</sup> ) _|Ai′j′ ∈ M }_ would form a candidate set _Cij_ and any dependents in _Tij_ fall within that set, _i.e._ , _Dij ⊂Cij_ . In the online setting, we continuously narrow down _Cij_ with the following: 


![](assets/041/paper-0006-07.png)


Note that the preceding actions depend on _M_ and may change between different episodes, while _Cij_ are shared across episodes. Taking _C_ into consideration, Eq. 8 becomes: 


![](assets/041/paper-0006-09.png)


6

<!-- Page 7 -->

It is possible (as shown in Fig. 5) that the algorithm may miss dependents in intransitive temporal beliefs, due to the flexibility of labels for the dependents as discussed in Rule (5). Missing dependents cause the intransitive temporal rule graph (Fig 3(b)) to be disjoint. To mitigate this situation, we leverage the spatial belief _S_ to find the minimum number of actions present in the episodic memory _M_ to connect any sub-graphs. Specifically, 


![](assets/041/paper-0007-01.png)


where PATH( _S, T_ ) finds the shortest path in _S_ that completes the rule graph of _T_ . To deal with accumulated mistake _¬Aij_ , we would add them into the dependent set of any ongoing order mistakes in context, _i.e._ , 


![](assets/041/paper-0007-03.png)


The BELIEFBUILDER (Alg. 1) is repeated for each step in the episodes. We show the overall algorithm in the Supplementary. 

|**Algor**|**ithm 2**Inference Step||
|---|---|---|
|1: **p**|**rocedure**INFERENCER(_M, v, i, j_)<br>||
|2:|**switch**_v_**do**||
|3:|**case**‘attach’||
|4:|ˆ_y ←_ATTACH(_M, i, j_)<br>|_▷_Eq. 13|
|5:|PUSH(_M, y_)||
|6:|**case**‘detach’||
|7:|ˆ_y ←_DETACH(_M, i, j_)|_▷_Eq. 14|
|8:|**if** ˆ_y_ ==_Dij_ **then**<br>||
|9:|POP(_M, ¬Aij_)||
|10:|**else**<br>||
|11:|POP(_M, Aij_)||
|12:|**end if**||
|13:|**return** ˆ_y_||



14: **end procedure** 

**INFERENCER.** The INFERENCER is also recurrent and makes predictions based on the belief sets and the previous decisions. Alg. 2 summarizes the INFERENCER step. At each time step ( _M, v, i, j_ ), the INFERENCER estimates for the tuple ( _v, i, j_ ) the mistake label based on the episodic memory _M_ , which has historical action labels up to the current step. When the action is to attach, _i.e._ , _v_ =‘attach’, multiple inference rules from both spatial and temporal beliefs, SPATIAL (Rule. 1), TEMPORAL (Rule. 3) and DEPENDENT (Rule. 6) will be applied jointly to decide on its label ˆ _y_ . While for a detach action that is being perceived at the moment, its label will depend on the episodic memory _M_ . If the attachment of the same object pairs exists as a mistake in the memory, this action would be regarded as a ‘correction’, and otherwise it is a mistake of ‘unnecessary detach’. Overall, the INFERENCER makes predictions with the following rule: 

ATTACH( _M, i, j_ ) _�→ y_ ˆ : 


![](assets/041/paper-0007-09.png)



![](assets/041/paper-0007-10.png)


# **4 Dataset and Experiments** 

## **4.1 Dataset.** 

Assembly101 [14] is the first to propose the mistake detection task in assembly sequences. The action labels in the dataset are ‘(verb, noun)’, _e.g._ , ‘attach arm_connector’. However, such annotations without mentioning the other interacting part in context introduce inconsistency and ambiguity. For example, two distinct actions attaching ‘arm_connector’ to ‘chassis’ or ‘boom’ would share 

7

> Original page for checking 1 unresolved font glyphs.

![Original page 7](assets/041/verify-page-007.png)

<!-- Page 8 -->

Table 2: Performance comparison with coarse mistake labels. 

||m|istake|cor|rection|co|rrect|Acc|F1|
|---|---|---|---|---|---|---|---|---|
||recall|precision|recall|precision|recall|precision|||
|TempAgg [16]|36.6|54.0|49.3|43.4|93.2|79.7|78.8|59.9|
|<br>LSTM|35.2|58.7|43.7|49.9|99.0|88.5|82.3|61.3|
|Ours|70.6|63.7|40.8|87.2|92.7|93.1|86.0|71.8|
|Gains|+35.4|+5.0|-2.9|+37.3|-6.3|+4.6|+3.7|+10.5|



the identical action label. Therefore, such annotations are not informative enough for the mistake detection task where spatial connectivity matters. To that end, for the assembly sequences, we create a new set of part-to-part annotations which includes both interacting objects, denoted in the form of ( `verb` _,_ `this` _,_ `that` ). Due to the nature of our approach, which focuses on logical reasoning, we only consider two types of `verb` s, _i.e._ , `attach` and `detach` . We hope that such explicit part annotations on Assembly101 [14] encourage more investigation on the task. 

**Self-looped and repetitive actions.** Certain toy parts from Assembly101 can be further split into two halves, _e.g._ , ‘chassis part’ and ‘water tank part’, as illustrated in supplementary. For simplicity, we keep a consistent level of annotation and do not consider the subpart level and annotate them as ‘attach chassis and chassis’. In this sense, any composition of subparts is a self-looped action. Due to the geometric symmetry of the toys, it is common for assembly sequences to involve repetitive steps. For example, four wheels can be attached at different sequential locations; they are annotated whenever they occur, regardless of their number of occurrences. 

**Splits.** There are 328 unique action sequences for assembling 101 toys in the Assembly101 dataset. To create our splits, we randomly sample one action sequence as the test set and use the remaining sequences as the training data for each toy. This process is repeated four times to obtain four different splits, and we report the results as the average over the four splits. 

**Evaluation metric.** We propose the following evaluation metrics to assess the mistake detection performance comprehensively. We report per class recall and precision, while Acc and mean F1 scores are reported over all classes. 

## **4.2 Experiments** 

**Baselines.** Following [14], we adopt the long-range temporal model TempAgg [16] as the mistake detection model, train with our part-to-part annotation for 15 epochs. In essence, the mistake detection problem can also be modeled using a recurrent neural network (RNNs) by treating it as a sequenceto-sequence task. As another baseline model to compare, we design an LSTM [8] comprising four hidden layers, and each hidden layer size is set to 256. We feed the one-hot action feature vector as input for each step and the action sequences are truncated or padded to a fixed length of 60. We train the LSTM on the training data with a learning rate of 1 _e_<sup>_−_3</sup> for 100 epochs. 

**Coarse mistake detection.** We report the results on Assembly101 dataset trained and evaluated on the coarse mistake labels for different approaches in Table. 2. Both TempAgg [16] and LSTM take the one-hot encoded feature vector as input. LSTM slightly outperforms TempAgg at the Acc (+3 _._ 5%) and F1 (+1 _._ 4%) scores. Such a performance gap mainly results from LSTM’s boost in ‘correct’ class. Our method achieves a high recall of 70 _._ 6% on the mistake class, which doubles that (35 _._ 2%) of the LSTM. In the meantime, ours is by 5% and 9 _._ 7% higher in mistake precision than LSTM and TempAgg, respectively. While for both ‘correction’ and ‘correct’ classes, our approach achieves lower recall values but has a high precision value. This indicates that our approach has a high confidence in the accuracy of instances from these classes. When evaluated across the classes, ours is the best in both Acc (86 _._ 0%) and F1 (71 _._ 8%), showing its strong ability to capture the ordering dynamics in assembly sequences. 

**Fine mistake detection.** We then compare the performance between our approach and LSTM on the fine mistake labels. The confusion matrix for each approach is plotted in Fig 4. As it is shown in Fig 4(a), the the LSTM model practically missed all ordering mistakes (on B, C, and D) and predicted them as correct. This is likely due to the significant imbalance ratio between each fine mistake class and the correct class (see Table. 1). However, the confusion LSTM makes in the bottom right corner 

8

<!-- Page 9 -->

![](assets/041/paper-0009-00.png)


<!-- Start of picture text -->
A 100% 0% 0% 0% 0% 0% A 94% 0% 0% 5% 0% 0%<br>B 100% 0% 0% 0% 0% 0% B 41% 31% 0% 27% 0% 0%<br>C 100% 0% 0% 0% 0% 0% C 46% 0% 53% 0% 0% 0%<br>D 100% 0% 0% 0% 0% 0% D 65% 2% 0% 31% 0% 0%<br>E 8% 0% 0% 0% 62% 29% E 0% 0% 0% 0% 87% 12%<br>F 15% 0% 0% 0% 42% 41% F 0% 0% 0% 0% 62% 37%<br>A B C D E F A B C D E F<br>Output Class Output Class<br>(a) LSTM (b) Ours<br>Target Class Target Class<br><!-- End of picture text -->

Figure 4: Confusion matrix comparison on the fine mistake labels. 

indicates the fact that LSTM is picking up the knowledge that a detach action can either be a mistake or a correction. In contrast, our approach (Fig 4(b)) is better at detecting the ordering mistakes and does not confuse a detach action (E and F) to a correct attach class (A) as the LSTM does. 


![](assets/041/paper-0009-03.png)


<!-- Start of picture text -->
Sequence 1 M Final<br>S :<br>1 + (chassis,interior) A 34 2 3<br>2 + (body, chassis) ¬A 03<br>3 + (cabin, roof) A 25 1 5 4 0 6<br>4 − (chassis, body) D 03<br>T 03 : S :<br>5 + (cabin, interior) A 24 2 3<br>CONTEXT(0 ,  3) =  { (2 ,  4) ,  (1 ,  2) }<br>6 + (bumper, cabin) A 12<br>C 03 =  { (3 ,  4) ,  (2 ,  5) ,  (2 ,  4) ,  (1 ,  2) }<br>7 + (body, chassis) A 03 1 5 4 0<br>D 03 = CONTEXT(0,3)  ∩C 03 =  { (2 ,  4) ,  (1 ,  2) }<br>8 + (chassis, wheel) −<br>D 03 = CONNECT( T 03 , M, S ) =  { (2 ,  4) ,  (1 ,  2) ,  (3 ,  4) }<br>Sequence 2 M<br>1 + (cabin, roof) − S : 2 3 6 T 03 :<br>2 + (chassis, wheel) A 36<br>3 − (cabin, roof) − 1 5 4 0 2 3<br>4 + (chassis, interior) A 34<br>T 03 :<br>5 + (cabin, interior) A 24 4 0<br>CONTEXT(0 ,  3) = ∅<br>6 + (body, chassis) A 03<br>7 + (bumper, cabin) − C 03 =  { (2 ,  4) ,  (3 ,  4) }<br>8 + (cabin, roof) − D 03 =  D 03  ∩C 03 =  { (2 ,  4) ,  (3 ,  4) }<br>D 03 = CONNECT( T 03 , M, S ) =  { (2 ,  4) ,  (3 ,  4) }<br><!-- End of picture text -->

Figure 5: A running example of our BELIEFBUILDER. Note that at the 7-th step in the first sequence, the _D_ 03 before the (highlighted in red) misses one dependent action (3 _,_ 4) since it is located outside the mistake context and includes an extra pair (1 _,_ 2) given the mistake context (Steps 5-6). The missing action is retrieved via the CONNECT step and the extra pair is removed when the RULEBUILDER sees the 6-th step in Sequence 2. The right side shows the final spatial and temporal rules. 

**Spatial and temporal beliefs.** We show an example of the beliefs building in Fig. 5. We additionally run our approach on the full set of sequences on Assembly101 dataset and yield in total 48 temporal beliefs. Among these, 23 are transitive, and the remaining 15 are intransitive. It is worth noting that these temporal rules are well aligned with the geometric constraints of the toy parts. 

# **5 Conclusion** 

This work is aimed at detecting ordering mistakes in toy assembly sequences. Accordingly, we propose a novel framework that maintains two belief sets to describe the spatial structure and temporal constraints in assembly. The belief sets are constructed in an online fashion with the BELIEFBUILDER and serve as rules for the INFERENCER. Our approach achieves promising ordering mistake detection results and consistently outperforms other approaches on the Assembly101 dataset. 

9

<!-- Page 10 -->

# **References** 

- [1] Yazan Abu Farha, Alexander Richard, and Juergen Gall. When will you do what?-anticipating temporal occurrences of activities. In _CVPR_ , 2018. 

- [2] Yizhak Ben-Shabat, Xin Yu, Fatemeh Saleh, Dylan Campbell, Cristian Rodriguez-Opazo, Hongdong Li, and Stephen Gould. The ikea asm dataset: Understanding people assembling furniture through actions, objects and pose. In _WACV_ , 2021. 

- [3] Chien-Yi Chang, De-An Huang, Danfei Xu, Ehsan Adeli, Li Fei-Fei, and Juan Carlos Niebles. Procedure planning in instructional videos. In _ECCV_ , 2020. 

- [4] Dima Damen, Hazel Doughty, Giovanni Maria Farinella, Antonino Furnari, Jian Ma, Evangelos Kazakos, Davide Moltisanti, Jonathan Munro, Toby Perrett, Will Price, and Michael Wray. Rescaling egocentric vision: Collection, pipeline and challenges for epic-kitchens-100. _IJCV_ , 130:33–55, 2022. 

- [5] Guodong Ding, Fadime Sener, and Angela Yao. Temporal action segmentation: An analysis of modern technique. _arXiv preprint arXiv:2210.10352_ , 2022. 

- [6] Dave Epstein, Boyuan Chen, and Carl Vondrick. Oops! predicting unintentional action in video. In _CVPR_ , 2020. 

- [7] Yazan Abu Farha and Jurgen Gall. Ms-tcn: Multi-stage temporal convolutional network for action segmentation. In _CVPR_ , 2019. 

- [8] Sepp Hochreiter and Jürgen Schmidhuber. Long short-term memory. _Neural computation_ , 9(8):1735–1780, 1997. 

- [9] Mahnaz Koupaee and William Yang Wang. Wikihow: A large scale text summarization dataset. _arXiv preprint arXiv:1810.09305_ , 2018. 

- [10] Xudong Lin, Fabio Petroni, Gedas Bertasius, Marcus Rohrbach, Shih-Fu Chang, and Lorenzo Torresani. Learning to recognize procedural activities with distant supervision. In _CVPR_ , pages 13853–13863, 2022. 

- [11] Jonathan Malmaud, Jonathan Huang, Vivek Rathod, Nicholas Johnston, Andrew Rabinovich, and Kevin Murphy. What’s cookin’? interpreting cooking videos using text, speech and vision. In _NAACL_ , 2015. 

- [12] Francesco Ragusa, Antonino Furnari, Salvatore Livatino, and Giovanni Maria Farinella. The meccano dataset: Understanding human-object interactions from egocentric videos in an industrial-like domain. In _WACV_ , 2021. 

- [13] Amaia Salvador, Nicholas Hynes, Yusuf Aytar, Javier Marin, Ferda Ofli, Ingmar Weber, and Antonio Torralba. Learning cross-modal embeddings for cooking recipes and food images. In _CVPR_ , 2017. 

- [14] Fadime Sener, Dibyadip Chatterjee, Daniel Shelepov, Kun He, Dipika Singhania, Robert Wang, and Angela Yao. Assembly101: A large-scale multi-view video dataset for understanding procedural activities. In _CVPR_ , pages 21096–21106, 2022. 

- [15] Fadime Sener, Rishabh Saraf, and Angela Yao. Transferring knowledge from text to video: Zero-shot anticipation for procedural actions. _IEEE Transactions on Pattern Analysis and Machine Intelligence_ , 2022. 

- [16] Fadime Sener, Dipika Singhania, and Angela Yao. Temporal aggregate representations for long-range video understanding. In _Computer Vision–ECCV 2020: 16th European Conference, Glasgow, UK, August 23–28, 2020, Proceedings, Part XVI 16_ , pages 154–171. Springer, 2020. 

- [17] Fadime Sener and Angela Yao. Zero-shot anticipation for instructional activities. In _ICCV_ , pages 862–871, 2019. 

- [18] Bilge Soran, Ali Farhadi, and Linda G. Shapiro. Generating notifications for missing actions: Don’t forget to turn the lights off! _ICCV_ , 2015. 

10

<!-- Page 11 -->

- [19] Waqas Sultani, Chen Chen, and Mubarak Shah. Real-world anomaly detection in surveillance videos. In _CVPR_ , 2018. 

- [20] Luowei Zhou, Chenliang Xu, and Jason J Corso. Towards automatic learning of procedures from web instructional videos. In _AAAI_ , 2018. 

- [21] Dimitri Zhukov, Jean-Baptiste Alayrac, Ramazan Gokberk Cinbis, David Fouhey, Ivan Laptev, and Josef Sivic. Cross-task weakly supervised learning from instructional videos. In _CVPR_ , 2019. 

11
