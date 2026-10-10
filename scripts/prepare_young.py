"""Small source-held-out exploratory adaptation; training labels are pseudo-labels."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
import torch
from ultralytics import YOLO
R=Path(__file__).resolve().parents[1];src=R/'data/young_candidates';out=R/'data/young_yolo'
torch.set_num_threads(8)
for s in ['train','val','test']:
 for t in ['images','labels']:(out/t/s).mkdir(parents=True,exist_ok=True)
selected=[f's0_{i:02}.jpg' for i in range(1,8)]+[f's11_{i:02}.jpg' for i in list(range(7,12))+list(range(13,27))]+[f's12_{i:02}.jpg' for i in list(range(10))+[11]]
model=YOLO(str(R/'runs/berry_aux/weights/best.pt'));manifest=[]
for name in selected:
 im=Image.open(src/name).convert('RGB');im.thumbnail((768,768))
 pred=model.predict(im,imgsz=640,conf=.25,iou=.5,max_det=1000,device='cpu',verbose=False)[0]
 boxes=pred.boxes.xywhn.tolist();im.save(out/'images/train'/name,quality=93)
 (out/'labels/train'/Path(name).with_suffix('.txt')).write_text('\n'.join('0 '+' '.join(f'{v:.8f}' for v in b) for b in boxes))
 manifest.append(dict(file=name,split='train',site='tomtom1ono.hatenablog.com',label_method='auxiliary-model pseudo labels, NOT ground truth',boxes=len(boxes),sha256=hashlib.sha256((src/name).read_bytes()).hexdigest()))
ann=json.loads((R/'annotations/young_review.json').read_text())
for name,a in ann['images'].items():
 im=Image.open(src/name).convert('RGB').resize(tuple(a['size']));x0,y0,x1,y1=a['roi'];im=im.crop(tuple(a['roi']));w,h=im.size;lines=[]
 for x,y,rx,ry in a['ellipses']:
  if rx<3 or ry<3:continue
  left=max(x0,x-rx);top=max(y0,y-ry);right=min(x1,x+rx);bottom=min(y1,y+ry)
  lines.append('0 '+' '.join(f'{v:.8f}' for v in [((left+right)/2-x0)/w,((top+bottom)/2-y0)/h,(right-left)/w,(bottom-top)/h]))
 s=a['split'];im.save(out/'images'/s/name,quality=95);(out/'labels'/s/Path(name).with_suffix('.txt')).write_text('\n'.join(lines))
 manifest.append(dict(file=name,split=s,site='kaju-fruits.com' if s=='val' else 'grapetopia.hatenablog.com',label_method=ann['method'],boxes=len(lines),roi=a['roi'],coordinate_size=a['size'],sha256=hashlib.sha256((src/name).read_bytes()).hexdigest()))
(out/'dataset.yaml').write_text(f'path: {out}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  0: berry\n')
(R/'reports/young_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));print('train',len(selected),'pseudo boxes',sum(m['boxes'] for m in manifest if m['split']=='train'));print('evaluation',[(m['file'],m['boxes']) for m in manifest if m['split']!='train'])
