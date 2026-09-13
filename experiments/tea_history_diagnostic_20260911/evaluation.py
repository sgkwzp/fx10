"""Read-only Tea inputs; all outputs reside next to this script.

Normal-bank and action-conditional nearest-neighbour diagnostics, not action-
effect models. Prediction never consumes validation/test labels. The oracle
branch explicitly does. See protocol.json and REPORT.md for evaluation scope.
"""
import json
import platform
from collections import Counter
from pathlib import Path
import numpy as np
import sklearn
from sklearn.metrics import average_precision_score, roc_auc_score, confusion_matrix
from threadpoolctl import threadpool_limits

EXP = Path(__file__).resolve().parent
ROOT = EXP.parents[1]
DATA = ROOT / "data/Tea"
OUT = EXP / "outputs"
CFG = json.loads((EXP / "protocol.json").read_text(encoding="utf-8"))
ANN = json.loads((ROOT / "data/annotation.json").read_text(encoding="utf-8"))["tea"]
ACTIONS = ANN["action2idx"]
TYPE_IDS = ANN["actiontype2idx"]
METHODS = CFG["methods"]


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def normalize(x):
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-8)


def read_labels(video):
    lines = (DATA / "refined_label_v3" / f"{video}.txt").read_text(encoding="utf-8").splitlines()
    fields = [s.split("|") for s in lines]
    assert all(len(p) in (2, 3) and p[1] in TYPE_IDS for p in fields)
    typ = np.array([TYPE_IDS[p[1]] for p in fields], dtype=np.int16)
    # Match the local GTG2Vid loader: additions have no normal action class.
    act = np.array([ACTIONS.get(p[0], -1) if p[1] != "Error_Addition" else -1 for p in fields], dtype=np.int16)
    return act, typ, lines


def smooth(x, window=None):
    window = window or CFG["causal_smoothing_frames"]
    cs = np.concatenate([np.zeros(1), np.cumsum(x, dtype=np.float64)])
    end = np.arange(1, len(x)+1)
    start = np.maximum(0, end-window)
    return (cs[end]-cs[start])/(end-start)


def runs(mask):
    changes = np.diff(np.r_[False, mask, False].astype(np.int8))
    return list(zip(np.flatnonzero(changes == 1).tolist(), np.flatnonzero(changes == -1).tolist()))


def gt_events(lines):
    boundaries = [0] + [i for i in range(1, len(lines)) if lines[i] != lines[i-1]] + [len(lines)]
    events = []
    for s, e in zip(boundaries[:-1], boundaries[1:]):
        parts = lines[s].split("|")
        if parts[1] != "Normal":
            events.append({"start": s, "end": e, "type": parts[1], "action": parts[0], "description": parts[2] if len(parts) == 3 else ""})
    return events


def inventory():
    splits = {s: (DATA / f"{s}.txt").read_text().split() for s in ("training", "validation", "test")}
    assert all(len(v) == len(set(v)) for v in splits.values())
    assert all(not(set(splits[a]) & set(splits[b])) for a,b in [("training","validation"),("training","test"),("validation","test")])
    raw_ann = {s["video_id"]: s["labels"] for s in ANN["segments"]}
    records = []
    for split, videos in splits.items():
        for v in videos:
            act, typ, lines = read_labels(v)
            rec = {"video": v, "split": split, "label_frames": len(lines), "types": {name:int((typ==k).sum()) for name,k in TYPE_IDS.items()}, "unsupported_action_frames":int((act<0).sum())}
            for family in ("vc_v_features_10fps", "features_10fps"):
                p = DATA / family / f"{v}.npy"
                info = {"exists": p.exists()}
                if p.exists():
                    x = np.load(p, mmap_mode="r", allow_pickle=False)
                    assert x.ndim == 2 and len(x) == len(lines), (v, family, x.shape, len(lines))
                    assert np.isfinite(x).all(), (v, family)
                    info.update(shape=list(x.shape), dtype=str(x.dtype), zero_rows=int((np.linalg.norm(x.astype(np.float32),axis=1)==0).sum()))
                rec[family] = info
            rec["json_annotation_available"] = v in raw_ann
            if v in raw_ann:
                stamps=raw_ann[v]["time_stamp"]
                rec["json_end_minus_frame_duration_s"] = round(stamps[-1][1]-len(lines)/CFG["fps"],3)
                # Compare interior timestamps (avoid endpoint-rounding conventions).
                checks=[]
                for (s,e),t in zip(stamps,raw_ann[v]["action_type"]):
                    a=int(np.ceil(s*CFG["fps"]))+1; b=int(np.floor(e*CFG["fps"]))
                    if 0<=a<b<=len(typ): checks.extend((typ[a:b]==t).tolist())
                rec["json_type_interior_agreement"] = float(np.mean(checks)) if checks else None
            records.append(rec)
    available = {s:[v for v in vs if (DATA/CFG["feature_family"]/f"{v}.npy").exists()] for s,vs in splits.items()}
    audit = {"splits_disjoint":True,"label_action_map":ACTIONS,"label_type_map":TYPE_IDS,"splits":{},"videos":records}
    for split in splits:
        rr=[r for r in records if r["split"]==split]
        audit["splits"][split]={"listed_videos":len(splits[split]),"available_videos":len(available[split]),"missing_videos":sorted(set(splits[split])-set(available[split])),"used_frames":sum(r["label_frames"] for r in rr if r[CFG["feature_family"]]["exists"])}
    write_json(OUT/"audit.json",audit)
    write_json(OUT/"split_manifest.json",{"listed":splits,"used":available})
    return available, audit


def load(video):
    x=np.load(DATA/CFG["feature_family"]/f"{video}.npy",allow_pickle=False).astype(np.float32)
    act,typ,lines=read_labels(video)
    assert len(x)==len(act)
    return normalize(x),act,typ,lines


def fit_bank(videos):
    chunks={k:[] for k in ACTIONS.values()}; provenance=[]
    for v in videos:
        x,act,typ,_=load(v)
        assert not (typ>0).any(), "This protocol expects all-normal training videos"
        for k in chunks:
            ids=np.flatnonzero((act==k)&(typ==0))
            if len(ids): chunks[k].append((v,ids,x[ids]))
    bank=[]; bank_labels=[]; centers=[]; keys=[]
    for k, groups in sorted(chunks.items()):
        if not groups: continue
        # Equal approximate allocation per video, then fill unused budget.
        cap=CFG["bank_per_class"]; quota=np.zeros(len(groups),dtype=int)
        while quota.sum()<cap and any(quota[i]<len(g[1]) for i,g in enumerate(groups)):
            for i,g in enumerate(groups):
                if quota.sum()<cap and quota[i]<len(g[1]): quota[i]+=1
        class_rows=[]
        for q,(v,ids,x) in zip(quota,groups):
            selected=np.linspace(0,len(ids)-1,q,dtype=int) if q else np.array([],dtype=int)
            class_rows.append(x[selected])
            provenance.extend({"video":v,"frame":int(ids[i]),"action":int(k)} for i in selected)
        b=np.concatenate(class_rows)
        bank.append(b); bank_labels.extend([k]*len(b)); keys.append(k)
        # Train-only action centroid; same underlying normal videos as the bank.
        centers.append(np.concatenate([g[2] for g in groups]).mean(axis=0))
    bank=np.concatenate(bank); centers=normalize(np.stack(centers)); keys=np.array(keys)
    assert len(bank)==len(provenance)
    np.savez_compressed(OUT/"normal_bank.npz",features=bank,actions=bank_labels,centers=centers,center_actions=keys)
    write_json(OUT/"bank_manifest.json",provenance)
    return bank,np.asarray(bank_labels),centers,keys


def predict(x,bank,bact,centers,keys):
    # No labels, video-level statistics, or future score samples enter here.
    matrix=[]; pred=[]
    for start in range(0,len(x),512):
        chunk=x[start:start+512]; sim=chunk@bank.T
        matrix.append(np.stack([1-np.max(sim[:,bact==k],axis=1) for k in keys],axis=1))
        pred.append(np.argmax(chunk@centers.T,axis=1))
    matrix=np.concatenate(matrix); p=np.concatenate(pred)
    g=matrix.min(axis=1); conditional=matrix[np.arange(len(x)),p]
    return matrix,p,{"global_nn":smooth(g),"predicted_action_nn":smooth(conditional)}


def attach_oracle(matrix,actions,keys,scores):
    # Oracle labels are isolated from both deployable scorers.
    oracle=matrix.min(axis=1).copy()
    for col,k in enumerate(keys):
        mask=actions==k; oracle[mask]=matrix[mask,col]
    scores["oracle_action_nn"]=smooth(oracle)
    return scores


def match_events(gt, alarms, iou_threshold):
    # One-to-one maximum cardinality matching of intervals above fixed tIoU.
    edges={}
    for i,g in enumerate(gt):
        edges[i]=[]
        for j,(a,b) in enumerate(alarms):
            inter=max(0,min(b,g["end"])-max(a,g["start"]))
            union=max(b,g["end"])-min(a,g["start"])
            if inter/union>=iou_threshold:edges[i].append(j)
    matched={}
    def visit(i,seen):
        for j in edges[i]:
            if j in seen:continue
            seen.add(j)
            if j not in matched or visit(matched[j],seen):matched[j]=i;return True
        return False
    for i in edges:visit(i,set())
    return set(matched.values())


def metric(y,s):
    return {"frames":len(y),"positive_frames":int(y.sum()),"positive_rate":float(y.mean()),"ap":float(average_precision_score(y,s)) if y.any() else None,"roc_auc":float(roc_auc_score(y,s)) if len(np.unique(y))==2 else None}


def evaluate(caches,thresholds):
    summaries={}; events=[]; pervideo=[]; alarms_table=[]
    for m in METHODS:
        total_gt=0;total_pred=0;matched_count=0;normal_onsets=0;normal_frames=0;delays=[]; onset_count=0
        for v,c in caches.items():
            s=c["scores"][m];typ=c["typ"];y=typ>0
            alarms=runs(s>thresholds[m]); gt=gt_events(c["lines"])
            matched=match_events(gt,alarms,CFG["event_iou"])
            normal_onsets+=sum(not y[a] for a,b in alarms);normal_frames+=int((~y).sum())
            total_gt+=len(gt);total_pred+=len(alarms);matched_count+=len(matched)
            for idx,g in enumerate(gt):
                starts=[a for a,b in alarms if g["start"]<=a<g["end"]]
                delay=(min(starts)-g["start"])/CFG["fps"] if starts else None
                onset_count+=bool(starts)
                if delay is not None:delays.append(delay)
                events.append({"method":m,"video":v,**g,"iou_matched":idx in matched,"onset_detected":bool(starts),"delay_seconds_if_detected":delay,"carried_alarm_at_start":any(a<g["start"]<b for a,b in alarms),"mean_score":float(np.mean(s[g["start"]:g["end"]]))})
            for a,b in alarms:alarms_table.append({"method":m,"video":v,"start":a,"end":b,"onset_is_normal":not bool(y[a]),"mean_score":float(s[a:b].mean())})
            pervideo.append({"method":m,"video":v,**metric(y,s),"gt_events":len(gt),"matched_events":len(matched),"alarm_events":len(alarms)})
        precision=matched_count/total_pred if total_pred else 0
        recall=matched_count/total_gt if total_gt else 0
        summaries[m]={"threshold":thresholds[m],"event_iou_threshold":CFG["event_iou"],"gt_events":total_gt,"alarm_events":total_pred,"matched_events":matched_count,"event_precision":precision,"event_recall":recall,"event_f1":2*precision*recall/(precision+recall) if precision+recall else 0,"onset_recall":onset_count/total_gt,"onset_miss_rate":1-onset_count/total_gt,"median_delay_seconds_detected_only":float(np.median(delays)) if delays else None,"normal_alarm_onsets_per_minute":normal_onsets/(normal_frames/CFG["fps"]/60)}
    write_json(OUT/"events.json",events);write_json(OUT/"alarms.json",alarms_table);write_json(OUT/"per_video.json",pervideo)
    y=np.concatenate([c["typ"]>0 for c in caches.values()]);t=np.concatenate([c["typ"] for c in caches.values()]);a=np.concatenate([c["act"] for c in caches.values()])
    subsets={"all_frames":np.ones(len(y),bool),"oracle_supported":a>=0,"correction_excluded":t!=TYPE_IDS["Error_Correction"]}
    frame={}
    for subset,mask in subsets.items():
        frame[subset]={m:metric(y[mask],np.concatenate([c["scores"][m] for c in caches.values()])[mask]) for m in METHODS}
    pertype={}
    for name,k in TYPE_IDS.items():
        if k==0:continue
        mask=(t==0)|(t==k);pertype[name]={}
        for m in METHODS:
            ev=[e for e in events if e["method"]==m and e["type"]==name]
            pertype[name][m]={**metric((t[mask]==k),np.concatenate([c["scores"][m] for c in caches.values()])[mask]),"events":len(ev),"onset_recall":sum(e["onset_detected"] for e in ev)/len(ev) if ev else None,"event_recall":sum(e["iou_matched"] for e in ev)/len(ev) if ev else None}
    return {"frame_metrics":frame,"event_metrics":summaries,"per_type_vs_Normal":pertype}

