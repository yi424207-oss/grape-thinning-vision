"""Original-only flower split; preserve adjacent-capture groups of ten."""
from pathlib import Path
from PIL import Image
import random,shutil,json,hashlib
from collections import Counter
R=Path(__file__).resolve().parents[1];src=R/'data/flower_original';out=R/'data/flower_yolo'
# Repeated source files are byte-identical; deduplicate before counting.
files=list({p.name:p for p in sorted(src.rglob('IMG_*.jpg'))}.values());groups=sorted(set(int(p.stem.split('_')[1])//10 for p in files));random.Random(20261010).shuffle(groups)
mapping={g:('train' if i<int(.7*len(groups)) else 'val' if i<int(.85*len(groups)) else 'test') for i,g in enumerate(groups)}
manifest=[];counts=Counter()
for p in files:
 g=int(p.stem.split('_')[1])//10;s=mapping[g]
 for kind in ['images','labels']:(out/kind/s).mkdir(parents=True,exist_ok=True)
 im=Image.open(p).convert('RGB');im.thumbnail((768,768));im.save(out/'images'/s/p.name,quality=93)
 shutil.copy(p.with_suffix('.txt'),out/'labels'/s/p.with_suffix('.txt').name)
 manifest.append(dict(file=p.name,split=s,group=g,sha256=hashlib.sha256(p.read_bytes()).hexdigest()));counts[s]+=1
(out/'dataset.yaml').write_text(f'path: {out}\ntrain: images/train\nval: images/val\ntest: images/test\nnames:\n  0: inflorescence\n  1: spikelet\n')
(R/'reports/flower_manifest.json').write_text(json.dumps(manifest,indent=2));print(dict(counts))
