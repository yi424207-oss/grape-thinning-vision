"""Recover exact candidate image URLs for private coursework. No public redistribution."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,json,hashlib,argparse
from PIL import Image
R=Path(__file__).resolve().parents[1]
def download(row,out):
 p=out/row['file']
 try:
  if not p.exists():
   with urllib.request.urlopen(row['url'],timeout=30) as res:p.write_bytes(res.read())
  with Image.open(p) as im:im.verify()
  return dict(file=p.name,status='valid',sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 except Exception as e:return dict(file=p.name,status='failed',error=str(e))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',default=str(R/'data/young_candidates'));args=a.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
 rows=json.loads((R/'reports/young_source_candidates.json').read_text());unique={x['file']:x for x in rows}
 with ThreadPoolExecutor(4) as ex:results=list(ex.map(lambda x:download(x,out),unique.values()))
 (out/'recovery_validation.json').write_text(json.dumps(results,indent=2));print(sum(x['status']=='valid' for x in results),'valid /',len(results))
