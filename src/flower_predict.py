"""Inflorescence / spikelet inference. Does not report berry counts."""
from pathlib import Path
import json,time
import cv2,numpy as np,torch
from ultralytics import YOLO

def run(image,weights,output,conf=.25):
 if not 0<conf<1:raise ValueError('confidence must be in (0, 1)')
 torch.set_num_threads(8);t=time.perf_counter();raw=cv2.imdecode(np.fromfile(str(image),np.uint8),1)
 if raw is None:raise ValueError('Cannot read image')
 result=YOLO(str(weights)).predict(raw,imgsz=384,conf=conf,device='cpu',rect=False,verbose=False,max_det=1000)[0]
 out=Path(output);out.mkdir(parents=True,exist_ok=True);cv2.imencode('.jpg',result.plot())[1].tofile(str(out/'annotated.jpg'))
 rows=[dict(class_id=int(c),label=result.names[int(c)],confidence=float(s),box=b) for c,s,b in zip(result.boxes.cls.tolist(),result.boxes.conf.tolist(),result.boxes.xyxy.tolist())]
 data=dict(image=Path(image).name,task='inflorescence_and_spikelet',counts={v:sum(x['label']==v for x in rows) for v in result.names.values()},detections=rows,elapsed_seconds=time.perf_counter()-t)
 (out/'result.json').write_text(json.dumps(data,ensure_ascii=False,indent=2));return data
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('--weights',required=True);p.add_argument('--output',default='outputs/flower');p.add_argument('--confidence',type=float,default=.25);a=p.parse_args();print(run(a.image,a.weights,a.output,a.confidence))
