# 给导师的汇报摘要

## 目标

验证一个研究想法：在程序性视频错误检测中，把 detector 的连续错误分数转化为带误报预算的 online interrupt/silence 决策。

## 已完成

使用 AEM 官方模型在 EgoPER 五个任务上完成推理，并导出逐帧 error score。AEM 的 test Micro AUC 分别为 Coffee 70.25%、Oatmeal 75.93%、Pinwheels 64.36%、Quesadilla 80.83%、Tea 71.07%，平均约 72.49%。因此 detector 有一定错误区分能力。

随后完成了多种校准审计：task-wise、pooled、block、persistence、leave-one-video-out、严格 validation-to-test、video-level maximum 和 video-wise z-score。严格 validation-to-test 在 alpha=0.05 时的 frame FPR 为 4.68%–11.30%，video FPR 为 33.33%–100%；video-level maximum calibration 的错误视频召回为 9.38%–68.75%；z-score normalization 仍出现 0–100% 的 video FPR。

## 主要发现

1. AEM score 有信息，但不同任务和视频的 score 尺度不同。
2. validation 到 test 存在明显分布偏移，Quesadilla 的 test q95 比 validation 高约 0.108。
3. 帧间相关性不是唯一问题；block max 和 persistence 没有稳定改善结果。
4. 每任务只有三个安全正常视频，无法支持稳定的视频级统计保证。
5. Coffee 有三个文件名为 error 但 frame-level error label 全零的 ambiguous videos，已单独排除视频级召回统计。

## 阶段结论

原始假设“直接对现有 detector 套 conformal threshold，即可得到可靠的 interrupt/silence 保证”在当前 EgoPER 设置下不成立。第一阶段应作为 feasibility/negative-result audit 收束。

## 后续选择

如果继续 R1，需要重新定义问题：few-normal-video、temporal dependence 和 cross-video/task shift 下的 video-adaptive calibration，并设计新的机制；如果目标是尽快形成主论文，建议把 R2（VLM teacher-to-student distillation）作为主线，把本阶段失败结果作为决策层动机和对照。

