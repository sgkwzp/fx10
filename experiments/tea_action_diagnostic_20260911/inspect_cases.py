"""Audit annotation versions and extract a small, deterministic visual case set."""
import sys
import json
import shutil
import zipfile
from pathlib import Path
from collections import Counter
import numpy as np
EXP=Path(__file__).resolve().parent
sys.path.insert(0,str(EXP/'vendor'))
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=EXP.parents[1]; DATA=ROOT/'data/Tea'; OUT=EXP/'outputs'
FPS=10


def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def annotation_audit():
    ann=json.loads((ROOT/'data/annotation.json').read_text())['tea']
    idx2type={v:k for k,v in ann['actiontype2idx'].items()}
    confusion=Counter(); differences=[]; original_only=[]
    for v in ann['segments']:
        video=v['video_id'];path=DATA/'refined_label_v3'/f'{video}.txt'
        if not path.exists():original_only.append(video);continue
        lines=path.read_text().splitlines();a=v['labels']
        for (start,end),typ,description in zip(a['time_stamp'],a['action_type'],a['error_description']):
            # Interior samples only; comparison is not affected by interval endpoint conventions.
            lo=int(np.ceil(start*FPS))+1;hi=min(len(lines),int(np.floor(end*FPS)))
            counts=Counter(s.split('|')[1] for s in lines[lo:hi])
            old=idx2type[typ]
            for new,count in counts.items():confusion[(old,new)]+=count
            mismatch=sum(n for k,n in counts.items() if k!=old)
            if mismatch:differences.append({'video':video,'start_seconds':start,'end_seconds':end,'original_type':old,'original_description':description,'refined_interior_types':dict(counts),'mismatched_frames':mismatch})
    total=sum(confusion.values());binary=sum(n for (a,b),n in confusion.items() if (a=='Normal')!=(b=='Normal'))
    result={'comparison':'interior time samples; boundary samples excluded','compared_samples':total,'type_disagreement_frames':sum(n for (a,b),n in confusion.items() if a!=b),'binary_disagreement_frames':binary,'confusion':[{'original':a,'refined':b,'frames':n} for (a,b),n in sorted(confusion.items())],'affected_videos':sorted(set(r['video'] for r in differences)),'changed_segments':differences,'original_without_refined_file':original_only}
    write(OUT/'annotation_version_audit.json',result)
    return result


def select_cases():
    ev=json.loads((OUT/'events.json').read_text()); alarms=json.loads((OUT/'alarms.json').read_text())
    threshold=json.loads((OUT/'thresholds.json').read_text())
    emap={(e['method'],e['video'],e['start']):e for e in ev}
    cases=[]
    mods=[e for e in ev if e['method']=='global_nn' and e['type']=='Error_Modification' and not e['onset_detected']]
    mods.sort(key=lambda e:(e['video'],e['start']))
    for e in mods:
        oracle=emap[('oracle_action_nn',e['video'],e['start'])]
        if oracle['onset_detected']:
            cases.append({'kind':'modification_missed_global_detected_oracle',**e});break
    slips=[e for e in ev if e['method']=='global_nn' and e['type']=='Error_Slip' and not e['onset_detected']]
    if slips:cases.append({'kind':'slip_missed',**sorted(slips,key=lambda e:(e['video'],e['start']))[0]})
    additions=[e for e in ev if e['method']=='global_nn' and e['type']=='Error_Addition' and e['onset_detected']]
    if additions:cases.append({'kind':'addition_detected',**sorted(additions,key=lambda e:(e['video'],e['start']))[0]})
    # Require the whole candidate alarm interval to be Normal, not just its onset.
    fa=[]
    for e in alarms:
        if e['method']!='global_nn' or not e['onset_is_normal']:continue
        p=np.load(OUT/'predictions'/f"{e['video']}.npz",allow_pickle=False)
        if np.all(p['type_gt'][e['start']:e['end']]==0):fa.append(e)
    for e in sorted(fa,key=lambda x:(-(x['end']-x['start']),x['video']))[:2]:
        lines=(DATA/'refined_label_v3'/f"{e['video']}.txt").read_text().splitlines()
        mid=(e['start']+e['end'])//2;parts=lines[mid].split('|')
        cases.append({'kind':'normal_false_alarm','type':'Normal','action':parts[0],'description':parts[0],**e})
    return cases,threshold


def main():
    audit=annotation_audit();cases,threshold=select_cases()
    frames_dir=EXP/'case_studies';frames_dir.mkdir(exist_ok=True)
    video_dir=frames_dir/'video_copies';video_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(DATA/'tea_videos.zip') as archive:
        for idx,c in enumerate(cases):
            video=c['video'];local=video_dir/f'{video}.mp4'
            if not local.exists():
                # Explicit member, no extractall or computed archive output paths.
                with archive.open(f'trim_videos/{video}.mp4') as src, local.open('wb') as dst:shutil.copyfileobj(src,dst)
            capture=cv2.VideoCapture(str(local));assert capture.isOpened()
            video_fps=capture.get(cv2.CAP_PROP_FPS);video_frames=capture.get(cv2.CAP_PROP_FRAME_COUNT)
            prediction=np.load(OUT/'predictions'/f'{video}.npz',allow_pickle=False)
            c['video_duration_seconds']=video_frames/video_fps
            c['feature_duration_seconds']=len(prediction['type_gt'])/FPS
            c['duration_difference_seconds']=c['video_duration_seconds']-c['feature_duration_seconds']
            times=np.linspace(c['start']/FPS,(c['end']-1)/FPS,4)
            fig=plt.figure(figsize=(14,6.2));grid=fig.add_gridspec(2,4,height_ratios=[1,1.1])
            for col,t in enumerate(times):
                capture.set(cv2.CAP_PROP_POS_MSEC,float(t*1000));ok,bgr=capture.read();assert ok,(video,t)
                ax=fig.add_subplot(grid[0,col]);ax.imshow(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB));ax.set_title(f't={t:.1f}s');ax.axis('off')
            capture.release()
            ax=fig.add_subplot(grid[1,:]);lo=max(0,c['start']-60);hi=min(len(prediction['type_gt']),c['end']+60);time=np.arange(lo,hi)/FPS
            for m,color in [('global_nn','#2a6fbb'),('predicted_action_nn','#d97925'),('oracle_action_nn','#7a4cab')]:
                ax.plot(time,prediction[m][lo:hi],label=m,color=color,lw=1.1)
                ax.axhline(threshold[m]['threshold'],color=color,linestyle=':',alpha=.6)
            ax.axvspan(c['start']/FPS,c['end']/FPS,color='#d95151' if c['type']!='Normal' else '#9b9b9b',alpha=.14)
            ax.set_xlabel('Feature/video time (seconds)');ax.set_ylabel('Cosine distance (trailing mean)');ax.legend(fontsize=8,loc='upper right')
            fig.suptitle(f"{c['kind']} | {video}\n{c['type']}: {c['description']}",fontsize=11)
            fig.tight_layout();filename=f'case_{idx+1:02d}.png';fig.savefig(frames_dir/filename,dpi=145);plt.close(fig)
            c['image']=filename;c['sampled_times_seconds']=times.tolist()
            region=slice(c['start'],c['end'])
            c['predicted_action_counts']=dict(Counter(map(str,prediction['action_pred'][region])))
    write(frames_dir/'cases.json',cases)
    print(json.dumps({'annotation_type_disagreements':audit['type_disagreement_frames'],'annotation_binary_disagreements':audit['binary_disagreement_frames'],'affected_videos':len(audit['affected_videos']),'cases':[{'image':c['image'],'video':c['video'],'kind':c['kind'],'duration_difference_seconds':c['duration_difference_seconds']} for c in cases]},indent=2))


if __name__=='__main__':main()
