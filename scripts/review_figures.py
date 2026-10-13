"""Review charts use saved detections, standardized matching and actual exports."""
from pathlib import Path
import json, csv, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
R=Path(__file__).resolve().parents[1];O=R/'docs/figures'
fontManager.addfont('/usr/share/fonts/opentype/grape_course/NotoSansCJKsc-Regular.otf')
plt.rcParams.update({'font.family':'Noto Sans CJK SC','axes.unicode_minus':False,'font.size':11})
from PIL import Image
from matplotlib.patches import Rectangle
samples=[]
for cultivar in ['Kyoho','ShineMuscat','SummerBlack']:
 samples.extend(sorted((R/'data/berry_yolo/images/train').glob(cultivar+'*.jpg'))[:2])
fig,axs=plt.subplots(2,3,figsize=(10,6.2))
for ax,path in zip(axs.flat,samples):
 im=Image.open(path);ax.imshow(im);w,h=im.size
 for line in (R/'data/berry_yolo/labels/train'/path.with_suffix('.txt').name).read_text().splitlines():
  cls,x,y,bw,bh=map(float,line.split());ax.add_patch(Rectangle(((x-bw/2)*w,(y-bh/2)*h),bw*w,bh*h,fill=False,ec='#00e5ff',lw=.7))
 ax.set_title(path.name,fontsize=9);ax.axis('off')
fig.tight_layout();fig.savefig(O/'berry_samples.png',dpi=200);plt.close(fig)
d=json.loads((R/'reports/review_statistics.json').read_text())
for task in ['berry_aux','flower','young']:
    classes=d['models'][task]['classes'];fig,axs=plt.subplots(1,len(classes),figsize=(8,3.5),squeeze=False)
    for ax,(name,stats) in zip(axs.flat,classes.items()):
        x=np.arange(3);v=stats['validation'];t=stats['test']
        a=ax.bar(x-.18,[v[k] for k in ['tp','fp','fn']],.36,label='验证集')
        b=ax.bar(x+.18,[t[k] for k in ['tp','fp','fn']],.36,label='测试集')
        ax.bar_label(a,padding=2,fontsize=9);ax.bar_label(b,padding=2,fontsize=9)
        ax.set_xticks(x,['TP 正确匹配','FP 未匹配预测','FN 未检出标签'],fontsize=9)
        ax.set_title(f'{name}  confidence={t["threshold"]:.2f}');ax.set_ylabel('目标框数');ax.legend();ax.margins(y=.18)
    fig.tight_layout();fig.savefig(O/f'{task}_cm_evidence.png',dpi=220);plt.close(fig)
fig,axs=plt.subplots(1,4,figsize=(12,3.5))
for ax,(task,name,title) in zip(axs,[('berry_aux','berry','辅助果粒'),('flower','inflorescence','整花序'),('flower','spikelet','小穗'),('young','berry','幼果试验')]):
    q=d['models'][task]['classes'][name]['test'];bars=ax.bar(['TP','FP','FN'],[q[k] for k in ['tp','fp','fn']],color=['#227c9d','#d9822b','#993f5c'])
    ax.bar_label(bars,padding=3);ax.set_title(title+f'\nconf={q["threshold"]:.2f}, F1={q["f1"]:.4f}');ax.set_ylabel('目标框数');ax.margins(y=.18)
fig.tight_layout();fig.savefig(O/'test_confusion.png',dpi=220);plt.close(fig)
v=json.loads((R/'outputs/public_v03/result.json').read_text())
rows=v['decisions'];keep=[r for r in rows if r['action']=='keep'][:2];remove=[r for r in rows if r['action']=='remove'][:2]
shown=keep+remove
fig,ax=plt.subplots(figsize=(10,3));ax.axis('off')
headers=['id','confidence','relative_scale','action','reason']
table=ax.table(cellText=[[f'{r[k]:.4f}' if isinstance(r[k],float) else r[k] for k in headers] for r in shown],colLabels=headers,loc='center',cellLoc='center',colWidths=[.06,.15,.2,.13,.29])
table.auto_set_font_size(False);table.set_fontsize(10);table.scale(1,1.9)
ax.set_title('实际导出样例  同时展示 keep 和 remove')
fig.tight_layout();fig.savefig(O/'csv_export_preview.png',dpi=220);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,3.8));ax.axis('off')
lines=['实际执行命令  ASCII 双连字符参数', '',
'python src/predict.py examples/berry_demo_input.jpg '+chr(92),
'  --weights runs/berry_aux/weights/best.pt '+chr(92),
'  --output outputs/public_v03 '+chr(92),
'  --confidence 0.30 --ratio 0.70','',
f'visible_count={v["visible_count"]}  remove_count={v["remove_count"]}  keep_count={v["keep_count"]}',
'exports: annotated.jpg / berries.csv / result.json',
'schema_version=2.0  relative_scale=sqrt(box area)/median(scale)']
ax.text(.02,.95,'\n'.join(lines),va='top',fontsize=11,linespacing=1.5)
fig.tight_layout();fig.savefig(O/'cli_run_record.png',dpi=240);plt.close(fig)
sys.path.insert(0,str(R/'src'));from thinning import decide
raw=json.loads((R/'outputs/berry_demo/result.json').read_text());boxes=np.array([r['box'] for r in raw['decisions']]);scores=np.array([r['confidence'] for r in raw['decisions']])
scale=np.sqrt(np.prod(boxes[:,2:]-boxes[:,:2],axis=1));order=np.argsort(scale);baseline=decide(boxes,scores)
responses=[]
for fraction in [0,.1,.2,.3]:
    retained=order[int(len(order)*fraction):];q=decide(boxes[retained],scores[retained]);flags=[x['action'] for x in q['decisions']]
    original_flags=[baseline['decisions'][i]['action'] for i in retained]
    responses.append({'simulated_smallest_fraction_lost':fraction,'remaining':len(retained),'median_scale':float(np.median(scale[retained])),
                     'remove_count':q['remove_count'],'remaining_action_flips':sum(a!=b for a,b in zip(flags,original_flags))})
(R/'reports/scale_missingness_sensitivity.json').write_text(json.dumps({'source':'saved licensed demonstration detections; simulated selective missingness, not new detector performance','rows':responses},indent=2)+'\n')
fig,axs=plt.subplots(1,2,figsize=(9,3.3));x=[r['simulated_smallest_fraction_lost']*100 for r in responses]
axs[0].plot(x,[r['median_scale'] for r in responses],'o-');axs[0].set(xlabel='模拟删除最小检测框比例 %',ylabel='剩余框尺度中位数 px')
axs[1].bar(x,[r['remaining_action_flips'] for r in responses],width=5);axs[1].set(xlabel='模拟删除最小检测框比例 %',ylabel='剩余对象动作改变数')
fig.tight_layout();fig.savefig(O/'scale_missingness_sensitivity.png',dpi=220);plt.close(fig)
index=json.loads((R/'reports/figure_evidence_index.json').read_text())
for entry in index:
    n=entry['figure']
    if n=='berry_samples.png': entry.update(source=[p.relative_to(R).as_posix() for p in samples])
    if n.endswith('_cm_evidence.png') or n=='test_confusion.png': entry.update(source='reports/review_statistics.json',protocol='match IoU 0.50; validation-selected confidence reused for test; TP/FP/FN only')
    if n in ['csv_export_preview.png','cli_run_record.png']: entry.update(source='outputs/public_v03/result.json',schema_version='2.0')
index=[x for x in index if x['figure'] not in ['scale_missingness_sensitivity.png','seed_repeat_results.png']]
index.append({'figure':'scale_missingness_sensitivity.png','source':'reports/scale_missingness_sensitivity.json'})
(R/'reports/figure_evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')

seed_report=json.loads((R/'reports/seed_repeats.json').read_text())
if len(seed_report['runs'])==9:
    entries=[('berry_aux','berry','辅助果粒'),('flower','inflorescence','整花序'),('flower','spikelet','小穗'),('young','berry','幼果试验')]
    fig,axs=plt.subplots(2,4,figsize=(11,5.3))
    for col,(task,label,title) in enumerate(entries):
        q=seed_report['summary'][task][label]
        for row,metric,ylabel in [(0,'f1','F1'),(1,'count_mae','计数 MAE')]:
            ax=axs[row,col];values=q[metric]['values'];ax.plot(range(3),values,'o-',color='#227c9d');ax.set_xticks(range(3),['10','12','13']);ax.set_xlabel('种子日期后缀 202610');ax.set_ylabel(ylabel);ax.grid(alpha=.2)
            if row==0:ax.set_title(title);ax.set_ylim(0,1)
            else:ax.set_ylim(bottom=0)
            for i,v in enumerate(values):ax.annotate(f'{v:.3f}',(i,v),xytext=(0,6),textcoords='offset points',ha='center',fontsize=8)
    fig.tight_layout();fig.savefig(O/'seed_repeat_results.png',dpi=220);plt.close(fig)
    index.append({'figure':'seed_repeat_results.png','source':'reports/seed_repeats.json','scope':'fixed-split seed variability; not independent field replication'})
    (R/'reports/figure_evidence_index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
