from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.font_manager import FontProperties, fontManager
R=Path(__file__).resolve().parents[1];O=R/'docs/figures';O.mkdir(parents=True,exist_ok=True)
import os
font_path=os.environ.get('GRAPE_CJK_FONT') or fontManager.findfont(FontProperties(family='Noto Sans CJK SC'),fallback_to_default=False)
fontManager.addfont(font_path)
font=FontProperties(fname=font_path);plt.rcParams['font.family']=font.get_name();plt.rcParams['axes.unicode_minus']=False
fig,axs=plt.subplots(1,3,figsize=(11,3.3))
for ax,task,title in zip(axs,['berry_aux','flower','young'],['辅助果粒','花序与小穗','幼果弱标注适配']):
 rows=list(csv.DictReader((R/'runs'/task/'results.csv').open()));x=[float(d['epoch']) for d in rows]
 for key,label in [('metrics/mAP50(B)','验证 mAP50'),('metrics/mAP50-95(B)','验证 mAP50-95')]:ax.plot(x,[float(d[key]) for d in rows],label=label)
 ax.set(xlabel='训练轮次',ylabel='平均精度',title=title,ylim=(0,1));ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(O/'training_curves.png',dpi=220);plt.close(fig)
# CC-BY examples, source/image identifiers retained in caption.
fig,axs=plt.subplots(1,2,figsize=(9,4.5))
for ax,folder,title in zip(axs,['berry_demo','flower_demo'],['果粒与疏除建议','花序与小穗识别']):
 im=Image.open(R/'outputs'/folder/'annotated.jpg');
 if folder=='berry_demo':im=im.crop((1050,400,2380,2350))
 ax.imshow(im);ax.set_title(title);ax.axis('off')
fig.tight_layout();fig.savefig(O/'public_examples.png',dpi=200);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,4));ax.axis('off')
positions=[(.22,.83,'图像与单穗 ROI'),(.75,.83,'花序或果粒模型'),(.75,.53,'坐标合并与 NMS'),(.22,.53,'相对大小阈值'),(.22,.23,'可见保留上限'),(.75,.23,'编号图与 CSV JSON')]
for x,y,t in positions:ax.text(x,y,t,ha='center',va='center',bbox=dict(boxstyle='round,pad=.7',facecolor='#f3f3f3',edgecolor='black'),fontsize=11)
for a,b in [(0,1),(1,2),(2,3),(3,4),(4,5)]:
 x,y,_=positions[a];u,v,_=positions[b]
 if y==v:xx=x+(.16 if u>x else -.16);uu=u-(.16 if u>x else -.16);yy=y;vv=v
 else:xx=x;uu=u;yy=y-.09;vv=v+.09
 ax.annotate('',xy=(uu,vv),xytext=(xx,yy),arrowprops=dict(arrowstyle='->',lw=1.5))
ax.text(.05,.02,'花序分支直接输出花序与小穗；大小阈值及上限仅用于果粒分支。',fontsize=10)
fig.savefig(O/'system_design.png',dpi=220,bbox_inches='tight');plt.close(fig)
# Publication-safe schematic derived from coordinates; no copyrighted photo reproduced.
rows=json.loads((R/'outputs/young_demo/result.json').read_text());fig,ax=plt.subplots(figsize=(4,5))
for d in rows['decisions']:
 x,y,u,v=d['box'];c='red' if d['action']=='remove' else 'green';ax.add_patch(plt.Rectangle((x,y),u-x,v-y,fill=False,edgecolor=c,lw=1));ax.text(x,y,str(d['id']),fontsize=6)
ax.set(xlim=(0,270),ylim=(527,0),aspect='equal',title='幼果检测坐标示意');ax.set_xlabel('像素 x');ax.set_ylabel('像素 y');fig.tight_layout();fig.savefig(O/'young_coordinates.png',dpi=220);plt.close(fig)
# Counts and thresholds, per-image values from actual output.
d=json.loads((R/'outputs/berry_demo/result.json').read_text());import sys;sys.path.insert(0,str(R/'src'));from thinning import decide
results=[decide([x['box'] for x in d['decisions']],[x['confidence'] for x in d['decisions']],t) for t in [.5,.6,.7,.8,.9]]
(R/'reports/threshold_sensitivity.json').write_text(json.dumps([{k:v for k,v in x.items() if k!='decisions'} for x in results],indent=2))
