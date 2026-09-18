# MistExit Learning to Exit for Early Mistake Detection in Procedural Videos

[Original PDF](../MistExit%20Learning%20to%20Exit%20for%20Early%20Mistake%20Detection%20in%20Procedural%20Videos.pdf)

Pages: 24

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

**MistExit: Learning to Exit for Early Mistake Detection in Procedural Videos** 

Sagnik Majumder<sup>1</sup> Anish Nethi<sup>1</sup> Ziad Al-Halah<sup>2</sup> Kristen Grauman<sup>1</sup> 1UT Austin 2University of Utah 

**Abstract.** We introduce the task of early mistake detection in video, where the goal is to determine whether a keystep in a procedural activity is performed correctly while observing as little of the streaming video as possible. To tackle this problem, we propose a method comprising a mistake detector and a reinforcement learning policy. At each timestep, the detector processes recently observed frames to estimate the keystep’s correctness while anticipating future visual features, enabling reliable early mistake estimates. Meanwhile, the policy aggregates the detector outputs and visual observations over time and adaptively decides when to exit ( _i.e_ ., stop processing incoming frames) while producing the final prediction. Using diverse real-world procedural video datasets, we demonstrate that our MistExit model achieves superior mistake detection accuracy while reducing the fraction of video observed compared to state-of-the-art models. Project: `https://vision.cs.utexas.edu/projects/mist_exit` . 

# **1 Introduction** 

Procedural videos illustrate how to perform a sequence of steps to complete diverse human tasks, such as cooking a meal or repairing a bike, and are driving a new frontier in AI coaching [25,32,52] and robotics [3,28,35]. Given the routine and ubiquitous nature of procedural tasks, understanding procedural videos is essential for developing capable AI assistants, including those deployed on smart glasses that provide real-time contextual guidance across various domains such as sports, cooking and music [14,25,31,52,70], and dexterous robots designed to assist humans with similar tasks. Mistake detection—the task of identifying errors in the execution of a procedural activity—is particularly important, as it enables real-time support [52], facilitates skill assessment [17,51,53], and helps identify areas for improvement during task execution [82]. These capabilities make mistake detection a key component for personalizing learning and building more competent agents for procedural tasks in real-world environments. 

Despite impressive progress, existing research on mistake detection largely operates in an offline, batch setting [12,23,30,42,49] that assumes access to the full video for identifying errors in the keysteps of a procedural activity. Consequently, such systems lack proactivity—that is, they cannot flag mistakes before the agent has fully committed to or completed a step. This limitation reduces their applicability in real-time and interactive scenarios in which humans and robots operate, as well as in resource-efficient settings where avoiding wastage or damage

<!-- Page 2 -->

2 Majumder et al. 


![](assets/057/paper-0002-01.png)


<!-- Start of picture text -->
Observed Frames<br>EXIT POINT<br>Correct,<br>7% of video<br>elapsed<br>EXIT POINT<br>Exit  Mistake<br>Policy Detector 12% of video Mistake,<br>elapsed<br><!-- End of picture text -->

**Fig. 1:** Our goal is to learn a policy that, given a streaming video of a keystep in a procedural activity, decides how much of the video to observe before exiting ( _i.e_ ., stopping inference), such that a mistake detector conditioned on the recently observed frames can accurately determine whether the keystep is a mistake or not while minimizing the fraction of the video observed. _E.g_ ., in a video like the one shown in row 2, a welltrained model may observe a drill bit (frame 3) and infer that the step will eventually result in a mistake—the glass breakage in later frames confirms this—and exit promptly, thereby using only about 12% of the video. 

to resources—such as ingredients during cooking or tools during a repair task—is critical. It also limits deployment in low-power setups [1,25,47,81], _e.g_ ., on smart glasses, where the mistake detector must operate within an energy budget. 

This motivates us to consider _early_ mistake detectors that operate on streaming procedural videos and identify errors in keysteps while observing only a minimal fraction of the video. Towards this goal, we introduce the task of _early detection of mistakes in procedural videos_ . In this task, the goal is to learn a policy that, given a streaming video of a keystep in a procedural activity— _e.g_ ., a chef `peeling a cucumber` for a salad, a mechanic `propping up a bike` to take off its wheel—decides _how much_ of the video to observe before _exiting_ (stopping inference). The objective is to ensure that a mistake detector, conditioned on the recently observed frames, can accurately determine whether the keystep is a mistake or not while minimizing the fraction of the video that must be observed. See Fig. 1. 

We consider diverse categories of procedural mistakes in our task setting, including ordering errors ( _e.g_ . adding oil to a saucepan before heating), technical mistakes ( _e.g_ . over-tightening a bolt leading to threading damage), and incorrect object usage ( _e.g_ . using a spoon instead of a whisk to beat eggs). 

To tackle this task, we propose MistExit, an early mistake detection framework comprising a mistake detector and a reinforcement learning (RL) policy. At each timestep of the streaming video, the detector processes the recently observed frames to produce an initial estimate of the keystep’s mistake label, along with predicted visual features for a sequence of future frames. Future anticipation enables the detector to better model the keystep’s correctness and provide reliable initial mistake estimates to the policy. The policy takes the detector’s outputs and the observed frames as inputs, aggregates them over time, and sequentially decides when to exit, while also producing the final prediction of the keystep’s correctness at the exit point. Whereas the detector outputs convey the detector’s uncertainty to the policy and indicate whether they are reliable enough to be incorporated into the policy’s model of the keystep’s correctness, the visual

<!-- Page 3 -->

MistExit 3 

inputs—accumulated over time—allow the policy to verify the visual evidence against the detector’s predictions and adjust its exit strategy accordingly. 

We train our policy using a novel reward comprising three components: a dense term that promotes continuous improvement in detection quality and stabilizes training on longer and more complex videos; a sparse term that encourages accurate predictions at the exit point, capturing the essence of the task; and a video-aware time penalty that incentivizes early exits commensurate with the video’s length and complexity. 

We evaluate our approach on two real-world datasets of procedural videos: CaptainCook4D (CC4D) [54] and Assembly101 [61]. Together, these datasets span diverse activity scenarios—cooking in CC4D vs. (dis)assembly in Assembly101— as well as different task environments, with an in-the-wild cooking setup in CC4D and a tabletop setting in Assembly101. Our model successfully learns to detect procedural mistakes accurately while exiting early, outperforming multiple strong baselines, including policies from early action recognition [16,24,73,78] and its variant without future anticipation. We will release our code and data. 

# **2 Related Work** 

_Mistake detection in procedural videos._ Mistake detection in procedural videos involves identifying deviations in the execution of keysteps within the demonstrated procedural activity [19, 23, 25, 30, 54, 56, 61, 70]. Such deviations may include missing, adding or modifying certain steps [33,42,54], incorrectly performing some steps [26,33,54,58,70] or altering their order [33,54,61]. Prior works identify mistakes of varying granularity–from sequence-level deviations [23,56] to errors in both fine-grained [42,58,70] and coarse-grained [54,61] actions, and tackle diverse activity scenarios–from indoor activities like cooking [25,42,54] and (dis-)assembly [23,25,56,58,61,70] to outdoor activities like pitching a tent [33]. 

Most of these models operate in an _offline_ setting, assuming access to the entire video and identifying mistakes after observing it in full. Such models determine step correctness by leveraging knowledge graphs constructed from video transcripts [12], employing hand-crafted error functions that rely on action preconditions to decide step correctness [23], comparing visual features of a step against pre-computed action-specific clusters [42], matching recognized step types against expected types extracted from a task graph [30], or detecting inconsistencies between predicted and observed gaze trajectories of the actor [49]. In contrast, we address _online_ mistake detection—specifically, a challenging setting in which the goal is to determine whether a step is correct or erroneous as early as possible. 

Select prior methods tackle the challenging online (streaming) setting, but they detect only the first incorrect step using one-class classification to compare actions recognized by an action recognition model against expected actions derived from a large language model [19, 55] or a procedural task graph [60]. However, these methods cannot detect mistakes beyond the first one because the action anticipation model becomes unreliable once the mistaken action is used as

<!-- Page 4 -->

4 Majumder et al. 

input for predicting subsequent actions. Unlike these models, which can detect only the first mistake in a procedural sequence, we aim to identify all mistakes and do so early within each step. Finally, unlike all prior approaches, we equip our detector with the ability to anticipate future visual features, allowing it to flag mistakes even earlier and improve task performance, as we show in results. 

_Online video understanding._ Prior works have studied various online video understanding tasks. Whereas online action recognition [4,40,65] requires classifying the action in a video clip using a small fraction of frames, the goal in online action detection [11,15,21,68,69,79,85] is to predict if a frame in a streaming video is from an action class or the background class. Other efforts tackle online action localization [34,36,63] and estimate action start and end times, predict action segments in streaming videos [22,62] or estimate the continuous progress of an action in a streaming setting [13,62]. In contrast, we tackle a distinct task of detecting mistakes in procedural videos in a streaming setting. Specifically, our focus is on both mistake detection accuracy and efficiency, and therefore, we evaluate an early detection setup where the goal is to recognize mistakes in a keystep as quickly as possible. 

_Early recognition in videos._ Early recognition [6,8,41,57,67,71] involves recognizing actions and events in videos by observing only a few frames at their onset. Earlier approaches leverage probabilistic modeling [6,41,43,57] by extracting handcrafted features from partially observed videos. These methods employ techniques such as bag-of-words representations [57], sparse coding [38,39], or hierarchical representations [41]. More recent methods use learned features [18, 29, 72, 84] produced through knowledge distillation between teacher models trained on full videos and student models trained on partial videos [5, 18, 29, 72], generating full videos using partially observed ones [80], residual propagation [84], inferring relations with graph neural nets [8,76,77], learning both instance-specific features and generic features shared across the dataset [20] or multi-scale representation of partial videos [64]. In contrast, we tackle the novel task of early recognition of mistakes in procedural videos. Moreover, unlike the above methods that rely on short, fixed-length video segments, our goal is to learn a model that _adaptively_ determines an early exit point aligned with the video’s length and complexity. 

More closely related to our work are methods that learn early exit policies for adaptively stopping inference in a streaming video when the recognition backbone makes a correct prediction, thereby aiming to achieve high accuracy while saving on inference cost [16, 24, 73–75, 78]. While some methods [73, 74] use simple heuristics like making the exit decision by comparing the prediction confidence [73] or prediction entropy [74, 75] against a pre-defined threshold, FrameExit [24] trains an exit policy in a supervised manner using exit pseudo-labels generated by comparing the recognition loss against video-progress-dependent thresholds during training. Some approaches [16,78] also use reinforcement learning (RL) to train exit policies with both dense rewards [78] that encourage an exit when there is no further potential for improvement in the prediction confidence for the target class, and sparse rewards [16] that not only incentivize maximizing the

<!-- Page 5 -->

MistExit 5 

target prediction confidence at the point of exit but also punish the model for consuming too many frames. 

Different from all early exit methods, we focus on achieving early exit for mistake detection in procedural videos and we do so by learning an RL-based exit policy. Our policy design enables the model to continuously refine its estimate of a keystep’s correctness by temporally aggregating visual information together with initial mistake estimates from the detector. Combined with an RL reward that promotes improving detection quality over time while encouraging early and accurate exits, this design leads to more stable training on longer and more complex episodes and substantially outperforms existing RL-based alternatives. 

# **3 Early mistake detection task** 

We introduce a new task: early detection of mistakes in procedural videos. In this task, the goal is to train a policy that operates on a streaming video of a keystep in a procedural activity ( _e.g_ ., a chef `whisking eggs` when preparing an omelette, a mechanic `jacking up a car` when fixing a flat tire) and intelligently decides _how much_ of the video to observe before exiting (stopping inference), such that the observed length is _very low_ compared to the full length of the video, while also ensuring a mistake detection model _accurately_ detects any mistakes in the video. Using visual inputs, potentially alongside the mistake detector’s predictions, the policy must infer whether sufficient evidence has been gathered to determine the step’s correctness and accordingly decide whether it is a good time to exit. 

_Task definition._ Formally, we consider a procedural video _V_ in a streaming setting. _V_ consists of a sequence of _N_ video clips<sup>1</sup> , such that _V_ = [ _V_ 1 _, . . . , VN_ ]. Each clip _Vi_ corresponds to a keystep in the procedural activity shown in _V_ and has length _Ti_ . Clip _Vi_ streams RGB frames at the rate of _f_ frames per second, such that _Ii_<sup>_t_ˆdenotestheimageframeattime</sup><sup>_t_and</sup><sup>_t_ˆ =</sup><sup>_⌊t ∗f⌋_providestheframe</sup> index for time _t_ . Here, 0 _≤ t ≤ Ti_ and _⌊y⌋_ indicates rounding down _y_ . 

In this task, we aim to train a model comprising a mistake detector _D_ and an exit policy _π_ . Given a streaming clip _Vi_ , the policy _π_ must take an action _a_<sup>_t_</sup> _i_<sup>_∈A_</sup> at each time _t_ , where _A_ = _{Continue, Exit_ - _mistake, Exit_ - _correct}_ denotes the action space. _Vi_ keeps producing image frames until the policy decides to _Exit_ — where _Exit_ - _mistake_ and _Exit_ - _correct_ correspond to stopping inference with the model’s final prediction for the clip being _mistake_ or _correct_ , respectively—or until _Vi_ reaches its end. 

Let _Ei_ denote this end point—natural or policy-induced—of the image stream. At any time _t_ before the end point _Ei_ , the mistake detector _D_ takes the sequence of _K_ most recent frames, _Si_<sup>_t_,suchthat</sup><sup>_S_</sup> _i_<sup>_t_= [</sup><sup>_I_</sup> _i_<sup>_t_ˆ</sup><sup>_−K_+1</sup> _, . . . , Ii_<sup>_t_ˆ],andproducesan</sup> estimate _M_<sup>˜</sup> _i_<sup>_t_ofthemistakelabel</sup><sup>_Mi_—0foramistakeand1forcorrect—for</sup> _Vi_ . _Mi_ indicates if the keystep corresponding to _Vi_ is being done correctly or not, and provides the policy with an initial estimate of the step’s correctness. 

> 1 We assume pre-segmented keysteps, as modern action detection models [2,69,85] can robustly estimate keystep start and end times.

<!-- Page 6 -->

6 Majumder et al. 


![](assets/057/paper-0006-01.png)


<!-- Start of picture text -->
Mistake Detector 𝒟 s !"#&( s !"#&' s !"#&) 𝑀#!#<br>Transformer<br>𝑠 !"#–%&( 𝑠 !"#–%&' 𝑠 !"# 𝑧 ( 𝑧 ' 𝑧 ) 𝑧 )&(<br>CNN CNN CNN All-zero features for future anticipation<br>and mistake prediction<br>𝐼!"#$%&( 𝐼!"#$%&' 𝐼!"# Exit Policy 𝜋 𝑇! 𝑀! 𝑀#!#<br>Reward Function<br>Dense Reward: ̈𝑀!"#$ 𝑀! −̈ 𝑀!" 𝑀!<br>CNN 𝑚!# Critic Sparse Reward:Time Penalty: 𝟏1/𝑇𝑎!"! ∈{𝐸−𝑚, 𝐸−𝑐} ∗𝟏 ℰ 𝑎!" = 𝑀!<br>Detector 𝑀#!# CNN 𝑜!# 𝑝!# ℎ#$(GRUℎ# 𝑔!# Actor 𝑎!# Continue/ExitStreaming Environment<br>Output<br><!-- End of picture text -->

**Fig. 2:** Our MistExit model for early mistake detection has two components: 1) a mistake detector _D_ (top), and 2) an exit policy _π_ (bottom). At each timestep in a streaming keystep clip, _D_ processes recent frames to predict the keystep’s mistake label and anticipate future features, improving the mistake detection quality. The policy _π_ takes the detector’s estimate and the latest frame, aggregates them over time, and decides when to exit. We train _π_ with a novel reward that encourages improving detection quality over time while promoting early and accurate exits. 

Given the visual frames and the mistake detector’s predictions, the policy must intelligently decide when to exit, such that the resulting end point _Ei_ occurs very early vis-a-vis the full clip length, _i.e_ . _Ei ≪ Ti_ , while its final prediction, as extracted from its action at the end point, matches the mistake label. That is, _E_ ( _a_<sup>_E_</sup> _i_<sup>) =</sup><sup>_Mi_,where</sup><sup>_E_extractstheclip’spredictedcorrectnesstypefroman</sup><sup>_Exit_</sup> action. 

Succeeding at this task requires a strong synergy between the exit policy and the mistake detector. The policy must reason from visual inputs—potentially alongside the detector’s predictions—about how far the keystep has progressed and whether sufficient evidence has been gathered for reliable mistake detection. In turn, the mistake detector must produce accurate estimates early in the streaming clip so that the policy can make prompt exit decisions. We evaluate the resulting performance–efficiency trade-off by measuring both the detection accuracy at the exit point and the fraction of the clip consumed (cf. Sec. 5.1). 

# **4 Approach** 

We pose our early mistake detection task as a reinforcement learning (RL) problem, and propose our **MistExit** model to solve the task. Our model has two key components: **1)** a mistake detector _D_ , and **2)** an exit policy _π_ . Given a streaming clip corresponding to a keystep in an instructional video, the mistake detector determines whether the step is correct or erroneous by not only leveraging recently observed frames to detect mistakes in the parts of the clip observed so far but also anticipating future visual features. Anticipation lets the model infer if the step can lead to a mistake in the _future_ ( _e.g_ ., vigorously beating eggs in a

<!-- Page 7 -->

MistExit 7 

small bowl may indicate a future spillover, taking off a tire before jacking up the car may damage the wheel hub), so that it can better facilitate early exits. 

Conditioned on the detector’s latest prediction and the current frame from the stream—aggregated over time—the policy sequentially decides whether to continue observing or to exit. On the one hand, the detector’s confidence scores provide an explicit signal of its current prediction uncertainty to the policy, guiding it to either gather additional evidence or rely on accumulated predictions from the past for immediate termination. On the other hand, the visual frames observed so far, together with the detector’s initial estimates, enable the policy to cross-check the visual evidence with the detector outputs and assess whether the detector’s estimates are reliable enough to be used in the decision making, especially when the estimtes are high-confidence. See Fig. 2. Next, we describe these two components in detail. 

## **4.1 Mistake detector** **_D_** 

Our mistake detector _D_ comprises a transformer encoder [19, 66] that takes as input a sequence of the most recently observed frames and predicts both an estimate of the keystep’s binary mistake label and the visual features for a sequence of future frames. By predicting the features for future frames, _D_ learns to anticipate the future and consequently can better model if a keystep is likely to end up being a mistake or not. This helps the policy to make even earlier exits while also ensuring improved mistake detection accuracy, as we show in results. 

Specifically, we first use a CNN encoder [7,44] to project the frame sequence _Si_<sup>_t_(cf.Sec.3)intoavisualfeaturesequence</sup><sup>_st_</sup> _i_<sup>,suchthat</sup><sup>_st_</sup> _i_<sup>= [</sup><sup>_st_</sup> _i_<sup>ˆ</sup><sup>_−K_+1</sup> _, . . . , s_<sup>_t_</sup> _i_<sup>ˆ]</sup> (cf. Sec. 3). Next, we produce a sequence of _L_ + 1 all-zero features, _z_ , such that first _L_ entries correspond to the features for the future frames that _D_ anticipates, and the last feature is the feature whose output will be used for estimating the mistake label. We then concatenate _s_<sup>_t_</sup> _i_<sup>and</sup><sup>_z_intoasinglefeature</sup> sequence _d_<sup>_t_</sup> _i_<sup>= [</sup><sup>_st_</sup> _i_<sup>_, z_].Wefurtheraddtoeachfeatureentryin</sup><sup>_dt_</sup> _i_<sup>theappropriate</sup> sinusoidal positional embeddings [66] and a learnable modality embedding [46,48] to distinguish among three different feature types: one for all features in _s_<sup>_t_</sup> _i_<sup>,one</sup> for the first _L_ features in _z_ , corresponding to the anticipated features, and one for the last feature in _z_ , which corresponds to the feature that is mapped to the mistake logits. 

Next, we aggregate _d_<sup>_t_</sup> _i_<sup>using transformer encoder layers [19,42,66,83] and store</sup> the last _L_ + 1 output features in a sequence _d_<sup>¯</sup><sup>_t_</sup> _i_<sup>.Finally,wetransformthefirst</sup><sup>_L_</sup> entries and the last entry in _d_<sup>¯</sup><sup>_t_</sup> _i_<sup>usingseparateMLPstoobtaintheestimates</sup><sup>_s_˜</sup><sup>_t_</sup> _i_ for the anticipated features, _s_ ¯<sup>_t_</sup> _i_<sup>= [</sup><sup>_st_</sup> _i_<sup>ˆ+1</sup> _, . . . , s_<sup>_t_</sup> _i_<sup>ˆ+</sup><sup>_L_</sup> ], and the logits _M_<sup>˜</sup> _i_<sup>_t_forbinary</sup> mistake classification. 

## **4.2 Exit policy** **_π_** 

Our second model component is our exit policy _π_ that takes the latest visual frames from the streaming clip and the predictions from the mistake detector, aggregates these inputs over time, and actively decides when to stop observing further frames. Specifically, for a clip _Vi_ , it uses the visual cues and detection

<!-- Page 8 -->

8 Majumder et al. 

scores to predict a sequence of actions _a_<sup>_t_</sup> _i_<sup>thatleadstoanaccuratepredictionof</sup> the keystep’s correctness at the exit point _Ei_ , while keeping the value of _Ei_ as low as possible (cf. Sec. 3). The policy comprises two main modules: 1) an input encoder, and 2) a policy network. 

_Inputs and encoding._ At every time _t_ in a streaming video clip _Vi_ , the exit policy receives a visual observation _Oi_<sup>_t_,alongwiththelatestpredictions</sup> _M_<sup>˜</sup> _i_<sup>_t_fromthe</sup> mistake detector. _Oi_<sup>_t_comprisesthelatestframe</sup><sup>_I_</sup> _i_<sup>_t_ˆfromthestream(cf.Sec.3).</sup> The visual input _Oi_<sup>_t_,coupledwithcuesfromthetemporallyaggregatedpast</sup> inputs _Oi_<sup>_<t_,enablesthemodeltoinferthecurrentstageoftheactivity—earlyor</sup> late—and to determine whether the frames observed thus far provide sufficient information _M_ ˜ _i_<sup>_t_directly inform the model of the detector’s prediction and its confidence at the</sup> to assess the correctness of the keystep. The mistake detection scores present time. The policy accumulates these estimates along with visual evidence over time and determines whether sufficient information has been gathered to decide the step’s correctness, adjusting its exit point accordingly. 

To encode the visual observation _Oi_<sup>_t_,weuseaCNN[7, 44]encoderand</sup> produce a 1D embedding _o_<sup>_t_</sup> _i_<sup>.Forthebinarymistakedetectionscores</sup> _M_<sup>˜</sup> _i_<sup>_t_,wefirst</sup> normalize them and obtain detection confidences by passing through a softmax layer and then encode the confidences _M_<sup>¨</sup> _i_<sup>_t_usinganMLPencodertoproduce</sup> another 1D embedding _m_<sup>_t_</sup> _i_<sup>.Next,weconcatenate</sup><sup>_ot_</sup> _i_<sup>and</sup><sup>_mt_</sup> _i_<sup>alongthechannel</sup> dimension to produce our policy embedding _p_<sup>_t_</sup> _i_<sup>,suchthat</sup><sup>_pt_</sup> _i_<sup>= [</sup><sup>_ot_</sup> _i_<sup>_, mt_</sup> _i_<sup>].</sup> 

_Policy network._ The policy network begins with a gated recurrent unit (GRU) [9, 10] that uses the policy embedding _p_<sup>_t_</sup> _i_<sup>andthepolicy’saggregatedhistoryof</sup> states _h_<sup>_t_</sup> _i_<sup>_−_1</sup> to produce an updated history _h_<sup>_t_</sup> _i_<sup>andarepresentationofthecurrent</sup> state, _gi_<sup>_t_.Next,anactor-criticmoduletakes</sup><sup>_g_</sup> _i_<sup>_t_and</sup><sup>_ht_</sup> _i_<sup>_−_1</sup> as inputs, and generates the policy distribution _πθ_ ( _a_<sup>_t_</sup> _i_<sup>_|g_</sup> _i_<sup>_t, ht_</sup> _i_<sup>_−_1</sup> ) and the value of the state, _Vθ_ ( _gi_<sup>_t, ht_</sup> _i_<sup>_−_1</sup> ), where _θ_ denotes the policy parameters. Finally, the policy samples an action _a_<sup>_t_</sup> _i_<sup>fromthepolicydistribution</sup><sup>_πθ_,therebydecidingto</sup><sup>_Continue_(cf.Sec.3)</sup> consuming frames or stop further inference and _Exit_ the stream. If the policy decides to exit, the model’s final prediction is determined by the chosen exit action–correct for _Exit_ - _correct_ and mistake for _Exit_ - _mistake_ . Importantly, the two _Exit_ actions enables the policy to temporally aggregate the detector’s initial predictions, which might be noisy due to the fixed-length observation window, and generate a more reliable and accurate final prediction at the exit point, guided by our reward function (Sec. 4.3). 

## **4.3 Model training** 

_Mistake detector training._ We set the training loss _L_<sup>_D_</sup> for our mistake detector _D_ to a weighted sum of the mistake detection loss _L_<sup>_M_</sup> and a future anticipation loss _L_<sup>_F_</sup> , such that 


![](assets/057/paper-0008-07.png)


Here, _L_<sup>_M_</sup> is the cross-entropy loss ( _CE_ ) between the mistake label _Mi_ (cf. Sec. 4.1) and the detector’s estimate of the same, _M_<sup>˜</sup> _i_<sup>_t_(cf.Sec.4.2),suchthat</sup>

<!-- Page 9 -->

MistExit 9 


![](assets/057/paper-0009-01.png)


Our future anticipation loss _L_<sup>_F_</sup> is the average L1 loss between the ground-truth future feature sequence _s_ ¯<sup>_t_</sup> _i_<sup>anditsestimate</sup><sup>_s_˜</sup><sup>_t_</sup> _i_<sup>,suchthat</sup> 


![](assets/057/paper-0009-03.png)


and _w_ 1 and _w_ 2 are the weights on the two losses, respectively. We set _w_ 1 and _w_ 2 on the basis of a disjoint validation split. 

_Policy training._ We propose a novel reward function to train our exit policy _π_ : 


![](assets/057/paper-0009-06.png)


Here, _M_<sup>¨</sup> _i_<sup>_t_denotesthedetector’spredictedconfidencescoresobtainedbyapplying</sup> a softmax normalization to _M_<sup>˜</sup> _i_<sup>_t_(cf.Sec.4.1).</sup><sup>_Mi_representstheground-truth</sup> mistake label for the keystep (cf. Sec. 3). We use _E_ - _m_ and _E_ - _c_ to denote the _Exit_ - _mistake_ and _Exit_ - _correct_ actions, respectively. Finally, _E_ extracts the clip’s predicted correctness type from the policy’s action at the exit time. In case the policy doesn’t exit, we use the detector’s final prediction as the mistake estimate. 

Our reward has three terms: 1) a dense reward, 2) a sparse reward, and 3) a penalty. We set the dense reward to the improvement in the prediction confidence _M_ ¨ _i_ [ _Mi_ ] for the mistake label from time _t_ to _t_ + 1, thereby incentivizing the policy to let the detector continuously improve its estimate of the step’s correctness over time. Moreover, our dense reward better handles long-horizon episodes arising from long and complex keysteps, improving RL training convergence. 

We additionally provide the policy with a sparse reward when it chooses to exit and its predicted clip type—derived from its action—matches the ground-truth label. This encourages the policy to refine potentially unreliable intermediate estimates from the mistake detector and produce a high-quality prediction at the exit point. Our last term is a time penalty that discourages late exits by the policy. Importantly, instead of using a fixed penalty for all clips, we set it to the inverse of the clip length _Ti_ (cf. Sec. 3). This allows the detector to consume more frames for determining the step’s correctness if the clip is longer and hence, possibly more challenging. Finally, we weight the sparse reward, the dense reward and the time penalty with _v_ 1, _v_ 2 and _v_ 3, respectively, where the weights are chosen using a held-out validation set. 

_Training curriculum._ We pre-train our mistake detector _D_ without an exit policy by first randomly selecting a clip _Vi_ and then randomly sampling a time _t_ in the

<!-- Page 10 -->

10 Majumder et al. 

clip. Next, we train our policy _π_ while freezing the pre-trained detector. Since our reward depends on the mistake detector outputs, freezing the detector during policy training ensures stationary rewards and improves convergence. 

# **5 Experiments** 

Here, we give an overview of setup details and then provide results. 

## **5.1 Experimental setup** 

_Datasets._ We evaluate our model on two instructional video datasets: CaptainCook4D (CC4D) [54] and Assembly101 [61]. Whereas CC4D comprises cooking videos recorded in real-world kitchens, Assembly101 contains videos of assembling and disassembling toy vehicles. The two datasets lets us evaluate diverse activity scenarios. In both datasets, each video consists of a sequence of keysteps, where each keystep may be performed either correctly or incorrectly. While both datasets provide two high-level mistake labels— _correct_ and _mistake_ , Assembly101 includes an additional category in its mistake taxonomy, _correction_ , which we treat as a mistake in our experiments. The video segments corresponding to individual keysteps serve as the streaming clips in our task (cf. Sec. 3). We construct train/val/test splits containing 2624/200/1037 clips for CC4D and 2726/200/343 clips for Assembly101, respectively, ensuring that clips across different splits are drawn from disjoint videos. This amounts to a total of 58.3 and 14.5 hours of video for CC4D and Assembly101, respectively. We set the frame rate to 2 fps for all videos. 

_Implementation._ We modify the action recognition module of the state-of-the-art PREGO [19] model to enable future anticipation and use it as our mistake detector. Specifically, given a streaming clip and any point in time in the clip, our mistake detector _D_ takes as inputs the visual features for the _K_ = 5 most recent frames and outputs an estimate of the features for the next _L_ = 20 frames, in addition to predicting if the clip is a mistake or not. We train the detector until convergence by setting the weights in its training loss (cf. Sec. 4.3) to _w_ 1 = 1 and _w_ 2 = 10<sup>_−_1</sup> , and using the AdamW [45] optimizer with a batch size of 128, an initial learning rate of 10<sup>_−_6</sup> , and a weight decay of 5 _×_ 10<sup>_−_2</sup> . We use PPO [59] to train our exit policy _π_ for a total of 42 million policy steps with 4 PPO updates after every 40 steps. To this end, we set the weights of our reward components (cf. Sec. 4.3) to _v_ 1 = 10<sup>_−_1</sup> and _v_ 2 = _v_ 3 = 1 and use the Adam [37] optimizer with a batch size of 8 and an initial learning rate of 10<sup>_−_4</sup> . See Supp. (Sec. 7.3) for more details. 

- _Baselines._ We compare against the following baselines and SOTA methods: **– Random:** a policy that randomly chooses an action from action space _A_ 

- **AdaFocusV2 [73]:** a policy that exits when the confidence of the mistake detector’s predicted class exceeds a threshold of 0.75. We also evaluate an enhanced version of this model, AdaFocusV2++, where the exit decision uses

<!-- Page 11 -->

MistExit 11 

the mean confidence over the past _P_ predictions, with _P_ = 5 for CC4D and _P_ = 3 for Assembly101. 

- **AdaFocusV3 [74]:** policy that exits when the entropy of the mistake detector’s predictions is below 0.1 for CC4D and 0.5 for Assembly101. Similar to AdaFocusV2++, we also evaluate AdaFocusV3++, which computes the mean entropy over the past _P_ predictions, with _P_ = 3 for CC4D and _P_ = 5 for Assembly101. 

- **FrameExit [24]:** a learned baseline that produces exit pseudo-labels by checking the mistake detector’s prediction loss against a time-dependent threshold— lower for earlier frames and higher for later ones—and trains a policy via supervised learning using these pseudo-labels. 

- **FastForward [16]:** another learned baseline that trains an RL policy using a reward that encourages the detector to continuously improve its predicted confidence of the target class over time while simultaneously discouraging late exits through a fixed penalty of 10<sup>_−_2</sup> per frame consumed. 

- **AdaFrame [78]:** an RL baseline that trains an actor-critic network with a dense reward defined as the improvement, if any, in the detector’s predicted confidence for the target class relative to its previous best confidence, and stops inference when the value estimate produced by the critic falls below the previous maximum predicted value by at least 0.7 twice in an episode. For fair comparison, all models use the same mistake detection backbone [19] 

- and are trained and validated using our train and val splits. Importantly, all three learned models were originally designed for skip-forward/backward video recognition with _offline_ video access; we adapt them to our streaming setup by equipping them with our action space. We select policy-specific hyperparameters—such as the threshold for the AdaFocus family and the time penalty for FastForward—based on validation performance. 

_Evaluation metrics._ Following existing early recognition works [6, 41, 57], we assess our model along two dimensions: **1)** mistake detection accuracy, and **2)** earliness of exit. We capture this accuracy vs. efficiency trade-off through scatter plots (shown below), where stronger models achieve higher accuracy while exiting earlier. To gauge accuracy, we use the **average precision** (AP) metric, which measures the area under the precision vs. recall curve. To measure model efficiency, we compute the mean **observation ratio** (OR) [6,41,57] across all test clips, where each exit time is normalized by the corresponding clip length and then averaged over all clips. 

## **5.2 Early mistake detection results** 

Fig. 3 shows the early detection quality of all models on both CaptainCook4D (CC4D) [54] (Fig. 3a) and Assembly101 [61] (Fig. 3b). Employing a naive exit heuristic, such as Random, is insufficient for achieving high-quality and efficient mistake detection, highlighting the challenging nature of our early mistake detection task. In comparison, the AdaFocus [73,74] policy family, which leverages prediction uncertainty to guide exit decisions, improves detection accuracy while

<!-- Page 12 -->

12 Majumder et al. 


![](assets/057/paper-0012-01.png)


<!-- Start of picture text -->
58<br>55<br>56<br>Random: OR = 4.5, AP = 54.1 54 Random: OR = 12.4, AP = 54.8<br>50 AdaFocusV2: OR = 15.2, AP = 54.5 AdaFocusV2: OR = 15.9, AP = 55.0<br>AdaFocusV2++: OR = 2.3, AP = 55.5 52 AdaFocusV2++: OR = 17.5, AP = 54.4<br>AdaFocusV3: OR = 2.9, AP = 56.2 AdaFocusV3: OR = 22.3, AP = 54.4<br>45 AdaFocusV3++: OR = 3.2, AP = 56.2 50 AdaFocusV3++: OR = 14.3, AP = 53.5<br>FrameExit: OR = 3.7, AP = 53.0 FrameExit: OR = 9.8, AP = 54.7<br>AdaFrame: OR = 7.1, AP = 57.2 48 AdaFrame: OR = 38.5, AP = 57.0<br>40 FastForward: OR = 3.8, AP = 56.1 FastForward: OR = 21.3, AP = 57.0<br>Ours : OR = 3.0, AP = 57.4 46 Ours : OR = 9.2, AP = 57.0<br>2.0% 4.0% 6.0% 8.0% 10.0% 12.0% 14.0% 10% 20% 30% 40% 50% 60%<br>Observation ratio (OR) % Observation ratio (OR) %<br>(a) CaptainCook4D [54] (b) Assembly101 [61]<br>Average precision (AP) % Average precision (AP) %<br><!-- End of picture text -->

**Fig. 3:** Early mistake detection results. Higher AP, lower OR is better. 

enabling earlier exits, particularly on CC4D. This suggests that the mistake detector’s predictions provide useful cues for determining the appropriate exit point. The FrameExit [24] further improves performance, especially on Assembly101, demonstrating the usefulness of learning an exit policy. Both RL baselines, AdaFrame [78] and FastForward [16], significantly improve detection accuracy compared to FrameExit, indicating that policies trained with RL, rather than supervised learning, can better adapt their exit decisions to the nature and complexity of the video. 

Our model outperforms all baselines on CC4D while also improving efficiency over most. On Assembly101, our model ranks again among the top performers while achieving significantly better efficiency. Notably, our gains over the other RL-based counterparts highlight the benefits of our superior reward formulation and the augmented input space, which includes the mistake detector’s prediction scores alongside the RGB frames. Moreover, comparing our performance with the FrameExit method illustrates that our well-designed RL policy not only substantially boosts the mistake detection accuracy but also enables earlier exits—identifying early segments of a streaming clip that are indicative of the keystep’s correctness. Overall, our approach consistently delivers a stronger accuracy-efficiency trade-off than existing methods. 

## **5.3 Model analysis** 

_Ablations._ In Fig. 4a, we show the results from ablating our model components. Disabling future anticipation in the mistake detector leads to a substantial drop in detection accuracy. This indicates that future anticipation (one of our contributions) allows the model to delay exit slightly to locate informative clip segments that yield more reliable mistake predictions. 

Removing visual inputs from the policy drastically increases the observation ratio, highlighting the importance of visual information for determining when sufficient evidence has been gathered. In particular, visual cues allow the policy to reason about the stage of the activity and whether it is too early to exit, while also cross-checking the visual evidence with the detector’s predictions to assess whether the detector’s estimates are reliable enough to trigger an immediate

<!-- Page 13 -->

MistExit 13 

exit. Removing access to the mistake detector’s logits also degrades performance, indicating that our model effectively leverages these initial estimates to build an implicit representation of the step’s correctness and adjust its exit point accordingly. Using a 


![](assets/057/paper-0013-02.png)


<!-- Start of picture text -->
58<br>56<br>54<br>Ours (D) w/o future prediction: OR = 2.7, AP = 56.6<br>52 Ours ( ) w/o vision: OR = 4.0, AP = 56.3<br>50 Ours ( ) w/o mistake logits: OR = 3.1, AP = 56.9<br>Ours ( ) w/o clip-aware time penalty: OR = 3.1, AP = 56.6<br>48 Ours ( ) w/o time penalty: OR = 3.8, AP = 57.1<br>46 Ours ( ) w/o dense reward: OR = 2.8, AP = 55.6<br>Ours ( ) w/o sparse reward: OR = 2.9, AP = 56.0<br>44 Ours : OR = 3.0, AP = 57.4<br>2.70% 3.00% 3.30% 3.60% 3.90%<br>Observation ratio (OR) %<br>(a) Model ablations<br>Average precision (AP) %<br><!-- End of picture text -->


![](assets/057/paper-0013-03.png)


<!-- Start of picture text -->
58.0<br>L = 5: OR = 2.9, AP = 56.1<br>L = 5: OR = 2.4, AP = 56.0<br>57.5 L = 40: OR = 2.6, AP = 56.3<br>Ours (L = 20) : OR = 3.0, AP = 57.4<br>57.0<br>56.5<br>56.0<br>55.5<br>2.40% 2.50% 2.60% 2.70% 2.80% 2.90% 3.00%<br>Observation ratio (OR) %<br>(b) Performance vs. detector anticipation length<br>Average precision (AP) %<br><!-- End of picture text -->

**Fig. 4: Left:** Ablation on larger-scale CaptainCook4D (CC4D) [54]. **Right:** Early mistake detection results on larger-scale CC4D for different lengths ( _L_ ) of the anticipated feature sequence in our mistake detector (Sec. 4.1). Higher AP, lower OR is better for both plots. 

fixed time penalty instead of one conditioned on the clip length also reduces performance, underscoring its role in helping the policy determine an appropriate exit point based on the length and complexity of the clip. Removing the time penalty also degrades performance, particularly policy efficiency, highlighting its role in encouraging early exits. Furthermore, because our task involves long horizons arising from variable clip lengths, the dense reward is critical for stable RL training, without which, the detection accuracy drops significantly. Removing the dense reward also affects detection accuracy, as it provides an important learning signal that captures the core objective of our task—maximizing detection accuracy at the point of exit. 

_Analysis of length of anticipated frame sequence L._ In Sec. 5 in main, we evaluated our method with the length of the anticipated future feature sequence in the mistake detector (Sec. 4.1) set to _L_ = 20 (Sec. 5.1). Here, we analyze the impact of _L_ on our model performance. Fig. 4b presents the results of this analysis. We observe that setting _L_ = 20 significantly improves mistake detection performance compared to variants with other values of _L_ , while only marginally increasing the amount of video consumed on average. This suggests that with _L_ = 20, our model is better able to anticipate how the step will evolve and leverage this information to improve mistake detection accuracy, even though doing so may require slightly more visual evidence. 

_Qualitative examples._ In Fig. 5, we show some success cases from CaptainCook4D [54] (top 2 rows) and Assembly101 [61] (bottom 2 rows). Notably, our

<!-- Page 14 -->

14 Majumder et al. 


![](assets/057/paper-0014-01.png)


<!-- Start of picture text -->
CaptainCook4D<br>Exit<br>Exit<br>Assembly101<br>Exit<br>Exit<br>Mistake<br>Correct<br>Mistake<br>Correct<br><!-- End of picture text -->

**Fig. 5:** Our model’s successful predictions on CaptainCook4D [54] (top 2 rows) and Assembly101 [61] (bottom 2 rows). Our model correctly detects mistakes by identifying cues such as incorrect technique—for example, the knife positioned to produce an abnormally thin slice in row 1—and signs of struggle by the actor, such as repeatedly moving the cabin back and forth in row 3. It can also correctly predict that a step will end in a successful execution by leveraging cues that indicate the correctness of the remaining portion of the step—for instance, a closed pepper container in row 2 may suggest that the actor will not add extra pepper to the eggs, while a correctly installed wheel in row 4 may indicate that the remaining wheels will also be installed correctly. 

model can detect incorrect techniques and flag mistakes early by anticipating that the step will ultimately result in an error. _E.g_ ., in row 1, the actor begins by holding the knife too close to the base of the bun, resulting in an abnormally thin cut, and our model successfully picks up on this cue. Furthermore, our model can detect signs of struggle and repeated actions by the actor, which often indicate that the step will be labeled as a mistake. _E.g_ ., in row 3, the actor unsuccessfully attempts to attach the cabin to the chassis and moves it back and forth multiple times. Our model likely identifies this repeated motion and infers that the actor will fail to successfully complete the step. 

In Fig. 6, we show qualitative examples that depict our model’s frame-level attention scores at the exit point for CaptainCook4D [54] (top) and Assembly101 [61] (bottom). We observe that the model consistently assigns the highest attention weights to frames that contain strong visual cues about whether the step will ultimately be executed correctly. For instance, in the CaptainCook4D example, the model places the most attention on the frame where the knife creates an initial cut on the bagel. This early cut reveals that the slice is likely to follow that trajectory and become excessively thin, providing an early visual signal that the step will end in a mistake. In the Assembly101 example, the base aligns well with the chassis in the third frame, indicating that the step is being

<!-- Page 15 -->

![](assets/057/paper-0015-00.png)


<!-- Start of picture text -->
MistExit 15<br>CaptainCook4D<br>Score: 0.06 Score: 0.08 Score: 0.21 Score: 0.35 Score: 0.30<br>Frame 1 Frame 2 Frame 3 Frame 4 Frame 5<br>Most attended<br>Assembly101<br>Score: 0.14 Score: 0.05 Score: 0.28 Score: 0.24 Score: 0.27<br>Frame 1 Frame 2 Frame 3 Frame 4 Frame 5<br>Most attended<br><!-- End of picture text -->

**Fig. 6:** Qualitative examples illustrating our model’s frame-level attention scores at the exit point for CaptainCook4D [54] (top) and Assembly101 [61] (bottom). We observe that the model attends the most to frames that are strongly indicative of whether the step will ultimately be executed correctly or not. For example, in the CaptainCook4D case, the model focuses most on the frame where the knife makes a small cut on the bagel, suggesting that the subsequent slice will follow that cut and become too thin, leading to a mistake. In the Assembly101 example, the base aligns well with the chassis in frame 3, indicating that the step is being executed correctly and leading the model to assign the highest attention to that frame. 

executed correctly and leading the model to assign the highest attention to that frame. Such examples highlight the model’s ability to identify informative frames that provide early evidence about the correctness of the ongoing keystep, while also suggesting its capacity to use these cues to anticipate how the remainder of the step is likely to unfold. 

Finally, our model can also anticipate that a step will end in a successful execution by leveraging visual cues that indicate the correctness of the remaining portion. For instance, in row 2, the pepper container is already closed after seasoning the eggs, suggesting that the actor is unlikely to add excess pepper. By identifying such cues early in the streaming clip, the model can infer the (likely) eventual correctness of the step without needing to observe the entire sequence. 

We also observe a common failure mode of our model. It sometimes predicts a step as correct when the observed portion of the clip shows a repetitive action being performed correctly, but the actor begins executing the action incorrectly after the model has already exited. Additionally, the model may incorrectly flag a mistake when a step appears to be performed clumsily but must be executed in that manner due to the nature of the action or the objects involved. In such cases, the model predicts a mistake even though the step is executed correctly. These failures arise when the observed portion of the clip is not representative of the remainder of the step containing non-standard object and action dynamics, and represents well the “no free lunch" principle of trying to skip seeing parts of the video while still confidently anticipating its results.

<!-- Page 16 -->

16 Majumder et al. 

See Supp. video (Sec. 7.1) for more qualitative examples. 

# **6 Conclusion** 

We introduced the task of early mistake detection in streaming videos, where the goal is to determine the correctness of a keystep in a procedural activity while observing only a minimal fraction of the video. To address this challenge, we proposed a framework that combines a future-anticipating mistake detector with a reinforcement learning policy that adaptively decides when to stop observing and produce a prediction. Experiments on two diverse real-world procedural video datasets show that our approach achieves superior mistake detection accuracy while substantially reducing the amount of video that must be observed compared to prior methods. In future work, we plan to extend our model to handle openworld mistakes, including fine-grained mistake classification.

<!-- Page 17 -->

MistExit 17 

# **References** 

1. Abrash, M.: Creating the future: Augmented reality, the next human-machine interface. In: 2021 IEEE International Electron Devices Meeting (IEDM). pp. 1–11 (2021). `https://doi.org/10.1109/IEDM19574.2021.9720526` 

2. An, J., Kang, H., Han, S.H., Yang, M.H., Kim, S.J.: Miniroad: Minimal rnn framework for online action detection. In: Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV). pp. 8377–8387 (October 2023) 

3. Bahl, S., Mendonca, R., Chen, L., Jain, U., Pathak, D.: Affordances from human videos as a versatile representation for robotics. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 13778–13790 (2023) 

4. Bloom, V., Makris, D., Argyriou, V.: Clustered spatio-temporal manifolds for online action recognition. In: 2014 22nd International Conference on Pattern Recognition. pp. 3963–3968 (2014). `https://doi.org/10.1109/ICPR.2014.679` 

5. Cai, Y., Li, H., Hu, J.F., Zheng, W.S.: Action knowledge transfer for action prediction with partial videos. In: Proceedings of the Thirty-Third AAAI Conference on Artificial Intelligence and Thirty-First Innovative Applications of Artificial Intelligence Conference and Ninth AAAI Symposium on Educational Advances in Artificial Intelligence. AAAI’19/IAAI’19/EAAI’19, AAAI Press (2019). `https: //doi.org/10.1609/aaai.v33i01.33018118` , `https://doi.org/10.1609/aaai. v33i01.33018118` 

6. Cao, Y., Barrett, D., Barbu, A., Narayanaswamy, S., Yu, H., Michaux, A., Lin, Y., Dickinson, S., Siskind, J.M., Wang, S.: Recognize human activities from partially observed videos. In: 2013 IEEE Conference on Computer Vision and Pattern Recognition. pp. 2658–2665 (2013). `https://doi.org/10.1109/CVPR.2013.343` 

7. Carreira, J., Zisserman, A.: Quo vadis, action recognition? a new model and the kinetics dataset. In: proceedings of the IEEE Conference on Computer Vision and Pattern Recognition. pp. 6299–6308 (2017) 

8. Chi, S., Chi, H.G., Huang, Q., Ramani, K.: Infogcn++: Learning representation by predicting the future for online skeleton-based action recognition. IEEE Transactions on Pattern Analysis and Machine Intelligence (2024) 

9. Cho, K., Van Merriënboer, B., Gulçehre, Ç., Bahdanau, D., Bougares, F., Schwenk, H., Bengio, Y.: Learning phrase representations using rnn encoder–decoder for statistical machine translation. In: Proceedings of the 2014 conference on empirical methods in natural language processing (EMNLP). pp. 1724–1734 (2014) 

10. Chung, J., Gulcehre, C., Cho, K., Bengio, Y.: Empirical evaluation of gated recurrent neural networks on sequence modeling. arXiv preprint arXiv:1412.3555 (2014) 

11. De Geest, R., Gavves, E., Ghodrati, A., Li, Z., Snoek, C., Tuytelaars, T.: Online action detection. In: European Conference on Computer Vision. pp. 269–284. Springer (2016) 

12. Ding, G., Sener, F., Ma, S., Yao, A.: Every mistake counts in assembly. arXiv preprint arXiv:2307.16453 (2023) 

13. Donahue, G., Elhamifar, E.: Learning to predict activity progress by self-supervised video alignment. In: 2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). pp. 18667–18677 (2024). `https://doi.org/10.1109/ CVPR52733.2024.01766` 

14. Doughty, H., Mayol-Cuevas, W., Damen, D.: The pros and cons: Rank-aware temporal attention for skill determination in long videos. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 7862–7871 (2019)

<!-- Page 18 -->

18 Majumder et al. 

15. Eun, H., Moon, J., Park, J., Jung, C., Kim, C.: Learning to discriminate information for online action detection. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 809–818 (2020) 

16. Fan, H., Xu, Z., Zhu, L., Yan, C., Ge, J., Yang, Y.: Watching a small portion could be as good as watching all: Towards efficient video classification. In: Proceedings of the Twenty-Seventh International Joint Conference on Artificial Intelligence, IJCAI-18. pp. 705–711. International Joint Conferences on Artificial Intelligence Organization (7 2018). `https://doi.org/10.24963/ijcai.2018/98` , `https://doi. org/10.24963/ijcai.2018/98` 

17. Feng, S., Wray, M., Mayol-Cuevas, W.: Evostruggle: A dataset capturing the evolution of struggle across activities and skill levels. arXiv preprint arXiv:2510.01362 (2025) 

18. Fernando, B., Herath, S.: Anticipating human actions by correlating past with the future with jaccard similarity measures. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 13224–13233 (2021) 

19. Flaborea, A., Di Melendugno, G.M.D., Plini, L., Scofano, L., De Matteis, E., Furnari, A., Farinella, G.M., Galasso, F.: Prego: online mistake detection in procedural egocentric videos. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 18483–18492 (2024) 

20. Foo, L.G., Li, T., Rahmani, H., Ke, Q., Liu, J.: Era: Expert retrieval and assembly for early action prediction. In: European Conference on Computer Vision. pp. 670–688. Springer (2022) 

21. Gao, M., Zhou, Y., Xu, R., Socher, R., Xiong, C.: Woad: Weakly supervised online action detection in untrimmed videos. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 1915–1923 (2021) 

22. Ghoddoosian, R., Dwivedi, I., Agarwal, N., Choi, C., Dariush, B.: Weakly-supervised online action segmentation in multi-view instructional videos. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 13780–13790 (2022) 

23. Ghoddoosian, R., Dwivedi, I., Agarwal, N., Dariush, B.: Weakly-supervised action segmentation and unseen error detection in anomalous instructional videos. In: Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV). pp. 10128–10138 (October 2023) 

24. Ghodrati, A., Bejnordi, B.E., Habibian, A.: Frameexit: Conditional early exiting for efficient video recognition. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 15608–15618 (2021) 

25. Grauman, K., Westbury, A., Torresani, L., Kitani, K., Malik, J., Afouras, T., Ashutosh, K., Baiyya, V., Bansal, S., Boote, B., et al.: Ego-exo4d: Understanding skilled human activity from first-and third-person perspectives. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 19383–19400 (2024) 

26. Haneji, Y., Nishimura, T., Kameko, H., Shirai, K., Yoshida, T., Kajimura, K., Yamamoto, K., Cui, T., Nishimoto, T., Mori, S.: Egooops: A dataset for mistake action detection from egocentric videos referring to procedural texts. arXiv preprint arXiv:2410.05343 (2024) 

27. He, K., Zhang, X., Ren, S., Sun, J.: Delving deep into rectifiers: Surpassing humanlevel performance on imagenet classification. In: Proceedings of the IEEE international conference on computer vision. pp. 1026–1034 (2015) 

28. Hoque, R., Huang, P., Yoon, D.J., Sivapurapu, M., Zhang, J.: Egodex: Learning dexterous manipulation from large-scale egocentric video. arXiv preprint arXiv:2505.11709 (2025)

<!-- Page 19 -->

MistExit 19 

29. Hu, J.F., Zheng, W.S., Ma, L., Wang, G., Lai, J., Zhang, J.: Early action prediction by soft regression. IEEE Transactions on Pattern Analysis and Machine Intelligence **41** (11), 2568–2583 (2019). `https://doi.org/10.1109/TPAMI.2018.2863279` 

30. Huang, W.J., Li, Y.M., Xia, Z.W., Tang, Y.M., Lin, K.Y., Hu, J.F., Zheng, W.S.: Modeling multiple normal action representations for error detection in procedural tasks. In: Proceedings of the Computer Vision and Pattern Recognition Conference. pp. 27794–27804 (2025) 

31. Huang, Y., Chen, G., Xu, J., Zhang, M., Yang, L., Pei, B., Zhang, H., Dong, L., Wang, Y., Wang, L., et al.: Egoexolearn: A dataset for bridging asynchronous ego-and exo-centric view of procedural activities in real world. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 22072–22086 (2024) 

32. Huh, M., Xue, Z., Das, U., Ashutosh, K., Grauman, K., Pavel, A.: Vid2coach: Transforming how-to videos into task assistants. In: Proceedings of the 38th Annual ACM Symposium on User Interface Software and Technology. pp. 1–24 (2025) 

33. Jang, Y., Sullivan, B., Ludwig, C., Gilchrist, I.D., Damen, D., Mayol-Cuevas, W.: Epic-tent: An egocentric video dataset for camping tent assembly. In: 2019 IEEE/CVF International Conference on Computer Vision Workshop (ICCVW). pp. 4461–4469 (2019). `https://doi.org/10.1109/ICCVW.2019.00547` 

34. Kang, H., Kim, K., Ko, Y., Kim, S.J.: Cag-qil: Context-aware actionness grouping via q imitation learning for online temporal action localization. In: 2021 IEEE/CVF International Conference on Computer Vision (ICCV). pp. 13709–13718 (2021). `https://doi.org/10.1109/ICCV48922.2021.01347` 

35. Kareer, S., Patel, D., Punamiya, R., Mathur, P., Cheng, S., Wang, C., Hoffman, J., Xu, D.: Egomimic: Scaling imitation learning via egocentric video. In: 2025 IEEE International Conference on Robotics and Automation (ICRA). pp. 13226–13233. IEEE (2025) 

36. Kim, Y.H., Kang, H., Kim, S.J.: A sliding window scheme for online temporal action localization. In: Avidan, S., Brostow, G., Cissé, M., Farinella, G.M., Hassner, T. (eds.) Computer Vision – ECCV 2022. pp. 653–669. Springer Nature Switzerland, Cham (2022) 

37. Kingma, D.P., Ba, J.: Adam: A method for stochastic optimization. arXiv preprint arXiv:1412.6980 (2014) 

38. Kong, Y., Fu, Y.: Max-margin action prediction machine. IEEE Transactions on Pattern Analysis and Machine Intelligence **38** (9), 1844–1858 (2016). `https: //doi.org/10.1109/TPAMI.2015.2491928` 

39. Kong, Y., Kit, D., Fu, Y.: A discriminative model with multiple temporal scales for action prediction. In: Fleet, D., Pajdla, T., Schiele, B., Tuytelaars, T. (eds.) Computer Vision – ECCV 2014. pp. 596–611. Springer International Publishing, Cham (2014) 

40. Kviatkovsky, I., Rivlin, E., Shimshoni, I.: Online action recognition using covariance of shape and motion. Computer Vision and Image Understanding **129** , 15– 26 (2014). `https://doi.org/https://doi.org/10.1016/j.cviu.2014.08.001` , `https://www.sciencedirect.com/science/article/pii/S1077314214001805` , special section: Advances in Discrete Geometry for Computer Imagery 

41. Lan, T., Chen, T.C., Savarese, S.: A hierarchical representation for future action prediction. In: Fleet, D., Pajdla, T., Schiele, B., Tuytelaars, T. (eds.) Computer Vision – ECCV 2014. pp. 689–704. Springer International Publishing, Cham (2014) 

42. Lee, S.P., Lu, Z., Zhang, Z., Hoai, M., Elhamifar, E.: Error detection in egocentric procedural task videos. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). pp. 18655–18666 (June 2024)

<!-- Page 20 -->

- 20 Majumder et al. 

43. Li, K., Hu, J., Fu, Y.: Modeling complex temporal composition of actionlets for activity prediction. In: Fitzgibbon, A., Lazebnik, S., Perona, P., Sato, Y., Schmid, C. (eds.) Computer Vision – ECCV 2012. pp. 286–299. Springer Berlin Heidelberg, Berlin, Heidelberg (2012) 

44. Lin, J., Gan, C., Han, S.: Tsm: Temporal shift module for efficient video understanding. In: Proceedings of the IEEE/CVF international conference on computer vision. pp. 7083–7093 (2019) 

45. Loshchilov, I., Hutter, F.: Decoupled weight decay regularization. arXiv preprint arXiv:1711.05101 (2017) 

46. Majumder, S., Chen, C., Al-Halah, Z., Grauman, K.: Few-shot audio-visual learning of environment acoustics. Advances in Neural Information Processing Systems **35** , 2522–2536 (2022) 

47. Majumder, S., Jiang, H., Moulon, P., Henderson, E., Calamia, P., Grauman, K., Ithapu, V.K.: Chat2map: Efficient scene mapping from multi-ego conversations. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 10554–10564 (2023) 

48. Majumder, S., Nagarajan, T., Al-Halah, Z., Grauman, K.: Switch-a-view: View selection learned from unlabeled in-the-wild videos. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp. 11969–11979 (2025) 

49. Mazzamuto, M., Furnari, A., Sato, Y., Farinella, G.M.: Gazing into missteps: Leveraging eye-gaze for unsupervised mistake detection in egocentric videos of skilled human activities. In: Proceedings of the Computer Vision and Pattern Recognition Conference. pp. 8310–8320 (2025) 

50. Nair, V., Hinton, G.E.: Rectified linear units improve restricted boltzmann machines. In: Proceedings of the 27th International Conference on International Conference on Machine Learning. p. 807–814. ICML’10, Omnipress, Madison, WI, USA (2010) 

51. Pan, Y., Zhang, C., Bertasius, G.: Basket: A large-scale video dataset for fine-grained skill estimation. In: Proceedings of the Computer Vision and Pattern Recognition Conference. pp. 28952–28962 (2025) 

52. Panchal, S., Bhattacharyya, A., Berger, G., Mercier, A., Böhm, C., Dietrichkeit, F., Pourreza, R., Li, X., Madan, P., Lee, M., et al.: What to say and when to say it: Live fitness coaching as a testbed for situated interaction. Advances in Neural Information Processing Systems **37** , 75853–75882 (2024) 

53. Parmar, P., Morris, B.T.: What and how well you performed? a multitask learning approach to action quality assessment. In: Proceedings of the IEEE/CVF conference on computer vision and pattern recognition. pp. 304–313 (2019) 

54. Peddi, R., Arya, S., Challa, B., Pallapothula, L., Vyas, A., Gouripeddi, B., Zhang, Q., Wang, J., Komaragiri, V., Ragan, E., et al.: Captaincook4d: A dataset for understanding errors in procedural activities. Advances in Neural Information Processing Systems **37** , 135626–135679 (2024) 

55. Plini, L., Scofano, L., De Matteis, E., di Melendugno, G.M.D., Flaborea, A., Sanchietti, A., Farinella, G.M., Galasso, F., Furnari, A.: Ti-prego: Chain of thought and in-context learning for online mistake detection in procedural egocentric videos. arXiv preprint arXiv:2411.02570 (2024) 

56. Qian, Y., Luo, W., Lian, D., Tang, X., Zhao, P., Gao, S.: Svip: Sequence verification for procedures in videos. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 19890–19902 (2022) 

57. Ryoo, M.S.: Human activity prediction: Early recognition of ongoing activities from streaming videos. In: 2011 International Conference on Computer Vision. pp. 1036–1043 (2011). `https://doi.org/10.1109/ICCV.2011.6126349`

<!-- Page 21 -->

MistExit 21 

58. Schoonbeek, T.J., Houben, T., Onvlee, H., Van der Sommen, F., et al.: Industreal: A dataset for procedure step recognition handling execution errors in egocentric videos in an industrial-like setting. In: Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision. pp. 4365–4374 (2024) 

59. Schulman, J., Wolski, F., Dhariwal, P., Radford, A., Klimov, O.: Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347 (2017) 

60. Seminara, L., Farinella, G.M., Furnari, A.: Differentiable task graph learning: Procedural activity representation and online mistake detection from egocentric videos. arXiv preprint arXiv:2406.01486 (2024) 

61. Sener, F., Chatterjee, D., Shelepov, D., He, K., Singhania, D., Wang, R., Yao, A.: Assembly101: A large-scale multi-view video dataset for understanding procedural activities. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 21096–21106 (2022) 

62. Shen, Y., Elhamifar, E.: Progress-aware online action segmentation for egocentric procedural task videos. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). pp. 18186–18197 (June 2024) 

63. Soomro, K., Idrees, H., Shah, M.: Predicting the where and what of actors and actions through online action localization. In: 2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR). pp. 2648–2657 (2016). `https://doi.org/ 10.1109/CVPR.2016.290` 

64. Stergiou, A., Damen, D.: The wisdom of crowds: Temporal progressive attention for early action prediction. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 14709–14719 (2023) 

65. Suárez-Hernández, A., Segovia-Aguas, J., Torras, C., Alenya, G.: Online action recognition. In: Proceedings of the AAAI Conference on Artificial Intelligence. vol. 35, pp. 11981–11989 (2021) 

66. Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł., Polosukhin, I.: Attention is all you need. Advances in neural information processing systems **30** (2017) 

67. Wang, B., Huang, L., Hoai, M.: Active vision for early recognition of human actions. In: 2020 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). pp. 1078–1088 (2020). `https://doi.org/10.1109/CVPR42600.2020. 00116` 

68. Wang, J., Chen, G., Huang, Y., Wang, L., Lu, T.: Memory-and-anticipation transformer for online action understanding. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp. 13824–13835 (2023) 

69. Wang, X., Zhang, S., Qing, Z., Shao, Y., Zuo, Z., Gao, C., Sang, N.: Oadtr: Online action detection with transformers. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp. 7565–7575 (2021) 

70. Wang, X., Kwon, T., Rad, M., Pan, B., Chakraborty, I., Andrist, S., Bohus, D., Feniello, A., Tekin, B., Frujeri, F.V., et al.: Holoassist: an egocentric human interaction dataset for interactive ai assistants in the real world. In: Proceedings of the IEEE/CVF International Conference on Computer Vision. pp. 20270–20281 (2023) 

71. Wang, X., Hu, J.F., Lai, J.H., Zhang, J., Zheng, W.S.: Progressive teacher-student learning for early action prediction. In: 2019 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). pp. 3551–3560 (2019). `https://doi.org/ 10.1109/CVPR.2019.00367` 

72. Wang, X., Hu, J.F., Lai, J.H., Zhang, J., Zheng, W.S.: Progressive teacher-student learning for early action prediction. In: 2019 IEEE/CVF Conference on Computer

<!-- Page 22 -->

22 Majumder et al. 

- Vision and Pattern Recognition (CVPR). pp. 3551–3560 (2019). `https://doi.org/ 10.1109/CVPR.2019.00367` 

- 73. Wang, Y., Yue, Y., Lin, Y., Jiang, H., Lai, Z., Kulikov, V., Orlov, N., Shi, H., Huang, G.: Adafocus v2: End-to-end training of spatial dynamic networks for video recognition. In: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR). pp. 20030–20040. IEEE (2022) 

- 74. Wang, Y., Yue, Y., Xu, X., Hassani, A., Kulikov, V., Orlov, N., Song, S., Shi, H., Huang, G.: Adafocusv3: On unified spatial-temporal dynamic video recognition. In: European Conference on Computer Vision. pp. 226–243. Springer (2022) 

- 75. Wang, Y., Zhang, H., Yue, Y., Song, S., Deng, C., Feng, J., Huang, G.: Uni-adafocus: spatial-temporal dynamic computation for video recognition. IEEE Transactions on Pattern Analysis and Machine Intelligence (2024) 

- 76. Wu, X., Wang, R., Hou, J., Lin, H., Luo, J.: Spatial–temporal relation reasoning for action prediction in videos. International Journal of Computer Vision **129** , 1484 – 1505 (2021), `https://api.semanticscholar.org/CorpusID:233904888` 

- 77. Wu, X., Zhao, J., Wang, R.: Anticipating future relations via graph growing for action prediction. In: AAAI Conference on Artificial Intelligence (2021), `https: //api.semanticscholar.org/CorpusID:232416180` 

- 78. Wu, Z., Xiong, C., Ma, C.Y., Socher, R., Davis, L.S.: Adaframe: Adaptive frame selection for fast video recognition. In: Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. pp. 1278–1287 (2019) 

- 79. Xu, M., Gao, M., Chen, Y.T., Davis, L.S., Crandall, D.J.: Temporal recurrent networks for online action detection. In: Proceedings of the IEEE/CVF international conference on computer vision. pp. 5532–5541 (2019) 

- 80. Xu, W., Yu, J., Miao, Z., Wan, L., Ji, Q.: Prediction-cgan: Human action prediction with conditional generative adversarial networks. In: Proceedings of the 27th ACM International Conference on Multimedia. p. 611–619. MM ’19, Association for Computing Machinery, New York, NY, USA (2019). `https://doi.org/10.1145/ 3343031.3351073` , `https://doi.org/10.1145/3343031.3351073` 

81. Yang, L., Radway, R.M., Chen, Y.H., Wu, T.F., Liu, H., Ansari, E., Chandra, V., Mitra, S., Beigné, E.: Three-dimensional stacked neural network accelerator architectures for ar/vr applications. IEEE Micro **42** (6), 116–124 (2022). `https: //doi.org/10.1109/MM.2022.3202254` 

82. Yi, H., Pan, Y., He, F., Liu, X., Zhang, B., Oguntola, O., Bertasius, G.: Exact: A video-language benchmark for expert action analysis. arXiv preprint arXiv:2506.06277 (2025) 

83. Zhang, C.L., Wu, J., Li, Y.: Actionformer: Localizing moments of actions with transformers. In: European Conference on Computer Vision. pp. 492–510. Springer (2022) 

84. Zhao, H., Wildes, R.: Spatiotemporal feature residual propagation for action prediction. In: 2019 IEEE/CVF International Conference on Computer Vision (ICCV). pp. 7002–7011 (2019). `https://doi.org/10.1109/ICCV.2019.00710` 

85. Zhao, Y., Krähenbühl, P.: Real-time online video detection with temporal smoothing transformers. In: European Conference on Computer Vision. pp. 485–502. Springer (2022)

<!-- Page 23 -->

||||MistExit|23|
|---|---|---|---|---|
|Model|AP %|OR %|||
|FastForward [16]|56.2|5.0|||
|**Ours**|**56.8**|**3.7**|||



**Table 1:** Early mistake detection results for our method and the state-of-the-art RL baseline FastForward [16], averaged across 3 random seeds. Higher AP, lower OR is better 

# **7 Supplementary material** 

In this supplementary material we provide additional details about: 

- Video for qualitatively illustrating (Sec. 7.1), as mentioned in ‘Qualitative examples’ in Sec. 5. 

- Analysis of the impact of random seeds on our model performance (Sec. 7.2) 

- Additional implementation details (Sec. 7.3), as referenced in Sec. 5.1. 

## **7.1 Supplementary video** 

Tne supplementary video, available at `https://vision.cs.utexas.edu/ projects/mist_exit` , qualitatively illustrates our task, Early Detection of Mistakes in Procedural Videos, and our MistExit method for tackling this task. We also show successful predictions by our model across both datasets, CaptainCook4D [54] and Assembly101 [61]. Finally, we illustrate our model’s failure cases (Sec. 5.2) with qualitative examples. 

## **7.2 Impact of random seed on our model performance** 

In Sec. 5, we evaluated our method using a single random seed. Here, we further evaluate the model with two additional seeds, report the mean performance across the three seeds—one from the main paper and two from this analysis—and compare it against the state-of-the-art RL baseline FastForward [16]. The results are shown in Table 1. Our method consistently outperforms the baseline while achieving better efficiency, demonstrating that our design is robust to different random seed initializations. 

## **7.3 Additional implementation details** 

Here, we provide our implementation details in addition to what we provided in main (Sec. 5.1). 

For both our mistake detector _D_ and policy _π_ , we use I3D [7] and TSM [44] encoders to embed video frames from CC4D and Assembly101, respectively, since

<!-- Page 24 -->

24 Majumder et al. 

these datasets provide such precomputed features and use them to benchmark several tasks introduced alongside the datasets. 

For our mistake detector, we project the visual feature inputs [7, 44] into 2048-dimensional features using a single linear layer. Next, we use a one-layer Transformer encoder [19,66] (Sec. 4.1) with a hidden dimensionality of 1024 to aggregate these features. Finally, to obtain the mistake label estimates and the anticipated features, we apply a single linear layer with the appropriate output dimensionality. 

For our policy, we encode its visual inputs and mistake detection score inputs (Sec. 4.2) using a 3-layer MLP with ReLU [50] activations. The weights of these layers are initialized using Kaiming-normal initialization [27]. Our policy network employs a one-layer bidirectional GRU [9,10] with 512 hidden units. The actor and critic networks each consist of a single fully connected layer. To train our policy using PPO [59] (Sec. 5.1), we weight the action loss by 1.0, the value loss by 0.5, and the entropy loss by 0.2. 

Finally, as mentioned in Sec. 1, we will release our code and data to ensure reproducibility.
