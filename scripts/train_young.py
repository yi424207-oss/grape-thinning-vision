"""Weakly supervised pilot; external evaluation is AI-annotated, not expert validated."""
import os
os.environ['YOLO_AUTOINSTALL']='false'
from pathlib import Path
import torch
from ultralytics import YOLO
R=Path(__file__).resolve().parents[1];torch.set_num_threads(8)
if __name__=='__main__':
 YOLO(str(R/'runs/berry_aux/weights/best.pt')).train(data=str(R/'data/young_yolo/dataset.yaml'),epochs=25,imgsz=384,batch=8,device='cpu',workers=0,seed=20261010,deterministic=True,project=str(R/'runs'),name='young',exist_ok=True,freeze=10,optimizer='AdamW',lr0=.0003,patience=25,close_mosaic=5,cache=False,plots=True,amp=False)
