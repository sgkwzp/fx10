# Gazing Into Missteps Leveraging Eye-Gaze for Unsupervised Mistake Detection in Egocentric Videos of Skilled Human Activities

[Original PDF](../Gazing%20Into%20Missteps%20Leveraging%20Eye-Gaze%20for%20Unsupervised%20Mistake%20Detection%20in%20Egocentric%20Videos%20of%20Skilled%20Human%20Activities.pdf)

Pages: 16

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

# **Gazing Into Missteps: Leveraging Eye-Gaze for Unsupervised Mistake Detection in Egocentric Videos of Skilled Human Activities** 

Michele Mazzamuto<sup>1</sup><sup>_∗_</sup> , Antonino Furnari<sup>1</sup><sup>_∗_</sup> , Yoichi Sato<sup>2</sup> , Giovanni Maria Farinella<sup>1</sup> 

1University of Catania, Catania, Italy 

michele.mazzamuto@phd.unict.it, antonino.furnari@unict.it, giovanni.farinella@unict.it 

2The University of Tokyo, Tokyo, Japan 

ysato@iis.u-tokyo.ac.jp 

*Co-first authors. 

## **Abstract** 

_We address the challenge of unsupervised mistake detection in egocentric video of skilled human activities through the analysis of gaze signals. While traditional methods rely on manually labeled mistakes, our approach does not require mistake annotations, hence overcoming the need of domainspecific labeled data. Based on the observation that eye movements closely follow object manipulation activities, we assess to what extent eye-gaze signals can support mistake detection, proposing to identify deviations in attention patterns measured through a gaze tracker with respect to those estimated by a gaze prediction model. Since predicting gaze in video is characterized by high uncertainty, we propose a novel gaze completion task, where eye fixations are predicted from visual observations and partial gaze trajectories, and contribute a novel gaze completion approach which explicitly models correlations between gaze information and local visual tokens. Inconsistencies between predicted and observed gaze trajectories act as an indicator to identify mistakes. Experiments highlight the effectiveness of the proposed approach in different settings, with relative gains up to_ +14% _,_ +11% _, and_ +5% _in EPIC-Tent, HoloAssist and IndustReal respectively, remarkably matching results of supervised approaches without seeing any labels. We further show that gaze-based analysis is particularly useful in the presence of skilled actions, low action execution confidence, and actions requiring hand-eye coordination and object manipulation skills. Our method is ranked first on the HoloAssist Mistake Detection challenge._ 

## **1. Introduction** 

Smart glasses are gaining more and more popularity, with various existing products capable of supporting the user 


![](assets/046/paper-0001-12.png)


<!-- Start of picture text -->
Place water container  Correct Action Execution Wrong Action Execution<br>video predicted trajectory<br>Mistake<br>Conv<br>time<br>Conv<br>partial gaze trajectory Visual Local Token Gaze Token Correct<br>(a) Input (b) Gaze Completion (c) Compare with GT<br>...<br><!-- End of picture text -->

Figure 1. Top: gaze trajectories of a correct and wrong execution of the “place water container” action, together with gaze fixation maps averaged across many action instances. Note the higher variability exhibited by wrong executions. Bottom: (a) The proposed unsupervised mistake detection method assumes as input a video with a partial gaze trajectory on the initial part of the video. (b) A gaze completion model predicts a gaze trajectory for the remaining part of the video, conditioned on the input video and the partial trajectory. (c) A mistake is detected if the predicted trajectory is significantly different from the observed one, suggesting a deviation from the expected attention patterns. 

through Augmented Reality. In order to provide timely assistance, wearable devices should be able to identify moments in which the user makes mistakes or is confused and requires help [7]. If such instances are properly detected, the AI system can proactively offer contextual information or suggestions on how to best carry out the task at hand [42]. 

Previous works tackled the problem of detecting mistakes from a fully supervised perspective, where mistake instances were labeled in egocentric video and machine learning algorithms were trained to discriminate between video segments of correct action executions and incorrect ones [34, 42]. Such a fully supervised approach has two main downsides: 1) It is domain-dependent, hence requiring an accurate characterization of what a mistake is, depending on the context (e.g., a mistake in a kitchen is different from

<!-- Page 2 -->

a mistake in the assembly line); 2) It requires to collect and label a sufficient number of mistake instances, which may be difficult to observe and record, involve time consuming procedures, and require expert knowledge. Another class of methods [9, 33] aim to detect mistakes without relying on mistake annotations, but still requires domain-specific and costly temporal action annotations. Ideally, a wearable assistant should be able to infer when the behavioral patterns of the user deviate from the norm in order to determine if they need assistance in a scenario-independent setting, i.e., without making specific assumptions on how a mistake is defined and without requiring costly labels. To overcome the aforementioned limitations, we propose to detect mistakes in egocentric videos of human activity in an unsupervised way, learning from unlabeled video. 

Mistakes in task execution, in particular for tasks requiring hand-eye coordination and object manipulation skills, often involve abnormal attention patterns of the camera wearer [17, 18]. For instance, imagine a user operating a coffee machine without first adding water. As they press the _brew_ button, they notice that no coffee is produced and start shifting their attention erratically between the cup, the water tank, and the LED indicator, deviating from the typical attention sequence of “button _→_ cup _→_ button.” (See Figure 1(top)). This behavior is well-documented in psychology literature, which shows that gaze patterns are crucial for the execution of even the most repetitive daily activities (e.g., making tea) [20], and that they change in response to task complexity [30] and mistakes [29]. 

Following these observations, we study how the analysis of eye-gaze fixations can support mistake detection in egocentric video of skilled human activities. We hence propose to learn a model of “normal” attention patterns in the form of a gaze predictor producing likely eye gaze trajectories from a video at inference time. Since gaze prediction can be governed by high uncertainty, depending on the user’s goals, we propose a novel “gaze completion” task in which a model takes as input a video and a partial gaze trajectory (Figure 1(a)) and is tasked to predict a likely continuation of the partial trajectory (Figure 1(b)). Gaze completion is tackled with a novel approach based on a Gaze-Frame Correlation module which explicitly models the correlation between gaze information and each local visual token. We expect videos of correct action executions to represent normal user behavior, and hence to be characterized by predictable gaze patterns, while human behavior will deviate from normality, and gaze will be unpredictable, when a mistake is made by the user. We hence signal a mistake by comparing the predicted gaze with the ground truth eye gaze trajectory obtained through a gaze tracker (Figure 1(c)). 

Experiments show the effectiveness of the proposed approach, both alone, or in combination with other techniques, when compared to one-class anomaly detection 

methods [8, 39], and various unsupervised mistake detection baselines, with relative gains up to +14%, +11%, and +5% in the on EPIC-Tent [15], HoloAssist [42] and IndustReal [32] datasets respectively, remarkably matching the results of supervised methods without any labels in one-class settings. Our analysis also shows that gaze is most effective in the presence of complex actions, lowconfidence executions, and actions requiring hand-eye coordination and object-manipulation skills. 

In summary, the contributions of this work are as follows: 1) We investigate for the first time the problem of unsupervised mistake detection from egocentric video of human activity and provide an initial benchmark based on three datasets. 2) We define the novel “gaze completion” task where models predict gaze trajectories from video and partial gaze inputs, and introduce an approach based on a Gaze-Frame Correlation module; 3) We propose an approach to unsupervised mistake detection leveraging gaze completion to identify instances of unpredicable gaze patterns. Experiments analyze under which conditions gazebased analysis is most useful and show the effectiveness of the approach, in one-class and unsupervised settings. 

We will publicly release the code and model checkpoints to support future research. 

## **2. Related Work** 

**Egocentric gaze estimation** Literature on gaze estimation from egocentric video is rich, with previous works investigating simultaneous gaze prediction and action recognition [5], describing gaze prediction approaches incorporating egocentric cues [21], modeling task-dependent attention transition [13], leveraging vanishing point, manipulation point, hand regions [41], introducing specific architectures [1, 19], and proposing datasets to study egocentric gaze estimation and its applications in a variety of scenarios [12, 14, 22, 32, 42]. We propose a novel gaze completion task and show its application to the problem of unsupervised mistake detection in egocentric video. Differently from previous works, we define and tackle the novel task of gaze completion, with the aim to reduce the uncertanty associated with gaze prediction. 

**Use of gaze in egocentric vision** While many previous works focused on gaze estimation from video, few works investigated the use of gaze, estimated through a dedicated gaze tracker, as an input to support downstream egocentric vision applications. Specifically, previous investigations focused on discovering object usage [3], detecting privacysensitive situations [38], finding attended objects [27], assisting large language models in classification tasks [16], enhancing visual tasks [44, 46], improving egocentric human motion prediction [45], and aiding natural language processing tasks [36]. We show the effectiveness of gaze in mistake detection. Our method compares gaze trajecto-

<!-- Page 3 -->

ries predicted from visual data with gaze estimated through a gaze tracker to identify mistakes when predictions deviates from the ground truth. 

**Mistake Detection in Egocentric Videos** Mistakes naturally occur in human activities. The ability to automatically detect them from egocentric video can be beneficial for an AR assistant to offer support. Identifying mistakes usually entails modeling procedural knowledge [4, 9, 34], skill assessment [10], action segmentation [11] or detecting forgotten actions [37]. Notably, previous works tackled the task in a supervised fashion, training models to classify an action segment as “correct” or “mistake” in manually annotated instances [34, 42]. While this approach is feasible in a closed-world scenario, it requires 1) a definition of what a mistake is, depending on the domain (e.g., kitchens vs the assembly line), 2) significant amounts of manually labeled data, which is expensive and requires expert knowledge. In this work, we tackle an unsupervised mistake detection task, in which models observe unlabeled video at training time and are tasked to detect mistakes from video at test time. Our unsupervised scheme is possible through the analysis of gaze attention patterns, which provide a supervisory signal to create a joint video-gaze model of normal behavior. **Video Anomaly Detection** Our research also relates to the problem of Video Anomaly Detection (VAD), which involves recognizing abnormal or anomalous events within videos [23, 39]. A line of video anomaly methods are based on one-class classification, in which models are trained on normal videos and aim to identify divergence from the norm at test time [6, 8, 24, 25, 39, 40, 43]. Notably, anomaly detection in egocentric vision remains under-explored [26]. Similar to video anomaly detection, we aim to detect mistakes by determining video segments which deviate from statistics observed at training time [8]. Differently from previous works in video anomaly detection, we ground our predictions in an egocentric gaze estimation model, which acts as a proxy for modeling normal human behavior, hence effectively achieving mistake prediction detection when anomalous behavior is observed. Moreover, we go beyond the one-class assumption and show that our method can also be used in unsupervised settings where unlabeled correct and mistake examples are included at training time. 

## **3. Proposed Approach** 

### **3.1. Mistake Detection Problem Setup** 

The mistake detection task consists in highlighting those parts of the video in which the user is making a mistake during the execution of a given activity. In our setup, at each time-step _t_ , a model Φ takes as input a video _V_ observed up to time-step _t_ , _V_ 1: _t_ , and a 2D gaze trajectory _T_ 1: _t_ obtained with a gaze tracker, where the _i_ -th element of the trajectory _Ti_<sup>(</sup><sup>_x,y_)</sup> is a 2D gaze fixation in frame _Vi_ . Given this input, 

the model has to return a score _st_ = Φ( _V_ 1: _t, T_ 1: _t_ ) indicating whether a mistake is happening at the current time _t_ . In this context, high _st_ scores indicate the occurrence of a mistake, while low _st_ scores indicate a correct action. We can hence see the mistake detection problem as a classification task, in which timestep _t_ is classified as a mistake if _st > θ_ , where _θ_ is a chosen threshold. We follow previous literature on anomaly detection [8, 39] and evaluate methods in a threshold-independent fashion by reporting the Receiver Operating Characteristics Area Under the Curve (ROC-AUC), where we consider “mistake” as the positive class<sup>1</sup> . For completeness, we also report the best _F_ 1 score achieved considering the different thresholds, as well as its related precision and recall values. 

### **3.2. Proposed Approach** 

At each timestep _t_ , we trim the input video _V_ 1: _t_ and gaze trajectory _T_ 1: _t_ to the last observed _F_ frames, hence considering _Vt−F_ : _t_ and _Tt−F_ : _t_ as inputs to our mistake detection method. (Figure 1(a)). Our method relies on two main components: a gaze completion model (Figure 1(b)), and a scoring function (Figure 1(c)). 

**Gaze Completion Model** Figure 2 illustrates the proposed gaze completion model. The model takes as input the video _Vt−F_ : _t_ and the first half of the input gaze trajectory _Tt−F_ : _t−F/_ 2 and predicts a gaze trajectory _T_<sup>ˆ</sup> _t−F/_ 2: _t_ aligned to the remaining part of the ground truth trajectory _Tt−F/_ 2: _t_ . The goal of this model is to predict where the user is looking in the video, conditioned on the initial trajectory. As we show in the experiments, the conditioning allows to reduce the uncertainty on gaze predictions and give a prior into the intention and characteristics of the user. For instance, the model can notice that the user is a novice from the partial input trajectory or get an understanding of the performed activity and adapt its prediction accordingly. We build on [19] and propose an encoder-decoder transformerbased architecture, including two approaches to condition gaze prediction on the input partial trajectory: channel fusion and correlation fusion. 

_Model Overview_ The input gaze trajectory _Tt−F_ : _t_ is encoded into a stack of heatmaps _Q_ obtained by centering a Gaussian distribution of standard deviation _σ_ around the gaze points. The first half of the stack _Q_ 1: _F/_ 2, corresponding to the input half trajectory _Tt−F_ : _t−F/_ 2, is forwarded to the two trajectory fusion models (paths (1) and (2) in Figure 2), which inject information on the input trajectory at different semantic levels in the model. Input frames _Vt−F_ : _t_ are processed by a token embedding layer which maps them to visual tokens with a convolution as in [19]. This mod- 

> 1A true positive is a mistake correctly classified as a mistake, a true negative is a correct execution correctly classified as a correct execution, a false positive is a correct execution wrongly classified as a mistake, and a false negative is a mistake wrongly classified as a correct execution.

<!-- Page 4 -->

![](assets/046/paper-0004-00.png)


<!-- Start of picture text -->
(1) Channel fusion<br>(2) Correlation fusion<br>GT Gaze Heatmap<br>Gaze Trajectory  (1) (2)<br>Conv<br>Conv<br>R<br>Visual Local Token Gaze Token<br>R G B Embedding Token TransformerEncoder GazeCorrelation-Visual TransformerDecoder<br>Predicted Gaze Heatmap<br>Egocentric Frames<br>...<br>...<br>...<br>...<br>Peak Finding<br><!-- End of picture text -->


![](assets/046/paper-0004-01.png)


Figure 2. The model takes as input _F_ RGB frames _Vt−F_ : _t_ and a partial 2D gaze trajectory _Tt−F_ : _t−F/_ 2 on the first _F/_ 2 input frames, and outputs a predicted trajectory _T_<sup>ˆ</sup> _t−F/_ 2: _t_ from the input video, conditioned on the input trajectory. The input trajectory is encoded as a spatio-temporal heatmap _Q_ . Trajectory and RGB inputs are fused using two strategies, channel fusion, which adds gaze heatmaps as a separate channel (1), and correlation fusion, which uses a dedicated gaze-visual correlation module (2). We follow the design of [19] and process our inputs with a transformer encoder-decoder architecture which outputs a predicted gaze heatmap _Q_<sup>ˆ</sup> , supervised via a standard Kullback–Leibler divergence loss using the ground truth unobserved trajectory _Tt−F/_ 2: _t_ . The output trajectory _T_<sup>ˆ</sup> _t−F/_ 2: _t_ is recovered from _Q_ ˆ using a peak finding operation. 

ule is also responsible for mapping the input heatmaps to a single trajectory token. Input tokens are then processed by the transformer encoder, by the gaze-visual correlation module and finally by the transformer decoder to output a likely completion of the gaze in the form of heatmaps _Q_ ˆ, which are supervised with a standard Kullback–Leibler loss. Specifically, _Q_<sup>ˆ</sup> contains _F_ heatmaps related to the _F_ input frames _Vt−F_ : _t_ . The final trajectory _T_<sup>ˆ</sup> is obtained by finding the global maxima of the predicted gaze heatmaps. _Channel Fusion_ The channel fusion module (Figure 2(1)) adds the heatmaps in _Q_ 1: _F/_ 2 to the first _F/_ 2 frames of the input video, _Vt−F_ : _t−F/_ 2 as an additional channel. The values of this channel are set to zero for the remaining frames. This form of early fusion acts as a _soft conditioning_ aiming to include information about the input gaze trajectory in the computation. Note that, in order to incorporate information about the relationships between haze and input frames, the model needs to learn how to compute suitable gaze representations from the additional input channel during training. _Correlation Fusion_ This approach (Figure 2(2)) aims to fuse visual tokens with the gaze trajectory token computed by the token embedding layer. Inspired by global-local fusion originally proposed in [19], this is done in two stages. First, within the transformer encoder, where attention between all visual features and the gaze token is computed. In this stage, correlations between all visual tokens and across visual and gaze tokens are leveraged to obtain a strong representation. Second, within the dedicated gaze-visual correlation module. Here, attention is computed only between the gaze token and the visual tokens, thus learning a ded- 

icated attention mechanism which explicitly enriches the representation of each visual token with gaze information. Note that this fusion mechanism operates both at the early (through the encoder) and mid (through the gaze-visual correlation module) levels, thus allowing to leverage low-level (co-occurrences of gaze and visual features) and more semantic (co-occurrences of gaze and semantic visual concepts) information. 

**Scoring Function** Our approach predicts the mistake confidence score _st_ by comparing the predicted trajectory _T_ ˆ _t−F/_ 2: _t_ with the ground truth one _Tt−F/_ 2: _t_ which is obtained by the gaze tracker of the wearable device. We explore four different ways to compare the two trajectories: Euclidean distance, Dynamic Time Warping (DTW), Heatmap, and Entropy. 

_Euclidean Distance_ This method consists in accumulating the Euclidean distances computed between corresponding points in each trajectory as the score _st_ : 


![](assets/046/paper-0004-07.png)


_Dynamic Time Warping_ This scoring function uses Dynamic Time Warping (DTW)[31] to measure the distance between trajectories: 


![](assets/046/paper-0004-09.png)


Where DTW returns the cost of aligning _T_ to _T_<sup>ˆ</sup> according to

<!-- Page 5 -->

the DTW algorithm<sup>2</sup> . 

_Heatmap_ Differently from previous functions, this approach explicitly considers the probability values predicted by the model at each location.Specifically, we evaluate the likelihood of a ground truth eye fixation _Ti_ obtained by the device under the predicted heatmap _Q_<sup>ˆ</sup> _i_ , which can be computed as: 


![](assets/046/paper-0005-02.png)


where _Ti_<sup>_x_and</sup><sup>_T y_</sup> _i_<sup>are the coordinates of the trajectory point</sup> _Ti_ = [ _Ti_<sup>_x, T_</sup> _i_<sup>_y_].Thescoreassociatedtothepredictedtra-</sup> jectory _T_<sup>ˆ</sup> is computed as the sum of the likelihoods of each trajectory point, considering the predicted heatmap _Q_<sup>ˆ</sup> : 


![](assets/046/paper-0005-04.png)


_Entropy_ This is the only method which does not require ground truth gaze for computation. We consider this measure as a way to check whether mistakes are systematically characterized by uncertain gaze predictions. In this case, the score _st_ is set as the mean entropy of all predicted heatmaps for a given trajectory _T_<sup>ˆ</sup> . The entropy _H_ of a single heatmap _Q_ ˆ is given by: 


![](assets/046/paper-0005-06.png)


_Q_<sup>(</sup> _j_<sup>_x,y_)</sup> is the value at coordinates ( _x, y_ ) of heatmap _Qj_ . 

## **4. Experiments and Results** 

### **4.1. Datasets and Implementation Details** 

We perform our experiments on three popular datasets. **EPIC-Tent** [14] includes 7 hours of egocentric video of 29 subjects wearing a head-mounded GoPro and an SMI eye tracker while assembling a camping tent. The dataset includes egocentric video, gaze and labels indicating video segments in which users make mistakes. Subjects also rated their level of confidence in action execution in each clip in the videos. EPIC-Tent contains 151 _,_ 689 mistake frames and 384 _,_ 558 frames of correct executions, hence with a 28:72 ratio between correct and mistake frames. Since no official train-test split is available, we randomly split videos in training, validation and test sets roughly following a 60:15:25 ratio, obtaining 86 _,_ 099, 27 _,_ 613, and 37 _,_ 977 mistake frames in the training, validation, and test sets respectively. Since the dataset contains a single video per subject, there is no subject overlap between the three sets. **IndustReal** [32] is designed for studying procedural tasks in industrial-like environments and consists of distinct training, validation, and test sets. The training set comprises 

> 2We used this implementation: https://pypi.org/project/ fastdtw/. 

78 _,_ 902 frames, with 95 _._ 68% frames labeled as correct and 4 _._ 32% labeled as mistakes. The validation set includes 38 _,_ 036 frames, with 95 _._ 18% correct and 4 _._ 82% mistaken frames. The test set contains 90 _,_ 105 frames, with 92 _._ 53% correct and 7 _._ 47% mistaken frames. 

**HoloAssist** [42] focuses on a variety of scenarios in which users perform tasks with the assistance of an expert. The training set comprises 11 _,_ 614 _,_ 033 frames, with 94% frames labeled as correct and 6% labeled as mistakes. The test set contains 1 _,_ 699 _,_ 562 frames, with 95% correct and 5% mistake frames. 

**Implementation Details** We process input frames with a stride of 1 and set the batch size to 4 clips of 8 frames each. Weight decay is set to 0 _._ 07 to prevent overfitting. See the supplementary material for more details. 

### **4.2. Supervision Levels and Compared Approaches** 

We compare the proposed approach to methods belonging to three different supervision levels: fully supervised, oneclass classification, and unsupervised. All baselines described below are compared with a random baseline which assigns a random score to each input clip. 

**Fully Supervised Methods** are trained assuming the availability of mistake labels for all image frames. We consider this class of methods to provide an upper-bound to performance when assessing one-class and unsupervised methods. We consider two approaches in this class: a TimeSformer [2] action recognition model which classifies the input video clips without access to any temporal context from actions executed before or after the current one, and a C2F [35] temporal action segmentation model operating on DINOv2 [28] features, which naturally performs action segmentation taking into account the temporal context in which an action (or mistake) is executed. 

**One-Class Classification Methods** are trained only on _videos of correct executions_ , following the standard setup of anomaly detection [8, 39]. In this context, we assume that the data is verified by an expert for correctness before being used for training. Note that this check does not require marking the temporal occurrence of mistakes, but only discarding any video which contains mistakes. For this class, we compare our method with respect to TrajREC [39] and MoCoDAD [8], two popular approaches for video anomaly detection based on the processing of human skeletal data. Since full human skeletons are not visible in egocentric videos, we replace skeletal data with hand joint keypoints<sup>3</sup> . We also adapt TrajREC and MoCoDAD to take a single gaze point instead of, or in addition to, the hand keypoints to assess the ability of such methods to leverage 

> 3We use ground truth hand keypoints in HoloAssist and IndustReal, while we extract keypoints with https://github.com/openmmlab/mmpose in EPIC-Tent.

<!-- Page 6 -->

||**Scoring**|**Fusion**|**F1**|**Precision**|**Recall**|**AUC**|
|---|---|---|---|---|---|---|
|1|Random|//|0.36|0.29|0.42|0.51|
|2|Entropy|//|0.41|0.27|0.62|0.51|
|3|Euclidean|//|0.42|0.29|0.60|0.55|
|4|DTW|//|0.44|0.31|0.68|0.56|
|5|Heatmap|//|0.45|0.32|0.70|0.57|
|6|Heatmap|CH|0.45|0.32|0.74|0.63|
|7|Heatmap|CORR|0.50|0.36|0.82|0.65|
|8|Heatmap|CH + CORR|**0.51**|**0.36**|**0.85**|**0.69**|



Table 1. Ablation of various scoring functions and fusion strategies on EPIC-Tent in the unsupervised setting. Best results perblock are <u>underlined,</u> while best global results are **in bold** . CH: channel fusion, CORR: correlation fusion. 

eye-gaze information<sup>4</sup> . We compare these models to an instantiation of the proposed approach in which the gaze completion model is trained only on correct executions, hence effectively replicating a one-class scheme. We also compare with respect to a baseline which replaces the proposed gaze completion module with a simple gaze prediction component based on GLC [19]. Following the one-class setup, we train the GLC method of [19] on correct executions only and compare the predicted and ground truth gaze using the considered scoring functions. 

**Unsupervised Methods** assume no knowledge of which examples are correct executions and which are mistakes. Hence, models are trained on a natural mix of correct and incorrect action executions. This is the least constrained case in which the collected data is not verified by an expert prior to training. We compare our model with TrajREC and MoCoDAD adapted as discussed above and with the gazeprediction baseline GLC [19]. 

### **4.3. Performance of Proposed Model and Ablations** 

Table 1 reports the performance of the proposed approach in unsupervised settings, evaluating the considered scoring functions and gaze-video fusion strategies in the unsupervised mistake detection settings on EPIC-Tent. Rows 2-5 compare scoring functions when both fusion strategies are turned off and the model is not conditioned on previous trajectories. The entropy scoring function achieved an AUC of 0 _._ 51 and an F1 score of 0 _._ 41 (row 2), only marginally above the random baseline (F1 of 0 _._ 36), suggesting that high entropy in the predictions marginally correlates with the presence of a mistake. Alternative scoring functions improved the results, yielding an AUC of 0 _._ 55 and 0 _._ 56 when using Euclidean distance and DTW scoring functions, respectively (rows 3-4). The heatmap-based scoring function produced the best results, with an AUC of 0 _._ 57 and an F1 score of 0 _._ 45, significantly above random level (compare with the F1 score of 0 _._ 36 in row 1). The advantage of the heatmap scoring function is likely due to the better 

> 4See supplementary material for more details. 

|**Method**|**Sup. Level**|**F1**|**Precision**|**Recall**|**AUC**|
|---|---|---|---|---|---|
|Random|//|0.36|0.29|0.42|0.51|
|TimeSformer [2]|Fully Supervised|0.49|0.35|0.80|0.67|
|C2F[35]|FullySupervised|**0.58**|**0.44**|**0.85**|**0.72**|
|TrajREC (G) [39]|One-Class|0.40|0.26|0.88|0.51|
|MoCoDAD (G) [8]|One-Class|0.43|0.27|**0.91**|0.50|
|TrajREC (H) [39]|One-Class|0.44|0.31|0.76|0.55|
|MoCoDAD (H) [8]|One-Class|0.46|0.33|0.79|0.60|
|TrajREC (H+G) [39]|One-Class|0.42|0.29|0.75|0.53|
|MoCoDAD (H+G) [8]|One-Class|0.43|0.30|0.77|0.56|
|TrajREC (H+G)* [39]|One-Class|0.47|0.34|0.77|0.63|
|MoCoDAD (H+G)* [8]|One-Class|0.49|0.35|0.81|0.65|
|GLC[19]|One-Class|0.46|0.37|0.62|0.66|
|Ours|One-Class|0.52|0.37|0.85|0.69|
|Ours + MoCoDAD(H)*|One-Class|**0.54**|**0.41**|0.86|**0.72**|
|TrajREC (G) [39]|Unsupervised|0.27|0.16|**0.94**|0.50|
|MoCoDAD (G) [8]|Unsupervised|0.33|0.21|0.88|0.51|
|TrajREC (H) [39]|Unsupervised|0.40|0.27|0.79|0.58|
|MoCoDAD (H) [8]|Unsupervised|0.41|0.27|0.86|0.60|
|MoCoDAD (H+G)* [8]|Unsupervised|0.41|0.27|0.88|0.60|
|GLC[19]|Unsupervised|0.44|0.33|0.70|0.61|
|Ours|Unsupervised|0.51|0.36|0.85|0.69|
|Ours + MoCoDAD(H)*|Unsupervised|**0.52**|**0.37**|0.88|**0.70**|



* Late fusion 

Table 2. Mistake detection results on EPIC-Tent. Best results are **in bold** , second best results are underlined. 

exploitation of the probability values computed by the gaze prediction model, as compared to other scoring functions. Hence, we adopted the heatmap-based scoring as our primary method in following comparisons. 

Rows 6-7 compare approaches using one of the two fusion strategies. While both fusion strategies improve results (compare rows 6-7 with 5), the proposed correlation strategy (CORR) systematically outperforms channel fusion, obtaining an AUC score of 0 _._ 65 and an F1 score of 0 _._ 50 and doubling the recall of the random baseline (0 _._ 82 vs 0 _._ 42) with better precision (0 _._ 36 vs 0 _._ 29). Combining the two fusion strategies (row 8) leads to an AUC of 0 _._ 69 and an F1 score of 0 _._ 51 ( _+0.12_ and _+0.06_ compared to the standard heatmap method - row 5). This configuration is the one referred to as “ours” in future comparisons.<sup>5</sup> 

### **4.4. Comparison with the state of the art** 

**EPIC-Tent** Table 2 compares the proposed mistake detection approach with competitors on EPIC-Tent, according to the three considered levels of supervision. C2F outperforms TimeSformer in all evaluated metrics, particularly in the F1 score (0 _._ 58 of C2F vs 0 _._ 49 of TimeSformer and 0 _._ 36 of the random baseline), suggesting that C2F is more adept at capturing temporal reasoning, which is crucial for identifying mistakes in dynamic activities. However, the reliance on fully labeled datasets poses limitations for both methods. One-class methods for anomaly detection adapted to take only gaze as input, namely, TrajREC (G) and MoCoDAD (G), show minor improvements over the random baseline in terms of AUC score (0 _._ 50 _−_ 0 _._ 51 vs 0 _._ 51) and only small 

> 5See supplementary material for additional ablations.

<!-- Page 7 -->

improvements in F1 score (0 _._ 40 _−_ 0 _._ 43 vs 0 _._ 36). High recall values, paired with low precision, suggest that these methods tend to classify most clips as mistakes. Incorporating hand skeleton data instead of gaze, namely, TrajREC (H) and MoCoDAD (H), leads to slight improvements, as evidenced by F1 scores of 0 _._ 44 and 0 _._ 45, and AUC values of 0 _._ 55 and 0 _._ 60. Combining (H) and (G) models through late fusion (denoted with<sup>_∗_</sup> ) improves the results, with MoCoDAD (H+G)<sup>_∗_</sup> achieving an F1 score of 0.49 and an AUC of 0.65, suggesting that the signals captured by gaze-based and hand-based analyses are complementary. The one-class approach based on GLC [19] gaze prediction shows improved results compared to previous one-class methods, being only slightly less effective than the late fused method, despite not analyzing any hand-based information. This highlights the value of leveraging gaze analysis for mistake detection. “‘ 

Finally, the proposed method based on gaze completion obtains the best results, yielding an AUC of 0 _._ 69, an F1score of 0 _._ 52, a precision of 0 _._ 37, and a recall of 0 _._ 85, which amount to relative improvements of +5 _/_ 13%<sup>6</sup> with respect to the best approach GLC and +35 _/_ 44% with respect to the random baseline. Late-fusing our approach with MoCoDAD (H) achieves enhanced results with an AUC of 0 _._ 72 and an F1 score of 0 _._ 54, improving over compared approaches, suggesting that gaze analysis can further benefit from integration with approaches based on different cues. It is worth noting that our best method remarkably achieves the same AUC score of 0 _._ 72 as the best supervised approach and a comparable _F_ 1 score (0 _._ 54 vs 0 _._ 58) without access to labels during training. We compare unsupervised approaches in the bottom part of Table 2. Similarly to the one-class case, TrajREC (H) and MoCoDAD (H) slightly improve over the random baseline (e.g., 0 _._ 40 and 0 _._ 41 vs 0 _._ 36 of the random baseline in F1 score). GLC outperforms these former two methods obtaining an F1 score of 0 _._ 44 and an AUC score of 0 _._ 61, which are lower than the scores of 0 _._ 46 and 0 _._ 66 obtained in the one-class setting. In these settings, the proposed method achieves an F1 score of 0 _._ 51, which is comparable to the score obtained in one-class settings 0 _._ 52 with similar and recall values and the same AUC of 0 _._ 69, despite the unsupervised setting being more challenging. Late fusion with MoCoDAD (H) brings some additional improvements, with an F1 score of 0.52 and AUC of 0.70. 

Table 3 compares the proposed method with competitors on HoloAssist, which presents a more varied and expansive context than EPIC-Tent, making mistake detection more challenging. The random baseline achieves an F1 score of only 0 _._ 04. One-class methods like TrajREC and MoCoDAD improve over the baseline but tend to classify most clips as mistakes, with high recall values (0 _._ 96 and 0 _._ 94). Hand keypoint-based methods show improvements, with 

> 6We compute the relative improvement of _b_ with respect to _a_ as _<u>b−b a</u>_ 

|**Method**|**Sup. Level**|**F1**|**Precision**|**Recall**|**AUC**|
|---|---|---|---|---|---|
|Random|//|0.04|0.02|0.39|0.50|
|TimeSformer [2]|Fully Supervised|0.21|0.35|0.13|0.58|
|C2F[35]|FullySupervised|**0.38**|**0.37**|**0.40**|**0.65**|
|TrajREC (G) [39]|One-Class|0.09|0.04|**0.96**|0.50|
|MoCoDAD (G) [8]|One-Class|0.11|0.06|0.94|0.51|
|TrajREC (H) [39]|One-Class|0.19|0.11|0.72|0.56|
|MoCoDAD (H) [8]|One-Class|0.17|0.10|0.71|0.55|
|TrajREC (H+G) [39]|One-Class|0.13|0.07|0.68|0.52|
|MoCoDAD (H+G) [8]|One-Class|0.14|0.08|0.62|0.52|
|TrajREC (H+G)* [39]|One-Class|0.20|0.12|0.71|0.56|
|MoCoDAD (H+G)* [8]|One-Class|0.21|0.12|0.75|0.57|
|GLC[19]|One-Class|0.19|0.11|0.56|0.60|
|Ours|One-Class|0.22|0.14|0.59|0.61|
|Ours + MoCoDAD(H)*|One-Class|**0.26**|**0.16**|0.73|**0.63**|
|TrajREC (G) [39]|Unsupervised|0.05|0.03|**0.92**|0.50|
|MoCoDAD (G) [8]|Unsupervised|0.07|0.04|**0.92**|0.50|
|TrajREC (H) [39]|Unsupervised|0.11|0.07|0.32|0.56|
|MoCoDAD (H) [8]|Unsupervised|0.14|0.10|0.25|0.55|
|MoCoDAD (H+G)* [8]|Unsupervised|0.15|0.11|0.25|0.56|
|GLC[19]|Unsupervised|0.10|0.06|0.34|0.54|
|Ours|Unsupervised|0.18|0.12|0.40|0.59|
|Ours + MoCoDAD(H)*|Unsupervised|**0.21**|**0.15**|0.40|**0.60**|



* Late fusion 

Table 3. Mistake detection result on HoloAssist. 

TrajREC (H) slightly outperforming MoCoDAD (H). GLC demonstrates better AUC and F1 scores, with more balanced precision and recall metrics. Our approach achieves an AUC of 0 _._ 61 and an F1 score of 0 _._ 22 in one-class settings, with the best results from late fusion with MoCoDAD, yielding an F1 score of 0 _._ 26 and an AUC of 0 _._ 63. In the unsupervised scenario, TrajREC (G) and MoCoDAD (G) show limited effectiveness, while the (H) approaches perform slightly better. Our method achieves an AUC of 0 _._ 59 and an F1 score of 0 _._ 18, showing robustness across evaluation settings and relative improvements over GLC, with gains of +9% and +80%, respectively. Combining with MoCoDAD (H) further enhances performance. 

Results on IndustReal, shown in Table 4, confirm the trends observed in HoloAssist. TrajREC and MoCoDAD bring small improvements over the random baseline in H, G, and H+G configurations. Our method outperforms competitors with improvements over GLC of +5% in AUC and +14% in F1 in one-class settings, and +6% in AUC in unsupervised settings, while late fusion with MoCoDAD (H) does not improve performance due to MoCoDAD’s reduced effectiveness in this scenario. 

### **4.5. Contribution of gaze across scenarios** 

In this section, we analyze the performance of our method with respect to scenarios in order to assess under which conditions gaze analysis is more or less predictive of mistakes. **Action Complexity** We investigated how action complexity correlates with gaze-predicted mistakes in procedural tasks. We asked 40 volunteers to rate the complexity of performing actions contained in HoloAssist without looking (1 = easy, 5 = difficult). We then compared the complexity of the action associated to a given video segment to the ability

<!-- Page 8 -->

|**Method**|**Sup. Level**|**F1**|**Precision**|**Recall**|**AUC**|
|---|---|---|---|---|---|
|Random|//|0.12|0.06|**0.62**|0.51|
|TimeSformer [2]|Fully Supervised|0.20|0.12|0.35|0.58|
|C2F[35]|FullySupervised|**0.31**|**0.29**|0.31|**0.67**|
|TrajRE(G) [39]|One-Class|0.17|0.09|0.90|0.53|
|MoCoDAD(G) [8]|One-Class|0.18|0.10|**0.91**|0.55|
|TrajREC(H) [39]|One-Class|0.21|0.12|0.88|0.57|
|MoCoDAD(H) [8]|One-Class|0.22|0.13|0.81|0.60|
|TrajREC(H+G) [39]|One-Class|0.18|0.10|0.86|0.55|
|MoCoDAD(H+G) [8]|One-Class|0.19|0.11|0.79|0.58|
|TrajREC(H+G)* [39]|One-Class|0.21|0.12|0.88|0.58|
|MoCoDAD(H+G)* [8]|One-Class|0.22|0.13|0.82|0.61|
|GLC[19]|One-Class|0.21|0.15|0.33|0.60|
|Ours|One-Class|0.24|**0.18**|0.35|0.63|
|Ours + MoCoDAD(H)*|One-Class|**0.26**|0.17|0.60|**0.65**|
|TrajREC (G) [39]|Unsupervised|0.11|0.06|**0.92**|0.51|
|MoCoDAD (G) [8]|Unsupervised|0.11|0.06|**0.92**|0.51|
|TrajREC (H) [39]|Unsupervised|0.15|0.11|0.28|0.55|
|MoCoDAD (H) [8]|Unsupervised|0.16|0.12|0.29|0.57|
|MoCoDAD (H+G)* [8]|Unsupervised|0.17|0.12|0.30|0.57|
|GLC[19]|Unsupervised|**0.21**|0.15|0.33|0.58|
|Ours|Unsupervised|**0.21**|**0.16**|0.33|**0.62**|
|Ours + MoCoDAD(H)*|Unsupervised|0.20|0.15|0.32|0.61|



* Late fusion 

Table 4. Mistake detection result on IndustReal. 

of our model to make a correct prediction (which we term “success”). Results (see Figure 3a) showed a positive correlation between difficulty and prediction success, measured with a Point Biserial Correlation of 0 _._ 3843, with _p <_ 0 _._ 05<sup>7</sup> . This suggests that our method is particularly effective in the case of complex actions which cannot be carried out without looking, while less effective in the case of trivial tasks. 

**Confidence Level** On the EPIC-Tent dataset, we compared if the self-rated confidence score reported by camera wearers was correlated to the success of our method. Results (see Figure 3b) obtained a Point Biserial Correlation of -0.1137, _p <_ 0 _._ 05 indicating a small but significant negative correlation: our method is most effective when the self-rated confidence is higher. This suggests that gaze-based analysis is more effective in the case of novices, which reported lower confidence and probably rely more on visual observations when executing their tasks. 

**Action Type** We finally assess whether the type of the performed action affects the performance of our method. To this aim, we grouped actions contained in all three datasets in four categories (Hand-Eye Coordination, Object Manipulation, Task Preparation, Inspection/Verification)<sup>8</sup> . We hence computed the number of co-ocurrences between success or failure of our method and the different action classes. Results (see Figure 4) show a Cramer’s V statistic of 0 _._ 27 (a moderate correlation of 0 _._ 27 in a 0 _−_ 1 scale) with a p-value _p <_ 0 _._ 05. Gaze-based analysis proves particularly useful in the case of actions requiring hand-eye coordination and object manipulation abilities, while less effective 

> 7We use Point Biserial Correlation as action difficulty is a continuous variable while the success of our method is a binary one. 

> 8See supplementary material for more details. 


![](assets/046/paper-0008-08.png)


<!-- Start of picture text -->
Difficulty Ratings by Prediction Type Confidence Ratings by Prediction Type<br>5.0 1.0<br>4.5<br>0.8<br>4.0<br>3.5 0.6<br>3.0<br>2.5 0.4<br>2.0<br>0.2<br>1.5<br>1.0 0.0<br>Wrong Prediction Correct Prediction Wrong Prediction Correct Prediction<br>(a) (b)<br>Difficulty Rating Confidence Rating<br><!-- End of picture text -->

Figure 3. Distributions of difficulty ratings (a) and execution confidence ratings (b) with respect to wrong and correct predictions. 


![](assets/046/paper-0008-10.png)


<!-- Start of picture text -->
Correct/Wrong prediction rate by Action Type<br>1.0 Wrong Prediction<br>Correct Prediction<br>0.8 p-value = 0.0002 = 627.68<br>Cramer's V = 0.27<br>0.6<br>0.4<br>0.2<br>0.0 Hand-Eye Coordination Object Manipulation Task Preparation Inspection/Verification<br>Rate<br><!-- End of picture text -->

Figure 4. Distributions of Correct/Wrong pred. by action type. 

for generic actions such as task preparation and inspection.<sup>9</sup> 

## **5. Conclusion** 

We proposed to perform mistake detection in egocentric videos in an unsupervised way, leveraging gaze signals. We introduced a novel _gaze completion task_ , where gaze trajectories are predicted based on observed video and partial gaze data, and an approach to tackle this task. Mistake detection is performed comparing predicted trajectories with ground truth, identifying instances where gaze becomes unpredictable as potential mistakes. Experimental validation on EPIC-Tent, HoloAssist, and IndustReal demonstrates the efficacy of our method, surpassing traditional one-class techniques and other unsupervised mistake detection methods. Our method is ranked first on the HoloAssist Mistake Detection challenge. Code will be publicly shared. 

## **Acknowledgments** 

This research has been supported by the project Future Artificial Intelligence Research (FAIR) – PNRR MUR Cod. PE0000013 - CUP: E63C22001940006. 

> 9See supp. for more details and per class F1 and AUC scores. Qualitative results are reported in the supplementary material

<!-- Page 9 -->

## **References** 

- [1] Mohammad Al-Naser, Shoaib Ahmed Siddiqui, Hiroki Ohashi, Sheraz Ahmed, Nakamura Katsuyki, Sato Takuto, and Andreas Dengel. Ogaze: Gaze prediction in egocentric videos for attentional object selection. In _2019 Digital Image Computing: Techniques and Applications (DICTA)_ , pages 1– 8. IEEE, 2019. 2 

- [2] Gedas Bertasius, Heng Wang, and Lorenzo Torresani. Is space-time attention all you need for video understanding?, 2021. 5, 6, 7, 8, 4 

- [3] Dima Damen, Teesid Leelasawassuk, Osian Haines, Andrew Calway, and W. Mayol-Cuevas. You-do, i-learn: Discovering task relevant objects and their modes of interaction from multi-user egocentric video. In _British Machine Vision Conference_ , 2014. 2 

- [4] Guodong Ding, Fadime Sener, Shugao Ma, and Angela Yao. Every mistake counts in assembly. _ArXiv_ , abs/2307.16453, 2023. 3 

- [5] Alireza Fathi, Yin Li, and James M Rehg. Learning to recognize daily actions using gaze. In _Computer Vision–ECCV 2012: 12th European Conference on Computer Vision, Florence, Italy, October 7-13, 2012, Proceedings, Part I 12_ , pages 314–327. Springer, 2012. 2 

- [6] Jianfeng Feng, Fa-Ting Hong, and Weishi Zheng. Mist: Multiple instance self-training framework for video anomaly detection. _2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)_ , pages 14004–14013, 2021. 3 

- [7] Shijia Feng, Michael Wray, Brian Sullivan, Youngkyoon Jang, Casimir J. H. Ludwig, Iain Gilchrist, and Walterio W. Mayol-Cuevas. Are you struggling? dataset and baselines for struggle determination in assembly videos. _ArXiv_ , abs/2402.11057, 2024. 1 

- [8] Alessandro Flaborea, Luca Collorone, Guido Maria D’Amely di Melendugno, Stefano D’Arrigo, Bardh Prenkaj, and Fabio Galasso. Multimodal motion conditioned diffusion model for skeleton-based video anomaly detection. In _Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)_ , pages 10318–10329, 2023. 2, 3, 5, 6, 7, 8 

- [9] Alessandro Flaborea, Guido Maria D’Amely di Melendugno, Leonardo Plini, Luca Scofano, Edoardo De Matteis, Antonino Furnari, Giovanni Maria Farinella, and Fabio Galasso. Prego: online mistake detection in procedural egocentric videos. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , pages 18483– 18492, 2024. 2, 3 

- [10] Yixin Gao, S Swaroop Vedula, Carol E Reiley, Narges Ahmidi, Balakrishnan Varadarajan, Henry C Lin, Lingling Tao, Luca Zappella, Benjamın B´ejar, David D Yuh, et al. Jhu-isi gesture and skill assessment working set (jigsaws): A surgical activity dataset for human motion modeling. In _MICCAI workshop: M2cai_ , 2014. 3 

- [11] Reza Ghoddoosian, Isht Dwivedi, Nakul Agarwal, and Behzad Dariush. Weakly-supervised action segmentation and unseen error detection in anomalous instructional videos. In 

   - _Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)_ , pages 10128–10138, 2023. 3 

- [12] Kristen Grauman, Andrew Westbury, Eugene Byrne, Zachary Chavis, Antonino Furnari, Rohit Girdhar, Jackson Hamburger, Hao Jiang, Miao Liu, Xingyu Liu, Miguel Martin, Tushar Nagarajan, Ilija Radosavovic, Santhosh Kumar Ramakrishnan, Fiona Ryan, Jayant Sharma, Michael Wray, Mengmeng Xu, Eric Zhongcong Xu, Chen Zhao, Siddhant Bansal, Dhruv Batra, Vincent Cartillier, Sean Crane, Tien Do, Morrie Doulaty, Akshay Erapalli, Christoph Feichtenhofer, Adriano Fragomeni, Qichen Fu, Christian Fuegen, Abrham Gebreselasie, Cristina Gonzalez, James Hillis, Xuhua Huang, Yifei Huang, Wenqi Jia, Weslie Khoo, Jachym Kolar, Satwik Kottur, Anurag Kumar, Federico Landini, Chao Li, Yanghao Li, Zhenqiang Li, Karttikeya Mangalam, Raghava Modhugu, Jonathan Munro, Tullie Murrell, Takumi Nishiyasu, Will Price, Paola Ruiz Puentes, Merey Ramazanova, Leda Sari, Kiran Somasundaram, Audrey Southerland, Yusuke Sugano, Ruijie Tao, Minh Vo, Yuchen Wang, Xindi Wu, Takuma Yagi, Yunyi Zhu, Pablo Arbelaez, David Crandall, Dima Damen, Giovanni Maria Farinella, Bernard Ghanem, Vamsi Krishna Ithapu, C. V. Jawahar, Hanbyul Joo, Kris Kitani, Haizhou Li, Richard Newcombe, Aude Oliva, Hyun Soo Park, James M. Rehg, Yoichi Sato, Jianbo Shi, Mike Zheng Shou, Antonio Torralba, Lorenzo Torresani, Mingfei Yan, and Jitendra Malik. Ego4d: Around the World in 3,000 Hours of Egocentric Video. In _IEEE/CVF Computer Vision and Pattern Recognition (CVPR)_ , 2022. 2 

- [13] Yifei Huang, Minjie Cai, Zhenqiang Li, and Yoichi Sato. Predicting gaze in egocentric video by learning taskdependent attention transition. _ArXiv_ , abs/1803.09125, 2018. 2 

- [14] Youngkyoon Jang, Brian Sullivan, Casimir Ludwig, Iain D. Gilchrist, Dima Damen, and Walterio Mayol-Cuevas. Epictent: An egocentric video dataset for camping tent assembly. In _2019 IEEE/CVF International Conference on Computer Vision Workshop (ICCVW)_ , pages 4461–4469, 2019. 2, 5 

- [15] Youngkyoon Jang, Brian Sullivan, Casimir Ludwig, Iain D. Gilchrist, Dima Damen, and Walterio Mayol-Cuevas. Epictent: An egocentric video dataset for camping tent assembly. In _2019 IEEE/CVF International Conference on Computer Vision Workshop (ICCVW)_ , pages 4461–4469, 2019. 2 

- [16] Robert Konrad, Nitish Padmanaban, J. Gabriel Buckmaster, Kevin C. Boyle, and Gordon Wetzstein. Gazegpt: Augmenting human capabilities using gaze-contingent contextual ai for smart eyewear, 2024. 2 

- [17] Fatemeh Koochaki and Laleh Najafizadeh. Predicting intention through eye gaze patterns. _2018 IEEE Biomedical Circuits and Systems Conference (BioCAS)_ , pages 1–4, 2018. 2 

- [18] Kyle Krafka, Aditya Khosla, Petr Kellnhofer, Harini Kannan, Suchendra M. Bhandarkar, Wojciech Matusik, and Antonio Torralba. Eye tracking for everyone. _2016 IEEE Conference on Computer Vision and Pattern Recognition (CVPR)_ , pages 2176–2184, 2016. 2 

- [19] Bolin Lai, Miao Liu, Fiona Ryan, and James Rehg. In the eye of transformer: Global-local correlation for egocentric

<!-- Page 10 -->

gaze estimation. _British Machine Vision Conference_ , 2022. 2, 3, 4, 6, 7, 8 

- [20] M. Land, Neil Mennie, and Jennifer Rusted. The roles of vision and eye movements in the control of activities of daily living. _Perception_ , 28:1311–28, 1999. 2 

- [21] Yin Li, Alireza Fathi, and James M Rehg. Learning to predict gaze in egocentric video. In _Proceedings of the IEEE international conference on computer vision_ , pages 3216–3223, 2013. 2 

- [22] Yin Li, Miao Liu, and James M. Rehg. In the eye of beholder: Joint learning of gaze and actions in first person video. In _Proceedings of the European Conference on Computer Vision (ECCV)_ , 2018. 2 

- [23] Zhian Liu, Yongwei Nie, Chengjiang Long, Qing Zhang, and Guiqing Li. A hybrid video anomaly detection framework via memory-augmented flow reconstruction and flow-guided frame prediction. In _Proceedings of the IEEE International Conference on Computer Vision_ , 2021. 3 

- [24] Cewu Lu, Jianping Shi, and Jiaya Jia. Abnormal event detection at 150 fps in matlab. In _2013 IEEE International Conference on Computer Vision_ , pages 2720–2727, 2013. 3 

- [25] Hui Lv, Zhongqi Yue, Qianru Sun, Bin Luo, Zhen Cui, and Hanwang Zhang. Unbiased multiple instance learning for weakly supervised video anomaly detection. _2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)_ , pages 8022–8031, 2023. 3 

- [26] Mana Masuda, Ryo Hachiuma, Ryo Fujii, and Hideo Saito. _Unsupervised Anomaly Detection of the First Person in Gait from an Egocentric Camera_ , page 604–617. SpringerVerlag, Berlin, Heidelberg, 2020. 3 

- [27] Michele Mazzamuto, Francesco Ragusa, Antonino Furnari, and Giovanni Maria Farinella. Learning to detect attended objects in cultural sites with gaze signals and weak object supervision. _J. Comput. Cult. Herit._ , 2024. 2 

- [28] Maxime Oquab, Timoth´ee Darcet, Th´eo Moutakanni, Huy Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fernandez, Daniel Haziza, Francisco Massa, Alaaeldin El-Nouby, et al. Dinov2: Learning robust visual features without supervision. _arXiv preprint arXiv:2304.07193_ , 2023. 5 

- [29] Candace E. Peacock, Ben Lafreniere, Ting Zhang, Stephanie Santosa, Hrvoje Benko, and Tanya R. Jonker. Gaze as an indicator of input recognition errors. _Proc. ACM Hum.Comput. Interact._ , 6(ETRA), 2022. 2 

- [30] Jeff Pelz and Roxanne Canosa. Oculomotor behavior and perceptual strategies in complex tasks. _Vision research_ , 41: 3587–96, 2001. 2 

- [31] Hiroaki Sakoe. Dynamic programming algorithm optimization for spoken word recognition. _IEEE Transactions on Acoustics, Speech, and Signal Processing_ , 26:159–165, 1978. 4 

- [32] Tim J Schoonbeek, Tim Houben, Hans Onvlee, Fons van der Sommen, et al. Industreal: A dataset for procedure step recognition handling execution errors in egocentric videos in an industrial-like setting. In _Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision_ , pages 4365–4374, 2024. 2, 5 

- [33] Luigi Seminara, Giovanni Maria Farinella, and Antonino Furnari. Differentiable task graph learning: Procedural activity representation and online mistake detection from egocentric videos. In _Advances in Neural Information Processing Systems_ , 2024. 2 

- [34] Fadime Sener, Dibyadip Chatterjee, Daniel Shelepov, Kun He, Dipika Singhania, Robert Wang, and Angela Yao. Assembly101: A large-scale multi-view video dataset for understanding procedural activities. In _Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition_ , pages 21096–21106, 2022. 1, 3 

- [35] Dipika Singhania, Rahul Rahaman, and Angela Yao. C2ftcn: A framework for semi-and fully-supervised temporal action segmentation. _IEEE Transactions on Pattern Analysis and Machine Intelligence_ , 45(10):11484–11501, 2023. 5, 6, 7, 8, 4 

- [36] Ekta Sood, Simon Tannert, Philipp Mueller, and Andreas Bulling. Improving natural language processing tasks with human gaze-guided neural attention. In _Advances in Neural Information Processing Systems_ , 2020. 2 

- [37] Bilge Soran, Ali Farhadi, and Linda Shapiro. Generating notifications for missing actions: Don’t forget to turn the lights off! In _2015 IEEE International Conference on Computer Vision (ICCV)_ , pages 4669–4677, 2015. 3 

- [38] Julian Steil, Marion Koelle, Wilko Heuten, Susanne Boll, and Andreas Bulling. Privaceye: privacy-preserving headmounted eye tracking using egocentric scene image and eye movement features. In _Proceedings of the 11th ACM symposium on eye tracking research & applications_ , pages 1–10, 2019. 2 

- [39] Alexandros Stergiou, Brent De Weerdt, and Nikos Deligiannis. Holistic representation learning for multitask trajectory anomaly detection. In _IEEE/CVF Winter Conference on Applications of Computer Vision (WACV)_ , 2024. 2, 3, 5, 6, 7, 8 

- [40] Waqas Sultani, Chen Chen, and Mubarak Shah. Real-world anomaly detection in surveillance videos. In _The IEEE Conference on Computer Vision and Pattern Recognition (CVPR)_ , 2018. 3 

- [41] Hamed Rezazadegan Tavakoli, Esa Rahtu, Juho Kannala, and Ali Borji. Digging deeper into egocentric gaze prediction. In _2019 IEEE Winter Conference on Applications of Computer Vision (WACV)_ , pages 273–282, 2019. 2 

- [42] Xin Wang, Taein Kwon, Mahdi Rad, Bowen Pan, Ishani Chakraborty, Sean Andrist, Dan Bohus, Ashley Feniello, Bugra Tekin, Felipe Vieira Frujeri, Neel Joshi, and Marc Pollefeys. Holoassist: an egocentric human interaction dataset for interactive ai assistants in the real world. In _Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)_ , pages 20270–20281, 2023. 1, 2, 3, 5 

- [43] Dan Xu, Elisa Ricci, Yan Yan, Jingkuan Song, and N. Sebe. Learning deep representations of appearance and motion for anomalous event detection. In _British Machine Vision Conference_ , 2015. 3 

- [44] Yushi Yao, Chang Ye, Junfeng He, and Gamaleldin F. Elsayed. Teacher-generated spatial-attention labels boost robustness and accuracy of contrastive models. In _2023_

<!-- Page 11 -->

_IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)_ , pages 23282–23291, 2023. 2 

- [45] Yang Zheng, Yanchao Yang, Kaichun Mo, Jiaman Li, Tao Yu, Yebin Liu, Karen Liu, and Leonidas J. Guibas. Gimo: Gaze-informed human motion prediction in context. In _European Conference on Computer Vision_ , 2022. 2 

- [46] Yuchen Zhou, Linkai Liu, and Chao Gou. Learning from observer gaze:zero-shot attention prediction oriented by human-object interaction recognition, 2024. 2

<!-- Page 12 -->

# **Gazing Into Missteps: Leveraging Eye-Gaze for Unsupervised Mistake Detection in Egocentric Videos of Skilled Human Activities** 

# Supplementary Material 


![](assets/046/paper-0012-02.png)


<!-- Start of picture text -->
ground truth trajectory predicted trajectory<br>Low High<br>(a) Entropy (b) Euclidean (c) DTW<br>(d) Heatmap<br>Probability<br><!-- End of picture text -->

Figure 5. We consider three approaches to compare the ground truth with respect to the predicted trajectories in order to determine a mistake. (a) Entropy. (b) Euclidean distance between the two trajectories. (c) Dynamic Time Warping (DTW). (d) Average value of the ground truth trajectory at the predicted heatmaps. 

## **A. Implementation details** 

Our model implementation is primarily based on the approach outlined in [19], with hyperparameters adjusted accordingly. Below, we elaborate on the key aspects of our implementation, highlighting the differences and specific choices made to enhance the model’s performance. 

**Code Availability:** To ensure reproducibility and provide further implementation details, we will share the complete codebase upon publication. 

**Stride Adjustment:** In contrast to the stride of 8 used in [19], we opted for a stride of 1 during training. This modification allows the model to process consecutive frames without skipping, leading to finer granularity in temporal feature extraction. Our experiments indicated that this adjustment results in marginal improvements in both gaze estimation and mistake prediction accuracy. 

**Overfitting Prevention:** To mitigate the risk of overfitting, we incorporated a weight decay parameter set to 0.07. This regularization technique helps in controlling the complexity of the model by penalizing large weights, thereby promoting generalization to unseen data. 

**Batch Size and Frame Processing:** We configured the batch size to process 4 clips, each containing 8 frames. Specifically, our approach involves processing each video using non-overlapping windows of 8 consecutive frames. Consequently, each batch comprises 4 such windows, total- 

ing 32 frames per batch (i.e., 8 frames/clip _×_ 4 clips/batch = 32 frames/batch). This setting ensures that the model captures sufficient temporal context while maintaining manageable memory usage. 

**Training Loss** Following [19], we consider gaze prediction as defining a probability distribution over the 2D image plane of each input frame. Our proposed method leverages an architecture modified for gaze completion to predict missing segments of gaze trajectories. Ablations on single frames showed that looking at sequences of frames, which create a trajectory, is more effective for detecting anomalies due to the importance of changes over time. We train the model by minimizing the sum of the Kullback–Leibler divergence between the predicted gaze maps _P_<sup>ˆ</sup> ( _i_ ) and the ground truth ones _Q_ ( _i_ ) at each frame _i_ : 


![](assets/046/paper-0012-12.png)


**Graphical Illustration of scoring functions** Figure 5 illustrates the scoring function considered in this study. Entropy is the only scoring function which does not require any ground truth gaze as input, but only evaluates the level of uncertainty of the predicted heatmaps. The Euclidean and DTW scoring functions compute two forms of distances between predicted and ground truth trajectories. The heatmap scoring function evaluates the probability of predicted gaze under the points indicated by the ground truth trajectory. The heatmap scoring function achieves best results in our experiments. The main paper reports the formal definition of such scoring functions. 

**MoCoDAD Baseline** Following methodologies from [8], we employ a sliding window approach to segment each agent’s gaze/hands history. A window size of 8 frames is utilized, with the initial 4 frames dedicated to condition setting and the subsequent frames for the diffusion process. Hyperparameters are set as _λ_ 1 = _λ_ 2 = 1. Training proceeds end-to-end using the Adam optimizer with a learning rate of 1 _×_ 10<sup>_−_4</sup> , employing exponential decay over 25 epochs. The diffusion process utilizes _β_ 1 = 1 _×_ 10<sup>_−_4</sup> , _βT_ = 2 _×_ 10<sup>_−_2</sup> for _T_ = 10, and incorporates the cosine variance scheduler. 

**TrajREC Baseline** We followed the implementation proposed in _TrajREC_ [39] official code release<sup>10</sup> , adapting it for 

10https://github.com/alexandrosstergiou/TrajREC

<!-- Page 13 -->

|**Method**|**Fusion**|**F1**|**Recall**|**Precision**|
|---|---|---|---|---|
|Gaze Prediction|//|0.37|0.65|0.26|
|Gaze Completion|CH|0.38|0.67|0.29|
|Gaze Completion|CH + CORR|**0.40**|**0.70**|**0.31**|



Table 5. Comparison of GLC and the proposed Gaze Completion approach for Gaze Estimation on EPIC-Tent. 

gaze/hands trajectory analysis. The approach encodes temporally occluded gaze/hands trajectories, jointly learns latent representations of occluded segments, and reconstructs trajectories based on expected motions across different temporal segments. 

For both methods, if a frame does not contain gaze or hand keypoints, we exclude that frame from the score calculation for the segment. 

**Action Type Classification** To assess whether the type of performed action affects the performance of our method, we grouped actions contained in all three datasets into four categories: _Hand-Eye Coordination_ , _Object Manipulation_ , _Task Preparation_ , and _Inspection/Verification_ . For categorization, we prompted GPT-4 with a full list of actions using the following prompt: 

_In the context of how gaze affects actions, organize the following actions into groups that align with gaze literature. Group the actions from those that involve the most finegrained gaze coordination to those that involve less gaze precision._ 

The list was then manually revised. The full classification is shown in Table 6 

## **B. Additional Ablations** 

This section reports additional ablations which could not be included in the submitted paper due to space limits. 

### **B.1. Performance Comparison Across Action Types** 

Table 7 compares the performance of the considered baselines and our proposed method across different action types. 

The fully supervised C2F method achieves overall F1 and AUC scores of 0.58 and 0.72, respectively, maintaining stable performance across the four action types. The best performance is observed in _Inspect/Verify_ actions (F1: 0.74, AUC: 0.85), likely due to the strong visual cues inherent to these tasks (e.g., instruction sheets). 

In contrast, under both _One-Class_ and _Unsupervised_ scenarios, the proposed gaze-based approaches show varying performance depending on the action type. Stronger results are observed in tasks requiring _Hand-Eye Coordination_ and _Object Manipulation_ skills. Under the _One-Class_ supervision level, our method achieves an F1 score of 0.741 and an AUC of 0.839 for hand-eye coordination tasks (+21% 

vs Overall AUC). This indicates its effectiveness in learning “normal” attention patterns and detecting mistakes during complex actions where gaze and motor coordination are crucial. 

Conversely, for simpler actions, such as _Task Preparation_ and _Inspect/Verify_ , the proposed approaches are less effective. This is likely due to the high gaze variability inherent in less skill-intensive tasks. For instance, under the _One-Class_ supervision level, our method achieves an F1 score of 0.257 and an AUC of 0.543 (-24% vs Overall AUC) for task preparation actions. 

#### **B.1.1. Performance of the proposed gaze completion approach vs standard gaze prediction** 

Results in main paper Table 1 compared the performance of the proposed mistake detection method based on gaze completion versus different methods, including a baseline method based on the standard gaze prediction task implemented with the method of [19]. In Table 5, we instead compare the performance of the proposed gaze completion approach with standard gaze prediction based on [19] on the EPIC-Tent dataset. Just using channel fusion brings a performance boost, achieving an F1-score of 0 _._ 38, recall of 0 _._ 67, and precision of 0 _._ 29, while combining channel and correlation fusion brings best results with an F1-score of 0 _._ 40, recall of 0 _._ 70, and precision of 0 _._ 31, suggesting that conditioning on partial trajectories makes gaze prediction less uncertain and the proposed approach can leverage the informative content provided by the input trajectory surpassing the performance of standard gaze prediction. Moreover, the performance in Table 5 correlates with the results in Table 1 of the main paper, suggesting that accurate gaze prediction enhances mistake detection performance. Specifically, the proposed approach excels in gaze prediction for “Correct execution” frames, although it loses accuracy for “Mistake” frames. Given that “Correct execution” frames are generally more frequent, the F1 score improves overall, but the gap in prediction accuracy between “Correct execution” and “Mistake” frames widens. This discrepancy, however, benefits trajectory-based comparisons in mistake detection, as the increased accuracy in “Correct execution” frames helps to better identify errors in subsequent frames. 

### **B.2. Length of prediction and performance** 

Table 8 ablates performance for different prediction lengths. Smaller windows lead to higher precision due to short future trajectories being more predictable, but also lower recall, with the best F1 score when predicting 4 frames into the future. 

As the prediction window extends from 1 to 4 frames, the model’s recall improves, indicating more mistakes detected.

<!-- Page 14 -->

|**Category**|**Dataset**|**Actions**|
|---|---|---|
||EpicTent|assemble, insert stake, insert support, insert support tab, tie top|
|Hand-Eye Coordination|HoloAssist|touch, place, lift, press, flip, unscrew, rotate, slide, insert, close, turn, screw, disassemble|
||IndustReal|fit, plug, tighten, loosen|
||EpicTent|spread tent, place guyline|
|Object Manipulation|HoloAssist|adjust, empty, drop, clean, make, pour, split, mix-stir, stack-pile, load, mount, lock, unlock, shift, grab, pull|
||IndustReal|put, take, pull|
||EpicTent|pickup/open stakebag, pickup/open supportbag, pickup/open tentbag|
|Task Preparation|HoloAssist|withdraw, exchange, hold, break, approach, stand, align|
||IndustReal|align|
||EpicTent|instruction, place ventcover|
|Inspection/Verification|HoloAssist|inspect, validate, point, tap, click, push|
||IndustReal|check, browse|



Table 6. Classification of actions by category across datasets based on gaze involvement. 

|**Method**|**Sup. Level**|**Overall F1**|**Overall AUC**|**Hand-E**|**ye Coord.**|**Object**|**Manip.**|**Task**|**Prep.**|**Inspec**|**t/Verif.**|
|---|---|---|---|---|---|---|---|---|---|---|---|
|||||F1|AUC|F1|AUC|F1|AUC|F1|AUC|
|Random|//|0.36|0.51|–|–|–|–|–|–|–|–|
|TimeSformer [2]|Fully Supervised|0.49|0.67|0.452|0.615|0.474|0.636|0.551|0.691|0.532|0.678|
|C2F[35]|FullySupervised|**0.58**|**0.72**|0.506|0.600|0.5622|0.771|0.5138|0.686|0.741|0.857|
|GLC [19]|One-Class|0.46|0.66|0.524|0.704|0.495|0.665|0.425|0.579|0.396|0.556|
|Ours|One-Class|0.52|0.69|0.741|0.839|0.612|0.734|0.489|0.643|0.244|0.543|
|Ours + MoCoDAD(H)*|One-Class|**0.54**|**0.72**|0.753|0.872|0.631|0.764|0.498|0.657|0.257|0.543|
|GLC [19]|Unsupervised|0.44|0.61|0.542|0.694|0.474|0.657|0.406|0.563|0.338|0.526|
|Ours|Unsupervised|0.51|0.69|0.711|0.839|0.603|0.723|0.483|0.637|0.240|0.531|
|Ours + MoCoDAD(H)*|Unsupervised|**0.52**|**0.70**|0.714|0.862|0.602|0.754|0.489|0.646|0.253|0.535|



* Late fusion 

Table 7. Mistake detection results on EPIC-Tent by category. Best results are **in bold** , second best results are underlined. 

|**Baseline**|**Future frames**|**F1**|**Precision**|**Recall**|
|---|---|---|---|---|
|Gaze Completion|1|0.46|0.39|0.59|
|Gaze Completion|2|0.47|0.38|0.62|
|Gaze Completion|3|0.47|0.37|0.63|
|Gaze Completion|4|0.49|0.34|0.88|



Table 8. Performance ablation for different prediction lengths. Smaller windows yield higher precision but lower recall. The best F1 score is achieved when predicting 4 frames into the future. 


![](assets/046/paper-0014-07.png)


<!-- Start of picture text -->
F1 Score vs. Threshold<br>0.50<br>0.45<br>0.40<br>0.35<br>0.30<br>0.0 0.2 0.4 0.6 0.8<br>Threshold<br>F1 Score<br><!-- End of picture text -->

Figure 6. Length of prediction. 

However, this is offset by a reduction in precision, leading to more false positives. 

### **B.3. Chosen thresholds and sensitivity** 

We report F1 scores obtained at each method’s optimal thresholds, which we’ll report in the paper. Figure 6 shows how the F1 score of our best method ( _Unsupervised - Ours_ , Table 2 of main paper) changes when varying the threshold. Performance is stable for a range of threshold values. 

### **B.4. Qualitative Results and Failure Cases** 

Figure 7 illustrates the performance of various baselines and the proposed approach for both correct predictions in _Correct Execution_ cases (a) and in _Incorrect Execution_ cases (b). The top row displays the ground truth, followed by predictions from the GLC method, our proposed “Channel” approach, and, at the bottom, the ”Gaze Frame Correlation” approach. The last four columns display the predicted heatmap, where red peaks symbolize the 2D gaze predicted points. 

Figure 7a focuses on correct predictions related to _Correct Execution_ . The first row shows the actual gaze coordinates. Notably, in the second row corresponding to GLC, the predicted heatmaps exhibit inconsistencies, with

<!-- Page 15 -->

![](assets/046/paper-0015-00.png)


<!-- Start of picture text -->
GT<br>GLC<br>OUR<br>(Channel)<br>OUR<br>(Gaze-Frame-Corr)<br>GT<br>GLC<br>OUR<br>(Channel)<br>OUR<br>(Gaze-Frame-Corr)<br>(a) Correct prediction of Correct action.<br>GT<br>GLC<br>OUR<br>(Channel)<br>OUR<br>(Gaze-Frame-Corr)<br>GT<br>GLC<br>OUR<br>(Channel)<br>OUR<br>(Gaze-Frame-Corr)<br>(b) Correct prediction of Mistake Action.<br><!-- End of picture text -->

Figure 7. Qualitative examples. The first four columns represent the inputs (with the input gaze 2D points highlighted in orange). The latter four columns show the predicted outputs in the form of heatmaps.

<!-- Page 16 -->

varying peaks across consecutive frames. In contrast, our proposed method leverages temporal information to produce temporally consistent predictions. The “Channel” approach demonstrates better consistency than GLC, while the “Gaze Frame Correlation” method generates more defined heatmaps with fewer, more localized peaks around the gaze region. In this case, a _Correct Execution_ is identified based on the small gap between the ground truth and the predicted gaze trajectory. 

Figure 7b highlights predictions related to _Incorrect Execution_ . Here, our approach’s gaze predictions diverge from the ground truth, effectively flagging mistakes in action execution.
