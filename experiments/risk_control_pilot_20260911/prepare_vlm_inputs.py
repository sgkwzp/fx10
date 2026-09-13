"""Prepare full EgoPER clips at three duration quantiles and task-specific prompts.

This is a throughput payload, not an exact ZeProM reproduction: the appendix's
task-specific object list and output schema need upstream-code reconciliation.
"""
from pathlib import Path
import json
import zipfile
import shutil
import numpy as np

EXP=Path(__file__).resolve().parent;ROOT=EXP.parents[1];DATA=ROOT/'data/Tea'
OUT=EXP/'vlm_inputs'


def main():
    OUT.mkdir(exist_ok=True)
    workload=json.loads((EXP/'sources/workload_metadata.json').read_text())
    picks=workload['profile_candidates']
    records=[]
    for item in picks:
        task=item['task'];v=item['video'];folder=ROOT/'data'/task
        with zipfile.ZipFile(folder/f'{task.lower()}_videos.zip') as archive:
            dest=OUT/f'{v}.mp4'
            if not dest.exists():
                with archive.open(f'trim_videos/{v}.mp4') as src,dest.open('wb') as dst:shutil.copyfileobj(src,dst)
            records.append({'task':task,'video':v,'duration_from_features_seconds':item['duration'],'path':dest.name,'prompt_file':task.lower()+'_profile_prompt.txt','approx_frames_at_4fps':int(np.ceil(item['duration']*4))})
        ann=json.loads((ROOT/'data/annotation.json').read_text())[task.lower()]['action2idx']
        graph=(ROOT/'data/task_graph.txt').read_text().split(task+':\n',1)[1].split('\n\n',1)[0]
        prompt=f'''You are analyzing a complete cooking procedure video and detecting mistakes.
Task: {task}. The following is a task graph, not a forced total execution order.
'''+ '\n'.join(f'[{i}] {a}' for a,i in ann.items())+'\n'+graph+'''
Segment the entire video into contiguous non-overlapping actions. Match each
segment to a named step, background, or unexpected. Compare the observed object,
tool, location, and execution details with the instruction. Mark wrong execution
or an unexpected action as has_error=true. Missing steps/prerequisites belong in
missing_steps, not automatically in each later action's error label. Do not invent
visible evidence. Task objects are those named in the instructions above.
Give explanations only for errors.
Return a JSON object with segments, missing_steps, and overall_verdict.
Each segment must contain start_time_sec, end_time_sec, matched_step, has_error
(boolean), error_type, and error_explanation. Cover the whole video; do not return
numeric self-reported confidence. Probabilities will be obtained from repeated
samples separately.
'''
        (OUT/(task.lower()+'_profile_prompt.txt')).write_text(prompt,encoding='utf-8')
    (OUT/'manifest.json').write_text(json.dumps({'purpose':'throughput trial; adapted prompt, not exact published-method scoring','clips':records},indent=2),encoding='utf-8')
    print(json.dumps(records,indent=2))


if __name__=='__main__':main()
