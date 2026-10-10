"""Offline image inference and auditable CSV/JSON export."""
import argparse,csv,json,time
from pathlib import Path
import cv2,numpy as np, torch
from ultralytics import YOLO
from thinning import decide

def run(image,weights,output,size_ratio=.7,target=None,conf=.3,roi=None,imgsz=384):
    if not 0<conf<1:raise ValueError('confidence must be in (0, 1)')
    torch.set_num_threads(8)
    raw=cv2.imdecode(np.fromfile(str(image),dtype=np.uint8),cv2.IMREAD_COLOR)
    if raw is None:raise ValueError('Cannot read image')
    h,w=raw.shape[:2];x0,y0,x1,y1=(0,0,w,h) if roi is None else roi
    if not (0<=x0<x1<=w and 0<=y0<y1<=h):raise ValueError('ROI outside image')
    crop=raw[y0:y1,x0:x1];t=time.perf_counter();model=YOLO(str(weights))
    # Overlapping tiles; final NMS removes duplicate detections.
    ch,cw=crop.shape[:2];boxes=[];scores=[]
    step=768;tile=1024
    starts=lambda n:sorted(set(list(range(0,max(1,n-tile+1),step))+[max(0,n-tile)]))
    for yy in starts(ch):
      for xx in starts(cw):
        patch=crop[yy:yy+tile,xx:xx+tile]
        r=model.predict(patch,imgsz=imgsz,conf=conf,iou=.5,max_det=1000,verbose=False,device='cpu')[0]
        if r.boxes is not None:
          b=r.boxes.xyxy.cpu().numpy();b+=np.array([xx+x0,yy+y0,xx+x0,yy+y0]);boxes.extend(b.tolist());scores.extend(r.boxes.conf.cpu().numpy().tolist())
    if boxes:
      b=np.array(boxes);xywh=np.column_stack((b[:,:2],b[:,2:]-b[:,:2])).tolist()
      inds=np.asarray(cv2.dnn.NMSBoxes(xywh,scores,conf,.45),dtype=int).reshape(-1)
      boxes=b[inds].tolist();scores=np.array(scores)[inds].tolist()
    result=decide(boxes,scores,size_ratio,target)
    result.update(image=Path(image).name,roi=[x0,y0,x1,y1],elapsed_seconds=time.perf_counter()-t,scope='visible berries only',model=Path(weights).name,confidence_threshold=conf,inference_imgsz=imgsz,tile_size=1024,tile_stride=768)
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    overlay=raw.copy()
    for row in result['decisions']:
      a,b,c,d=map(int,row['box']);color=(20,50,230) if row['action']=='remove' else (30,190,30)
      cv2.rectangle(overlay,(a,b),(c,d),color,2);cv2.putText(overlay,str(row['id']),(a,max(12,b)),cv2.FONT_HERSHEY_SIMPLEX,.45,color,1)
    cv2.imencode('.jpg',overlay)[1].tofile(str(output/'annotated.jpg'))
    (output/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    with (output/'berries.csv').open('w',newline='',encoding='utf-8-sig') as f:
      writer=csv.DictWriter(f,fieldnames=['id','box','confidence','relative_diameter','action','reason']);writer.writeheader();writer.writerows(result['decisions'])
    return result

if __name__=='__main__':
 p=argparse.ArgumentParser(description='Visible grape berry thinning support')
 p.add_argument('image');p.add_argument('--weights',required=True);p.add_argument('--output',default='outputs/demo');p.add_argument('--ratio',type=float,default=.7);p.add_argument('--visible-target',type=int);p.add_argument('--confidence',type=float,default=.3);p.add_argument('--roi',type=int,nargs=4)
 a=p.parse_args();r=run(a.image,a.weights,a.output,a.ratio,a.visible_target,a.confidence,a.roi);print(json.dumps({k:v for k,v in r.items() if k!='decisions'},ensure_ascii=False,indent=2))
