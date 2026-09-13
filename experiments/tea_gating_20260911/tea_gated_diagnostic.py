"""Unsupervised residual gating for Tea.

Fits a robust Mahalanobis gate on normal training residuals only, then evaluates
held-out test videos. This avoids using positive test labels for fitting.
"""
from pathlib import Path
import json
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = Path(__file__).resolve().parents[2]
FEAT = ROOT / "data/Tea/vc_v_features_10fps"
LABEL = ROOT / "data/Tea/refined_label_v3"
PROTO = ROOT / "data/Tea/vc_normal_action_features"
OUT = ROOT / "results/tea_gated_diagnostic"

def norm(x): return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-8)
def labels(v):
    ys=[]; ts=[]
    for line in (LABEL/f"{v}.txt").read_text().splitlines():
        p=line.split('|'); t=p[1] if len(p)>1 else 'Normal'; ys.append(t!='Normal'); ts.append(t)
    return np.asarray(ys, dtype=np.int8), ts

def raw_scores(x, protos, ref, delta_ref):
    x=norm(x)
    visual=1-(x@protos.T).max(1)
    dx=np.vstack([np.zeros((1,x.shape[1]),dtype=x.dtype),np.diff(x,axis=0)])
    order=np.linalg.norm(dx-delta_ref,axis=1)
    effect=1-(x@ref.T).max(1)
    return np.stack([visual,order,effect],1)

def main():
    train=(ROOT/'data/Tea/training.txt').read_text().split()
    test=(ROOT/'data/Tea/test.txt').read_text().split()
    protos=norm(np.stack([np.load(p) for p in sorted(PROTO.glob('Action_*.npy'))]))
    xs=[]; ds=[]
    for v in train:
        p=FEAT/f'{v}.npy'
        if not p.exists(): continue
        x=norm(np.load(p).astype('float32')); y,_=labels(v); xs.append(x[y==0])
        keep=(y[1:]==0)&(y[:-1]==0); ds.append((x[1:][keep]-x[:-1][keep]))
    ref=norm(np.concatenate(xs)); ref=ref[::max(1,len(ref)//2000)]
    delta_ref=np.median(np.concatenate(ds),0)
    train_res=[]
    for v in train:
        p=FEAT/f'{v}.npy'
        if not p.exists(): continue
        x=norm(np.load(p).astype('float32')); y,_=labels(v)
        train_res.append(raw_scores(x[y==0],protos,ref,delta_ref))
    R=np.concatenate(train_res); mu=R.mean(0); sd=R.std(0)+1e-6; Z=(R-mu)/sd
    # Shrunk covariance makes the gate stable with correlated residuals.
    cov=np.cov(Z,rowvar=False)+0.1*np.eye(3); inv=np.linalg.inv(cov)
    def gate(S):
        Q=(S-mu)/sd
        return np.einsum('ni,ij,nj->n',Q,inv,Q)
    out={}
    for split, vids in [('test',test)]:
        all_y=[]; all_g=[]; all_e=[]; by={}
        for v in vids:
            p=FEAT/f'{v}.npy'
            if not p.exists(): continue
            x=np.load(p).astype('float32'); y,ts=labels(v); n=min(len(x),len(y)); y=y[:n]; ts=ts[:n]
            S=raw_scores(x[:n],protos,ref,delta_ref); g=gate(S)
            all_y.append(y); all_g.append(g); all_e.append(S[:,2])
            for t in sorted(set(ts)):
                m=np.asarray([z==t for z in ts]); by.setdefault(t,[]).extend(g[m].tolist())
        y=np.concatenate(all_y); g=np.concatenate(all_g); e=np.concatenate(all_e)
        out['test']={'frames':int(len(y)),'positive_rate':float(y.mean()),
          'effect_only':{'roc_auc':float(roc_auc_score(y,e)),'average_precision':float(average_precision_score(y,e))},
          'mahalanobis_gate':{'roc_auc':float(roc_auc_score(y,g)),'average_precision':float(average_precision_score(y,g))}}
        out['error_type_gate_mean']={k:float(np.mean(v)) for k,v in by.items()}
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'summary.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))

if __name__=='__main__': main()
