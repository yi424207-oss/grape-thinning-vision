"""Three independent training seeds on fixed splits; no test-based model selection."""
import os
os.environ['YOLO_AUTOINSTALL']='false'
os.environ['OMP_NUM_THREADS']='8'
from pathlib import Path
import argparse, json, gc, statistics, time
import numpy as np
import torch, yaml
from ultralytics import YOLO
from evaluate import collect, score
R=Path(__file__).resolve().parents[1]

def execute(external_data=None):
    torch.set_num_threads(8)
    seeds=[20261010,20261012,20261013]
    report={'seeds':seeds,'epochs':25,'fixed_splits':True,'threads':8,'workers':0,
            'selection':'best checkpoint and operating confidence use validation only; all seeds reported',
            'scope':'Training-seed variability conditional on these fixed datasets and labels, not generalization to new orchards or expert label accuracy.',
            'runs':[],'summary':{}}
    for task in ['berry_aux','flower','young']:
        if task=='young' and external_data is None:continue
        data=external_data if task=='young' else R/'data'/('berry_yolo' if task=='berry_aux' else 'flower_yolo')
        config=yaml.safe_load((data/'dataset.yaml').read_text());config['path']=str(data.resolve());(data/'dataset.yaml').write_text(yaml.safe_dump(config))
        for seed in seeds:
            name=f'{task}_seed{seed}';out=R/'runs/repeats'/name
            model=YOLO(str(R/'runs/berry_aux/weights/best.pt' if task=='young' else R/'models/yolov8n.pt'))
            start=time.perf_counter()
            model.train(data=str(data/'dataset.yaml'),epochs=25,imgsz=384,batch=8 if task=='young' else 16,
                device='cpu',workers=0,seed=seed,deterministic=True,project=str(R/'runs/repeats'),name=name,
                exist_ok=True,pretrained=True,freeze=10,optimizer='AdamW',lr0=.0003 if task=='young' else .001,
                patience=25,close_mosaic=5,cache=False,plots=False,save=True,verbose=False,amp=False)
            best=YOLO(str(out/'weights/best.pt'))
            rows={split:collect(best,data,split) for split in ['val','test']}
            result={'task':task,'seed':seed,'train_seconds':time.perf_counter()-start,'classes':{}}
            for c,label in best.names.items():
                sweep=[score(rows['val'],t,c) for t in [.05,.1,.15,.2,.25,.3,.4,.5]]
                chosen=max(sweep,key=lambda x:x['f1']);test=score(rows['test'],chosen['threshold'],c)
                result['classes'][label]={k:v for k,v in test.items() if k!='per_image'}
            ap=best.val(data=str(data/'dataset.yaml'),split='test',imgsz=384,batch=16,conf=.001,iou=.5,
                max_det=1000,device='cpu',workers=0,plots=False,project='/tmp/grape-repeat-eval',name=name,exist_ok=True,verbose=False)
            result['test_AP']=ap.results_dict
            report['runs'].append(result)
            for model_name in ['berry_aux','flower','young']:
                subset=[x for x in report['runs'] if x['task']==model_name]
                if not subset:continue
                summary={}
                for label in subset[0]['classes']:
                    summary[label]={}
                    for metric in ['f1','count_mae']:
                        values=[x['classes'][label][metric] for x in subset]
                        summary[label][metric]={'mean':statistics.mean(values),'sample_std':statistics.stdev(values) if len(values)>1 else None,'n':len(values),'values':values}
                report['summary'][model_name]=summary
            (R/'reports/seed_repeats.json').write_text(json.dumps(report,indent=2)+'\n')
            # Do not publish any input image, mosaic, annotation or private source path.
            for f in out.rglob('*'):
                if f.is_file() and f.suffix.lower() in ['.jpg','.png','.cache']:f.unlink()
            config_file=out/'args.yaml';cfg=yaml.safe_load(config_file.read_text());cfg['data']='external_dataset.yaml' if task=='young' else f'data/{data.name}/dataset.yaml';cfg['model']='runs/berry_aux/weights/best.pt' if task=='young' else 'models/yolov8n.pt';cfg['project']='runs/repeats';cfg['save_dir']=f'runs/repeats/{name}';config_file.write_text(yaml.safe_dump(cfg))
            for f in (out/'weights').glob('*.pt'):
                ckpt=torch.load(f,map_location='cpu',weights_only=False)
                if isinstance(ckpt.get('train_args'),dict):
                    for key in ['data','model','project','save_dir']:ckpt['train_args'][key]=cfg[key]
                torch.save(ckpt,f)
            print('COMPLETED',name,flush=True)
            del model,best,ap,rows;gc.collect()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--external-dataset',type=Path);a=p.parse_args();execute(a.external_dataset)
