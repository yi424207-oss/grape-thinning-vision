"""Recreate best-weight validation plots; separate from fixed-threshold test scoring."""
from pathlib import Path
import json
import torch
from ultralytics import YOLO
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    torch.set_num_threads(8);report={}
    for task,data in [('berry_aux','berry_yolo'),('flower','flower_yolo'),('young','young_yolo')]:
        result=YOLO(ROOT/'runs'/task/'weights/best.pt').val(data=str(ROOT/'data'/data/'dataset.yaml'),split='val',imgsz=384,batch=16,conf=.001,iou=.5,max_det=1000,device='cpu',workers=0,plots=True,project=str(ROOT/'runs'),name=task+'_visual_val',exist_ok=True,verbose=False)
        report[task]={'metrics':result.results_dict,'confusion_matrix':result.confusion_matrix.matrix.tolist(),'split':'validation','weights':f'runs/{task}/weights/best.pt','input_size':384,'prediction_conf':.001,'nms_iou':.5,'plotting_matrix_threshold':.001,'matrix_matching_iou':.45}
    (ROOT/'reports/visual_validation.json').write_text(json.dumps(report,indent=2))
