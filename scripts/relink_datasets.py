"""Refresh absolute dataset paths after extracting the delivered datasets."""
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    for name in ['berry_yolo','flower_yolo','young_yolo']:
        p=ROOT/'data'/name/'dataset.yaml'
        if not p.exists():continue
        d=yaml.safe_load(p.read_text());d['path']=str(p.parent)
        p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
        print(name, d['path'])
