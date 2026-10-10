from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib.request,concurrent.futures,json
r=Path(__file__).resolve().parents[1]/'data/young_candidates'
sources=['https://grapetopia.hatenablog.com/entry/2020/06/10/210438','https://tomtom1ono.hatenablog.com/entry/2026/06/25/205921','https://tomtom1ono.hatenablog.com/entry/2026/06/19/225730','https://grapetopia.hatenablog.com/entry/2020/06/06/222016']
rows=[]
for k,u in enumerate(sources,10):
 try:
  html=urllib.request.urlopen(u,timeout=20).read();s=BeautifulSoup(html,'html.parser');(r/f'source_{k}.html').write_bytes(html)
  for j,im in enumerate(s.select('img.hatena-fotolife')):
   url=im.get('src');rows.append(dict(file=f's{k}_{j:02}.jpg',source=u,url=url,license='unspecified; source links only in public archive',stage='candidate needs inspection'))
 except Exception as e:print(str(e))
def get(row):
 try:urllib.request.urlretrieve(row['url'],r/row['file']);return row
 except Exception as e:print(str(e));return None
with concurrent.futures.ThreadPoolExecutor(6) as ex:good=[x for x in ex.map(get,rows) if x]
(r/'more_manifest.json').write_text(json.dumps(good,ensure_ascii=False,indent=2));print('downloaded',len(good))
