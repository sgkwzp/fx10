"""Summarize frozen intervention evidence; no fitting or score modification."""
import json
import re
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

EXP=Path(__file__).resolve().parent;OUT=EXP/'outputs'
NAMES={'global_nn':'全局最近邻','history_soft_nn':'原历史软条件','observable_freeze':'可观测分数触发屏蔽','oracle_freeze':'Oracle：全部错误屏蔽','oracle_weak':'Oracle：错误更新降至 25%','oracle_exclude_correction':'Oracle：保留 Correction 更新','shifted_mask_freeze':'Oracle 对照：平移错误掩码','oracle_action_nn':'Oracle：真实动作参照'}


def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')


def summarize_groups():
    local=read('event_local_metrics.json');updates=read('direct_observation_updates.json');gates=read('gate_coverage.json')
    summary={}
    for typ in sorted(set(r['type'] for r in gates)):
        g=[r for r in gates if r['type']==typ];u=[r for r in updates if r['type']==typ];l=[r for r in local if r['type']==typ]
        n=sum(r['frames'] for r in g)
        d={'frames':n,'observable_mask_coverage':sum(r['observable_suppressed_frames'] for r in g)/n,'shifted_mask_coverage':sum(r['shifted_mask_suppressed_frames'] for r in g)/n}
        if u:
            nu=sum(r['frames'] for r in u)
            d['direct_observation_delta_probability']=sum(r['frames']*r['mean_current_observation_delta_probability'] for r in u)/nu
            d['direct_observation_decrease_fraction']=sum(r['frames']*r['fraction_observation_decreases_nominal_probability'] for r in u)/nu
        if l:
            d.update(events=len(l),event_macro_freeze_delta_late=float(np.mean([r['freeze_delta_late_probability'] for r in l])),event_macro_weak_delta_late=float(np.mean([r['weak_delta_late_probability'] for r in l])),baseline_early_quarter=float(np.mean([r['baseline_early_quarter_probability'] for r in l])),baseline_late_quarter=float(np.mean([r['baseline_late_quarter_probability'] for r in l])),freeze_positive_events=sum(r['freeze_delta_late_probability']>0 for r in l))
        summary[typ]=d
    write(OUT/'group_summary.json',summary)
    return local,summary


def plots(s,local):
    figs=EXP/'figures';figs.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(13,4.8))
    methods=['history_soft_nn','observable_freeze','oracle_weak','oracle_freeze','shifted_mask_freeze']
    labels=['History baseline','Observable freeze','Oracle weaken','Oracle freeze','Shifted mask (oracle)']
    vals=[s['frame_metrics']['oracle_supported'][m]['ap'] for m in methods]
    axes[0].barh(labels,vals,color=['#497d9b','#3b947e','#b394c7','#9567b0','#ad9b7c']);axes[0].invert_yaxis();axes[0].set_xlim(0,.65);axes[0].set_xlabel('AP on frames with a nominal action')
    for i,v in enumerate(vals):axes[0].text(v+.007,i,f'{v:.4f}',va='center',fontsize=9)
    g=s['bootstrap']['local_freeze_delta_late_probability'];keys=['all_supported','Error_Modification','Error_Slip','Error_Correction']
    for i,k in enumerate(keys):
        r=g[k];ci=r['95pct_CI'];value=r['video_macro_delta']
        axes[1].plot(ci,[i,i],color='#497d9b',lw=2);axes[1].scatter([value],[i],color='#497d9b',s=30)
    axes[1].axvline(0,color='#777777',linestyle=':');axes[1].set_yticks(range(4),['All supported errors','Modification','Slip','Correction']);axes[1].invert_yaxis();axes[1].set_xlabel('Local freeze - baseline: target-action prior\n(last quarter; video-level 95% interval)')
    fig.suptitle('Oracle detection gain does not imply preserved nominal-action belief',fontsize=12);fig.tight_layout();fig.savefig(figs/'intervention_summary.png',dpi=150);plt.close(fig)
    chosen=[]
    for typ in ['Error_Modification','Error_Slip']:
        candidates=[r for r in local if r['type']==typ];median=np.median([r['freeze_delta_late_probability'] for r in candidates])
        c=min(candidates,key=lambda r:(abs(r['freeze_delta_late_probability']-median),r['video'],r['start']))
        chosen.append({'selection':'nearest_type_median',**c})
    positive=[r for r in local if r['freeze_delta_late_probability']>0]
    if positive:chosen.append({'selection':'largest_local_positive_example',**max(positive,key=lambda r:r['freeze_delta_late_probability'])})
    for i,c in enumerate(chosen):
        tr=np.load(OUT/'event_local_traces'/f"{c['video']}.npz",allow_pickle=False);p=np.load(OUT/'predictions'/f"{c['video']}.npz",allow_pickle=False)
        st=str(c['start']);ts=np.arange(c['start'],c['end'])/10
        fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True)
        for method,label,col in [('baseline','Normal visual updates','#497d9b'),('weak','Local updates x0.25','#dd9239'),('freeze','Local observation freeze','#a16eb8')]:axes[0].plot(ts,tr[st+'_'+method],label=label,color=col)
        axes[0].set_ylabel('Nominal-action prior');axes[0].set_ylim(0,1);axes[0].legend(fontsize=8)
        for m,col in [('history_soft_nn','#497d9b'),('observable_freeze','#3b947e'),('oracle_freeze','#a16eb8')]:axes[1].plot(ts,p[m][c['start']:c['end']],label=m,color=col)
        axes[1].set_ylabel('Full-trajectory distance score');axes[1].set_xlabel('Feature time (seconds)');axes[1].legend(fontsize=8)
        fig.suptitle(f"{c['video']} | {c['type']}\n{c['description']} | Local branches start from identical belief",fontsize=10);fig.tight_layout()
        c['figure']=f'local_case_{i+1:02d}.png';fig.savefig(figs/c['figure'],dpi=140);plt.close(fig)
    write(EXP/'figures/cases.json',chosen)
    return chosen


def report(s,groups,chosen):
    frame=s['frame_metrics'];boot=s['bootstrap'];ev=s['event_metrics']
    lines=['# Tea：错误区间的信念更新干预验证','',
    '**验证结论：本轮没有支持“屏蔽错误视觉能保住正确动作信念”这一总体解释。真实错误掩码带来了较大的检测 AP 增益，但从相同事件起点出发，屏蔽视觉更新使名义正确动作的信念下降。两种指标指向不同机制，不能把 oracle 的 AP 增益当成实际方法收益。**','',
    '## 验证设计','',
    '所有新增文件位于本目录。26 个正常训练视频拟合的特征库、动作中心、历史转移矩阵及正常验证选出的温度 0.15/观测强度 0.1 均继承上一轮，未重新拟合或根据本轮测试结果调参。验证仍为 3 个正常视频，测试为 35 个视频。主诊断子集为 45,596 个有正常动作对应帧。','',
    '在时间 t，历史模型先输出读取当前视觉之前的动作先验，再更新隐状态。屏蔽操作只取消当前视觉似然的乘入；状态转移继续推进。它不是把整个状态冻结在原地。','',
    '| 分支 | 更新方式 | 是否使用真实错误标签 |',
    '|---|---|---|',
    '| 原历史软条件 | 每帧正常更新 | 否 |',
    '| 可观测分数触发屏蔽 | 当前全局最近邻分数超过已有正常验证阈值时，跳过视觉更新 | 否 |',
    '| Oracle 全错误屏蔽 | 所有非 Normal 帧跳过视觉更新 | 是，仅诊断 |',
    '| Oracle 弱化 | 错误帧的观测强度变为原值的 25% | 是，仅诊断 |',
    '| Oracle 保留 Correction | 仅屏蔽 Modification、Slip、Addition，Correction 正常更新 | 是，仅诊断 |',
    '| 平移掩码对照 | 将每个视频的错误掩码循环平移半个视频，保留屏蔽总帧数 | 是，仅诊断 |',
    '| 真实动作参照 | 用真实名义动作选参考库，不是更新干预 | 是，仅诊断 |','',
    '实际分支的预测函数只接收特征、模型参数及固定阈值，不接收动作或错误标签。真实标签在实际预测完成后才进入独立的 oracle 分支和评测。平移掩码不是无标签方法，也不能保证与真实错误区间完全不重叠。','',
    '完整视频干预观察累计影响；事件局部干预则从原模型在事件开始前的同一隐状态出发，比较该事件内正常、25% 弱化、屏蔽三种更新。局部分支没有重置成真实正确状态，亦没有把真实动作作为模型输入，只在计算目标动作信念时使用标注。','',
    '## 完整视频检测结果','',
    '| 方法 | 主诊断子集 AP | 全测试 AP | 事件 F1 | 正常误报/分钟 |',
    '|---|---:|---:|---:|---:|']
    for m,n in NAMES.items():lines.append(f"| {n} | {frame['oracle_supported'][m]['ap']:.4f} | {frame['all_frames'][m]['ap']:.4f} | {ev[m]['event_f1']:.4f} | {ev[m]['normal_alarm_onsets_per_minute']:.3f} |")
    lines+=['','Oracle 分支在全正常验证视频上等同原模型，因此其检测阈值与原模型完全相同；可观测分支使用相同 99% 正常分位规则计算自己的阈值。所有阈值在测试评分前保存。事件指标沿用上一轮 tIoU≥0.1 一对一匹配；这些不是相同测试误报率下的比较。','',
    '| 比较 | ΔAP | 配对视频 Bootstrap 95% 区间 |',
    '|---|---:|---:|']
    for pair,r in boot['detection'].items():
        a,b=pair.split(' minus ');ci=r['delta_AP_95pct_CI'];d=frame['oracle_supported'][a]['ap']-frame['oracle_supported'][b]['ap'];lines.append(f"| {NAMES[a]} − {NAMES[b]} | {d:+.4f} | [{ci[0]:+.4f}, {ci[1]:+.4f}] |")
    lines+=['','Oracle 全屏蔽 AP 超过真实动作参照 AP，也不矛盾：两者使用的特权信息不同，真实动作参照不是严格上界。Oracle 掩码已经告知模型错误位置，干预将这些位置的信息注入后续评分。平移掩码较弱只能说明位置相关性重要，不能证明正确语义信念得到了保留。','',
    '可观测策略的 ΔAP 约为 +0.0010，区间在当前重复使用的测试样本上略高于零，但绝对收益很小，正常误报频率还从约 1.094 升至 1.163 次/分钟。它没有实现 oracle 的增益。','',
    '## 从相同起点出发的局部信念验证','',
    '分析 84 个有正常动作对应的错误事件：Modification 36、Slip 24、Correction 24。Addition 没有合法正常动作类，未计入该信念分析，但仍保留在完整视频检测中。衡量每个事件最后四分之一内“名义正确动作先验概率”的均值。先对每个视频中的事件取均值，再对视频取均值，避免长视频和长事件占据过大权重。','',
    '| 类别 | 事件数 | 屏蔽 − 正常更新：末段概率差 | 视频 Bootstrap 95% 区间 |',
    '|---|---:|---:|---:|']
    for name,r in boot['local_freeze_delta_late_probability'].items():
        num=84 if name=='all_supported' else groups[name]['events'];ci=r['95pct_CI'];lines.append(f"| {name} | {num} | {r['video_macro_delta']:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] |")
    lines+=['','尤其在 Slip 事件中，正常视觉更新有助于识别名义动作，而屏蔽会丢掉这种信息。检测 AP 增加与正确动作信念下降同时出现，不支持将前者解释成后者改善。Correction 的区间跨零，因此不对该类型作总体有害/有益判定。','',
    '下面列出每次观测更新后相对更新前的名义动作概率变化，以及局部屏蔽出现正收益的事件数。该分析不等同于真实动作正确执行与否；视频可能仍在做同一动作，只是对象、参数或结果有误。','',
    '| 类别 | 单次观测 Δ概率（逐帧均值） | 局部屏蔽末段概率改善事件/总事件 |',
    '|---|---:|---:|']
    for typ,d in groups.items():
        if 'direct_observation_delta_probability' in d:
            count=f"{d['freeze_positive_events']}/{d['events']}" if 'events' in d else '不适用'
            lines.append(f"| {typ} | {d['direct_observation_delta_probability']:+.4f} | {count} |")
    lines+=['','全部信念干预是模型内部的计算对照，不是物理环境因果实验。名义动作标签也是有限代理，不能据此宣称正确程序进度或对象状态已经被识别。','',
    '## 可观测触发器覆盖了什么','',
    '| 标注类型 | 被可观测策略屏蔽的帧比例 |',
    '|---|---:|']
    for typ,d in groups.items():lines.append(f"| {typ} | {d['observable_mask_coverage']:.2%} |")
    lines+=['','当前触发器主要覆盖 Addition，Modification 和 Slip 覆盖较少。简单依赖已有异常分数触发冻结，既缺少对这些错误的识别能力，也没有解决“同动作却执行错误”的判别问题。','',
    '## 可视检查','',
    '![干预结果](figures/intervention_summary.png)','',
    '选取 Modification、Slip 中与该类局部概率差中位数最接近的事件，以及一个最大正向个例，展示平均结论之外的差异。上图局部分支均从相同原模型状态出发；下图为完整视频滚动干预的分数，两种起始条件不同，不应逐点当成同一干预。','']
    for c in chosen:lines.append(f"- [{c['selection']} / {c['type']}](figures/{c['figure']})：{c['video']}，{c['start']/10:.1f}–{c['end']/10:.1f}s，{c['description']}，局部屏蔽末段概率差 {c['freeze_delta_late_probability']:+.3f}。")
    lines+=['','## 决策','',
    '**这项验证已完成；不建议把“冻结错误视觉以保护正确历史判断”作为目前的主方法叙事。** 当前证据更符合：错误视频仍含有识别动作类别的有用视觉信息，单靠动作类别/正常特征距离不足以区分执行是否正确；使用真实错误掩码进行屏蔽会改变评分，却不保证改善语义信念。','',
    '下一步应把动作身份与执行正确性分开检验。具体可先利用上一轮已发现的同动作 Slip 漏检，检查目标对象、对象间关系及动作前后状态是否能提供额外可区分信息；以动作标签正确但仍漏检的片段作为明确诊断集合。物体关系或状态信号若可用，再设计实际可观测的执行核验机制，而不是继续用当前异常分数给同一模型加门控。','',
    '这只是有证据支持的收窄方向，尚未验证对象/关系方法有效。继续实现前需要盘点对应原视频与对象标注的覆盖，并对照 AEM、GTG2Vid 等最近工作明确差异。','',
    '## 复现与证据边界','',
    '```powershell',
    'python experiments/tea_belief_intervention_20260911/run_intervention.py',
    'python experiments/tea_belief_intervention_20260911/analyze.py',
    '```','',
    '- 配置：[protocol.json](protocol.json)；固定模型和划分出处：[frozen_inputs.json](outputs/frozen_inputs.json)。',
    '- 检测结果和区间：[summary.json](outputs/summary.json)；局部事件数据：[event_local_metrics.json](outputs/event_local_metrics.json)；单步更新：[direct_observation_updates.json](outputs/direct_observation_updates.json)；触发器覆盖：[gate_coverage.json](outputs/gate_coverage.json)。',
    '- 原始预测与信念在 `outputs/predictions/`；同起点局部轨迹在 `outputs/event_local_traces/`；逐事件命中和延迟继续保存于 `outputs/events.json`。',
    '- 检查通过：[checks.json](outputs/checks.json)，覆盖旧评分和先验复现、正常验证下 oracle 不变、只屏蔽观测而保持转移、当前掩码不改变当前评分先验、可观测分支前缀一致性、局部分支共同起点与基线等价、平移掩码等帧数。',
    '- Bootstrap 为 300 次视频级配对重采样。当前测试集已反复用于探索，区间不能消除选择偏差或支持跨任务结论；未进行多重比较校正。',
    '- 256 维特征的精确提取窗口尚未核实，算法评分具有前缀因果性，但不能宣称端到端在线性能。标签沿用 refined_label_v3，Correction 仍计入主检测正类。',
    '- 所有新文件均在当前目录，旧代码、旧结果与数据没有改动。评测代码是前轮函数的本地快照，只向当前目录写入。','']
    (EXP/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    text=(EXP/'REPORT.md').read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)',text):assert (EXP/target).exists(),target
    print(json.dumps({'group_summary':groups,'figures':[c['figure'] for c in chosen],'report':'REPORT.md'},ensure_ascii=False,indent=2))


def main():
    s=read('summary.json');local,groups=summarize_groups();chosen=plots(s,local);report(s,groups,chosen)


if __name__=='__main__':main()
