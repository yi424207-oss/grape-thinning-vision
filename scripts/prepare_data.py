"""Convert CC-BY GBISC annotations; split source groups before making tiles."""
from pathlib import Path
from collections import defaultdict, Counter
import json, hashlib, random
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'data/gbisc_original'; out=ROOT/'data/berry_yolo'
images={}; annotations=defaultdict(list)
for split in ['train','val','test']:
    d=json.loads((src/f'annotations_COCO_{split}.json').read_text())
    ids={i['id']:i['file_name'] for i in d['images']}
    for i in d['images']: images[i['file_name']]=i
    for a in d['annotations']: annotations[ids[a['image_id']]].append(a['bbox'])
# Neighboring capture numbers are kept together, rather than randomly splitting patches.
rng=random.Random(20261010); groups={}
for cultivar in ['Kyoho','ShineMuscat','SummerBlack']:
    order=list(range(10));rng.shuffle(order)
    for j,g in enumerate(order):groups[(cultivar,g)]='train' if j<6 else ('val' if j<8 else 'test')
manifest=[];counts=Counter()
for name,meta in sorted(images.items()):
    cultivar,num=name.rsplit('_',1);group=(int(num.split('.')[0])-1)//5;split=groups[(cultivar,group)]
    path=src/'images'/name; im=Image.open(path).convert('RGB');w,h=im.size
    boxes=np.array(annotations[name],dtype=float).reshape(-1,4)
    # Four non-overlapping source tiles: test independence remains at original-image level.
    for iy in range(2):
      for ix in range(2):
        x0=ix*w//2;y0=iy*h//2;x1=(ix+1)*w//2;y1=(iy+1)*h//2;tw=x1-x0;th=y1-y0
        labels=[]
        for x,y,bw,bh in boxes:
            xx=max(x,x0);yy=max(y,y0);xe=min(x+bw,x1);ye=min(y+bh,y1)
            if xe<=xx or ye<=yy:continue
            # Exclude heavily cut objects, but record this policy in evaluation.
            if (xe-xx)*(ye-yy)/(bw*bh)<.65:continue
            labels.append(f'0 {((xx+xe)/2-x0)/tw:.8f} {((yy+ye)/2-y0)/th:.8f} {(xe-xx)/tw:.8f} {(ye-yy)/th:.8f}')
        stem=f'{Path(name).stem}_{iy}{ix}'
        for kind in ['images','labels']:(out/kind/split).mkdir(parents=True,exist_ok=True)
        tile=im.crop((x0,y0,x1,y1));tile.thumbnail((768,768));tile.save(out/'images'/split/f'{stem}.jpg',quality=92)
        (out/'labels'/split/f'{stem}.txt').write_text('\n'.join(labels))
        counts[split+'_tiles']+=1;counts[split+'_boxes']+=len(labels)
    manifest.append(dict(file=name,split=split,group=f'{cultivar}-{group}',cultivar=cultivar,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),boxes=len(boxes),source='GBISC',stage='enlarging_or_mature; not verified thinning stage'))
    counts[split+'_originals']+=1
(out/'dataset.yaml').write_text(f'path: {out}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  0: berry\n')
(ROOT/'reports/data_manifest.json').write_text(json.dumps(manifest,indent=2))
(ROOT/'reports/data_counts.json').write_text(json.dumps(dict(counts),indent=2));print(dict(counts))
assert len({m['sha256'] for m in manifest})==len(manifest),'Exact duplicate originals'
