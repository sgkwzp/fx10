"""Native-video throughput/MC sampler for an explicitly provided vLLM endpoint.

Not executed on the local 6GB GPU. Uses the official Qwen model-card video_url
and mm_processor_kwargs.fps interface. Saves raw outputs; does not invent or
repair model confidence. Run on the server host to measure GPU memory locally.
"""
import argparse
import base64
import json
import statistics
import subprocess
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

EXP=Path(__file__).resolve().parent


def memory_sample():
    try:
        r=subprocess.run(['nvidia-smi','--query-gpu=name,memory.used','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
        return r.stdout.strip() if r.returncode==0 else None
    except (OSError,subprocess.SubprocessError):return None


def validate_segments(content,duration):
    text=content.strip()
    if text.startswith('```'):
        text='\n'.join(text.splitlines()[1:-1])
    try:
        data=json.loads(text);segments=data.get('segments') if isinstance(data,dict) else data
        if not isinstance(segments,list) or not segments:return {'valid':False,'reason':'missing nonempty segments'}
        previous=0
        for seg in segments:
            start=seg['start_time_sec'];end=seg['end_time_sec']
            if not isinstance(seg['has_error'],bool) or abs(start-previous)>.15 or not start<end:return {'valid':False,'reason':'invalid type, order, interval, gap or overlap'}
            previous=end
        if abs(previous-duration)>.5:return {'valid':False,'reason':'does not cover full supplied duration'}
        return {'valid':True,'segments':segments}
    except (ValueError,TypeError,KeyError):return {'valid':False,'reason':'unparseable expected JSON schema'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url',required=True,help='Explicit accessible endpoint, for example http://127.0.0.1:8000/v1')
    parser.add_argument('--model',required=True,help='Exact server model name; record quantization separately')
    parser.add_argument('--video',required=True,type=Path)
    parser.add_argument('--duration-seconds',required=True,type=float)
    parser.add_argument('--prompt-file',required=True,type=Path)
    parser.add_argument('--fps',type=float,nargs='+',default=[4.0,1.0])
    parser.add_argument('--mc-samples',type=int,default=5,help='Additional stochastic samples after one temperature-0 reference')
    parser.add_argument('--max-tokens',type=int,default=8192)
    parser.add_argument('--timeout-seconds',type=int,default=600)
    parser.add_argument('--measure-local-gpu',action='store_true',help='Only meaningful when client runs on model-server host')
    parser.add_argument('--run-name',default='vlm_trial')
    args=parser.parse_args()
    if '/' in args.run_name or '\\' in args.run_name:parser.error('run-name must be a simple folder name')
    target=EXP/'vlm_benchmarks'/args.run_name
    target.mkdir(parents=True,exist_ok=False)
    prompt=args.prompt_file.read_text(encoding='utf-8')+f'\nThe supplied video duration is {args.duration_seconds:.3f} seconds.'
    video_uri='data:video/mp4;base64,'+base64.b64encode(args.video.read_bytes()).decode('ascii')
    results=[]
    for fps in args.fps:
        for sample in range(args.mc_samples+1):
            body={'model':args.model,'messages':[{'role':'user','content':[{'type':'video_url','video_url':{'url':video_uri}},{'type':'text','text':prompt}]}],'max_tokens':args.max_tokens,'temperature':0 if sample==0 else .7,'mm_processor_kwargs':{'fps':fps,'do_sample_frames':True}}
            memory=[];stop=threading.Event()
            def monitor():
                while not stop.is_set():
                    value=memory_sample()
                    if value:memory.append({'time':time.time(),'gpu':value})
                    stop.wait(.5)
            thread=threading.Thread(target=monitor,daemon=True) if args.measure_local_gpu else None
            if thread:thread.start()
            start=time.perf_counter();response=None;error=None
            try:
                request=urllib.request.Request(args.base_url.rstrip('/')+'/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
                with urllib.request.urlopen(request,timeout=args.timeout_seconds) as r:response=json.load(r)
            except urllib.error.HTTPError as e:error={'type':'HTTPError','status':e.code,'body':e.read().decode(errors='replace')[:4000]}
            except (OSError,ValueError) as e:error={'type':type(e).__name__,'message':str(e)}
            finally:
                elapsed=time.perf_counter()-start;stop.set()
                if thread:thread.join(timeout=6)
            validation={'valid':False,'reason':'request failed'}
            finish=None
            if response and response.get('choices'):
                choice=response['choices'][0];finish=choice.get('finish_reason');validation=validate_segments(choice['message'].get('content') or '',args.duration_seconds)
                if finish=='length':validation={'valid':False,'reason':'output truncated by token limit'}
            used=[]
            for snapshot in memory:
                for line in snapshot['gpu'].splitlines():
                    try:used.append(float(line.rsplit(',',1)[-1]))
                    except ValueError:pass
            entry={'fps_requested':fps,'sample':sample,'temperature':body['temperature'],'wall_seconds':elapsed,'video_seconds':args.duration_seconds,'usage':response.get('usage') if response else None,'finish_reason':finish,'validation':validation,'error':error,'gpu_samples_local_host_only':memory,'peak_sampled_device_memory_MiB_all_processes':max(used) if used else None}
            (target/f'fps{fps:g}_sample{sample}_raw.json').write_text(json.dumps(response if response else error,indent=2),encoding='utf-8')
            results.append(entry)
            (target/'measurements.json').write_text(json.dumps({'model':args.model,'max_tokens':args.max_tokens,'media_mode':'native video; exact sampled-frame counts need server-side logging','results':results},indent=2),encoding='utf-8')
            print(json.dumps({'fps':fps,'sample':sample,'seconds':elapsed,'valid':validation['valid'],'error':error}),flush=True)
            if error:
                # Avoid repeating failing or unsupported requests.
                return
    good=[r['wall_seconds'] for r in results if r['validation']['valid']]
    summary={'valid_requests':len(good),'total_requests':len(results),'median_valid_wall_seconds':statistics.median(good) if good else None,'actual_sampled_frame_counts':'not measured; fps is requested, not verified','method_status':'ZeProM-style native-video engineering profile; model/prompt/quantization must be matched before research comparisons'}
    (target/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')


if __name__=='__main__':main()
