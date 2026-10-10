"""CPU-reproducible YOLOv8n auxiliary berry training. No implicit downloads."""
import os
os.environ['YOLO_AUTOINSTALL']='false'
os.environ['OMP_NUM_THREADS']='8'
from pathlib import Path
import torch
from ultralytics import YOLO
ROOT=Path(__file__).resolve().parents[1]
torch.set_num_threads(8)
if __name__=='__main__':
 model=YOLO(str(ROOT/'models/yolov8n.pt'))
 model.train(data=str(ROOT/'data/berry_yolo/dataset.yaml'),epochs=25,imgsz=384,batch=16,device='cpu',workers=4,seed=20261010,deterministic=True,project=str(ROOT/'runs'),name='berry_aux',exist_ok=True,pretrained=True,freeze=10,optimizer='AdamW',lr0=.001,patience=8,close_mosaic=5,cache=False,plots=True,save=True,verbose=False,amp=False)
