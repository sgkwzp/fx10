# Understanding-Enhanced Model Collaboration for Long-Tailed Egocentric Mistake Detection

[Original PDF](../Understanding-Enhanced%20Model%20Collaboration%20for%20Long-Tailed%20Egocentric%20Mistake%20Detection.pdf)

Pages: 5

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

# **Understanding-Enhanced Model Collaboration for Long-Tailed Egocentric Mistake Detection** 

Boyu Han<sup>1,2</sup> Qianqian Xu<sup>1,3,*</sup> Shilong Bao<sup>2</sup> Zhiyong Yang<sup>2</sup> Ruochen Cui<sup>4,5</sup> Qingming Huang<sup>2,1,*</sup> 

1 State Key Laboratory of AI Safety, Institute of Computing Technology, CAS 

2 School of Computer Science and Tech., University of Chinese Academy of Sciences 

3 Beijing Academy of Artificial Intelligence 

4 Institute of Information Engineering, CAS 

5 School of Cyber Security, University of Chinese Academy of Sciences 

_{_ hanboyu23z, xuqianqian _}_ @ict.ac.cn 

_{_ baoshilong,yangzhiyong21,qmhuang _}_ @ucas.ac.cn 

cuiruochen25@mails.ucas.ac.cn 

## **Abstract** 

## **1. Introduction** 

_In this report, we address the problem of determining whether a user performs an action incorrectly from egocentric video data. To this end, we propose an UnderstandingEnhanced Model Collaboration Method (UE-MCM) that combines efficient coarse-grained video understanding with accurate fine-grained action reasoning. Specifically, UEMCM contains a small model branch and a large model branch. The large model branch focuses on whether the fine-grained action itself is executed incorrectly, while the small model branch jointly takes the coarse-grained video and fine-grained segment as input to identify actions that may be locally correct but inconsistent with the overall workflow. The small model branch is built on a CLIP4CLIP video encoder initialized from a CLIP model enhanced by Diffusion Contrastive Reconstruction, and the large model branch uses the Qwen3-VL Embedding model to extract high-capacity representations from fine-grained action segments. The small-branch prediction and the large-branch prediction are then adaptively fused by a lightweight collaboration gate. To handle the long-tailed distribution of mistake instances, we optimize the classifiers with complementary objectives, including reweighted cross-entropy, AUCoriented learning, and label-aware adjustment. The resulting system balances speed and accuracy, making it effective for detecting subtle, rare, and ambiguous mistakes in egocentric instructional videos._ 

This document introduces the solution proposed by the MR-CAS team for the Mistake Detection Challenge of the HoloAssist 2026 competition [12]. The goal of the task is to determine whether a user performs an action correctly in egocentric videos. Compared with standard action recognition, mistake detection requires not only recognizing what action is being performed, but also judging whether the execution deviates from the expected procedure. This makes the task sensitive to temporal context, hand-object interactions, and subtle visual differences between correct and incorrect operations. 

The problem is challenging for **two main reasons** . **First** , mistake samples are rare and often ambiguous, resulting in a long-tailed binary distribution where conventional crossentropy training tends to overfit the dominant correct class. **Second** , mistakes can occur at different semantic levels. Some mistakes are local execution errors, where the current fine-grained action itself is wrong. Others are procedural errors, where an action may be executed correctly in isolation but is inappropriate for the current stage of the coarse-grained workflow. Using a single model [5–7, 13] to cover both types of information is often inefficient and may weaken either coarse contextual understanding or finegrained action reasoning. 

To address these challenges, we design an **Understanding-Enhanced Model Collaboration Method (UE-MCM)** . UE-MCM contains a small model branch and a large model branch with different responsibilities. The large model branch focuses on fine-grained action correctness and predicts whether the observed action itself contains an execution mistake. The small model branch 

*Corresponding authors.

<!-- Page 2 -->

![](assets/079/paper-0002-00.png)


<!-- Start of picture text -->
Legend Weighted<br>MoE Diffusion Contrastive  CE<br>CLIP<br>Frozen Parameters Reconstruction<br>AUC LA<br>Optimizing Parameters<br>Original Enhanced<br>Coarse Grained Action<br>Small Model Branch<br>Long-tail<br>Optimization<br>𝑓<br>0 1<br>CLIP4CLIP Classifier<br>Large Model Branch<br>0 1<br>𝑓 Prediction<br>Fine Grained Action 0 1<br>Qwen3-VL Classifier<br>···<br><!-- End of picture text -->

Figure 1. **An overview of our UE-MCM.** The large model branch uses Qwen3-VL Embedding to determine whether the fine-grained action itself contains a mistake. The small model branch uses a DCR-enhanced CLIP4CLIP encoder to jointly encode the coarse-grained video and the fine-grained segment, thereby reasoning about whether the action is consistent with the overall workflow. 

performs fast coarse-grained video understanding by jointly observing the coarse-grained video and the fine-grained segment, which helps identify cases where an action looks correct locally but is wrong in the current workflow. We first enhance the visual representation of CLIP [11] using Diffusion Contrastive Reconstruction (DCR) [4]. The enhanced CLIP is then used to construct a CLIP4CLIP-style video encoder [9] for the small branch. In parallel, the large model branch adopts Qwen3-VL Embedding [8] to extract semantically rich features from fine-grained action segments. 

The predictions from the two branches are finally integrated by an adaptive collaboration gate, allowing the system to balance workflow-level consistency reasoning and action-level correctness judgment for each input. During optimization, we further combine multiple long-tail learning objectives, including reweighted cross-entropy [1], AUC-oriented learning [2, 14], and label-aware adjustment [10]. These objectives improve mistake recall, decision ranking, and probability calibration under skewed data distributions. 

Overall, UE-MCM integrates action-level mistake reasoning, workflow-level consistency reasoning, representation enhancement, and long-tail optimization. The following sections describe the proposed method and the experimental settings used for the HoloAssist mistake detection benchmark. 

## **2. Method** 

### **2.1. Overview** 

Given an egocentric video, the task is to predict whether the target action contains a mistake. We denote the coarsegrained action video as _V_ 0:<sup>_c_</sup> _T_<sup>, where</sup><sup>_T_is the total temporal</sup> length, and the fine-grained action segment as _Vt_<sup>_f_</sup> : _t_ + _τ_<sup>, where</sup> _t ≥_ 0 and _t_ + _τ ≤ T_ . The model outputs a binary prediction, where label 1 indicates a mistake and label 0 indicates a correct action. 

Figure 1 illustrates the proposed UE-MCM. The framework contains two complementary model branches. The large model branch is a Qwen3-VL Embedding encoder that takes only the fine-grained segment _Vt_<sup>_f_</sup> : _t_ + _τ_<sup>as input and</sup> judges whether the action itself is incorrectly executed. The small model branch is a DCR-enhanced CLIP4CLIP encoder that takes both the coarse-grained video _V_ 0:<sup>_c_</sup> _T_<sup>and the</sup> fine-grained segment _Vt_<sup>_f_</sup> : _t_ + _τ_<sup>asinput,allowingittojudge</sup> whether the action is consistent with the overall workflow. The two branch predictions are fused by an adaptive collaboration gate. During training, we use long-tail optimization objectives to improve the recognition of rare mistake samples. 

### **2.2. Small Model Branch** 

The small model branch is designed for efficient workflowlevel video understanding. CLIP provides strong image-

<!-- Page 3 -->

level semantic priors through large-scale image-text contrastive pre-training [11]. However, directly applying CLIP to egocentric mistake detection is insufficient because subtle mistakes often depend on both visual details and procedural context. 

To strengthen the visual encoder, we employ Diffusion Contrastive Reconstruction (DCR) [4]. DCR improves CLIP by introducing reconstruction-guided contrastive signals, encouraging the visual representation to preserve both class-discriminative semantics and detail-aware perceptual information. We use the enhanced CLIP visual encoder as the frame-level backbone of CLIP4CLIP [9]. The small model branch encodes both the coarse-grained video and the fine-grained segment: 


![](assets/079/paper-0003-02.png)


where _ϕs_ denotes the DCR-enhanced CLIP4CLIP encoder. The two representations are fused before classification: 


![](assets/079/paper-0003-04.png)


where _ψs_ ( _·_ ) is a lightweight fusion projection, and _⊙_ denotes element-wise multiplication. Since this branch is lightweight and observes both temporal scopes, it provides stable coarse action context and helps detect cases where an action may be correct in isolation but wrong within the current procedure. 

### **2.3. Large Model Branch** 

The large model branch focuses on fine-grained actionlevel mistake reasoning. We use Qwen3-VL Embedding [8] to encode the fine action segment. Compared with the small model branch, Qwen3-VL has stronger multimodal representation capacity and is better suited for recognizing whether the observed manipulation itself is incorrectly executed. For each fine-grained segment, the large model branch extracts 


![](assets/079/paper-0003-08.png)


where _ϕl_ denotes the Qwen3-VL Embedding model. We freeze the large embedding model during classifier training and use its output for the large-branch classifier. This keeps optimization efficient while preserving the semantic strength of the large model. 

### **2.4. Model Collaboration** 

The two branches provide complementary information. The large model branch predicts action-level mistakes from finegrained execution cues, while the small model branch predicts workflow-level inconsistencies by jointly observing the coarse-grained video and fine-grained segment. The branch representations are fed into their corresponding classification heads: 


![](assets/079/paper-0003-12.png)


where _gs_ and _gl_ are lightweight classification heads, and **z** _s,_ **z** _l ∈_ R<sup>2</sup> are logits for correct and mistake classes. 

To adaptively combine the two predictions, we use a collaboration gate. The gate takes the projected branch features as input and outputs normalized branch weights: 


![](assets/079/paper-0003-15.png)


[ _αs, αl_ ] = softmax � _Wg_ [ **h**<sup>¯</sup> _s_ ; **h**<sup>¯</sup> _l_ ; **h**<sup>¯</sup> _s ⊙_ **h**<sup>¯</sup> _l_ ] + **b** _g_ � _,_ (6) where _Ps_ ( _·_ ) and _Pl_ ( _·_ ) project branch features into a shared fusion space, and _⊙_ denotes element-wise multiplication. The final logits are computed as 


![](assets/079/paper-0003-17.png)


This design keeps the branch inputs explicit: the small branch combines coarse and fine videos for workflow-level reasoning, while the large branch focuses on the fine segment for action-level reasoning. Prediction-level collaboration then dynamically balances the two decisions. 

### **2.5. Long-Tail Optimization** 

Mistake detection is naturally imbalanced because correct actions appear much more frequently than mistakes. We therefore optimize the classifiers with complementary longtail objectives. 

**Reweighted CE Loss [1].** We use class-rebalanced crossentropy to increase the penalty for underrepresented mistake samples: 


![](assets/079/paper-0003-22.png)


where _pi,yi_ is the predicted probability of the ground-truth class and _wyi_ is computed according to class frequency. **AUC Loss [14].** To improve ranking quality under class imbalance, we adopt an AUC-oriented objective: 


![](assets/079/paper-0003-24.png)


where _s_<sup>+</sup> _i_<sup>and</sup><sup>_s−_</sup> _j_<sup>aremistakeandcorrectscores,respec-</sup> tively. This loss encourages mistake samples to receive higher scores than correct samples. **Label-Aware Loss [10].** We further use label-aware adjustment to calibrate the decision boundary for long-tailed data: 


![](assets/079/paper-0003-26.png)


where **_π_** denotes the empirical class prior. The final objective is 


![](assets/079/paper-0003-28.png)


By combining these objectives, the classifier learns from both calibrated class priors and pairwise ranking constraints, improving robustness for rare mistakes.

> Original page for checking 2 unresolved font glyphs.

![Original page 3](assets/079/verify-page-003.png)

<!-- Page 4 -->

Table 1. **Results obtained on the test set.** The champion and the runner-up are highlighted in **bold** and underline. 

|**Method**|**Modality**|**F-score**|**Corre**<br>**Precision**|**ct**<br>**Recall**|**Mista**<br>**Precision**|**ke**<br>**Recall**|
|---|---|---|---|---|---|---|
|Random|-|0.28|0.61|0.10|**0.15**|0.46|
||RGB|0.35|0.83|0.52|0.13|0.27|
||Hands|0.40|0.93|0.52|0.13|0.31|
|TimeSformer [12] (Baseline)|RGB+Hands|0.36|0.86|0.43|0.10|0.12|
||RGB+Hands+Eyes|0.32|0.89|0.43|0.11|0.50|
|UNICT Solution (2024 Top1)|RGB+Eyes|0.51|0.95|**0.93**|0.06|0.09|
|MR-CAS Solution [3] (2025 Top1)|RGB|0.57|**0.97**|0.60|0.08|**0.63**|
|Ours|RGB|**0.60**|**0.97**|0.72|0.11|0.62|



## **3. Experiments** 

In this section, we describe some details of the experiments and present our results. 

### **3.1. Implementation Details** 

We conduct all experiments using eight NVIDIA A100 GPUs. Frames are uniformly sampled from both the full coarse-grained video and the fine-grained segment. The backbone encoders are frozen during classifier training, and only the projection layers, classification heads, and collaboration gate are optimized. Branch features are projected into a shared hidden space before collaborative fusion. The classifier heads are implemented as lightweight multilayer perceptrons with dropout. We train the system with AdamW and a cosine learning-rate schedule. The entire model is optimized using the Adam optimizer with a learning rate of 1 _×_ 10<sup>_−_5</sup> . We set the batch size to 128 clips, each consisting of 32 frames. The model is trained for a total of 5 epochs. 

### **3.2. Results** 

Table 1 presents the performance of various models on the mistake detection task. Compared to Random and TimeSformer, our method significantly improves the F-score. Furthermore, in comparison to the top-performing method of 2024, our method achieves a substantial improvement in mistake recall. Compared with the top-performing method of 2025, our method further improves correct recall. Most notably, our method attains competitive performance using only the RGB modality, matching or even surpassing models that rely on multimodal inputs. 

## **References** 

- [1] Yin Cui, Menglin Jia, Tsung-Yi Lin, Yang Song, and Serge Belongie. Class-balanced loss based on effective number of samples. In _CVPR_ , pages 9268–9277, 2019. 2, 3 

- [2] Boyu Han, Qianqian Xu, Zhiyong Yang, Shilong Bao, Peisong Wen, Yangbangyan Jiang, and Qingming Huang. Aucseg: Auc-oriented pixel-level long-tail semantic segmentation. In _NeurIPS_ , pages 126863–126907, 2024. 2 

- [3] Boyu Han, Qianqian Xu, Shilong Bao, Zhiyong Yang, Sicong Li, and Qingming Huang. Dual-stage reweighted moe for long-tailed egocentric mistake detection. _arXiv preprint arXiv:2509.12990_ , 2025. 4 

- [4] Boyu Han, Qianqian Xu, Shilong Bao, Zhiyong Yang, Ruochen Cui, Xilin Zhao, and Qingming Huang. Guiding diffusion-based reconstruction with contrastive signals for balanced visual representation. In _CVPR_ , 2026. 2, 3 

- [5] Boyu Han, Qianqian Xu, Shilong Bao, Zhiyong Yang, Kangli Zi, and Qingming Huang. Lightfair: Towards an efficient alternative for fair t2i diffusion via debiasing pre-trained text encoders. In _NeurIPS_ , pages 22671–22724, 2026. 1 

- [6] Zhiying Leng, Shun-Cheng Wu, Mahdi Saleh, Antonio Montanaro, Hao Yu, Yin Wang, Nassir Navab, Xiaohui Liang, and Federico Tombari. Dynamic hyperbolic attention network for fine hand-object reconstruction. In _ICCV_ , pages 14894–14904, 2023. 

- [7] Zhiying Leng, Tolga Birdal, Xiaohui Liang, and Federico Tombari. Hypersdfusion: Bridging hierarchical structures in language and geometry for enhanced 3d text2shape generation. In _CVPR_ , pages 19691–19700, 2024. 1 

- [8] Mingxin Li, Yanzhao Zhang, Dingkun Long, Keqin Chen, Sibo Song, Shuai Bai, Zhibo Yang, Pengjun Xie, An Yang, Dayiheng Liu, et al. Qwen3-vl-embedding and qwen3-vl-reranker: A unified framework for state-of-theart multimodal retrieval and ranking. _arXiv preprint arXiv:2601.04720_ , 2026. 2, 3 

- [9] Huaishao Luo, Lei Ji, Ming Zhong, Yang Chen, Wen Lei, Nan Duan, and Tianrui Li. Clip4clip: An empirical study of clip for end to end video clip retrieval and captioning. _Neurocomputing_ , 508:293–304, 2022. 2, 3 

- [10] Aditya Krishna Menon, Sadeep Jayasumana, Ankit Singh Rawat, Himanshu Jain, Andreas Veit, and Sanjiv Kumar.

<!-- Page 5 -->

Long-tail learning via logit adjustment. In _ICLR_ , 2020. 2, 3 

- [11] Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, Gretchen Krueger, and Ilya Sutskever. Learning transferable visual models from natural language supervision. In _ICML_ , pages 8748–8763, 2021. 2, 3 

- [12] Xin Wang, Taein Kwon, Mahdi Rad, Bowen Pan, Ishani Chakraborty, Sean Andrist, Dan Bohus, Ashley Feniello, Bugra Tekin, Felipe Vieira Frujeri, et al. Holoassist: an egocentric human interaction dataset for interactive ai assistants in the real world. In _ICCV_ , pages 20270–20281, 2023. 1, 4 

- [13] Yin Wang, Zhiying Leng, Haitian Liu, Frederick WB Li, Mu Li, and Xiaohui Liang. Dynamic worlds, dynamic humans: Generating virtual human-scene interaction motion in dynamic scenes. _arXiv preprint arXiv:2601.19484_ , 2026. 1 

- [14] Zhiyong Yang, Qianqian Xu, Shilong Bao, Xiaochun Cao, and Qingming Huang. Learning with multiclass auc: Theory and algorithms. _TPAMI_ , 44(11):7747–7763, 2021. 2, 3
