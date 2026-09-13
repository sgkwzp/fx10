"""Generate a standard-mode first-pass report from measured pilot artifacts."""
from pathlib import Path
import json
import re

EXP=Path(__file__).resolve().parent;OUT=EXP/'outputs'


def main():
    rows=json.loads((OUT/'all_risk_results.json').read_text());inv=json.loads((OUT/'inventory.json').read_text());ranking=json.loads((OUT/'rankings.json').read_text())
    def row(mode,task,unit,alpha=.05):return next(x for x in rows if x['protocol']==mode and x['target_task']==task and x['unit']==unit and x['alpha']==alpha)
    lines=['# R1 风险受控程序性错误检测：首轮验证','',
    '**状态：已开始，完成理论边界核对、ZeProM 硬件与方法核对，以及五任务诊断评分器的 100 个风险运行点。完整的“已发表监督检测器 + ZeProM/VLM”验证尚未完成，4090 吞吐尚未实测。**','',
    '## 目的、来源与模式','',
    '- Mode：standard / experiment design + measured pilot。延续 CCFA 实验设计与证据纪律。',
    '- Search purpose：验证 R1 的风险单位、校准样本量与模型可行性；不是重新宣称整个领域的新颖性。',
    '- Queries/sources used：读取本地 ZeProM 全文、更新后的 papers.md 与方向备忘录；以公开模型名访问 Hugging Face 官方模型元数据、权重索引与模型卡。没有把私有方法文本发送到搜索服务。',
    '- Source policy：本轮使用用户本地全文及官方模型记录，无 MDPI。先前“无交集命中”的搜索结果未被当作不存在相关工作的证明。',
    '- Folder written：`experiments/risk_control_pilot_20260911/`。原文献、数据、项目代码及之前实验全部只读。','',
    '## 三个改变验证计划的事实','',
    '1. **主 ZeProM 配置超出单卡预算。** Q-L 的实际量化权重约 219.47 GiB，Q-M BF16 约 66.97 GiB。论文主结果来自 4×H100；当前机器实际是 RTX 2060 6GB。35B 4-bit/9B 可以成为 4090 工程候选，但不能继承 Q-L 的论文性能。',
    '2. **ZeProM 已有 MC 概率。** 它明确指出自报置信度不理想，并用多次随机采样生成错误概率。应审计这类概率和分段一致性；其他 VideoQA 论文的“18→6 帧置信度不变”不能直接外推。',
    '3. **校准单位决定能保证什么。** 每任务 3 个正常验证视频，意味着视频级 5% conformal 阈值退化。更多帧或更多相邻块不会自动增加独立/可交换的视频单位。另一方面，冻结的零样本 VLM 可考虑使用已有正常训练视频校准，不能把官方验证集小直接当作整个方向无解。','',
    '## 声明—证据对应','',
    '| 要验证的命题 | 本轮证据 | 能得出的结论 |',
    '|---|---|---|',
    '| 池化帧阈值是否可靠 | 五任务名义 1%、5%、10% 的经验运行点 | 某些任务经验超标；不能仅凭这点归因为时间相关 |',
    '| 分块能否修好 | 固定 1 秒块最大值，与对应块风险比较 | 部分任务仍超标；分块本身不提供交换性 |',
    '| 视频级保证是否非平凡 | 正确有限样本秩及视频 CRC 校正 | 当前 n=3/12、低风险目标下退化为永不报警 |',
    '| 阈值能否迁移未见任务 | 源四任务参考库和验证阈值，在完全排除目标任务拟合的第五任务测试 | 此诊断评分器迁移明显退化；不代表所有已发表检测器或 VLM |',
    '| VLM 能否在 4090 达到可接受吞吐 | 官方权重容量、模型卡、可运行的采样脚本和实际视频输入 | 主模型不适合单卡完整驻留；候选模型吞吐仍待真实 4090 |',
    '| AURC/ECE 排名是否分离 | 对诊断距离给出定义明确的 AURC；没有合法错误概率 | 不计算虚假的 ECE，不声称已发现检测器排名反转 |','',
    '## 数据与评分器','',
    '使用正常特征余弦最近邻诊断器：每任务从可用正常训练视频均匀分配 512 个参考特征；分数为当前特征到参考库的最小余弦距离，再做 5 帧因果均值。这是独立命名的诊断实现，不冒充 AMNAR/AEM/ZeProM。','',
    '| 任务 | 可用训练视频 | 正常验证视频 | 测试视频 | 全部 Normal 的测试视频 |',
    '|---|---:|---:|---:|---:|']
    for task,d in inv.items():lines.append(f"| {task} | {len(d['training']['used'])}/{len(d['training']['listed'])} | {len(d['validation']['used'])} | {len(d['test']['used'])} | {d['test']['normal_videos']} |")
    lines+=['','合计 131 个可用训练视频、15 个正常验证视频、188 个测试视频。错误标签使用已有 refined_label_v3，非 Normal 为正类，包括 Correction；遗漏错误不包含在该逐帧标签定义内。正常视频的定义是这些标签下没有错误帧，不能自动推断不存在遗漏步骤。','',
    'Within-task：目标任务正常训练数据建立参考库，其 3 个正常验证视频校准。LOTO：只使用其余四任务的参考库和 12 个正常验证视频，目标任务训练/验证完全不参与。每个 LOTO fold 内，对源校准和目标测试使用同一个固定评分器。两种协议的参考库也不同，因此差距是整体移位压力测试，不是只改变阈值的因果消融。','',
    '## 名义 5% 风险：只在完整正常测试视频上观察','',
    '帧阈值对应“正常帧超阈值比例”；1 秒块阈值对应“正常块最大值超阈值比例”。它们是不同风险单位，分别与自己的 5% 名义水平比较，不能把两列差值当作同一指标改善。完整正常视频更接近正常校准视频的抽样对象，仍只有每任务 3–6 个测试视频。','',
    '| 任务 | 任务内：帧 FPR | 任务内：块报警比例 | LOTO：帧 FPR | LOTO：块报警比例 |',
    '|---|---:|---:|---:|---:|']
    for task in inv:
        a=row('within_task',task,'pooled_frames');b=row('within_task',task,'pooled_1s_block_max');c=row('leave_one_task_out',task,'pooled_frames');d=row('leave_one_task_out',task,'pooled_1s_block_max')
        lines.append(f"| {task} | {a['all_normal_video_frame_FPR']:.2%} | {b['all_normal_video_block_alert_fraction']:.2%} | {c['all_normal_video_frame_FPR']:.2%} | {d['all_normal_video_block_alert_fraction']:.2%} |")
    lines+=['','结果不符合“第一步失败、第二步普遍修好”的预设叙事。例如 Oatmeal、Quesadilla 的块报警比例仍约为 9.52% 和 10%。LOTO 的退化更大，但也可能来自正常视觉分布与评分器适配的变化，不能自动归因于某个校准算法。','',
    '## 混合错误视频中的 Normal 时段','',
    '| 任务 | 任务内帧 FPR（全部 Normal 标签帧） | 其中完整正常视频帧 FPR |',
    '|---|---:|---:|']
    for task in inv:
        d=row('within_task',task,'pooled_frames');lines.append(f"| {task} | {d['normal_frame_FPR']:.2%} | {d['all_normal_video_frame_FPR']:.2%} |")
    lines+=['','Pinwheels、Quesadilla 在包含错误视频的 Normal 时段时达到约 15%–16%，但完整正常视频的值更低。这进一步说明校准与评测的抽样对象必须对齐，不能把所有经验超标都说成“帧相关导致保证失效”。每个正常视频是否报警及条件性二项区间也保存在原始结果中；这些小样本区间不能证明任意任务的有效性。','',
    '## 保证的代价','',
    '| 规则 | 当前校准数 | 当前低风险运行结果 |',
    '|---|---|---|',
    '| 每视频最大值 split-conformal，alpha=5% | 任务内 3；LOTO 源视频 12 | 秩超出校准样本数，阈值正无穷，永不报警 |',
    '| 视频损失 CRC，1 秒块、1 次/分钟 | 任务内 3；LOTO 源视频 12 | 保守校正最低界分别为 15、约 4.615 次/分钟；退化为永不报警 |','',
    '非平凡视频最大值 5% 阈值至少需 19 个交换的正常校准视频。这里的交换条件是明确假设，不是分块后自动满足。CRC 控制的是抽样新正常视频的期望块报警率，也不是无限时域条件误报或任意未见任务保证。详细推导与目标修订见 [THEORY_SCOPE.md](THEORY_SCOPE.md)。','',
    '为了使数量关系直观：1 秒一决策时，5% 块报警比例相当于 3 次/分钟，而非 1 次/分钟。若合并连续报警或加入冷却，应重新定义有界损失与延迟；一般的阈值连通区间计数甚至未必随阈值单调。','',
    '## AURC 与五步实验完成状态','',
    '已计算固定 5% 帧阈值分类器的 AURC：置信排序定义为离阈值的绝对距离，损失为二分类错误；同分时用随机排序的期望风险处理。结果见 [rankings.json](outputs/rankings.json)。这是一个评分器的诊断，不是两个已发表检测器的排名比较。', '',
    '| 原五步 | 状态 |',
    '|---|---|',
    '| 帧级校准与经验预算 | 已完成诊断评分器五任务试验；未完成监督+VLM比较 |',
    '| 分段/分块能否修复 | 已完成固定 1 秒块及视频单位；未假定动作段独立 |',
    '| AURC 与 ECE 是否出现排名分离 | AURC 定义和计算已实现；错误概率不足，ECE及双检测器比较未完成 |',
    '| 留一任务阈值迁移 | 已完成诊断评分器 5 folds；未形成跨任务保证 |',
    '| VLM 18/6 帧证据敏感性 | 未运行；须使用匹配设置的 MC 概率及核实的实际采样帧数 |','',
    '## 下一步执行入口','',
    '1. 获得可运行 4090 环境或已部署 VLM 服务，用已准备的 93/206.6/366.1 秒完整视频测原生 4 fps 的内存、吞吐、输出完整性，再决定是否采用 35B 量化或 9B。主 Q-L 不作为单卡目标。',
    '2. 固定 VLM 后，利用未用于模型拟合的现有正常视频建立独立校准集；明确“每视频至少一次报警”还是“每分钟报警次数”的研究目标。分布移位先做经验审计，保证必须附条件。',
    '3. 从真实监督模型导出有明确语义的错误分数及正常校准输出。现有 AMNAR test-only cache 的 score 未被误用为错误概率。',
    '4. 对齐 ZeProM-MC 的参考分割与多样本汇总，再做帧预算变化、弃答和风险—覆盖实验；不要预设一定出现排名反转或置信度失效。','',
    '这条路线可以继续验证，但“决策层已核验为空”和“任意依赖、任意未见任务下分布无关保证”都应撤回为待检索/带条件的命题。本轮没有触碰用户原文档，这些修订仅记录在新实验目录。','',
    '## 复现、来源及检查','',
    '```powershell',
    'python experiments/risk_control_pilot_20260911/run_risk_pilot.py',
    'python experiments/risk_control_pilot_20260911/report.py',
    '```','',
    '- [模型可行性与 VLM 测试包说明](FEASIBILITY.md)，包括实际硬件、官方权重容量、MC 方法和监督缓存缺口。',
    '- [理论与风险单位](THEORY_SCOPE.md)；[固定配置](protocol.json)；[100 个运行点](outputs/all_risk_results.json)；[校验记录](outputs/checks.json)。',
    '- [VLM 吞吐脚本](benchmark_vlm.py)已检查命令入口和 JSON 解析；原始视频与提示位于 `vlm_inputs/`，尚未产生任何 VLM 推理结果。',
    '- 主计算使用当前 CUDA GPU，运行约 42 秒。时间只属于特征距离与风险计算，绝不是 VLM 吞吐。',
    '- 特征来源及本地诊断性质与前序一致；原始 256 维提取的时间窗口未核实，因此没有宣称端到端在线效果。','']
    (EXP/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)',(EXP/'REPORT.md').read_text(encoding='utf-8')):assert (EXP/target).exists(),target
    print('REPORT.md written; measured tables and links verified.')


if __name__=='__main__':main()
