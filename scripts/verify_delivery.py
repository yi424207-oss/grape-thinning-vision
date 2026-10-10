"""Real offline inference, ROI offset/count/export agreement and invalid input tests."""
from pathlib import Path
import sys,json,csv,tempfile
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'))
from predict import run
from flower_predict import run as flower_run
from thinning import decide

def main():
 checks=[]
 for task,name in [('berry_aux','berry_demo'),('flower','flower_demo'),('young','young_demo')]:
  p=R/'outputs'/name/'result.json';assert p.exists();d=json.loads(p.read_text());assert (p.parent/'annotated.jpg').stat().st_size>1000;checks.append(task+' real image export')
 with tempfile.TemporaryDirectory() as td:
  p=Path(td);blank=np.zeros((120,160,3),dtype=np.uint8);Image.fromarray(blank).save(p/'空白图片.jpg');d=run(p/'空白图片.jpg',R/'runs/berry_aux/weights/best.pt',p/'out',roi=[20,20,100,100]);assert d['visible_count']==0 and d['keep_count']==0
  assert len(list(csv.DictReader((p/'out/berries.csv').open(encoding='utf-8-sig'))))==0;checks.append('Unicode path and empty detections')
  try:run(p/'空白图片.jpg',R/'runs/berry_aux/weights/best.pt',p/'bad',roi=[-1,0,99,99]);raise AssertionError('ROI accepted')
  except ValueError:checks.append('invalid ROI rejected')
  try:run(p/'missing.jpg',R/'runs/berry_aux/weights/best.pt',p/'bad');raise AssertionError('missing accepted')
  except (ValueError,FileNotFoundError):checks.append('missing image rejected')
 d=json.loads((R/'outputs/berry_demo/result.json').read_text());assert d['visible_count']==d['keep_count']+d['remove_count'];assert len(list(csv.DictReader((R/'outputs/berry_demo/berries.csv').open(encoding='utf-8-sig'))))==d['visible_count']
 for row in d['decisions']:
  a,b,c,e=row['box'];x0,y0,x1,y1=d['roi'];assert x0<=a<c<=x1+1 and y0<=b<e<=y1+1
 checks.append('ROI original coordinates and JSON CSV count agreement')
 for ratio in [.5,.6,.7,.8,.9]:
  q=decide([x['box'] for x in d['decisions']],[x['confidence'] for x in d['decisions']],ratio)
  assert q['keep_count']+q['remove_count']==q['visible_count']
 checks.append('ratio sensitivity and count conservation')
 report=dict(status='passed',checks=checks,gui='Syntax/import reviewed; desktop event loop not executed: environment cannot open X server sockets',limitation='Engineering tests do not validate agronomic decisions or field performance.')
 (R/'reports/delivery_verification.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':main()
