"""Re-run original best checkpoint AP; external data is not copied into public files."""
from pathlib import Path
import argparse,json,os
os.environ['YOLO_AUTOINSTALL']='false'
import torch,yaml
from ultralytics import YOLO
R=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--task',choices=['berry_aux','flower','young'],required=True);parser.add_argument('--external-dataset',type=Path);a=parser.parse_args()
 data=a.external_dataset or R/'data'/({'berry_aux':'berry_yolo','flower':'flower_yolo','young':'young_yolo'}[a.task])
 cfg=yaml.safe_load((data/'dataset.yaml').read_text());cfg['path']=str(data.resolve());(data/'dataset.yaml').write_text(yaml.safe_dump(cfg))
 torch.set_num_threads(8);model=YOLO(str(R/'runs'/a.task/'weights/best.pt'))
 q=model.val(data=str(data/'dataset.yaml'),split='test',imgsz=384,batch=16,conf=.001,iou=.5,max_det=1000,device='cpu',workers=0,plots=False,project='/tmp/grape-original-ap',name=a.task,exist_ok=True,verbose=False)
 p=R/'reports/review_test_AP.json';report=json.loads(p.read_text()) if p.exists() else {}
 report[a.task]={'results':q.results_dict,'class_AP':{model.names[int(c)]:{'AP50':float(q.box.ap50[i]),'AP50_95':float(q.box.ap[i])} for i,c in enumerate(q.box.ap_class_index)}}
 p.write_text(json.dumps(report,indent=2)+'\n');print(a.task,report[a.task])
