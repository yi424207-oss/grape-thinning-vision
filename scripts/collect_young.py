from pathlib import Path
import urllib.request,json,concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urljoin
r=Path(__file__).resolve().parents[1]/'data/young_candidates';r.mkdir(parents=True,exist_ok=True)
urls=['https://tomtom1ono.hatenablog.com/entry/2025/06/24/222657','https://grapetopia.hatenablog.com/entry/2020/06/10/210438','https://kaju-fruits.com/%E3%82%B7%E3%83%A3%E3%82%A4%E3%83%B3%E3%83%9E%E3%82%B9%E3%82%AB%E3%83%83%E3%83%88%E3%80%80%E7%B2%97%E6%91%98%E6%88%BF%E3%83%BB%E7%B2%97%E6%91%98%E7%B2%92/']
rows=[]
for si,url in enumerate(urls):
 try:
  html=urllib.request.urlopen(url,timeout=30).read();soup=BeautifulSoup(html,'html.parser');(r/f'source_{si}.html').write_bytes(html)
  scope=soup.select_one('.entry-content') or soup.select_one('article') or soup
  links=set()
  for im in scope.find_all('img'):
   s=im.get('data-src') or im.get('src')
   if s and not s.startswith('data:'):links.add(urljoin(url,s))
  for j,u in enumerate(sorted(links)):
   try:
    data=urllib.request.urlopen(u,timeout=20).read();p=r/f's{si}_{j:02}.jpg';p.write_bytes(data);rows.append(dict(file=p.name,source=url,url=u,license='unspecified: do not redistribute',use='candidate only; stage and labels unverified'))
   except Exception as e:print('image',str(e),flush=True)
  print(si,len(links),flush=True)
 except Exception as e:print('source',str(e),flush=True)
(r/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
