"""Belief-update interventions with frozen models and explicit oracle isolation."""
import json
from pathlib import Path
import platform
import time
import numpy as np
from scipy.special import softmax, logsumexp
from sklearn.metrics import average_precision_score
from threadpoolctl import threadpool_limits
import evaluation as ev

EXP=Path(__file__).resolve().parent; OUT=EXP/'outputs'
HISTORY=EXP.parent/'tea_history_diagnostic_20260911'
ACTION=EXP.parent/'tea_action_diagnostic_20260911'
CFG=ev.CFG;METHODS=CFG['methods']
FILTER_METHODS=['history_soft_nn','observable_freeze','oracle_freeze','oracle_weak','oracle_exclude_correction','shifted_mask_freeze']


def features(video):
    return ev.normalize(np.load(ev.DATA/CFG['feature_family']/f'{video}.npy',allow_pickle=False).astype(np.float32))


def distance_score(distance,prior):
    tau=CFG['distance_softmin_temperature']
    raw=-tau*logsumexp(np.log(np.maximum(prior,1e-15))-distance/tau,axis=1)
    return ev.smooth(raw)


def filter_updates(likelihood,classes,transition,initial,strength,multipliers=None):
    """Score-time prior precedes the current observation update and multiplier."""
    n=len(likelihood);K=likelihood.shape[1]
    multipliers=np.ones(n) if multipliers is None else np.asarray(multipliers)
    prior=np.empty((n,K));post=np.empty((n,K));hidden=np.empty((n,len(classes)))
    state=initial.copy()
    for t in range(n):
        predicted=initial if t==0 else state@transition
        prior[t]=np.bincount(classes,weights=predicted,minlength=K)
        emission=np.maximum(likelihood[t,classes],1e-15)**(strength*multipliers[t])
        state=predicted*emission;state/=state.sum()
        hidden[t]=state;post[t]=np.bincount(classes,weights=state,minlength=K)
    return prior,post,hidden


def observable_predictions(x,bank,bact,centers,keys,classes,transition,initial,temperature,strength,gate_threshold):
    """Actual candidate interface has features/models only; no action/error labels."""
    distance,_,baseline=ev.predict(x,bank,bact,centers,keys)
    likelihood=softmax((x@centers.T)/temperature,axis=1)
    prior,post,hidden=filter_updates(likelihood,classes,transition,initial,strength)
    gate=baseline['global_nn']>gate_threshold
    op,oq,oh=filter_updates(likelihood,classes,transition,initial,strength,(~gate).astype(float))
    scores={'global_nn':baseline['global_nn'],'history_soft_nn':distance_score(distance,prior),'observable_freeze':distance_score(distance,op)}
    traces={'history_soft_nn':(prior,post,hidden),'observable_freeze':(op,oq,oh)}
    return scores,traces,distance,likelihood,gate


def oracle_branches(typ,likelihood,distance,classes,transition,initial,strength):
    errors=typ>0
    multipliers={
        'oracle_freeze':np.where(errors,0.,1.),
        'oracle_weak':np.where(errors,CFG['weak_update_multiplier'],1.),
        'oracle_exclude_correction':np.where(errors&(typ!=ev.TYPE_IDS['Error_Correction']),0.,1.),
        'shifted_mask_freeze':np.where(np.roll(errors,len(errors)//2),0.,1.)
    }
    assert int((multipliers['oracle_freeze']==0).sum())==int((multipliers['shifted_mask_freeze']==0).sum())
    scores={};traces={}
    for m,w in multipliers.items():
        result=filter_updates(likelihood,classes,transition,initial,strength,w)
        traces[m]=result;scores[m]=distance_score(distance,result[0])
    return scores,traces,multipliers


def local_rollout(likelihood,start,end,hidden,classes,transition,initial,strength,multiplier,target):
    """Start from the identical unmodified state, not an oracle-corrected state."""
    state=hidden[start-1].copy() if start else initial.copy()
    probabilities=[]
    for t in range(start,end):
        predicted=initial if t==0 else state@transition
        probabilities.append(float(predicted[classes==target].sum()))
        state=predicted*np.maximum(likelihood[t,classes],1e-15)**(strength*multiplier)
        state/=state.sum()
    return np.asarray(probabilities)


def local_events(video,lines,likelihood,traces,classes,transition,initial,strength):
    result=[];series={};baseprior,basepost,hidden=traces['history_soft_nn']
    for event in ev.gt_events(lines):
        target=ev.ACTIONS.get(event['action'],-1)
        if event['type']=='Error_Addition' or target<0:continue
        start,end=event['start'],event['end'];reference=baseprior[start:end,target]
        # Control rollout must reproduce the baseline for the whole same event.
        control=local_rollout(likelihood,start,end,hidden,classes,transition,initial,strength,1.,target)
        assert np.allclose(control,reference,atol=1e-12)
        frozen=local_rollout(likelihood,start,end,hidden,classes,transition,initial,strength,0.,target)
        weak=local_rollout(likelihood,start,end,hidden,classes,transition,initial,strength,CFG['weak_update_multiplier'],target)
        assert np.isclose(frozen[0],control[0]) and np.isclose(weak[0],control[0])
        n=len(control);quarter=max(1,int(np.ceil(n/4)))
        row={'video':video,**event,'target_action':target,'frames':n,'start_target_prior':float(control[0]),'baseline_mean_probability':float(control.mean()),'baseline_early_quarter_probability':float(control[:quarter].mean()),'baseline_late_quarter_probability':float(control[-quarter:].mean()),'baseline_late_minus_early':float(control[-quarter:].mean()-control[:quarter].mean()),'freeze_delta_mean_probability':float((frozen-control).mean()),'freeze_delta_late_probability':float((frozen[-quarter:]-control[-quarter:]).mean()),'weak_delta_mean_probability':float((weak-control).mean()),'weak_delta_late_probability':float((weak[-quarter:]-control[-quarter:]).mean())}
        result.append(row);series[str(start)]={'baseline':control,'freeze':frozen,'weak':weak}
    return result,series


def direct_updates(video,act,typ,traces):
    prior,post,_=traces['history_soft_nn'];records=[]
    for name,k in ev.TYPE_IDS.items():
        mask=(act>=0)&(typ==k);ids=np.flatnonzero(mask)
        if not len(ids):continue
        p=prior[ids,act[ids]];q=post[ids,act[ids]]
        records.append({'video':video,'type':name,'frames':len(ids),'mean_current_observation_delta_probability':float((q-p).mean()),'mean_current_observation_delta_log_probability':float((np.log(q+1e-12)-np.log(p+1e-12)).mean()),'fraction_observation_decreases_nominal_probability':float((q<p).mean())})
    return records


def checks(model,likelihood,gate):
    classes,T,initial,temp,strength=model
    length=min(len(likelihood),73);z=likelihood[:length];w=np.ones(length)
    p,q,h=filter_updates(z,classes,T,initial,strength,w)
    cut=min(31,length-1);w[cut:]=0
    p2,q2,h2=filter_updates(z,classes,T,initial,strength,w)
    assert np.allclose(p[:cut+1],p2[:cut+1])
    assert np.allclose(p2[cut:],q2[cut:])
    assert np.allclose(h2[cut+1],h2[cut]@T)
    pp,_,_=filter_updates(z[:cut+1],classes,T,initial,strength,(~gate[:cut+1]).astype(float))
    full,_,_=filter_updates(z,classes,T,initial,strength,(~gate[:length]).astype(float))
    assert np.allclose(pp,full[:cut+1])
    assert np.allclose(h.sum(1),1) and np.allclose(p.sum(1),1)


def bootstrap(cache,local):
    videos=list(cache);rng=np.random.default_rng(CFG['seed'])
    comparisons=[('oracle_freeze','history_soft_nn'),('oracle_weak','history_soft_nn'),('oracle_exclude_correction','history_soft_nn'),('observable_freeze','history_soft_nn'),('oracle_freeze','shifted_mask_freeze')]
    ap_deltas={a+' minus '+b:[] for a,b in comparisons}
    groups={'all_supported':None,'Error_Modification':'Error_Modification','Error_Slip':'Error_Slip','Error_Correction':'Error_Correction'}
    loc_ci={k:[] for k in groups}
    # Video-average of event-average delta: long videos/events do not dominate.
    local_by_group={g:{v:np.mean([r['freeze_delta_late_probability'] for r in local if r['video']==v and (typ is None or r['type']==typ)]) for v in videos if any(r['video']==v and (typ is None or r['type']==typ) for r in local)} for g,typ in groups.items()}
    for _ in range(CFG['bootstrap_video_replicates']):
        chosen=[videos[i] for i in rng.integers(0,len(videos),len(videos))]
        mask=np.concatenate([cache[v]['act']>=0 for v in chosen]);y=np.concatenate([cache[v]['typ']>0 for v in chosen])[mask]
        if len(np.unique(y))==2:
            need={m for pair in comparisons for m in pair}
            aps={m:average_precision_score(y,np.concatenate([cache[v]['scores'][m] for v in chosen])[mask]) for m in need}
            for a,b in comparisons:ap_deltas[a+' minus '+b].append(aps[a]-aps[b])
        for g,by_video in local_by_group.items():
            vals=[by_video[v] for v in chosen if v in by_video]
            if vals:loc_ci[g].append(float(np.mean(vals)))
    return {'detection':{k:{'delta_AP_95pct_CI':np.percentile(v,[2.5,97.5]).tolist(),'replicates':len(v),'subset':'oracle_supported'} for k,v in ap_deltas.items()},'local_freeze_delta_late_probability':{g:{'video_macro_delta':float(np.mean(list(local_by_group[g].values()))),'95pct_CI':np.percentile(vals,[2.5,97.5]).tolist(),'videos':len(local_by_group[g]),'replicates':len(vals)} for g,vals in loc_ci.items()}}


def main():
    OUT.mkdir(exist_ok=True);tic=time.perf_counter()
    split=json.loads((ACTION/'outputs/split_manifest.json').read_text())['used']
    selection=json.loads((HISTORY/'outputs/normal_validation_selection.json').read_text())['history']
    model=json.loads((HISTORY/'outputs/transition_model.json').read_text())
    classes=np.array(model['state_output_action']);T=np.array(model['transition']);initial=np.array(model['initial'])
    temp=selection['temperature'];strength=selection['strength']
    b=np.load(ACTION/'outputs/normal_bank.npz',allow_pickle=False);bank,bact,centers,keys=[b[k] for k in ('features','actions','centers','center_actions')]
    gate_threshold=json.loads((ACTION/'outputs/thresholds.json').read_text())['global_nn']['threshold']
    caches={};event_rows=[];updates=[];gate_stats=[];baseline_thresholds=json.loads((HISTORY/'outputs/thresholds.json').read_text())
    for sp in ('validation','test'):
        cache={}
        for video in split[sp]:
            x=features(video)
            scores,traces,distance,likelihood,gate=observable_predictions(x,bank,bact,centers,keys,classes,T,initial,temp,strength,gate_threshold)
            # Actual candidate is complete; all labels below are diagnostic-only.
            act,typ,lines=ev.read_labels(video)
            oscores,otraces,multipliers=oracle_branches(typ,likelihood,distance,classes,T,initial,strength)
            scores.update(oscores);traces.update(otraces)
            scores=ev.attach_oracle(distance,act,keys,scores)
            old=np.load(HISTORY/'outputs/predictions'/f'{video}.npz',allow_pickle=False)
            assert all(np.allclose(scores[m],old[m],atol=2e-6) for m in ('global_nn','history_soft_nn','oracle_action_nn'))
            assert np.allclose(traces['history_soft_nn'][0],old['history_prior'],atol=2e-6)
            assert len(act)==len(x) and all(np.isfinite(s).all() for s in scores.values())
            if sp=='validation':
                assert not (typ>0).any()
                assert all(np.allclose(scores[m],scores['history_soft_nn']) for m in multipliers)
            cache[video]={'act':act,'typ':typ,'lines':lines,'scores':scores,'traces':traces}
            pred=OUT/'predictions';pred.mkdir(exist_ok=True)
            arrays={m+'_prior':v[0] for m,v in traces.items()}
            np.savez_compressed(pred/f'{video}.npz',action_gt=act,type_gt=typ,observable_gate=gate,**scores,**arrays)
            if sp=='test':
                local,series=local_events(video,lines,likelihood,traces,classes,T,initial,strength)
                event_rows.extend(local);updates.extend(direct_updates(video,act,typ,traces))
                localdir=OUT/'event_local_traces';localdir.mkdir(exist_ok=True)
                np.savez_compressed(localdir/f'{video}.npz',**{start+'_'+m:a for start,curves in series.items() for m,a in curves.items()})
                for name,k in ev.TYPE_IDS.items():
                    mask=typ==k
                    if mask.any():gate_stats.append({'video':video,'type':name,'frames':int(mask.sum()),'observable_suppressed_frames':int(gate[mask].sum()),'shifted_mask_suppressed_frames':int((multipliers['shifted_mask_freeze'][mask]==0).sum())})
            if video==split['validation'][0]:
                checks((classes,T,initial,temp,strength),likelihood,gate)
                # Full actual score prefix and current/future feature perturbation.
                prefix=observable_predictions(x[:73],bank,bact,centers,keys,classes,T,initial,temp,strength,gate_threshold)[0]
                assert all(np.allclose(prefix[m],scores[m][:73],atol=2e-6) for m in prefix)
        caches[sp]=cache
        if sp=='validation':
            thresholds={m:float(np.quantile(np.concatenate([c['scores'][m] for c in cache.values()]),CFG['normal_validation_quantile'],method='higher')) for m in METHODS}
            assert all(np.isclose(thresholds[m],baseline_thresholds['history_soft_nn']) for m in ('oracle_freeze','oracle_weak','oracle_exclude_correction','shifted_mask_freeze'))
            ev.write_json(OUT/'thresholds.json',thresholds)
            ev.write_json(OUT/'frozen_inputs.json',{'gate_global_distance_threshold':gate_threshold,'history_temperature':temp,'history_strength':strength,'used_splits':split,'protocol':CFG,'bank_source':'../tea_action_diagnostic_20260911/outputs/normal_bank.npz','transition_source':'../tea_history_diagnostic_20260911/outputs/transition_model.json','new_fitting_or_selection':False})
            print('Validation thresholds fixed. Oracle masks leave normal validation identical.',flush=True)
    ev.write_json(OUT/'event_local_metrics.json',event_rows);ev.write_json(OUT/'direct_observation_updates.json',updates);ev.write_json(OUT/'gate_coverage.json',gate_stats)
    result=ev.evaluate(caches['test'],thresholds)
    print('Whole-video and event-local rollouts complete; calculating video-level intervals.',flush=True)
    result['bootstrap']=bootstrap(caches['test'],event_rows)
    recognition={}
    for m in FILTER_METHODS:
        recognition[m]={}
        for name,k in ev.TYPE_IDS.items():
            rows=[];probs=[]
            for c in caches['test'].values():
                mask=(c['act']>=0)&(c['typ']==k);a=c['act'][mask];p=c['traces'][m][0][mask]
                if len(a):rows.extend((p.argmax(1)==a).tolist());probs.extend(p[np.arange(len(a)),a].tolist())
            if rows:recognition[m][name]={'frames':len(rows),'action_accuracy':float(np.mean(rows)),'mean_nominal_prior':float(np.mean(probs))}
    result['action_prediction']=recognition;result['runtime_seconds']=time.perf_counter()-tic
    ev.write_json(OUT/'summary.json',result)
    ev.write_json(OUT/'checks.json',{'previous_baseline_scores_and_priors':'passed','normal_validation_oracle_invariance':'passed','observation_freeze_leaves_transition_active':'passed','current_mask_cannot_change_current_scoring_prior':'passed','observable_score_prefix_invariance':'passed','event_local_baseline_rollout_equivalence':'passed','event_local_equal_initial_belief':'passed','shifted_mask_same_suppression_count':'passed','all_new_outputs':'current experiment directory'})
    print(json.dumps({'AP':{m:d['ap'] for m,d in result['frame_metrics']['oracle_supported'].items()},'bootstrap':result['bootstrap']},indent=2),flush=True)


if __name__=='__main__':
    with threadpool_limits(limits=2):main()
