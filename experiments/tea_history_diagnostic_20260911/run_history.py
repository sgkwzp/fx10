"""Train-normal procedural history filtering with held-out normal selection.

No error labels or action labels enter prediction. Hidden background states
remember the last foreground action. Prediction at t uses observations < t;
only after scoring do emissions at t update the state belief.
"""
import json
import time
from pathlib import Path
import numpy as np
from scipy.special import softmax, logsumexp
from sklearn.metrics import average_precision_score
from threadpoolctl import threadpool_limits
import evaluation as ev

EXP=Path(__file__).resolve().parent
OUT=EXP/'outputs'
BASE=EXP.parent/'tea_action_diagnostic_20260911'
CFG=ev.CFG
METHODS=CFG['methods']


def get_features(v):
    # Input-only scorer interface: label files are never accessed here.
    return ev.normalize(np.load(ev.DATA/CFG['feature_family']/f'{v}.npy',allow_pickle=False).astype(np.float32))


def fit_transitions(videos, keys):
    states=[(0,True)]+[(int(k),bg) for k in keys if k!=0 for bg in (False,True)]
    lookup={s:i for i,s in enumerate(states)};classes=np.array([0 if bg else k for k,bg in states])
    counts=np.zeros((len(states),len(states)));initial=np.zeros(len(states));occupancy=np.zeros(len(states))
    segment_routes={}
    for v in videos:
        act,typ,_=ev.read_labels(v);assert not (typ>0).any()
        last=0;seq=[]
        for a in act:
            if a!=0:last=int(a)
            seq.append(lookup[(last,a==0)])
        initial[seq[0]]+=1
        np.add.at(counts,(seq[:-1],seq[1:]),1)
        np.add.at(occupancy,seq,1)
        segment_routes[v]=[states[seq[i]] for i in range(len(seq)) if i==0 or seq[i]!=seq[i-1]]
    alpha=CFG['transition_pseudocount']
    transition=(counts+alpha)/(counts.sum(1,keepdims=True)+alpha*len(states))
    start=(initial+alpha)/(initial.sum()+alpha*len(states))
    # Ablation: retain each state's learned persistence and redistribute exit mass
    # uniformly over every other state. It removes learned successors, including
    # background-memory successor structure; it is not a pure graph-edge ablation.
    no_order=np.empty_like(transition)
    for i in range(len(states)):
        no_order[i]=(1-transition[i,i])/(len(states)-1);no_order[i,i]=transition[i,i]
    params={'states':states,'state_output_action':classes.tolist(),'transition':transition.tolist(),'no_order_transition':no_order.tolist(),'initial':start.tolist(),'counts':counts.tolist(),'occupancy':occupancy.tolist(),'train_routes':segment_routes}
    ev.write_json(OUT/'transition_model.json',params)
    return classes,transition,no_order,start


def filter_history(similarity, classes, transition, initial, temperature, strength):
    likelihood=softmax(similarity/temperature,axis=1)
    priors=np.empty_like(likelihood,dtype=np.float64);posteriors=np.empty_like(priors)
    state=initial.copy()
    for t in range(len(similarity)):
        predicted=initial if t==0 else state@transition
        priors[t]=np.bincount(classes,weights=predicted,minlength=similarity.shape[1])
        emission=np.maximum(likelihood[t,classes],1e-15)**strength
        state=predicted*emission;state/=state.sum()
        posteriors[t]=np.bincount(classes,weights=state,minlength=similarity.shape[1])
    return priors,posteriors


def action_nll(p,actions):
    return float(-np.log(np.maximum(p[np.arange(len(p)),actions],1e-12)).mean())


def select_parameters(validation,centers,classes,transition,initial):
    # Only normal validation action labels, never test labels or error examples.
    cache=[]
    for v in validation:
        x=get_features(v);a,t,_=ev.read_labels(v);assert not (t>0).any()
        cache.append((x@centers.T,a))
    records=[];visual=[]
    for temp in CFG['emission_temperature_candidates']:
        visual.append({'temperature':temp,'normal_validation_action_nll':float(np.mean([action_nll(softmax(sim/temp,axis=1),a) for sim,a in cache]))})
        for strength in CFG['emission_strength_candidates']:
            vals=[]
            for sim,a in cache:
                prior,_=filter_history(sim,classes,transition,initial,temp,strength)
                vals.append(action_nll(prior,a))
            records.append({'temperature':temp,'strength':strength,'normal_validation_predictive_action_nll':float(np.mean(vals)),'per_video_nll':vals})
    chosen=min(records,key=lambda r:r['normal_validation_predictive_action_nll'])
    vchosen=min(visual,key=lambda r:r['normal_validation_action_nll'])
    result={'history':chosen,'visual':vchosen,'history_candidates':records,'visual_candidates':visual,'selection_videos':validation}
    ev.write_json(OUT/'normal_validation_selection.json',result)
    return chosen,vchosen


def soft_distance(distance,probability):
    tau=CFG['distance_softmin_temperature']
    return -tau*logsumexp(np.log(np.maximum(probability,1e-15))-distance/tau,axis=1)


def score_video(x,bank,bact,centers,keys,classes,transition,no_order,initial,chosen,vchosen):
    distance,p,scores=ev.predict(x,bank,bact,centers,keys)
    sim=x@centers.T
    prior,post=filter_history(sim,classes,transition,initial,chosen['temperature'],chosen['strength'])
    nprior,_=filter_history(sim,classes,no_order,initial,chosen['temperature'],chosen['strength'])
    visual=softmax(sim/vchosen['temperature'],axis=1)
    scores['visual_soft_nn']=ev.smooth(soft_distance(distance,visual))
    scores['history_hard_nn']=ev.smooth(distance[np.arange(len(distance)),prior.argmax(1)])
    scores['history_soft_nn']=ev.smooth(soft_distance(distance,prior))
    scores['no_order_soft_nn']=ev.smooth(soft_distance(distance,nprior))
    trace={'history_prior':prior,'history_posterior':post,'no_order_prior':nprior,'visual_probability':visual,'current_action_pred':keys[p],'history_action_pred':prior.argmax(1)}
    return scores,distance,trace


def checks(centers,bank,bact,keys,model,params,validation_video):
    classes,transition,no_order,initial=model;chosen,vchosen=params
    assert np.array_equal(keys,np.arange(len(keys)))
    assert np.allclose(transition.sum(1),1) and np.allclose(no_order.sum(1),1)
    assert np.allclose(np.diag(transition),np.diag(no_order))
    assert classes[0]==0 and initial.sum()>0
    # Perturb current/future observations: predictive priors through this index
    # remain unchanged, while the current score may respond to current evidence.
    x=get_features(validation_video)[:97];sim=x@centers.T
    prior,_=filter_history(sim,classes,transition,initial,chosen['temperature'],chosen['strength'])
    changed=sim.copy();changed[50:]=np.flip(changed[50:],axis=1)
    alternate,_=filter_history(changed,classes,transition,initial,chosen['temperature'],chosen['strength'])
    assert np.allclose(prior[:51],alternate[:51])
    full,_,_=score_video(x,bank,bact,centers,keys,*model,*params)
    prefix,_,_=score_video(x[:51],bank,bact,centers,keys,*model,*params)
    assert all(np.allclose(prefix[m],full[m][:51],atol=2e-6) for m in prefix)
    return {'causal_prior_current_and_future_perturbation':'passed','score_prefix_invariance':'passed','transition_rows_and_persistence_ablation':'passed','test_labels_in_scorer_interface':False}


def bootstrap(cache):
    rows=list(cache.values());rng=np.random.default_rng(CFG['seed'])
    comparisons=[('history_hard_nn','predicted_action_nn'),('history_soft_nn','global_nn'),('history_soft_nn','visual_soft_nn'),('history_soft_nn','no_order_soft_nn')]
    values={a+' minus '+b:[] for a,b in comparisons}
    for _ in range(CFG['bootstrap_video_replicates']):
        ids=rng.integers(0,len(rows),len(rows));mask=np.concatenate([rows[i]['act']>=0 for i in ids]);y=np.concatenate([rows[i]['typ']>0 for i in ids])[mask]
        if len(np.unique(y))<2:continue
        needed={m for pair in comparisons for m in pair}
        ap={m:average_precision_score(y,np.concatenate([rows[i]['scores'][m] for i in ids])[mask]) for m in needed}
        for a,b in comparisons:values[a+' minus '+b].append(ap[a]-ap[b])
    return {k:{'delta_ap_95pct_video_CI':np.percentile(v,[2.5,97.5]).tolist(),'replicates':len(v),'subset':'oracle_supported'} for k,v in values.items()}


def main():
    OUT.mkdir(exist_ok=True);tic=time.perf_counter()
    splits=json.loads((BASE/'outputs/split_manifest.json').read_text())['used']
    assert all(not set(splits[a])&set(splits[b]) for a,b in [('training','validation'),('training','test'),('validation','test')])
    b=np.load(BASE/'outputs/normal_bank.npz',allow_pickle=False)
    bank,bact,centers,keys=[b[k] for k in ('features','actions','centers','center_actions')]
    assert np.array_equal(keys,np.arange(len(keys)))
    model=fit_transitions(splits['training'],keys);classes,transition,no_order,initial=model
    params=select_parameters(splits['validation'],centers,classes,transition,initial);chosen,vchosen=params
    print('Normal-validation parameter choice:',chosen,flush=True)
    check=checks(centers,bank,bact,keys,model,params,splits['validation'][0])
    caches={};thresholds=None
    for split in ('validation','test'):
        cache={}
        for v in splits[split]:
            x=get_features(v)
            scores,distance,trace=score_video(x,bank,bact,centers,keys,*model,*params)
            # Labels enter only after all non-oracle predictions have been made.
            act,typ,lines=ev.read_labels(v)
            scores=ev.attach_oracle(distance,act,keys,scores)
            assert len(act)==len(x) and all(np.isfinite(a).all() for a in scores.values())
            # Baselines must reproduce the previous diagnostic exactly.
            old=np.load(BASE/'outputs/predictions'/f'{v}.npz',allow_pickle=False)
            assert all(np.allclose(scores[m],old[m],atol=2e-6) for m in ('global_nn','predicted_action_nn','oracle_action_nn'))
            cache[v]={'act':act,'typ':typ,'lines':lines,'scores':scores,'trace':trace}
            pred_dir=OUT/'predictions';pred_dir.mkdir(exist_ok=True)
            np.savez_compressed(pred_dir/f'{v}.npz',action_gt=act,type_gt=typ,**scores,**trace)
        caches[split]=cache
        if split=='validation':
            thresholds={m:float(np.quantile(np.concatenate([c['scores'][m] for c in cache.values()]),CFG['normal_validation_quantile'],method='higher')) for m in METHODS}
            ev.write_json(OUT/'thresholds.json',thresholds)
            print('Thresholds fixed before test scoring.',flush=True)
    print('Scoring completed; computing paired video intervals.',flush=True)
    result=ev.evaluate(caches['test'],thresholds)
    result['paired_video_bootstrap']=bootstrap(caches['test'])
    recognition={};calibration={}
    for split,cache in caches.items():
        act=np.concatenate([c['act'] for c in cache.values()]);typ=np.concatenate([c['typ'] for c in cache.values()]);recognition[split]={}
        for name,mask in {'known_all':act>=0,'known_normal':(act>=0)&(typ==0),'known_errors':(act>=0)&(typ>0)}.items():
            recognition[split][name]={}
            for m,key in [('visual','visual_probability'),('history','history_prior'),('no_order','no_order_prior')]:
                prob=np.concatenate([c['trace'][key] for c in cache.values()])[mask];a=act[mask]
                recognition[split][name][m]={'frames':len(a),'accuracy':float((prob.argmax(1)==a).mean()) if len(a) else None,'top3_accuracy':float((np.argsort(prob,axis=1)[:,-3:]==a[:,None]).any(1).mean()) if len(a) else None,'action_nll':action_nll(prob,a) if len(a) else None}
        calibration[split]={}
        for m in METHODS:
            negatives=0;fp=0;onsets=0
            for c in cache.values():
                neg=c['typ']==0;above=c['scores'][m]>thresholds[m]
                negatives+=int(neg.sum());fp+=int((above&neg).sum());onsets+=sum(neg[a] for a,b in ev.runs(above))
            calibration[split][m]={'normal_frame_exceedance':fp/negatives,'normal_alarm_onsets_per_minute':onsets/(negatives/CFG['fps']/60)}
    result['action_prediction']=recognition;result['normal_calibration']=calibration
    result['runtime_seconds']=time.perf_counter()-tic
    ev.write_json(OUT/'summary.json',result)
    ev.write_json(OUT/'checks.json',{**check,'previous_three_baselines_reproduced':'passed','split_disjoint':'passed','parameter_and_threshold_selection':'normal validation only','fit_videos':splits['training']})
    ev.write_json(OUT/'run_manifest.json',{'config':CFG,'used_splits':splits,'bank_source':'../tea_action_diagnostic_20260911/outputs/normal_bank.npz','evaluation_source':'local snapshot of previous run.py metric functions','no_order_hyperparameters':'same chosen history parameters; no separate retuning'})
    print(json.dumps({'main_AP':{m:d['ap'] for m,d in result['frame_metrics']['oracle_supported'].items()},'bootstrap':result['paired_video_bootstrap'],'action_prediction':recognition['test']},indent=2),flush=True)


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
