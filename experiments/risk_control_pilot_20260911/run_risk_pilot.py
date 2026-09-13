"""A matched-unit risk audit using an explicitly labelled diagnostic scorer.

Pooled frame/block conformal thresholds are heuristics here. Valid video-level
statements require exchangeable whole videos; no arbitrary task-shift guarantee.
"""
from pathlib import Path
import json
import math
import time
import numpy as np
import torch
from sklearn.metrics import average_precision_score
from scipy.stats import beta
from threadpoolctl import threadpool_limits

EXP=Path(__file__).resolve().parent;ROOT=EXP.parents[1];OUT=EXP/'outputs'
CFG=json.loads((EXP/'protocol.json').read_text())
DEVICE='cuda' if torch.cuda.is_available() else 'cpu'


def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def normalize(x):return x/np.maximum(np.linalg.norm(x,axis=1,keepdims=True),1e-8)
def label(task,video):
    lines=(ROOT/'data'/task/'refined_label_v3'/f'{video}.txt').read_text().splitlines()
    return np.array([s.split('|')[1]!='Normal' for s in lines],dtype=bool)
def feature(task,video):return normalize(np.load(ROOT/'data'/task/CFG['feature_family']/f'{video}.npy',allow_pickle=False).astype(np.float32))
def smooth(x):
    cs=np.r_[0.,np.cumsum(x,dtype=float)];end=np.arange(1,len(x)+1);start=np.maximum(0,end-CFG['causal_mean_frames']);return (cs[end]-cs[start])/(end-start)


def inventory():
    result={}
    for task in CFG['tasks']:
        folder=ROOT/'data'/task;task_info={}
        for split in ['training','validation','test']:
            listed=(folder/f'{split}.txt').read_text().split()
            present=[v for v in listed if (folder/CFG['feature_family']/f'{v}.npy').exists()]
            missing=sorted(set(listed)-set(present));frames=0;positive=0;normal_videos=0
            for v in present:
                x=np.load(folder/CFG['feature_family']/f'{v}.npy',mmap_mode='r');y=label(task,v)
                assert x.ndim==2 and len(x)==len(y) and np.isfinite(x).all(),(task,v)
                frames+=len(y);positive+=int(y.sum());normal_videos+=not y.any()
            task_info[split]={'listed':listed,'used':present,'missing':missing,'frames':frames,'positive_frames':positive,'normal_videos':normal_videos}
        for a,b in [('training','validation'),('training','test'),('validation','test')]:assert not set(task_info[a]['used'])&set(task_info[b]['used'])
        assert task_info['training']['positive_frames']==0 and task_info['validation']['positive_frames']==0
        result[task]=task_info
    write(OUT/'inventory.json',result);return result


def build_bank(task,videos):
    # Sample equally across available training videos; retain exact row provenance.
    q,r=divmod(CFG['reference_rows_per_task'],len(videos));arrays=[];records=[]
    for i,v in enumerate(videos):
        x=feature(task,v);y=label(task,v);assert not y.any()
        ids=np.linspace(0,len(x)-1,min(len(x),q+(i<r)),dtype=int)
        arrays.append(x[ids]);records.extend({'task':task,'video':v,'frame':int(k)} for k in ids)
    write(OUT/f'bank_{task}_manifest.json',records)
    bank=np.concatenate(arrays);np.save(OUT/f'bank_{task}.npy',bank);return bank


def score(task,video,bank):
    x=feature(task,video);b=torch.from_numpy(bank.T.copy()).to(DEVICE);result=[]
    with torch.inference_mode():
        for i in range(0,len(x),1024):
            v=torch.from_numpy(x[i:i+1024]).to(DEVICE);result.append((1-(v@b).max(1).values).clamp(0,2).cpu().numpy())
    return smooth(np.concatenate(result))


def cp_threshold(values,alpha):
    values=np.asarray(values);n=len(values);rank=math.ceil((n+1)*(1-alpha))
    return (float(np.sort(values)[rank-1]) if rank<=n else float('inf')),rank,n


def blocks(scores):
    width=int(CFG['block_seconds']*CFG['fps']);n=len(scores)//width
    return scores[:n*width].reshape(n,width).max(1)


def crc_threshold(calibration,budget):
    # L_i(t) in [0,1]: fraction of fixed-size blocks whose maxima exceed t.
    # Corrected mean risk = (sum_i L_i(t) + 1)/(n+1).
    groups=[blocks(s) for s in calibration];n=len(groups)
    risk_target=budget*CFG['block_seconds']/60
    candidates=np.unique(np.concatenate(groups))
    for t in candidates:
        corrected=(sum(float((g>t).mean()) for g in groups)+1)/(n+1)
        if corrected<=risk_target+1e-12:return float(t),corrected,n
    # The explicit never-alarm policy is known to have zero loss. It is returned
    # as a vacuous policy, not falsely certified by the infeasible correction.
    return float('inf'),1/(n+1),n


def risk_curve(scores,y,threshold):
    # Error of a fixed threshold classifier; confidence is distance to threshold.
    # Ties use expected risk under random ordering, not accidental frame order.
    if not np.isfinite(threshold):return {'aurc':None,'reason':'never-alarm threshold has no finite margin confidence'}
    pred=scores>threshold;err=(pred!=y).astype(float);conf=np.abs(scores-threshold)
    order=np.argsort(-conf,kind='stable');conf=conf[order];err=err[order]
    boundaries=np.r_[0,np.flatnonzero(np.diff(conf)!=0)+1,len(conf)]
    risks=[];prev_error=0.
    for a,b in zip(boundaries[:-1],boundaries[1:]):
        j=np.arange(1,b-a+1);p=err[a:b].mean();risks.extend(((prev_error+j*p)/(a+j)).tolist());prev_error+=err[a:b].sum()
    risks=np.asarray(risks)
    return {'aurc':float(risks.mean()),'full_coverage_error':float(err.mean()),'confidence':'absolute raw-score margin to fixed threshold; not a probability','risk_at_coverage':{str(c):float(risks[max(0,math.ceil(c*len(risks))-1)]) for c in [.1,.25,.5,.75,1.]}}


def binomial_interval(k,n):
    return [0. if k==0 else float(beta.ppf(.025,k,n-k+1)),1. if k==n else float(beta.ppf(.975,k+1,n-k))] if n else None


def evaluate(test,threshold):
    negatives=0;fp=0;positive=0;tp=0;normal_blocks=0;block_alerts=0;normal_video_alerts=[]
    nv_frames=0;nv_fp=0;nv_blocks=0;nv_block_alerts=0
    width=int(CFG['block_seconds']*CFG['fps'])
    for c in test:
        s,y=c['scores'],c['y'];above=s>threshold;negatives+=int((~y).sum());fp+=int((above&~y).sum());positive+=int(y.sum());tp+=int((above&y).sum())
        b=blocks(s);yb=y[:len(b)*width].reshape(len(b),width).any(1);normal_blocks+=int((~yb).sum());block_alerts+=int(((b>threshold)&~yb).sum())
        if not y.any():
            normal_video_alerts.append(bool(above.any()))
            nv_frames+=len(y);nv_fp+=int(above.sum());nv_blocks+=len(b);nv_block_alerts+=int((b>threshold).sum())
    nv=len(normal_video_alerts);na=sum(normal_video_alerts)
    return {'normal_frames':negatives,'normal_frame_FPR':fp/negatives,'error_frame_recall':tp/positive if positive else None,'all_normal_blocks':normal_blocks,'normal_block_alert_fraction':block_alerts/normal_blocks,'normal_block_alerts_per_minute':block_alerts/(normal_blocks*CFG['block_seconds']/60),'normal_videos':nv,'normal_videos_with_any_alert':na,'normal_video_any_alarm_fraction':na/nv if nv else None,'normal_video_binomial_95pct_interval_if_iid':binomial_interval(na,nv),'all_normal_video_frame_FPR':nv_fp/nv_frames if nv_frames else None,'all_normal_video_block_alert_fraction':nv_block_alerts/nv_blocks if nv_blocks else None}


def case_protocol(name,task,sources,bank,inv):
    base=OUT/name/task;base.mkdir(parents=True,exist_ok=True)
    cal=[];cal_ids=[]
    for source in sources:
        for v in inv[source]['validation']['used']:
            s=score(source,v,bank);assert not label(source,v).any();cal.append(s);cal_ids.append((source,v))
    # All decision rules fixed before scoring target test clips.
    configs=[]
    for alpha in CFG['alphas']:
        for unit,values in [('pooled_frames',np.concatenate(cal)),('pooled_1s_block_max',np.concatenate([blocks(s) for s in cal])),('video_max',np.array([s.max() for s in cal]))]:
            threshold,rank,n=cp_threshold(values,alpha)
            configs.append({'unit':unit,'alpha':alpha,'threshold':threshold,'rank':rank,'calibration_units':n})
    threshold,bound,n=crc_threshold(cal,CFG['alarm_budget_per_minute'])
    configs.append({'unit':'video_CRC_block_alert_rate','alpha':None,'threshold':threshold,'calibration_units':n,'budget_per_minute':CFG['alarm_budget_per_minute'],'correction_floor_per_minute':60/CFG['block_seconds']*bound})
    serial=[{**c,'threshold':c['threshold'] if np.isfinite(c['threshold']) else None,'never_alarm':not np.isfinite(c['threshold'])} for c in configs]
    write(base/'thresholds.json',{'source_tasks':sources,'calibration_videos':cal_ids,'rules':serial})
    test=[]
    for v in inv[task]['test']['used']:
        s=score(task,v,bank);y=label(task,v);assert len(s)==len(y)
        test.append({'video':v,'scores':s,'y':y});np.savez_compressed(base/f'{v}.npz',scores=s,error_labels=y)
    rows=[]
    for c in configs:
        original=c['threshold'];info={**c,'threshold':original if np.isfinite(original) else None,'never_alarm':not np.isfinite(original),'protocol':name,'target_task':task}
        rows.append({**info,**evaluate(test,original)})
    primary=next(c for c in configs if c['unit']=='pooled_frames' and c['alpha']==.05)
    scores=np.concatenate([c['scores'] for c in test]);y=np.concatenate([c['y'] for c in test])
    ranking={'ap':float(average_precision_score(y,scores)),'positive_rate':float(y.mean()),'risk_curve':risk_curve(scores,y,primary['threshold'])}
    write(base/'risk_results.json',rows);write(base/'ranking.json',ranking)
    return rows,ranking


def main():
    OUT.mkdir(exist_ok=True);tic=time.perf_counter();inv=inventory()
    banks={t:build_bank(t,inv[t]['training']['used']) for t in CFG['tasks']}
    all_rows=[];rankings={}
    for task in CFG['tasks']:
        for mode,sources in [('within_task',[task]),('leave_one_task_out',[t for t in CFG['tasks'] if t!=task])]:
            bank=np.concatenate([banks[t] for t in sources]);rows,ranking=case_protocol(mode,task,sources,bank,inv)
            all_rows.extend(rows);rankings[mode+'/'+task]=ranking
            print(mode,task,'complete',flush=True)
    write(OUT/'all_risk_results.json',all_rows);write(OUT/'rankings.json',rankings)
    write(OUT/'run_metadata.json',{'scorer':CFG['scorer'],'device':DEVICE,'torch':torch.__version__,'numpy':np.__version__,'runtime_seconds':time.perf_counter()-tic,'parameters_selected_on_test':False})
    # Decision-relevant edge cases: rank correction and ties.
    assert math.isinf(cp_threshold([.1,.2,.3],.05)[0])
    assert cp_threshold(np.arange(19),.05)[0]==18
    assert not (np.array([.5])>cp_threshold(np.repeat(.5,19),.05)[0]).any()
    write(OUT/'checks.json',{'normal_only_reference_and_calibration':'passed','within_task_split_disjoint':'passed','LOTO_target_excluded_from_bank_and_calibration':True,'conformal_small_n_infinity_and_ties':'passed','thresholds_written_before_target_test_scoring':True,'ECE_from_uninterpreted_distances':False})
    print('Finished',len(all_rows),'risk operating points.',flush=True)


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
