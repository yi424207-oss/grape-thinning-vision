"""Observed CPU throughput; warm timings exclude model load and disk decoding."""
import argparse, json, platform, time, statistics, resource, sys
from pathlib import Path
import cv2, numpy as np, torch, ultralytics
from ultralytics import YOLO
R=Path(__file__).resolve().parents[1]

def main(repeats=20):
    torch.set_num_threads(8)
    cpu=next((s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')), 'unknown')
    report={'cpu':cpu,'platform':platform.platform(),'python':platform.python_version(),
            'torch':torch.__version__,'ultralytics':ultralytics.__version__,'opencv':cv2.__version__,
            'threads':8,'imgsz':384,'rect':False,'warmup_calls':3,'repeats':repeats,'tasks':[]}
    for task in ['berry_aux','flower','young']:
        w=R/'runs'/task/'weights/best.pt';start=time.perf_counter();model=YOLO(str(w));load=time.perf_counter()-start
        image=R/'examples'/('flower_demo_input.jpg' if task=='flower' else 'berry_demo_input.jpg')
        raw=cv2.imdecode(np.fromfile(image,dtype=np.uint8),cv2.IMREAD_COLOR)
        for batch in [1,4]:
            images=[raw]*batch
            for _ in range(3):model.predict(images,imgsz=384,rect=False,conf=.3,iou=.5,max_det=1000,device='cpu',verbose=False)
            timings=[]
            for _ in range(repeats):
                start=time.perf_counter();model.predict(images,imgsz=384,rect=False,conf=.3,iou=.5,max_det=1000,device='cpu',verbose=False);timings.append(time.perf_counter()-start)
            mean=statistics.mean(timings)
            report['tasks'].append({'model':task,'weights_bytes':w.stat().st_size,'parameters':sum(p.numel() for p in model.model.parameters()),
                'batch':batch,'load_seconds':load,'mean_batch_seconds':mean,'std_batch_seconds':statistics.stdev(timings),
                'mean_per_image_seconds':mean/batch,'throughput_images_per_second':batch/mean,
                'process_peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
                'raw_batch_seconds':timings})
    report['scope']='Same decoded image repeated; includes preprocessing, forward and NMS. Excludes model load, decode, ROI tiling and exports. Peak RSS is cumulative for the process, not model-only memory. Throughput is not an end-to-end interactive FPS promise. Young model timed on licensed auxiliary image, not validated young-fruit accuracy.'
    (R/'reports/cpu_benchmark.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='tasks'},indent=2));print([(x['model'],x['batch'],x['mean_per_image_seconds']) for x in report['tasks']])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repeats',type=int,default=20);a=p.parse_args();main(a.repeats)
