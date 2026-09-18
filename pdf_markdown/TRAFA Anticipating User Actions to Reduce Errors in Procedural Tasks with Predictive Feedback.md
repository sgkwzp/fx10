# TRAFA Anticipating User Actions to Reduce Errors in Procedural Tasks with Predictive Feedback

[Original PDF](../TRAFA%20Anticipating%20User%20Actions%20to%20Reduce%20Errors%20in%20Procedural%20Tasks%20with%20Predictive%20Feedback.pdf)

Pages: 13

> Automatically converted from PDF. Check the original for exact equations, symbols, table alignment, and figure details.

<!-- Page 1 -->

# **TRAFA: Anticipating User Actions to Reduce Errors in Procedural Tasks with Predictive Feedback** 

Sassan Mokhtar 

Sassan Mokhtar Lars Doorenbos mokhtar@iai.uni-bonn.de doorenbos@iai.uni-bonn.de University of Bonn University of Bonn Bonn, Germany Bonn, Germany Lamarr Institute for Machine Learning and Artificial Intelligence Dortmund, Germany 

## Marius Bock 

Dominik Bach 

bock@iai.uni-bonn.de d.bach@uni-bonn.de University of Bonn University of Bonn Bonn, Germany Bonn, Germany Lamarr Institute for Machine Learning and Artificial Intelligence Dortmund, Germany 

Fatemeh Jabbari jabbari@iai.uni-bonn.de University of Bonn Bonn, Germany 

Juergen Gall gall@iai.uni-bonn.de University of Bonn Bonn, Germany Lamarr Institute for Machine Learning and Artificial Intelligence Dortmund, Germany 


![](assets/076/paper-0001-09.png)


<!-- Start of picture text -->
A B C<br><!-- End of picture text -->

**Figure 1: Overview of the prototype of the predictive feedback system. (A) A participant is tasked to assemble colored blocks in a specific order on a tabletop workspace, while the system observes hand motion and scene state. (B) The system forecasts near-future hand motion from recent observations, illustrated as fading hand trajectories, and combines these forecasts with scene context to anticipate the likely next placement. (C) When an imminent error, that is an incorrect placement, is anticipated, the system provides feedback through visual and auditory cues, enabling error prevention rather than post-hoc correction.** 

### **Abstract** 

Interactive assistance systems typically provide feedback after an action has been completed, supporting error recovery but not preventing the error itself. We present TRAFA, a real-time predictive feedback system for procedural tasks that intervenes before errors are committed. TRAFA operationalizes predictive feedback through a Track-Forecast-Act framework that tracks hand and object state, forecasts user motion conditioned on scene context, and triggers feedback when a predicted action is likely to violate task constraints. We instantiate this pipeline in a sequential assembly setting and evaluate it through both technical benchmarking and a controlled user study against conventional reactive feedback. Our results show that predictive feedback improves task accuracy and efficiency while maintaining a comparable number of feedback 

events. These findings position feedback timing as a key dimension in system design and show how real-time anticipation can be integrated into interactive systems to prevent errors before they occur. 

### **CCS Concepts** 

• **Human-centered computing** → **User studies** ; _Empirical studies in HCI_ . 

### **Keywords** 

error prevention, anticipatory interaction, hand motion forecasting

<!-- Page 2 -->

Mokhtar et al. 

### **1 Introduction** 

Humans frequently make mistakes in everyday activities, and in many domains, these errors are costly to detect and recover from. For instance, over 50% of surgical complications are directly caused by mistakes [44] and up to 90% of defects in assembly line production systems stem from human errors [26]. While some errors can be corrected at minimal cost if detected in time, others are costly to undo or even irreversible, leading to substantial damages. Reducing human error is therefore a central challenge in domains where task safety, reliability, and efficiency matter. 

Human-computer interaction (HCI) research has long addressed this challenge through feedback mechanisms that guide users toward correct task execution, with prior work exploring visual, auditory, and multimodal feedback across a wide range of procedural tasks. However, much of this work emphasizes feedback mechanisms that support post-hoc correction rather than anticipating errors before they occur [42]. Even systems that incorporate anticipatory sensing often evaluate prediction accuracy and early recognition rather than addressing how such predictions can be operationalized in a low-latency interactive loop that intervenes during ongoing action [27, 34, 51]. Although some recent work has begun to model the timing of intelligent suggestions [50], the system design question of how to turn anticipation into timely and actionable feedback remains largely open. 

In this work, we investigate _predictive feedback_ : feedback delivered while users can still redirect an ongoing action before making an error. Moving from reactive to predictive feedback requires more than detecting mistakes earlier; it requires a system that continuously tracks task-relevant states, anticipates near-future user motion, and decides when to intervene (Figure 2). To address this challenge, we present TRAFA, a real-time predictive feedback system that operationalizes this loop through a _Track-Forecast-Act_ paradigm: the system tracks hand and scene state, forecasts shorthorizon hand motion, and triggers feedback when a predicted action is likely to violate task constraints (Figure 1). We instantiate this framework in a controlled sequential assembly task, where users reproduce a target color sequence by stacking interlocking blocks. In this setting, the system continuously predicts near-future hand trajectories and uses these forecasts together with scene state to assess whether an incorrect placement is likely to occur. By grounding intervention decisions in short-horizon motion prediction, the system can provide feedback while the action is still in progress, making predictive feedback practical for continuous procedural interaction. 

We evaluate the proposed system in two ways. First, we benchmark the anticipation module against alternative designs to assess whether the system is accurate enough to support pre-commitment intervention. Second, we conduct a within-subject user study with 20 participants comparing predictive feedback against reactive feedback and a no-feedback baseline across auditory, visual, and multimodal conditions. Across conditions, predictive feedback significantly improves task accuracy and efficiency relative to reactive feedback, while maintaining a comparable number of feedback events. These findings show that the benefit of the proposed system comes not from issuing more feedback, but from issuing it early enough to prevent an incorrect action from being completed. 

Together, the results demonstrate how real-time anticipation can be operationalized in an interactive system to support error prevention in procedural tasks. 

Our main contributions are as follows: 

- (1) A _Track-Forecast-Act_ system for predictive feedback that couples scene tracking, short-horizon motion forecasting, and intervention logic in real time. 

- (2) A scene-aware anticipation and intervention method that uses hand motion forecasts together with the task state to trigger feedback before an incorrect placement is made. 

- (3) An evaluation combining technical benchmarking and a controlled user study, showing that predictive feedback improves task accuracy and efficiency without increasing feedback frequency. 

### **2 Related Work** 

Feedback is a foundational concept in human–computer interaction, supporting error awareness, learning, and task regulation. Classic HCI frameworks emphasize feedback as a way to keep users informed about the system state and results of their actions, helping them understand what has occurred and to recognize and recover from errors [31, 33]. Prior work has demonstrated that feedback design strongly influences how users interpret system behavior and regulate their actions [19]. 

A large body of research has explored feedback content and modality, most commonly visual, auditory, and tactile feedback. While tactile systems have been shown to be able to steer human movements [6], this work specifically focuses on audio and visual feedback and their combination. Visual and auditory feedback have been widely studied as a reactive mechanism, signaling errors or confirming correctness after an action has been completed in sequential and procedural tasks [16, 38]. Prior studies show that modalities can improve learnability, usability, and task performance [15, 35]. At the same time, visual feedback can be distracting in cognitively demanding tasks [48], motivating research on auditory and multimodal alternatives. Early works on non-speech audio showed that simple auditory cues can effectively convey errors and status without requiring visual attention [18], while later work examined how different modalities can play complementary roles in interaction [12, 13, 43, 49]. 

Beyond feedback modality, HCI research has long emphasized the importance of anticipation in interaction. Early work argued that systems should help users understand the expected outcomes of their actions rather than relying solely on feedback after action completion [11]. This perspective motivated feedforward design strategies, in which expected action outcomes are revealed prior to commitment to support planning and decision-making [46]. Feedforward mechanisms, however, are typically defined in advance by the interface and present static previews of possible outcomes, independent of the user’s ongoing motion or moment-to-moment action execution. In parallel, research in motor control shows that the timing of information, such as delayed or anticipatory feedback, can influence how people coordinate actions and engage in anticipatory behavior [41, 45]. Together, these perspectives suggest that not only the content of feedback, but also its timing relative to ongoing action, can shape user behavior.

<!-- Page 3 -->

TRAFA: Anticipating User Actions to Reduce Errors in Procedural Tasks with Predictive Feedback 


![](assets/076/paper-0003-01.png)


<!-- Start of picture text -->
Reactive Feedback<br>Feedback User Undo<br>User Action Mistake Made System Detect User Retry Correct Action<br>Issued Action<br>Predictive Feedback<br>User Action System Feedback User Redirect Correct Action<br>Forecast Issued<br>Time<br><!-- End of picture text -->

**Figure 2: Difference between reactive and predictive feedback. Reactive feedback (top) intervenes after error completion, whereas predictive feedback (bottom) intervenes earlier based on anticipated action outcomes. In this way, predictive feedback redirects users before committing to errors.** 

At the same time, prediction of human motion and intent has been widely studied in interactive and collaborative systems, particularly in robotics and assistive domains. Prior work used motion forecasting, and in some cases intent inference, to enable smoother handovers, safer collaboration, and more efficient coordination by allowing systems to adapt their behavior in anticipation of human actions [17, 25, 32]. Related research has also leveraged human motion prediction to provide anticipatory warning or corrective feedback in ergonomics and posture training systems [7]. Other research has explored real-time intention recognition using multimodal signals to support assistive or cooperative behavior [9, 10], or to enable anticipatory intervention in domains such as autonomous driving [21]. In most of these systems, prediction is primarily used to guide system behavior, such as motion planning or safety constraints, rather than to determine when evaluative feedback should be delivered to the user. 

Although prior work offers extensive guidance on feedback content, modality, and adaptivity in procedural tasks [14, 36], feedback timing is treated as an implicit consequence of system state changes rather than an explicit interaction design variable. Recent work on context-aware procedural assistants further motivates this area: prior work has explores smartwatch-based task support through step tracking, context-aware assistance, and proactive intervention, while later work scales such assistants through demonstrationbased learning and mixed-initiative dialogue [2–5]. Related work on work interruptions [37], robotic decision support [30] and coactive design [22] emphasizes that supportive systems should preserve observability, predictability, and directability in joint activity. To our knowledge, this work presents the first predictive feedback system forecasting hand motion to control the timing of feedback delivered to a user during an ongoing task. This framing positions feedback timing as a central design concern and motivates an empirical investigation of how earlier intervention affects performance and behavior in a procedural task. 

### **3 Method** 

We consider procedural tasks in which users manipulate physical objects given task instructions, and where an incorrect action becomes costly once it is completed. In such settings, conventional feedback is often reactive: the system detects an error only after the user has already committed the action, requiring recovery through undoing or correction. Our goal is to enable _predictive feedback_ , in which the system intervenes while the action is still in progress and the user can still change course. 

Realizing predictive feedback requires solving three coupled problems in real time. First, the system must maintain a taskrelevant state, including the current configuration of objects and the user’s recent interactions with them. Second, it must anticipate the user’s near-future motion early enough for intervention to remain actionable. Third, it must translate predicted motion and task state into feedback decisions that are specific enough to prevent errors without over-triggering unnecessary alerts. We address this challenge in the context of a sequential assembly task, but design the system around a more general requirement shared by many procedural interactions: anticipating likely action outcomes before commitment. 

To implement predictive feedback, we introduce TRAFA, a _TrackForecast-Act_ system (Figure 3). The system takes as input a short RGB video sequence and produces feedback when the predicted next action is likely to violate task constraints. The pipeline consists of three stages: _Track_ , which estimates task-relevant hand and scene state; _Forecast_ , which predicts short-horizon future hand motion conditioned on scene context; and _Act_ , which converts predicted motion and task state into feedback decisions. 

### **3.1 Track: Perception and Task-State Estimation** 

The _Track_ stage obtains and maintains the task-relevant state required for predictive intervention. In our setup, which will be described in more detail in Sec. 3.4, observations come from an overhead RGB camera observing a tabletop sequential assembly task, where users are tasked to stack seven distinct Duplo blocks in a given order. From this video stream, the system estimates both the

<!-- Page 4 -->

Mokhtar et al. 


![](assets/076/paper-0004-01.png)


<!-- Start of picture text -->
Track Forecast Act<br>Hand Pose  Expected: Red<br>Estimator Motion<br>MediaPipe Encoder Predicted: Cyan<br>ST-GCN Mismatch Detected!<br>Fusion<br>ColorsScene Head<br>Object MLP Scene MLP<br>Detector<br>Encoder<br>YOLO CenterColor MLP<br>Input:  RGB Video of last 15 MLP<br>frames (~1 sec) Forecast next 15 frames<br>Scene State<br>(~1 sec)<br><!-- End of picture text -->

**Figure 3: Overview of TRAFA, our Track-Forecast-Act system. The system takes as input the last 15 observed RGB frames. The Track module estimates hand pose and scene state from the detected objects. The Forecast module predicts the hand pose for the next 15 frames using a scene-aware forecasting model composed of a motion encoder, scene encoder, and fusion head. The Act module uses the predicted motion and current task state to anticipate whether the next placement will violate task instructions, and issues visual and/or auditory feedback before the incorrect action is done.** 

current scene configuration and the user’s recent interaction history. This includes detecting the available blocks in the workspace, inferring their colors and positions, identifying the current top block in the assembly region, and tracking which block the user most recently interacted with. 

To maintain this state, we use a lightweight multi-stage vision pipeline. First, a YOLOv8n detector [20, 40] identifies all Duplo blocks in the workspace. The detector was trained on a custom dataset generated through a semi-automated annotation pipeline: SAM2 [39] was used to produce initial segmentation masks on recorded task trajectories, which were then manually verified and corrected. The resulting dataset comprises approximately 900 annotated frames. Following detection, block colors are inferred using 3-layer MLPs applied to masked image regions. We use two specialized MLPs: (1) a scene-level color classifier that assigns a color label to each detected block in the workspace, and (2) a center-piece classifier that determines the color of the top block on the base plate. Separating these two predictions improves robustness when the center region is partially occluded by the user’s hands. 

In parallel, hand pose is extracted from the RGB stream using MediaPipe [28]. Recent hand-object interactions are inferred from spatial overlap between the detected block bounding boxes and the fingertips’ location. The estimated hand trajectories are also used to provide the motion history required for forecasting. Detected blocks are assigned discrete symbolic states (e.g., _resting_ , _candidate_ , _placed_ ) based on their spatial location and interaction history. This scene representation decouples downstream forecasting and intervention logic from raw detector outputs and enables low-latency reasoning about likely placement outcomes. 

actions in assembly tasks are strongly constrained by the locations of candidate blocks and the assembly region. 

We implement this stage using a scene-aware Spatio-Temporal Graph Convolutional Network (ST-GCN) [47]. The model takes as input the last 15 observed hand-pose frames (approximately one second) and predicts the next 15 frames. Hand motion is represented as a graph over 42 keypoints (two hands), with per-keypoint features given by 2D image coordinates and instantaneous velocities. A motion encoder based on stacked ST-GCN blocks extracts a compact representation of recent hand dynamics. In parallel, the bounding boxes of the detected blocks are encoded by a lightweight MLP to produce a scene embedding summarizing the spatial layout of the workspace. The motion and scene embeddings are fused and decoded to predict future hand poses over the forecasting horizon. The full forecaster contains approximately 210 _,_ 000 trainable parameters. 

The one-second prediction horizon was chosen to preserve actionability: it is long enough to be perceived and acted upon during an ongoing movement, given typical human visual-motor response latencies of 200 − 300 _𝑚𝑠_ [8], but short enough to avoid the uncertainty associated with longer-range motion prediction. To support reliable intervention, the model is trained with the objective 

L = L _𝑡𝑖𝑝_ + _𝛽_ L _𝑝𝑜𝑠𝑒_ + _𝜆_ L _𝑠𝑚𝑜𝑜𝑡ℎ_ 

where L _𝑡𝑖𝑝_ is a temporally weighted mean squared error on fingertip positions, L _𝑝𝑜𝑠𝑒_ is the mean squared error over all hand keypoints, and L _𝑠𝑚𝑜𝑜𝑡ℎ_ penalizes velocity inconsistency between predicted and ground-truth trajectories. This design emphasizes fingertip accuracy, which is most relevant for assembly tasks. We use _𝛽_ = 0 _._ 1 and _𝜆_ = 0 _._ 05. 

### **3.2 Forecast: Scene-Aware Motion Anticipation** 

Given the tracked scene state and recent hand motion, the _Forecast_ stage forecasts the user’s hand trajectory as illustrated in Figure 4. We formulate this as a conditional motion forecasting problem: rather than predicting motion in isolation, the model conditions future hand motion on the spatial configuration of objects, since 

### **3.3 Act: Intervention Logic and Feedback Policy** 

The _Act_ stage converts predicted motion and current task state into intervention decisions. A predictive alert is triggered if the forecast hand trajectory is predicted to enter the assembly region R, where the assembly happens, within the next 15 frames and the block most recently interacted with does not match the next required color in

<!-- Page 5 -->

TRAFA: Anticipating User Actions to Reduce Errors in Procedural Tasks with Predictive Feedback 

the sequence. In this way, the system uses anticipated motion and current task state to infer that an incorrect placement is imminent, allowing intervention during the ongoing action rather than after the error has already been made. 

The feedback implementation itself is modular: the system can render visual feedback, auditory feedback, or both. Visual feedback is presented on the monitor by flashing the screen red and displaying the expected color together with the incorrect one as illustrated in Figure 6. Auditory feedback is delivered through speakers using a warning tone followed by a spoken color cue. The experimental comparison of predictive, reactive, and no-feedback conditions across these output modalities is described in Section 3.5. 

### **3.4 Task Instantiation** 

We instantiate the proposed system in a tabletop sequential assembly task as illustrated in Figure 6. The workspace consists of seven distinct Duplo<sup>1</sup> blocks (Red, Orange, Yellow, Blue, Lime, Cyan, Pink) arranged around a fixed green base plate on a matte white surface (Figures 4 and 5). Before each trial, the seven blocks were placed in fixed spatial locations around the base plate, while the color assigned to each location was randomized. Participants were free to grasp, move, and reorganize pieces during the task. 

At the beginning of each trial, a three-second countdown preceded the presentation of a target sequence of the seven colors on a 24-inch monitor positioned 90 cm in front of the participant as illustrated in Figure 6. The sequence was shown as written color names for one second and then removed. Participants were then asked to reproduce the target sequence by stacking the corresponding blocks onto the central base plate in the correct order. 

We define errors in the following way: let R denote the assembly region, defined as a fixed rectangular area of 95 × 60 pixels centered on the base plate. An error occurs when a block is placed in R and its color does not match the next required color in the target sequence. Touching, grasping, or moving an incorrect block without placing it on the base plate was not considered an error. This conservative definition is typical in assembly tasks [24], since it preserves exploratory behavior and allows participants to inspect, rearrange, and reconsider pieces without triggering feedback prematurely. 

This task provides a controlled testbed for predictive feedback for three reasons. First, it has a clearly defined symbolic task state, since correctness depends on the next required block in the sequence. Second, errors become identifiable only at placement time, while still leaving a short pre-commitment window during the ongoing reach-to-place motion. Third, the task permits exploratory behavior such as touching or rearranging blocks before placement, making it suitable for studying when intervention should occur without over-triggering feedback. 

All tracking, forecasting, and feedback components were implemented as ROS2 nodes [29] and executed on a workstation equipped with an NVIDIA TITAN RTX GPU (24 GB VRAM). The workspace was captured using an overhead Intel RealSense D455 camera mounted perpendicular to the table surface. The camera streamed RGB video at a resolution of 1280 × 720 pixels and 15 FPS. 

> 1Duplo blocks are large interlocking plastic building blocks designed for young children, www.lego.com/en-us/themes/duplo/about 

For processing, frames were cropped to a 720 × 720 region containing only the workspace. Hand pose was extracted from the RGB stream using MediaPipe [28] at approximately 15 Hz, which served as the control frequency for forecasting and intervention. Across all components, the full system achieved a mean effective processing rate of 15 _._ 02 FPS (SD= 0 _._ 58), corresponding to an average processing cycle of approximately 67 ms per frame. This runtime is below the typical human visual–motor response latency [8], allowing the system to issue feedback while the user’s action is still in progress. 

### **3.5 User Study Protocol** 

To evaluate the interaction effects of predictive feedback, we conducted a within-subject user study with 20 participants (15 male, 5 female; age 23–38 years, _𝑀_ = 29, _𝑆𝐷_ = 4 _._ 3), recruited at university campus. 

None of the participants was affiliated with any of the authors or had used the system previously. All participants provided their informed consent. Participants took part individually. Each session lasted approximately 15 to 20 minutes and was conducted in the same laboratory room, with the door closed and the overhead lights turned on throughout the experiment. Two researchers were present throughout each session to provide instructions, operate the experimental scripts, and set up the blocks in the appropriate randomized order at the start of each trial. To limit the effect of external interventions during the experiment, researchers refrained from talking to participants, yet allowed them to ask questions if something remained unclear. 

Participants received printed task instructions before the experiment. To avoid biasing participants toward a specific feedback modality or particular movement strategies through demonstration, no practice trials or demonstration videos were provided to participants prior to their first session. Each participant completed two experimental rounds to reduce noise from single-trial variability, with results then being averaged per participant for analysis. In each round, participants performed the task once under each of the seven feedback conditions, resulting in a total of 2 × 7 × 20 = 280 trials. To eliminate measured differences between each feedback trial being the result of participants getting accustomed to the task, a new target color sequence was randomly generated for each individual trial, and the order of the seven feedback conditions was randomized within each round. Short breaks were allowed to be taken by participants at any point in the experiment to reduce fatigue. 

Across all conditions, the task, sensing pipeline, and feedback representations were identical; only the timing and modality of feedback differed: 

- **No Feedback:** no feedback was provided during the task. 

- **Reactive Audio:** auditory feedback was provided only after the system detected an incorrect placement. 

- **Reactive Visual:** visual feedback was provided only after the system detected an incorrect placement. 

- **Reactive Audio+Visual:** both auditory and visual feedback were provided only after the system detected an incorrect placement. 

- **Predictive Audio:** auditory feedback was provided when the system predicted an imminent incorrect placement.

<!-- Page 6 -->

Mokhtar et al. 


![](assets/076/paper-0006-01.png)


<!-- Start of picture text -->
Possible Feedback<br>Time<br><!-- End of picture text -->

**Figure 4: Example of predictive intervention from forecast hand motion. From recent hand observations, the system forecasts near-future hand trajectories (colored curves). If the forecast motion is expected to enter the assembly region and the most recently interacted block does not match the next required block, the system anticipates an incorrect placement and issues feedback before the action is completed.** 


![](assets/076/paper-0006-03.png)


exactly matches the target sequence. Any trial containing at least one incorrect placement was counted as a failure, even if the incorrect block was later removed or corrected. 

- **Edit Distance** captures stepwise differences in performance beyond binary success using the edit distance. Specifically, we computed the minimum number of insertions, deletions, or substitutions required to transform the participant’s placed sequence into the target sequence. 

- **Feedback Frequency** assesses the cost of assistance, measured by the average number of feedback events per trial. 

- **Efficiency** measures the number of correctly placed blocks per minute. 

- **Total time** is the time taken for the trial. 

**Figure 5: Seven distinct colored Duplo building blocks used during the experiment.** 

- **Predictive Visual:** visual feedback was provided when the system predicted an imminent incorrect placement. 

- **Predictive Audio+Visual:** both auditory and visual feedback were provided when the system predicted an imminent incorrect placement. 

After completing both rounds, participants filled out a brief poststudy questionnaire. In addition to demographic information, the questionnaire asked participants to indicate their preferred feedback condition, rank the feedback modalities (audio, visual, and audio+visual), and optionally provide free-text comments explaining their preferences. These responses were used to complement the quantitative analysis. 

### **4 Results** 

To evaluate the effectiveness of predictive feedback relative to other conditions, we measure task performance using a set of complementary metrics: 

- **Success Rate** measures whether a trial was considered successful (binary). A trial is considered successful if and only if the sequence of blocks placed on the base plate 

As several metrics are bounded or non-normally distributed (e.g., binary success and discrete edit distance), we used non-parametric tests for all within-subject comparisons. Specifically, we applied two-sided Wilcoxon signed-rank tests to participant-averaged outcomes when comparing predictive, reactive, and no-feedback conditions. To control family-wise error across these four related comparisons, we applied the Holm–Bonferroni procedure. In addition to _𝑝_ -values, we report Wilcoxon effect sizes as _𝑟_ = _𝑍_ /√ _𝑁_ , where _𝑁_ = 20 participants. We complement the metrics with participantlevel distribution plots showing medians, interquartile ranges, and individual data points. 

### **4.1 Main Results** 

**Predictive Feedback Improves Accuracy and Efficiency.** Table 1 shows that predictive feedback substantially improved task accuracy compared to both reactive feedback and no feedback. When aggregated across modalities, predictive feedback increased the average task success rate from 15 _._ 0% in reactive and 12 _._ 5% in nofeedback conditions to 65 _._ 0%. Similarly, the edit distance decreased from an average of 2 _._ 06 and 2 _._ 70 errors per trial to 0 _._ 74 with predictive feedback. The Wilcoxon signed-rank tests confirmed that predictive feedback significantly outperformed reactive feedback in both success rate ( _𝑝_ = 0 _._ 0001) and edit distance ( _𝑝_ = 0 _._ 0001).

<!-- Page 7 -->

TRAFA: Anticipating User Actions to Reduce Errors in Procedural Tasks with Predictive Feedback 


![](assets/076/paper-0007-01.png)


<!-- Start of picture text -->
Begin<br>User Action<br>(i)<br>Target  Motion<br>Forecast<br>sequence<br>Correct Incorrect<br>Move Move<br>+<br>Feedback<br>issued<br>(ii)<br>User<br>Error  Redirect<br>display<br>Correct<br>User Action<br>(a) Experimental setup (b) Auditory + visual feedback (c) Predictive feedback<br>Time<br>low-latency prediction<br><!-- End of picture text -->

**Figure 6: Experimental setup and feedback paradigm. (a) Participants performed a tabletop sequential assembly task while an overhead camera captured the workspace. (b) The monitor displayed (i) the target color sequence at the beginning of each trial and (ii) the visual error display; auditory cues could be presented together with the visual display. (c) In the predictive condition, the system forecasted the user’s ongoing motion and issued feedback before an incorrect placement was completed, allowing the user to redirect the action toward the correct move.** 

Furthermore, predictive feedback led to a significant increase in efficiency, from 7 _._ 7 correct blocks per minute to 8 _._ 7 ( _𝑝_ = 0 _._ 012), indicating faster progress through the task while maintaining correctness. Predictive feedback did not lead to a significant reduction in overall task completion time. This is expected given the low cost of errors in the task, where incorrect blocks could easily be removed and corrected without much penalty. Instead, the gains in efficiency arise from fewer incorrect placements and corrections. Together, these findings demonstrate that predictive feedback improves both absolute and relative accuracy while increasing task efficiency, showing its effectiveness for preventing errors in sequential manual assembly tasks. 

Notably, reactive feedback resulted in success rates comparable to the no-feedback conditions, while yielding lower edit distances. This reflects the timing constraints of reactive feedback. Since it is delivered only after an incorrect placement is completed, it cannot prevent task failure in a strictly ordered sequence. However, it can still reduce the number of subsequent errors once a mistake has occurred. No-feedback trials produced the highest edit distances overall, indicating that feedback in general supports reliable task completion. 

**Predictive Feedback Does Not Increase Feedback Frequency.** 

A central design goal of predictive feedback is to improve task performance without increasing the amount of feedback delivered, as excessive or frequent feedback can disrupt user attention and increase cognitive load [1]. To assess this, we compared the number of feedback events across reactive and predictive feedback conditions. As shown in Table 1, the average number of feedback events did not differ significantly between predictive and reactive feedback. Wilcoxon signed-rank tests revealed no significant effect of feedback type on feedback frequency ( _𝑝_ = 0 _._ 57). Thus, the accuracy and efficiency gains observed with predictive feedback were 

not achieved by issuing more feedback. Instead, predictive feedback improved performance by changing _when_ feedback was delivered, intervening earlier in the action sequence before incorrect placements were completed. All reported main effects remained significant under family-wise correction. 

Figure 7 visualizes the participant-level distributions underlying all comparisons. The distributional view is consistent with the nonparametric analysis: predictive feedback increased success rate and reduced edit distance relative to reactive feedback, while feedback frequency remained comparable. After Holm correction across the four primary outcomes, predictive feedback remained significantly better in success rate ( _𝑝_ corr = 0 _._ 0003, _𝑟_ = 0 _._ 88), edit distance ( _𝑝_ corr = 0 _._ 0003, _𝑟_ = 0 _._ 88), and efficiency ( _𝑝_ corr = 0 _._ 0240, _𝑟_ = 0 _._ 56), whereas feedback frequency did not differ significantly ( _𝑝_ corr = 0 _._ 5730, _𝑟_ = 0 _._ 13). Participant-level paired-difference plots for the four primary metrics are provided in Appendix A to visualize the within-subject effect patterns underlying these aggregate results. 

### **4.2 Modality Analysis** 

We next examined whether feedback modality (Audio, Visual, or Audio+Visual) influenced task performance or feedback cost for predictive feedback. Wilcoxon signed-rank tests revealed no statistically significant differences between audio and visual feedback for success rate ( _𝑝_ = 0 _._ 24), edit distance ( _𝑝_ = 0 _._ 25), efficiency ( _𝑝_ = 0 _._ 08), or feedback count ( _𝑝_ = 0 _._ 29). Similarly, no significant differences were observed between Audio-only and Audio+Visual feedback for success rate ( _𝑝_ = 0 _._ 35), edit distance ( _𝑝_ = 0 _._ 38), efficiency ( _𝑝_ = 0 _._ 26), or feedback count ( _𝑝_ = 0 _._ 51). 

Although none of these comparisons reached statistical significance, audio feedback showed slightly higher success rates and efficiency than visual-only feedback (Table 1). These trends suggest a possible advantage of auditory cues for maintaining task flow, but given the absence of significant effects, modality differences should be interpreted cautiously.

<!-- Page 8 -->

Mokhtar et al. 

**Table 1: Evaluating the effectiveness of predictive feedback in our user study. We report five performance metrics for the seven different feedback conditions (mean** ± **SD across participants,** _𝑁_ = 20 **) and their averages, with the best numbers shown in bold. Predictive feedback significantly improves the absolute task success rate and decreases edit distance without increasing feedback frequency. Aggregated rows report participant-level averages pooled across feedback modalities within each feedback timing condition.** 

||**Success**<br>**Rate**<br>↑|**Edit**<br>**Distance** <sup>↓</sup>|**Feedback**<br>**Frequency** <sup>↓</sup>|**Efficiency**<br>**(# correct/min)** <sup>↑</sup>|**Total time**<br>**(in sec)**<br>↓|
|---|---|---|---|---|---|
|**No Feedback**|12.5%|2.70 (±0.98)|-|7.3 (±3.4)|33.1 (±10.7)|
|**Reactive Audio**|17.5%|1.98 (±1.02)|2.3 (±1.5)|7.6 (±3.2)|46.0 (±7.1)|
|**Reactive Visual**|10.0%|2.30 (±1.20)|2.6 (±1.5)|7.3 (±3.2)|49.3 (±11.8)|
|**Reactive Audio+Visual**|17.5%|1.90 (±1.01)|**2.1 (±1.0)**|8.3 (±2.5)|46.1 (±9.9)|
|**Reactive (aggregated)**|15.0%|2.06 (±1.08)|2.3 (±1.3)|7.7 (±3.0)|47.1 (±9.6)|
|**Predictive Audio**|**70.0%**|0.75 (±1.19)|2.5 (±1.5)|**9.1 (±2.7)**|44.4 (±10.3)|
|**Predictive Visual**|60.0%|0.93 (±1.28)|2.7 (±1.6)|8.0 (±2.0)|49.7 (±8.9)|
|**Predictive Audio+Visual**|65.0%|**0.53 (±0.62)**|2.3 (±1.3)|8.9 (±2.4)|46.7 (±9.0)|
|**Predictive (aggregated)**|65.0%|0.74 (±1.03)|2.5 (±1.5)|8.7 (±2.4)|46.9 (±9.4)|
|Success Rate<br>Edit|Distance|Feedback Fr|equency<br>20.0|Efficiency|Total Time|
|No Feedback<br>Reactive<br>Predictive<br>0.00<br>0.25<br>0.50<br>0.75<br>1.00<br>*<br>No Feedback<br>R<br>0<br>1<br>2<br>3<br>4|eactive<br>Predictive<br>*|Reactive<br>1<br>2<br>3<br>4<br>5|Predictive<br>N<br>2.5<br>5.0<br>7.5<br>10.0<br>12.5<br>15.0<br>17.5|o Feedback<br>Reactive<br>Predictive<br>*|No Feedback<br>Reactive<br>Predictive<br>20<br>30<br>40<br>50<br>60<br>70|



**Figure 7: Distribution of participant-level metrics across conditions (** _𝑁_ = 20 **). Each violin shows the kernel density estimate; horizontal bars indicate the median and interquartile range; dots are individual participant values. Stars denote pairwise comparisons between Reactive and Predictive conditions that were statistically significant (Wilcoxon signed-rank,** _𝑝 <_ 0 _._ 05 **).** 

### **4.3 User Preferences** 

A post-study questionnaire completed by all participants after exposure to all feedback conditions provided additional insight into their subjective experiences. A majority of participants reported a preference for predictive feedback over reactive feedback (12 vs. 7), with one participant preferring the no-feedback condition (see Figure 8). Participants’ explanations emphasized differences in how feedback supported ongoing action. While most responses favored predictive feedback, some concerns were raised: one participant described predictive audio feedback as _“sometimes too aggressive”_ though this effect was mitigated when combined with visual cues. Overall, the stronger preference for predictive feedback suggests that participants valued assistance that helped them avoid errors in advance and did not perceive such intervention as intrusive. 

Across feedback modalities, many participants expressed a preference for auditory over visual feedback, describing audio cues as _“fast”_ and _“more direct”_ , allowing them to maintain visual attention on the workspace. As one participant remarked, _“The sound let me know immediately without having to look away from the blocks”_ . In contrast, visual feedback alone was often perceived as requiring users to actively shift attention and _“actively look for feedback”_ . Nevertheless, visual feedback was valued for its ability to convey contextual information, such as task state and progress. Consequently, the combination of auditory and visual feedback was most frequently preferred overall. Participants characterized audio feedback as an immediate warning signal and visual feedback as supporting error interpretation and task understanding, as illustrated by one participant’s comment: _“The sound caught my attention, and the visual feedback helped me see what went wrong.”_ .

<!-- Page 9 -->

TRAFA: Anticipating User Actions to Reduce Errors in Procedural Tasks with Predictive Feedback 


![](assets/076/paper-0009-01.png)


<!-- Start of picture text -->
(a) Preferred Feedback Mode (b) Modality Ranking Distribution<br>12 17.5 Ranking PositionRanked 1st<br>3 3 Ranked 2nd<br>10 15.0 Ranked 3rd<br>8 12.5 12 4<br>10.0 9<br>6 12<br>7.5<br>4 7 5.0 11<br>2 2.5 6 5<br>0 No Feedback 1 Reactive Predictive 0.0 Audio Visual 1 Audio+Visual<br>Vote Count<br>Number of Participants<br><!-- End of picture text -->

**Figure 8: Participant preferences from the post-study questionnaire. (a) Preferred feedback mode across all conditions. Predictive feedback was preferred by most participants. (b) Ranking distribution for audio, visual, and audio+visual feedback modalities. Although audio was generally preferred over visual feedback, the combined condition received the strongest overall preference.** 

These findings align with prior work demonstrating that different feedback modalities provide distinct and complementary strengths, with visual feedback particularly well suited for identifying required components and illustrating assembly actions [15]. 

### **4.4 Forecasting Module Ablation** 

We justify our design of the forecasting module and evaluate whether it is more reliable to use for predictive feedback compared to other baselines. Table 2 compares four approaches: a linear extrapolation baseline, an immediate-placement baseline, a vanilla ST-GCN, and our scene-aware forecasting model. The linear extrapolation baseline that does not use learning: it extrapolates future hand motion directly from the recent pose history. The immediate-placement baseline assumes that a block will be placed next at the center as soon as the system detects contact between the hand and a block’s bounding box. The vanilla ST-GCN [47] predicts future hand motion from pose history alone. The forecasting models were trained using recorded task trajectories split into 288 training trajectories, 17 validation trajectories, and 19 held-out test trajectories. We report _precision_ , _recall_ , and _F1-score_ , where a correct prediction corresponds to correctly anticipating the block that will be placed at the center. 

The linear extrapolation baseline achieved the lowest overall performance, indicating that simple kinematic heuristics are insufficient for reliable anticipation of upcoming placements. The immediate-placement baseline performed substantially better, showing that the most recently touched object is indeed informative about the likely next action. However, its performance remained below our full scene-aware model, indicating that anticipation cannot be reduced to touch detection alone. The vanilla ST-GCN improved substantially over linear extrapolation, demonstrating that learned motion forecasting captures structure beyond simple kinematic heuristics; however, it did not surpass the immediate-placement baseline. In contrast, our scene-aware model achieved the best overall results, with the highest recall, precision, and F1-score among all compared approaches. These results show that conditioning motion forecasts on scene context substantially improves task-aligned anticipation of placement outcomes. 

**Table 2: Ablating next block placement forecasting performance. Higher values indicate better results and more reliable support for predictive intervention.** 

||**Recall(%)**|**Precision(%)**|**F1(%)**|
|---|---|---|---|
|**Linear Extrapolation**|54.1|71.7|61.7|
|**Instant Placement**|78.7|96.0|86.5|
|**Vanilla ST-GCN**|65.6|87.9|75.1|
|**Scene-aware ST-GCN**|**86.9**|**99.1**|**92.6**|



### **5 Discussion** 

### **5.1 Effectiveness of Predictive Feedback for Error Prevention** 

Our results show that predictive feedback improves performance by intervening before errors are made. Compared to reactive feedback, it increased the success rate from 15% to 65%, reduced edit distance from 2 _._ 06 to 0 _._ 74, and improved efficiency from 7 _._ 7 to 8 _._ 7 correctly placed blocks per minute. These gains were observed without increasing feedback frequency. Conceptually, this shows the benefits of shifting feedback from a corrective to a preventive role. Reactive feedback is issued only after an incorrect placement has already occurred, forcing users to undo and recover from the mistake. Predictive feedback instead intervenes during the ongoing action, allowing users to redirect their motion before making the error. Importantly, the benefit comes from feedback timing rather than issuing more alerts, which is crucial as frequent, poorly timed feedback can disrupt task flow and reduce user acceptance [1]. By reallocating feedback earlier in the action sequence, predictive feedback improves accuracy and efficiency while preserving the overall amount of system intervention. 

### **5.2 User Adaptation under Predictive Feedback** 

Although predictive feedback significantly improved accuracy and efficiency, it did not reduce total task completion time. We observed that participants adapted their behavior in response to anticipatory interventions, becoming more cautious and sometimes pausing briefly to reassess their actions when warned. In this sense, predictive feedback appears to have shifted behavior away from rapid trial-and-error and toward more deliberate action. This highlights an important property of predictive systems: users do not simply react to feedback, but incorporate it into their action planning. Thus, in our study, predictive feedback influenced not only task outcomes but also how participants approached the task, favoring error avoidance over speed. 

### **5.3 Complementary Roles of Feedback Modalities** 

Although feedback modality did not significantly affect task performance, participants’ preferences suggest that different modalities supported the task in different ways. Audio feedback was often described as less disruptive because it allowed participants to keep visual attention on the workspace, whereas visual feedback provided clearer contextual information about what went wrong. Consistent with this interpretation, the combined audio+visual condition was

<!-- Page 10 -->

Mokhtar et al. 

most frequently preferred overall. At the same time, these observations should be interpreted in the context of our task. Because the assembly pieces were primarily differentiated by color, auditory cues may have been especially effective as rapid warnings, while visual feedback mainly supported confirmation and interpretation. This makes modality a secondary design dimension relative to intervention timing, but still an important factor for usability and user preference. 

### **5.4 Design Trade-offs in Feedback Timing and Error Definition** 

An important design choice in this study was the definition of error used to trigger feedback. Errors were defined at the level of completed placements on the assembly target, rather than at intermediate actions such as reaching toward or touching an incorrect block. This definition was intended to preserve exploratory behavior and user agency, allowing participants to handle, rearrange, or reconsider pieces without immediately triggering feedback. 

Alternative definitions, such as treating approaching an incorrect piece as errors, could enable even earlier intervention but would likely increase false positives and feedback frequency and reduce tolerance for exploration. In manual assembly tasks, such exploratory actions are often part of normal problem-solving behavior. Prior work on epistemic actions shows that people frequently manipulate objects to simplify cognition rather than to advance task completion, and that interrupting such actions can be counterproductive [23]. Treating these behaviors as errors may therefore lead to unnecessary interruptions and reduced user acceptance. 

Our results suggest that combining a late error definition with predictive feedback provides a useful balance. Predictive alerts were issued early enough to prevent incorrect placements, while still allowing users flexibility in how they interacted with the pieces. This balance likely contributed to the system’s ability to improve accuracy without increasing feedback volume. These findings highlight a broader design trade-off in anticipatory feedback systems: increasing sensitivity can enable earlier intervention but risks overinterruption, while more conservative definitions may better support user autonomy at the cost of delayed correction. Selecting an appropriate error definition should therefore depend on task demands, error costs, and the degree of exploration expected during interaction. 

### **5.5 Reliable Anticipation as a Requirement for Predictive Feedback** 

Predictive feedback requires reliable task-aligned anticipation beyond simple heuristics. While the immediate-placement baseline confirms that recently touched objects are informative, its performance remained below that of the full scene-aware model. Likewise, linear extrapolation was insufficient for anticipating upcoming placements. These findings indicate that effective pre-commitment intervention requires more than detecting contact or extrapolating recent motion: the system must model how ongoing hand movement relates to the spatial configuration of task objects. Our sceneaware forecaster achieved the strongest overall anticipation performance, showing that incorporating scene context is critical for deciding whether and when to intervene. 

### **6 Limitations** 

This study was conducted in a controlled table-top environment using a sequential assembly task. While this setting allowed precise measurement of error prevention and feedback timing, it does not capture the full complexity of real-world assembly scenarios involving varied object geometries, force interactions, or multi-step tool use. By focusing on a task in which motion cues alone are sufficient to understand user intent, our system is capable of accurately anticipating actions and reducing the amount of mistimed feedback. As more complex activities may require higher-level representations of user intent, such as action recognition or task-state modeling, the generalizability of our findings to more complex assembly tasks should be interpreted with caution. Nevertheless, in cases where user intent can be modeled accurately, we expect the benefits of predictive feedback to increase even further when faced with complex tasks that involve high error costs. 

The study also involved a relatively small sample size (N=20) and short task durations, which are typical for controlled laboratory studies but limit the ability to assess longer-term learning effects or changes in user behavior over repeated sessions. Additionally, participants interacted with the system in a single session, and adaptation over extended use was not examined. However, we mitigated these effects by shuffling the order in which users encounter the different feedback modes, ensuring that, on average, they all occur at the same stage of a user’s learning process. Finally, the system was evaluated in a fixed hardware configuration with an overhead camera and a predefined feedback setup. Performance and user experience may differ under alternative sensing configurations, display placements, or environmental conditions. 

### **7 Conclusion** 

We presented TRAFA, the first real-time predictive feedback system for procedural tasks based on a _Track-Forecast-Act_ framework. By combining scene tracking, short-horizon hand motion forecasting, and intervention logic, the system can issue feedback before an incorrect placement is completed. Across both technical benchmarking and a controlled user study, our results show that predictive feedback is both feasible and effective. The scene-aware forecasting model achieved the strongest task-aligned anticipation performance, and the interactive evaluation showed that predictive feedback significantly improved success rate, edit distance, and efficiency relative to reactive feedback and no feedback, without increasing feedback frequency. 

The results show how real-time anticipation can be operationalized in an interactive system to shift feedback from post-hoc correction toward pre-commitment intervention. In this sense, we view the present system as a building block for more complex assistance problems: it isolates the core loop of tracking, forecasting, and intervening, and demonstrates that this loop can improve performance in a real interactive setting. This work is the first step toward predictive assistance systems that will inspire future work for richer procedural domains, including settings that require stronger task representations, more complex notions of user intent, and adaptive feedback policies that evolve with user behavior over time.

<!-- Page 11 -->

TRAFA: Anticipating User Actions to Reduce Errors in Procedural Tasks with Predictive Feedback 

### **References** 

- [1] Piotr D Adamczyk and Brian P Bailey. 2004. If not now, when? The effects of interruption at different moments within task execution. In _Proceedings of the SIGCHI conference on Human factors in computing systems_ . 271–278. 

- [2] Riku Arakawa, Jill Fain Lehman, and Mayank Goel. 2024. Prism-q&a: Step-aware voice assistant on a smartwatch enabled by multimodal procedure tracking and large language models. _Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies_ 8, 4 (2024), 1–26. 

- [3] Riku Arakawa, Prasoon Patidar, Will Page, Jill Lehman, and Mayank Goel. 2025. Scaling Context-Aware Task Assistants that Learn from Demonstration and Adapt through Mixed-Initiative Dialogue. In _Proceedings of the 38th Annual ACM Symposium on User Interface Software and Technology_ . 1–19. 

- [4] Riku Arakawa, Hiromu Yakura, and Mayank Goel. 2024. PrISM-Observer: Intervention agent to help users perform everyday procedures sensed using a smartwatch. In _Proceedings of the 37th Annual ACM Symposium on User Interface Software and Technology_ . 1–16. 

- [5] Riku Arakawa, Hiromu Yakura, Vimal Mollyn, Suzanne Nie, Emma Russell, Dustin P DeMeo, Haarika A Reddy, Alexander K Maytin, Bryan T Carroll, Jill Fain Lehman, et al. 2023. Prism-tracker: A framework for multimodal procedure tracking using wearable sensors and state transition information with userdriven handling of errors and uncertainty. _Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies_ 6, 4 (2023), 1–27. 

- [6] Dominik Bial, Dagmar Kern, Florian Alt, and Albrecht Schmidt. 2011. Enhancing outdoor navigation systems through vibrotactile feedback. In _CHI’11 Extended Abstracts on Human Factors in Computing Systems_ . 1273–1278. 

- [7] Mattias Billast, Jonas De Bruyne, Klaas Bombeke, Tom De Schepper, and Kevin Mets. 2024. Physical ergonomics anticipation with human motion prediction. SciTePress. 

- [8] Stuart K Card. 2018. _The psychology of human-computer interaction_ . Crc Press. [9] Francesco Chiossi, Julian Rasch, Robin Welsch, Albrecht Schmidt, and Florian Michahelles. 2025. Designing Intent: A Multimodal Framework for Human-Robot Cooperation in Industrial Workspaces. _arXiv preprint arXiv:2506.15293_ (2025). 

- [10] Tanvir Ahmed Chowdhury and Raihanul Kabir Hasan. 2025. Real-Time Human Intention Recognition for Safe and Efficient Interaction in Assistive Robotic Platforms. _Transactions on Machine Learning, Artificial Intelligence, and Advanced Intelligent Systems_ 15, 4 (2025), 1–14. 

- [11] Tom Djajadiningrat, Kees Overbeeke, and Stephan Wensveen. 2002. But how, Donald, tell us how? On the creation of meaning in interaction design through feedforward and inherent feedback. In _Proceedings of the 4th conference on Designing interactive systems: processes, practices, methods, and techniques_ . 285–291. 

- [12] Christopher Frauenberger and Tony Stockman. 2009. Auditory display design—an investigation of a design pattern approach. _International Journal of HumanComputer Studies_ 67, 11 (2009), 907–922. 

- [13] Euan Freeman, Graham Wilson, Dong-Bach Vo, Alex Ng, Ioannis Politis, and Stephen Brewster. 2017. Multimodal feedback in HCI: haptics, non-speech audio, and their applications. In _The Handbook of Multimodal-Multisensor Interfaces: Foundations, User Modeling, and Common Modality Combinations-Volume 1_ . 277– 317. 

- [14] Markus Funk, Tilman Dingler, Jennifer Cooper, and Albrecht Schmidt. 2015. Stop Helping Me - I’m Bored!: Why Assembly Assistance Needs to Be Adaptive. In _Proceedings of the 2015 ACM International Joint Conference on Pervasive and Ubiquitous Computing and Proceedings of the 2015 ACM International Symposium on Wearable Computers - UbiComp ’15_ . ACM Press, Osaka, Japan, 1269–1273. doi:10.1145/2800835.2807942 

- [15] Markus Funk, Juana Heusler, Elif Akcay, Klaus Weiland, and Albrecht Schmidt. 2016. Haptic, Auditory, or Visual?: Towards Optimal Error Feedback at Manual Assembly Workplaces. In _Proceedings of the 9th ACM International Conference on PErvasive Technologies Related to Assistive Environments_ . ACM, Corfu Island Greece, 1–6. doi:10.1145/2910674.2910683 

- [16] Markus Funk, Sven Mayer, and Albrecht Schmidt. 2015. Using In-Situ Projection to Support Cognitively Impaired Workers at the Workplace. In _Proceedings of the 17th International ACM SIGACCESS Conference on Computers & Accessibility - ASSETS ’15_ . ACM Press, Lisbon, Portugal, 185–192. doi:10.1145/2700648.2809853 

- [17] Gerard Gómez-Izquierdo, Javier Laplaza, Alberto Sanfeliu, and Anaís Garrell. 2025. Enhancing context-aware human motion prediction for efficient robot handovers. In _2025 IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS)_ . IEEE, 16917–16922. 

- [18] James Hereford and William Winn. 1994. Non-speech sound in human-computer interaction: A review and design guidelines. _Journal of Educational Computing Research_ 11, 3 (1994), 211–233. 

- [19] Edward Howie, Sharleen Sy, Louisa Ford, and Kim J Vicente. 2000. Human– computer interface design can reduce misperceptions of feedback. _System Dynamics Review: the Journal of the System Dynamics Society_ 16, 3 (2000), 151–171. 

- [20] Glenn Jocher, Ayush Chaurasia, and Jing Qiu. 2023. _Ultralytics YOLOv8_ . https: //github.com/ultralytics/ultralytics Version 8.x. 

- [21] Mishel Johns, Brian Mok, Walter Talamonti, Srinath Sibi, and Wendy Ju. 2017. Looking ahead: Anticipatory interfaces for driver-automation collaboration. In 

- _2017 IEEE 20th International Conference on Intelligent Transportation Systems (ITSC)_ . IEEE, 1–7. 

- [22] Matthew Johnson, Jeffrey M Bradshaw, Paul J Feltovich, Catholijn M Jonker, M Birna Van Riemsdijk, and Maarten Sierhuis. 2014. Coactive design: Designing support for interdependence in joint activity. _Journal of Human-Robot Interaction_ 3, 1 (2014), 43–69. 

- [23] David Kirsh and Paul Maglio. 1994. On distinguishing epistemic from pragmatic action. _Cognitive science_ 18, 4 (1994), 513–549. 

- [24] Bjoern Klages, Jennifer Graf, and Michael Zaeh. 2024. Human errors in manual assembly–A survey on current and future relevance. _Procedia CIRP_ 130 (2024), 1556–1561. 

- [25] Javier Laplaza, Francesc Moreno, and Alberto Sanfeliu. 2025. Enhancing robotic collaborative tasks through contextual human motion prediction and intention inference. _International Journal of Social Robotics_ 17, 10 (2025), 2077–2096. 

- [26] Yang Le, Su Qiang, and Shen Liangfa. 2012. A novel method of analyzing quality defects due to human errors in engine assembly line. In _2012 International conference on information management, innovation management and industrial engineering_ , Vol. 3. IEEE, 154–157. 

- [27] Chenyi Li, Guande Wu, Gromit Yeuk-Yin Chan, Dishita Gdi Turakhia, Sonia Castelo Quispe, Dong Li, Leslie Welch, Claudio Silva, and Jing Qian. 2025. Satori: Towards Proactive AR Assistant with Belief-Desire-Intention User Modeling. In _Proceedings of the 2025 CHI Conference on Human Factors in Computing Systems_ . 1–24. 

- [28] Camillo Lugaresi, Jiuqiang Tang, Hadon Nash, Chris McClanahan, Esha Uboweja, Michael Hays, Fan Zhang, Chuo-Ling Chang, Ming Guang Yong, Juhyun Lee, et al. 2019. Mediapipe: A framework for building perception pipelines. _arXiv preprint arXiv:1906.08172_ (2019). 

- [29] Steven Macenski, Tully Foote, Brian Gerkey, Chris Lalancette, and William Woodall. 2022. Robot operating system 2: Design, architecture, and uses in the wild. _Science robotics_ 7, 66 (2022), eabm6074. 

- [30] Manisha Natarajan and Matthew Gombolay. 2024. Trust and dependence on robotic decision support. _IEEE Transactions on Robotics_ 40 (2024), 4670–4689. 

- [31] Jakob Nielsen. 1994. _Usability engineering_ . Morgan Kaufmann. [32] Victor Noppeney, Felix M Escalante, Lucas Maggi, and Thiago Boaventura. 2024. HuMAn–the Human Motion Anticipation Algorithm Based on Recurrent Neural Networks. _IEEE Robotics and Automation Letters_ 9, 12 (2024), 11521–11528. 

- [33] Don Norman. 2013. _The design of everyday things: Revised and expanded edition_ . Basic books. 

- [34] Shraddha Vijay Pawar, Balavarun Pedapudi, Pramod Kaushik, Sarath Sivaprasad, Mario Fritz, and Shirish Karande. 2025. EARL: Early Intent Recognition in GUI Tasks Using Theory of Mind. In _ICML 2025 Workshop on Computer Use Agents_ . 

- [35] Ronald Poelman, Zoltan Rusak, Alexander Verbraeck, and L Sorasu Alcubilla. 2010. The Effect of Visual Feedback on Learnability and Usability of Design Methods. _Journal of Mechanical Engineering/Strojniški Vestnik_ 56, 11 (2010). 

- [36] Stefan-Alexandru Precup, Snehal Walunj, Arpad Gellert, Christiane Plociennik, Jibinraj Antony, Constantin-Bala Zamfirescu, and Martin Ruskowski. 2023. Recognising Worker Intentions by Assembly Step Prediction. In _2023 IEEE 28th International Conference on Emerging Technologies and Factory Automation (ETFA)_ . IEEE, Sinaia, Romania, 1–8. doi:10.1109/ETFA54631.2023.10275423 

- [37] Harshad Puranik, Joel Koopman, and Heather C Vough. 2020. Pardon the interruption: An integrative review and future research agenda for research on work interruptions. _Journal of Management_ 46, 6 (2020), 806–842. 

- [38] Matthias Rauterberg and Erich Styger. 1994. Positive effects of sound feedback during the operation of a plant simulator. In _International Conference on HumanComputer Interaction_ . Springer, 35–44. 

- [39] Nikhila Ravi, Valentin Gabeur, Yuan-Ting Hu, Ronghang Hu, Chaitanya Ryali, Tengyu Ma, Haitham Khedr, Roman Rädle, Chloe Rolland, Laura Gustafson, et al. 2025. Sam 2: Segment anything in images and videos. In _International Conference on Learning Representations_ , Vol. 2025. 28085–28128. 

- [40] Joseph Redmon, Santosh Divvala, Ross Girshick, and Ali Farhadi. 2016. You only look once: Unified, real-time object detection. In _Proceedings of the IEEE conference on computer vision and pattern recognition_ . 779–788. 

- [41] Iran R Roman, Auriel Washburn, Edward W Large, Chris Chafe, and Takako Fujioka. 2019. Delayed feedback embedded in perception-action coordination cycles results in anticipation behavior during synchronized rhythmic action: A dynamical systems approach. _PLoS computational biology_ 15, 10 (2019), e1007371. 

- [42] Beat Rossmy, Nađa Terzimehić, Tanja Döring, Daniel Buschek, and Alexander Wiethoff. 2023. Point of no undo: Irreversible interactions as a design strategy. In _Proceedings of the 2023 chi conference on human factors in computing systems_ . 1–18. 

- [43] Nina Schaffert, Thenille Braun Janzen, Klaus Mattes, and Michael H. Thaut. 2019. A Review on the Relationship Between Sound and Movement in Sports and Rehabilitation. _Frontiers in Psychology_ 10 (2019), 244. doi:10.3389/fpsyg.2019. 00244 

- [44] James W Suliburk, Quentin M Buck, Chris J Pirko, Nader N Massarweh, Neal R Barshes, Hardeep Singh, and Todd K Rosengart. 2019. Analysis of human performance deficiencies associated with surgical adverse events. _JAMA network open_ 2, 7 (2019), e198067.

<!-- Page 12 -->

Mokhtar et al. 

- [45] Julian Jonathan Tramper. 2013. _Feedforward and feedback mechanisms in sensory motor control_ . Sl: sn. 

- [46] Jo Vermeulen, Kris Luyten, Elise Van Den Hoven, and Karin Coninx. 2013. Crossing the bridge over Norman’s Gulf of Execution: revealing feedforward’s true identity. In _Proceedings of the SIGCHI Conference on Human Factors in Computing Systems_ . 1931–1940. 

- [47] Sijie Yan, Yuanjun Xiong, and Dahua Lin. 2018. Spatial temporal graph convolutional networks for skeleton-based action recognition. In _Proceedings of the AAAI conference on artificial intelligence_ , Vol. 32. 

- [48] Koji Yatani, Darren Gergle, and Khai Truong. 2012. Investigating effects of visual and tactile feedback on spatial coordination in collaborative handheld systems. In _Proceedings of the ACM 2012 conference on Computer Supported Cooperative Work_ . 661–670. 

- [49] Guofan Yin, Martin J.-D. Otis, Pascal E. Fortin, and Jeremy R. Cooperstock. 2019. Evaluating Multimodal Feedback for Assembly Tasks in a Virtual Environment. _Proceedings of the ACM on Human-Computer Interaction_ 3, EICS (2019), 1–11. doi:10.1145/3331163 

- [50] Difeng Yu, Ruta Desai, Ting Zhang, Hrvoje Benko, Tanya R Jonker, and Aakar Gupta. 2022. Optimizing the timing of intelligent suggestion in virtual reality. In _Proceedings of the 35th Annual ACM Symposium on User Interface Software and Technology_ . 1–20. 

- [51] Guanhua Zhang, Susanne Hindennach, Jan Leusmann, Felix Bühler, Benedict Steuerlein, Sven Mayer, Mihai Bâce, and Andreas Bulling. 2022. Predicting next actions and latent intents during text formatting. In _Workshop on Computational Approaches for Understanding, Generating, and Adapting User Interfaces_ . Selfpublished. 

### **A Per-Participant Paired Differences** 

Figure 9 shows the participant-level paired differences between the aggregated Predictive and Reactive conditions for the four primary metrics reported in Table 1. The plots make the within-subject structure of the comparison explicit and are consistent with the patterns reported in Section 4.4. For Success Rate (a) and Edit Distance (b), the effect is large and highly consistent across participants: 19/20 participants showed higher success under Predictive feedback, and 20/20 showed lower edit distance under Predictive feedback (both two-sided Wilcoxon signed-rank tests, _𝑝 <_ 0 _._ 001). For Efficiency (c), most participants (15/20) also favored Predictive feedback ( _𝑝_ = 0 _._ 012), although the smaller and more variable paired differences indicate greater between-participant variation in task pacing. In contrast, Feedback Frequency (d) did not differ significantly between conditions ( _𝑝_ = 0 _._ 573), indicating that Predictive and Reactive feedback triggered a comparable number of interventions. This supports the interpretation that the performance gains of Predictive feedback arise from improved timing of intervention rather than from issuing more feedback events.

<!-- Page 13 -->

TRAFA: Anticipating User Actions to Reduce Errors in Procedural Tasks with Predictive Feedback 


![](assets/076/paper-0013-01.png)


<!-- Start of picture text -->
19/20 participants favour Predictive 20/20 participants favour Predictive<br>(a) Wilcoxon p = 0.000 (b) Wilcoxon p = 0.000<br>95% CI [-1.58, -1.07]<br>P20 P20<br>Mean  = -1.32<br>P19 P19<br>P18 P18<br>P17 P17<br>P16 P16<br>P15 P15<br>P14 P14<br>P13 P13<br>P12 P12<br>P11 P11<br>P10 P10<br>P9 P9<br>P8 P8<br>P7 P7<br>P6 P6<br>P5 P5<br>P4 P4<br>P3 P3<br>P2 P2<br>95% CI [0.42, 0.58]<br>P1 P1<br>Mean  = 0.50<br>0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 2.5 2.0 1.5 1.0 0.5 0.0<br> Success Rate (Pred   Reac)  Edit Distance (Pred   Reac, ops)<br>15/20 participants favour Predictive 8/20 participants favour Predictive<br>(c) Wilcoxon p = 0.012 (d) Wilcoxon p = 0.573<br>P20 P20<br>P19 P19<br>P18 P18<br>P17 P17<br>P16 P16<br>P15 P15<br>P14 P14<br>P13 P13<br>P12 P12<br>P11 P11<br>P10 P10<br>P9 P9<br>P8 P8<br>P7 P7<br>P6 P6<br>P5 P5<br>P4 P4<br>P3 P3<br>P2 P2<br>95% CI [0.26, 1.59] 95% CI [-0.17, 0.58]<br>P1 P1<br>Mean  = 0.91 Mean  = 0.18<br>2 1 0 1 2 3 4 1.0 0.5 0.0 0.5 1.0 1.5 2.0<br> Efficiency (Pred   Reac, pieces/min)  Feedback Frequency (Pred   Reac, events)<br><!-- End of picture text -->

**Figure 9: Per-participant differences (Predictive-Reactive, aggregated) for four performance metrics (N=20). Each bar represents one participant; blue bars indicate the participant favored the Predictive condition, red bars indicate the participant favored the Reactive condition. The shaded region shows the bootstrapped** 95% **CI of the mean difference; the dashed line marks the mean** Δ **. (a) Success Rate, (b) Edit Distance, (c) Efficiency, (d) Feedback Frequency. Statistical significance was assessed using two-sided Wilcoxon signed-rank tests.**
