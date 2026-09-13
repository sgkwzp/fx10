"""Phase-conditioned unsupervised residual gate for the Tea diagnostic.

All fitting uses normal training videos. A frame phase is the nearest normal
action prototype. Each phase gets its own residual mean/covariance when enough
normal frames are available; otherwise the global model is used.
"""
from pathlib import Path
import json
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = Path(__file__).resolve().parents[2]
FEAT = ROOT / "data/Tea/vc_v_features_10fps"
LABEL = ROOT / "data/Tea/refined_label_v3"
PROTO = ROOT / "data/Tea/vc_normal_action_features"
OUT = ROOT / "experiments/tea_gating_20260911/results/phase_conditioned_gate"

def norm(x): return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-8)
def labels(v):
    ys=[]; ts=[]
    for line in (LABEL/f"{v}.txt").read_text().splitlines():
        p=line.split('|'); t=p[1] if len(p)>1 else 'Normal'; ys.append(t!='Normal'); ts.append(t)
    return np.asarray(ys, dtype=np.int8), ts
def residuals(x, protos, ref, delta_ref):
    x=norm(x); phase=(x@protos.T).argmax(1)
    visual=1-(x@protos.T).max(1)
    dx=np.vstack([np.zeros((1,x.shape[1]),dtype=x.dtype),np.diff(x,axis=0)])
    order=np.linalg.norm(dx-delta_ref,axis=1)
    effect=1-(x@ref.T).max(1)
    return np.stack([visual,order,effect],1), phase
def fit(R):
    mu=R.mean(0); sd=R.std(0)+1e-6; z=(R-mu)/sd
    cov=np.cov(z,rowvar=False)+0.1*np.eye(3)
    return mu,sd,np.linalg.inv(cov)
def score(R, model):
    mu,sd,inv=model; q=(R-mu)/sd
    return np.einsum('ni,ij,nj->n',q,inv,q)

def main():
    train=(ROOT/'data/Tea/training.txt').read_text().split(); test=(ROOT/'data/Tea/test.txt').read_text().split()
    protos=norm(np.stack([np.load(p) for p in sorted(PROTO.glob('Action_*.npy'))]))
    normal_ref=[]; delta=[]; train_cache=[]
    for v in train:
        p=FEAT/f'{v}.npy'
        if not p.exists(): continue
        x=norm(np.load(p).astype('float32')); y,_=labels(v); normal_ref.append(x[y==0])
        keep=(y[1:]==0)&(y[:-1]==0); delta.append(x[1:][keep]-x[:-1][keep])
    ref=norm(np.concatenate(normal_ref)); ref=ref[::max(1,len(ref)//2000)]; delta_ref=np.median(np.concatenate(delta),0)
    for v in train:
        p=FEAT/f'{v}.npy'
        if not p.exists(): continue
        x=norm(np.load(p).astype('float32')); y,_=labels(v); R,ph=residuals(x,protos,ref,delta_ref)
        train_cache.append((R[y==0],ph[y==0]))
    allR=np.concatenate([r for r,_ in train_cache]); global_model=fit(allR)
    phase_models={}
    for k in range(len(protos)):
        vals=np.concatenate([r[p==k] for r,p in train_cache if np.any(p==k)],axis=0) if any(np.any(p==k) for _,p in train_cache) else np.empty((0,3))
        phase_models[k]=fit(vals) if len(vals)>=100 else global_model
    ys=[]; gate=[]; effect=[]; types=[]
    for v in test:
        p=FEAT/f'{v}.npy'
        if not p.exists(): continue
        x=np.load(p).astype('float32'); y,t=labels(v); n=min(len(x),len(y)); R,ph=residuals(x[:n],protos,ref,delta_ref)
        g=np.asarray([score(R[i:i+1],phase_models[int(ph[i])])[0] for i in range(n)])
        ys.append(y[:n]); gate.append(g); effect.append(R[:,2]); types.extend(t[:n])
    y=np.concatenate(ys); g=np.concatenate(gate); e=np.concatenate(effect)
    result={'test':{'frames':int(len(y)),'positive_rate':float(y.mean()),'effect_only':{'roc_auc':float(roc_auc_score(y,e)),'average_precision':float(average_precision_score(y,e))},'phase_conditioned_gate':{'roc_auc':float(roc_auc_score(y,g)),'average_precision':float(average_precision_score(y,g))}},'phase_model_frame_counts':{str(k):sum(int(np.sum(p==k)) for _,p in train_cache) for k in phase_models}}
    by={}
    for s,t in zip(g,types): by.setdefault(t,[]).append(float(s))
    result['error_type_gate_mean']={k:float(np.mean(v)) for k,v in by.items()}
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'summary.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
if __name__=='__main__': main()
