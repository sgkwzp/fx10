"""Analyze frozen history predictions and render gains/failures without tuning."""
import json
from pathlib import Path
import numpy as np
from scipy.special import softmax
from threadpoolctl import threadpool_limits
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import evaluation as ev

EXP=Path(__file__).resolve().parent;OUT=EXP/'outputs'
BASE=EXP.parent/'tea_action_diagnostic_20260911'
NAMES={'global_nn':'全局最近邻','predicted_action_nn':'当前帧硬条件','visual_soft_nn':'当前帧软条件','history_hard_nn':'历史硬条件','history_soft_nn':'历史软条件','no_order_soft_nn':'去后继结构的软条件','oracle_action_nn':'真实动作条件（oracle）'}


def mechanisms():
    manifest=json.loads((OUT/'run_manifest.json').read_text());videos=manifest['used_splits']['test']
    saved=np.load(BASE/'outputs/normal_bank.npz');bank=saved['features'];labels=saved['actions'];keys=saved['center_actions']
    collected={};trace={}
    for v in videos:
        x=ev.normalize(np.load(ev.DATA/ev.CFG['feature_family']/f'{v}.npy').astype(np.float32))
        p=np.load(OUT/'predictions'/f'{v}.npz')
        ds=[]
        for start in range(0,len(x),512):
            sim=x[start:start+512]@bank.T
            ds.append(np.stack([1-sim[:,labels==k].max(1) for k in keys],axis=1))
        d=np.concatenate(ds);prior=p['history_prior'];act=p['action_gt'];types=p['type_gt']
        # The mixture responsibility shows which branch dominates the softmin.
        responsibility=softmax(np.log(np.maximum(prior,1e-15))-d/ev.CFG['distance_softmin_temperature'],axis=1)
        true_prior=np.full(len(act),np.nan);true_resp=np.full(len(act),np.nan)
        known=act>=0;idx=np.flatnonzero(known)
        true_prior[idx]=prior[idx,act[idx]];true_resp[idx]=responsibility[idx,act[idx]]
        trace[v]={'prior_true':true_prior,'responsibility_true':true_resp,'prior_all':prior,'responsibility_all':responsibility}
        for typ in np.unique(types):
            mask=known&(types==typ);ix=np.flatnonzero(mask)
            if not len(ix):continue
            rows=np.stack([prior[ix,act[ix]],responsibility[ix,act[ix]],p['visual_probability'][ix,act[ix]],(responsibility[ix].argmax(1)==act[ix]).astype(float),(prior[ix].argmax(1)==act[ix]).astype(float)],axis=1)
            collected.setdefault(int(typ),[]).append(rows)
    result={}
    for name,typ in ev.TYPE_IDS.items():
        if typ not in collected:continue
        r=np.concatenate(collected[typ])
        result[name]={'frames':len(r),'mean_nominal_action_history_prior':float(r[:,0].mean()),'mean_nominal_action_mixture_responsibility':float(r[:,1].mean()),'mean_nominal_action_visual_probability':float(r[:,2].mean()),'mixture_dominant_action_accuracy':float(r[:,3].mean()),'history_prior_argmax_accuracy':float(r[:,4].mean())}
    ev.write_json(OUT/'mechanism_diagnostics.json',result)
    return trace


def cases(trace):
    events=json.loads((OUT/'events.json').read_text());threshold=json.loads((OUT/'thresholds.json').read_text())
    indexed={(e['method'],e['video'],e['start']):e for e in events};global_events=[e for e in events if e['method']=='global_nn']
    selected=[]
    def choose(tag,criterion):
        candidates=[e for e in global_events if criterion(e,indexed[('history_soft_nn',e['video'],e['start'])])]
        if candidates:selected.append({'selection':tag,**sorted(candidates,key=lambda e:(e['video'],e['start']))[0]})
    choose('modification_gain',lambda g,h:g['type']=='Error_Modification' and not g['iou_matched'] and h['iou_matched'])
    choose('regression',lambda g,h:g['iou_matched'] and not h['iou_matched'])
    choose('slip_still_missed',lambda g,h:g['type']=='Error_Slip' and not g['onset_detected'] and not h['onset_detected'])
    plotdir=EXP/'case_studies';plotdir.mkdir(exist_ok=True)
    for i,c in enumerate(selected):
        v=c['video'];p=np.load(OUT/'predictions'/f'{v}.npz');lo=max(0,c['start']-80);hi=min(len(p['type_gt']),c['end']+80);t=np.arange(lo,hi)/ev.CFG['fps']
        fig,axes=plt.subplots(2,1,figsize=(11,6),sharex=True)
        for m,col in [('global_nn','#2878b5'),('visual_soft_nn','#b17b36'),('history_soft_nn','#218967'),('oracle_action_nn','#9358aa')]:
            axes[0].plot(t,p[m][lo:hi],label=m,color=col,lw=1.2);axes[0].axhline(threshold[m],linestyle=':',color=col,alpha=.55)
        axes[0].set_ylabel('Smoothed distance');axes[0].legend(fontsize=8)
        target_action=ev.ACTIONS[c['action']]
        axes[1].plot(t,trace[v]['prior_all'][lo:hi,target_action],label='History prior: event target action',color='#218967')
        axes[1].plot(t,trace[v]['responsibility_all'][lo:hi,target_action],label='Softmin responsibility: event target action',color='#ce5a45')
        c['fixed_target_action_id']=target_action
        axes[1].set_ylim(-.02,1.02);axes[1].set_ylabel('Weight');axes[1].set_xlabel('Feature time (s)');axes[1].legend(fontsize=8)
        for ax in axes:ax.axvspan(c['start']/10,c['end']/10,color='#dc7777',alpha=.12)
        fig.suptitle(f"{c['selection']} | {v}\n{c['type']}: {c['description']}",fontsize=10);fig.tight_layout()
        c['figure']=f'case_{i+1:02d}.png';fig.savefig(plotdir/c['figure'],dpi=140);plt.close(fig)
        c['comparison']={m:{k:indexed[(m,v,c['start'])][k] for k in ('iou_matched','onset_detected','delay_seconds_if_detected')} for m in NAMES}
    ev.write_json(plotdir/'cases.json',selected)
    return selected


def report(selected):
    s=json.loads((OUT/'summary.json').read_text());sel=json.loads((OUT/'normal_validation_selection.json').read_text());mec=json.loads((OUT/'mechanism_diagnostics.json').read_text())
    f=s['frame_metrics'];a=s['action_prediction']['test']
    lines=['# Tea 历史条件诊断','',
    '**本轮结论：历史信息改善了错误帧的动作预测，但检测收益仍不明确。历史软条件超过当前帧软条件及去后继结构对照，却没有可靠超过全局最近邻；固定验证阈值规则下事件 F1 还略有下降。当前应继续做机制辨析，不能把结果写成已验证的新检测方法。**','',
    '## 实验范围','',
    '新增文件全部位于本目录。读取上一轮固定正常特征库及同一划分，正常训练 26 个视频、正常验证 3 个、测试 35 个；所有旧实验文件和数据保持只读。原特征缺失清单及标签版本核对继承[上一轮来源报告](../tea_action_diagnostic_20260911/PROVENANCE.md)。', '',
    '本轮只训练正常动作历史模型，不训练目标对象/状态识别器。没有使用测试动作或错误标签参与实际预测。Oracle 与机制分析可读取真实标签，均不作为可部署分支。','',
    '## 机制与对照','',
    '- 从正常训练逐帧动作序列估计 21 个隐状态的转移概率。每个前景动作有执行状态和背景状态，背景状态保留最后一个前景动作，防止所有 BG 都抹掉历史；另有初始 BG 状态。',
    '- 在时间 t，先由上一时刻状态分布和转移矩阵计算动作先验 q(a_t|x_<t)，用于选择/加权当前动作参考距离；随后才用当前视觉证据更新状态。这里的“应执行动作”是正常过程统计预测，不是经过因果验证的意图。',
    '- 每行转移计数加入 0.1 伪计数，允许训练中未出现的转移；因此是软转移先验，不是严格合法动作判定。',
    '- 历史硬条件选择先验最大动作；历史软条件保留动作分布，用 `-tau * log(sum_a [q(a) * exp(-d_a/tau)])` 评分，tau=0.05。外层仍为与上一轮相同的 5 帧因果均值。',
    '- 当前帧软条件使用视觉动作分布做同样的加权软最小距离，区分历史收益与软加权本身的收益。',
    '- 去后继结构对照保留各隐状态自转移概率，将离开该状态的概率均匀分配给其他状态；它同时去除了背景记忆后继结构，不是只删一类任务图边的严格消融。此对照与历史模型共用参数，未单独调优。',
    '- 只有正常验证动作负对数似然用于选择温度和观测强度；历史目标评价的是读取当前帧之前的动作先验。共有 9 组历史候选、3 组视觉温度，候选表在测试评分前写入。',
    f"- 选中历史温度 {sel['history']['temperature']}、观测强度 {sel['history']['strength']}；当前帧视觉温度 {sel['visual']['temperature']}。转移模型拟合来自训练集；参数选择和 99% 正常分位阈值来自验证集。参数落在候选范围边缘，本轮未据测试结果扩展搜索。",'',
    '## 检测结果','',
    '主诊断子集与上一轮一致：45,596 个具有正常动作对应关系的帧，含 BG，排除 Addition；全测试集为 48,827 帧。各方法使用相同掩码、特征库和评分后处理。上一轮三条基线逐视频分数复现通过。','',
    '| 方法 | 主诊断子集 AP | 全测试 AP | 全测试 AUROC | 事件 F1 | 正常误报/分钟 |',
    '|---|---:|---:|---:|---:|---:|']
    for m,n in NAMES.items():
        e=s['event_metrics'][m];lines.append(f"| {n} | {f['oracle_supported'][m]['ap']:.4f} | {f['all_frames'][m]['ap']:.4f} | {f['all_frames'][m]['roc_auc']:.4f} | {e['event_f1']:.4f} | {e['normal_alarm_onsets_per_minute']:.3f} |")
    lines+=['','事件采用上一轮 tIoU≥0.1 的一对一匹配。误报频率分母为 Normal 时长。阈值均按正常验证分数 99% 分位选取，不能解释成相同测试误报预算。','',
    '| 配对比较（主诊断子集） | ΔAP | 视频 Bootstrap 95% 区间 |',
    '|---|---:|---:|']
    for pair,d in s['paired_video_bootstrap'].items():
        left,right=pair.split(' minus ');delta=f['oracle_supported'][left]['ap']-f['oracle_supported'][right]['ap'];ci=d['delta_ap_95pct_video_CI']
        lines.append(f"| {NAMES[left]} − {NAMES[right]} | {delta:+.4f} | [{ci[0]:+.4f}, {ci[1]:+.4f}] |")
    lines+=['','区间基于 300 次视频级配对重采样。当前测试集此前已参与方向探索，多个比较也未做多重检验校正；区间只用于此协议下的诊断，不能替代独立任务验证。','',
    '## 动作判断改善为何尚未变成检测改善','',
    '| 错误帧动作判断（10,503 个有正常动作对应帧） | Top-1 | Top-3 | 动作 NLL |',
    '|---|---:|---:|---:|']
    for m,n in [('visual','当前帧视觉'),('history','历史先验'),('no_order','去后继结构')]:
        r=a['known_errors'][m];lines.append(f"| {n} | {r['accuracy']:.1%} | {r['top3_accuracy']:.1%} | {r['action_nll']:.3f} |")
    lines+=['','历史先验在错误帧的 Top-1/Top-3 均提高，但将其压成一个动作的历史硬条件表现较差。保留多个动作可减少错误硬决策；同时，软最小距离也可能让外观更相似的错误参照支配评分。','',
    '下面的“评分后责任权重”为 `q(a)*exp(-d_a/tau)` 归一化后的权重，表示各动作分支对软最小距离的相对贡献，不是新的动作预测器或错误概率。表中均只统计有正常动作对应的帧。','',
    '| 类型 | 正确名义动作的历史先验均值 | 评分后责任权重均值 |',
    '|---|---:|---:|']
    for t,r in mec.items():lines.append(f"| {t} | {r['mean_nominal_action_history_prior']:.3f} | {r['mean_nominal_action_mixture_responsibility']:.3f} |")
    lines+=['','真实标签仅用于这些统计，不进入评分。各类型平均责任权重并没有低于平均先验，因此本轮不能声称软最小距离普遍抹除了正确动作信念；应结合个案及独立干预验证。Modification 的名义动作先验均值仍低，Slip 的名义动作分支权重较高却仍漏检，这两类错误的瓶颈不同。','',
    '## 类型与事件分析','',
    '| 类型 | 全局 AP | 当前帧软条件 AP | 历史软条件 AP | Oracle AP |',
    '|---|---:|---:|---:|---:|']
    for t,d in s['per_type_vs_Normal'].items():lines.append(f"| {t} | {d['global_nn']['ap']:.4f} | {d['visual_soft_nn']['ap']:.4f} | {d['history_soft_nn']['ap']:.4f} | {d['oracle_action_nn']['ap']:.4f} |")
    lines+=['','各类型 AP 以对应类型为正类、Normal 为负类，排除其他错误。类型之间正类比例不同。Modification 有改善，Slip 与 Correction 仍低于全局距离。Addition 没有正常动作对应类，oracle 对其回退至全局原始距离，不适合用于估计这类错误的条件信息上界。','',
    '| 方法 | 事件召回 | 事件内新报警召回 | 新报警漏检率 | 命中延迟中位数/s |',
    '|---|---:|---:|---:|---:|']
    for m in ('global_nn','visual_soft_nn','history_soft_nn','oracle_action_nn'):
        d=s['event_metrics'][m];lines.append(f"| {NAMES[m]} | {d['event_recall']:.3f} | {d['onset_recall']:.3f} | {d['onset_miss_rate']:.3f} | {d['median_delay_seconds_detected_only']:.1f} |")
    lines+=['','延迟仅对命中事件统计，从真实事件起点到区间内第一次新报警；前一事件或背景已开始的持续报警不算新报警。由于源特征窗口未核实，不能据此宣称端到端在线性能。','',
    '## 个案','',
    '案例按固定规则选择：一个 Modification 匹配改善、一个全局匹配成功而历史匹配失败的退化事件、一个两者仍漏检的 Slip；满足条件后按视频名/起点排序取首例，不根据曲线外观挑选。图中阴影是真实事件，虚线是正常验证阈值，下图固定追踪该事件名义动作的先验与评分责任权重，不随邻近帧标签切换。事件匹配失败可能来自报警时机或持续区间不佳，并不等于没有任何报警。','']
    for c in selected:lines.append(f"- [{c['selection']}](case_studies/{c['figure']})：{c['video']}，{c['start']/10:.1f}–{c['end']/10:.1f}s，{c['type']}，{c['description']}。")
    lines+=['','这些是分数与信念轨迹分析，本轮没有新增视频内容语义标注；原视频抽帧观察见[上一轮案例](../tea_action_diagnostic_20260911/REPORT.md)。','',
    '## 决策与后续','',
    '保留“历史预期与当前执行分离”作为候选机制，停止把普通 HMM/软融合包装成新方法。接下来最值得验证的是：当前错误执行的视觉证据是否持续把历史信念拉向错误解释，以及是否需要保留独立的程序进度信念。这里是待检验假设，不是本轮已证明的结论。',
    '',
    '一个具体的后续实验是对错误区间内的信念更新做离线 oracle 干预诊断：仅在分析分支冻结/弱化状态更新，实际方法仍不得读错误标签。若该干预并不能缩小 oracle 动作参照差距，应优先检查目标对象/关系信息，而不是继续堆叠历史模块。若干预有效，再设计仅凭可观测残差控制更新的机制，并在新的独立任务上验证。',
    '',
    '当前剩余限制：26 个训练视频、3 个正常验证视频、重复使用的单任务测试集、精确特征提取记录缺失。不能声称跨任务泛化、动作效果建模或论文级优越性。新增机制仍需针对 PREGO、GTG2Vid、正常动作多原型、Action Effect Modeling 等最近工作进行定位。','',
    '## 复现','',
    '```powershell',
    'python experiments/tea_history_diagnostic_20260911/run_history.py',
    'python experiments/tea_history_diagnostic_20260911/analyze.py',
    '```','',
    '- 依赖：numpy、scipy、scikit-learn、threadpoolctl、matplotlib，使用已有环境。',
    '- 参数：[protocol.json](protocol.json)；训练序列与转移矩阵：[transition_model.json](outputs/transition_model.json)；全部正常验证候选：[normal_validation_selection.json](outputs/normal_validation_selection.json)。',
    '- 结果：[summary.json](outputs/summary.json)；正常验证阈值：[thresholds.json](outputs/thresholds.json)；机制统计：[mechanism_diagnostics.json](outputs/mechanism_diagnostics.json)。',
    '- 逐视频分数与历史分布保存在 `outputs/predictions/`；事件/报警明细在 `outputs/events.json` 和 `outputs/alarms.json`。',
    '- 测试通过：[checks.json](outputs/checks.json)，覆盖历史先验不受当前/未来观测改动影响、评分前缀一致性、持续性消融不变量、旧基线复现和划分隔离。',
    '- `evaluation.py` 是上一轮评测函数的本地快照，输出固定在当前目录；旧代码不被导入执行。使用上一轮正常特征库作为只读输入，不重建或覆盖它。','']
    (EXP/'REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'mechanisms':mec,'cases':[{'selection':c['selection'],'video':c['video'],'figure':c['figure']} for c in selected]},ensure_ascii=False,indent=2))


def main():
    trace=mechanisms();selected=cases(trace);report(selected)


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
