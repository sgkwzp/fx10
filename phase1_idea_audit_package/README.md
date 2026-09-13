# 第一阶段 Idea 验证复盘包

本包用于向导师汇报“程序性视频错误检测的统计决策层”第一阶段探索结果。

## 研究问题

在冻结的 AEM 错误检测器上，能否通过 conformal 或相关后处理校准，得到具有可控误报预算的 online interrupt/silence 决策？

## 数据与 detector

- 数据：EgoPER 五个任务：Coffee、Oatmeal、Pinwheels、Quesadilla、Tea。
- Detector：AEM 官方 checkpoint，未重新训练。
- 输出：逐帧 `score = 1 - framewise_action_sim`。
- Test 输出已在服务器 `code/AEM/outputs/aem_scores/` 生成；原始 JSONL 很大，仍保留在服务器。

## 实验顺序

1. Task-wise frame calibration
2. Pooled frame calibration
3. Pooled block calibration（约 1/2/4 秒）
4. Persistence rule（K=3/5/10）
5. Leave-one-normal-video-out
6. Strict validation-to-test calibration
7. Video-level maximum-score calibration
8. Video-wise z-score normalization

## 结论

AEM score 含有错误信号，但简单 frame/block/task-wise/pooled/video-level conformal 不能稳定控制视频级误报。主要原因是 validation-to-test score shift、跨任务分布差异、时序依赖，以及每个任务仅有三个安全正常视频。第一阶段不支持“直接套 conformal threshold 即可获得可靠 interrupt/silence 保证”的原始假设。

## 建议

将 R1 作为已完成的 feasibility/negative-result audit，不再继续堆叠固定阈值变体。若继续研究，应改成更有机制性的 video-adaptive calibration 或转向 R2（VLM teacher-to-student distillation），并使用 R1 的失败结果作为动机。

## 统计限制

这些结果是方向判断，不是正式统计保证：安全正常视频数量太少，video-level FPR 只能取 0、1/3、2/3、1；Coffee 还有三个文件名为 error 但 frame label 全零的 ambiguous videos。

