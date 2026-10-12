"""Independent fixed-threshold detection/count evaluation. Threshold uses val only."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]
def ious(b,g):
 a=np.maximum(b[:2],g[:,:2]);z=np.minimum(b[2:],g[:,2:]);inter=np.prod(np.maximum(0,z-a),axis=1)
 return inter/np.maximum(1e-9,np.prod(b[2:]-b[:2])+np.prod(g[:,2:]-g[:,:2],axis=1)-inter)
def score(rows,threshold,cls=0):
 tp=fp=fn=0;errors=[];per=[]
 for row in rows:
  gt=np.array([b[1:] for b in row['gt'] if b[0]==cls]).reshape(-1,4)
  pred=sorted([b for b in row['pred'] if b[0]==cls and b[1]>=threshold],key=lambda b:-b[1]);used=set();hit=0
  for p in pred:
   ov=ious(np.array(p[2:]),gt) if len(gt) else np.array([])
   for j in used:ov[j]=-1
   if len(ov) and ov.max()>=.5:used.add(int(ov.argmax()));hit+=1
  tp+=hit;fp+=len(pred)-hit;fn+=len(gt)-hit;e=len(pred)-len(gt);errors.append(e)
  per.append(dict(file=row['file'],ground_truth=len(gt),predicted=len(pred),tp=hit,error=e))
 p=tp/max(1,tp+fp);r=tp/max(1,tp+fn)
 return dict(threshold=threshold,class_id=cls,precision=p,recall=r,f1=2*p*r/max(1e-9,p+r),tp=tp,fp=fp,fn=fn,images=len(rows),count_mae=float(np.mean(np.abs(errors))),count_rmse=float(np.sqrt(np.mean(np.square(errors)))),count_bias=float(np.mean(errors)),per_image=per)
def collect(model,data,split):
 files=sorted((data/'images'/split).glob('*.jpg'));rows=[]
 for k in range(0,len(files),16):
  results=model.predict([str(p) for p in files[k:k+16]],imgsz=384,batch=16,conf=.01,iou=.5,max_det=1000,device='cpu',rect=False,verbose=False)
  for p,res in zip(files[k:k+16],results):
   w,h=Image.open(p).size;gt=[]
   for line in (data/'labels'/split/(p.stem+'.txt')).read_text().splitlines():
    c,x,y,bw,bh=map(float,line.split());gt.append([int(c),(x-bw/2)*w,(y-bh/2)*h,(x+bw/2)*w,(y+bh/2)*h])
   rows.append(dict(file=p.name,gt=gt,pred=[[int(c),float(s),*b] for c,s,b in zip(res.boxes.cls.tolist(),res.boxes.conf.tolist(),res.boxes.xyxy.tolist())]))
 return rows
if __name__=='__main__':
 import torch
 from ultralytics import YOLO
 a=argparse.ArgumentParser();a.add_argument('--task',choices=['berry_aux','flower','young'],default='berry_aux');a.add_argument('--weights');a.add_argument('--report-name');args=a.parse_args();task=args.task;report_name=args.report_name or task
 torch.set_num_threads(8);data=R/'data'/({'berry_aux':'berry_yolo','flower':'flower_yolo','young':'young_yolo'}[task]);model=YOLO(args.weights or str(R/'runs'/task/'weights/best.pt'))
 rows={s:collect(model,data,s) for s in ['val','test']};(R/'reports'/f'{report_name}_predictions.json').write_text(json.dumps(rows))
 report={'task':task,'imgsz':384,'iou_match':.5,'nms_iou':.5,'max_det':1000,'threshold_selection':'maximum validation F1; never test','classes':{}}
 for c in range(len(model.names)):
  sweep=[score(rows['val'],t,c) for t in [.05,.1,.15,.2,.25,.3,.4,.5]];best=max(sweep,key=lambda x:x['f1']);report['classes'][model.names[c]]={'validation_sweep':[{k:v for k,v in x.items() if k!='per_image'} for x in sweep],'validation':best,'test':score(rows['test'],best['threshold'],c)}
 ap=model.val(data=str(data/'dataset.yaml'),split='test',imgsz=384,batch=16,conf=.001,iou=.5,max_det=1000,device='cpu',workers=0,plots=False,project=str(R/'runs'),name=task+'_test',exist_ok=True,verbose=False)
 report['test_AP']=ap.results_dict
 (R/'reports'/f'{report_name}_evaluation.json').write_text(json.dumps(report,indent=2));print(report['test_AP'])
