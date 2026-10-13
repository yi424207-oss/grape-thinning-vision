"""Validate all seed runs and remove machine paths before public archiving."""
from pathlib import Path
import json,statistics
import torch,yaml
R=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 p=R/'reports/seed_repeats.json';report=json.loads(p.read_text());assert len(report['runs'])==9
 for row in report['runs']:
  if 'train_seconds' in row:row['training_and_operating_point_evaluation_seconds']=row.pop('train_seconds')
  out=R/'runs/repeats'/f"{row['task']}_seed{row['seed']}";cfg=yaml.safe_load((out/'args.yaml').read_text())
  assert len((out/'results.csv').read_text().splitlines())==26
  for f in (out/'weights').glob('*.pt'):
   ckpt=torch.load(f,map_location='cpu',weights_only=False)
   mappings=[ckpt.get('train_args')]+[getattr(ckpt.get(k),'args',None) for k in ['model','ema']]
   for mapping in mappings:
    if isinstance(mapping,dict):
     for key in ['data','model','project','save_dir']:mapping[key]=cfg[key]
   torch.save(ckpt,f)
 report['test_AP_summary']={}
 for task in ['berry_aux','flower','young']:
  subset=[row for row in report['runs'] if row['task']==task];assert len(subset)==3
  report['test_AP_summary'][task]={}
  for key in ['metrics/mAP50(B)','metrics/mAP50-95(B)']:
   values=[row['test_AP'][key] for row in subset];report['test_AP_summary'][task][key]={'mean':statistics.mean(values),'sample_std':statistics.stdev(values),'n':3,'values':values}
 p.write_text(json.dumps(report,indent=2)+'\n');print('All nine 25-epoch runs verified; model paths sanitized')
