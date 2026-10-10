"""Exact hashes and low-resolution perceptual checks across source splits."""
from pathlib import Path
import json
from collections import defaultdict
import numpy as np
from PIL import Image
from scipy.fft import dctn
R=Path(__file__).resolve().parents[1]
def phash(p):
 a=np.asarray(Image.open(p).convert('L').resize((32,32)),float);v=dctn(a,norm='ortho')[:8,:8].ravel()[1:];return v>np.median(v)
reports={}
for task,filename,folder in [('berry','data_manifest.json','gbisc_original/images'),('flower','flower_manifest.json','flower_yolo')]:
 rows=json.loads((R/'reports'/filename).read_text());hashes=defaultdict(set)
 for row in rows:hashes[row['sha256']].add(row['split'])
 exact=[h for h,s in hashes.items() if len(s)>1];items=[]
 for row in rows:
  p=R/'data'/folder/row['file'] if task=='berry' else R/'data'/folder/'images'/row['split']/row['file']
  items.append((row,phash(p)))
 near=[]
 for i,(a,ha) in enumerate(items):
  for b,hb in items[i+1:]:
   if a['split']!=b['split']:
    d=int(np.count_nonzero(ha!=hb))
    if d<=8:near.append(dict(first=a['file'],second=b['file'],distance=d))
 reports[task]=dict(images=len(rows),cross_split_exact_hashes=exact,phash_distance_le8_candidates=near,limitation='No match is not proof of independent scenes; sequential capture groups are a heuristic.')
(R/'reports/duplicate_audit.json').write_text(json.dumps(reports,indent=2));print(reports)
