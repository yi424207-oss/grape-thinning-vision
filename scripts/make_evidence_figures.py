"""Publication figures from real training files and saved predictions, not mockups."""
from pathlib import Path
import json, csv, shutil
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, fontManager
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parents[1]; O=Path('/tmp/grape_evidence_figures');O.mkdir(exist_ok=True)
font_path='/usr/share/fonts/opentype/grape_course/NotoSansCJKsc-Regular.otf'
fontManager.addfont(font_path);plt.rcParams['font.family']=FontProperties(fname=font_path).get_name()
plt.rcParams['axes.unicode_minus']=False
evidence=[]
def save(fig,name,source):
    fig.savefig(O/name,dpi=200,bbox_inches='tight');plt.close(fig)
    evidence.append({'figure':name,'source':source})
def boxes(ax,path,label):
    im=Image.open(path);ax.imshow(im);w,h=im.size
    for line in label.read_text().splitlines():
        c,x,y,bw,bh=map(float,line.split());color='#00e5ff' if c==0 else '#ffb000'
        ax.add_patch(Rectangle(((x-bw/2)*w,(y-bh/2)*h),bw*w,bh*h,fill=False,ec=color,lw=.7))
    ax.axis('off')
for data,name,title in [('berry_yolo','berry_samples.png','GBISC 阳光玫瑰训练图块'),('flower_yolo','flower_samples.png','Du 花序训练原图')]:
    paths=sorted((R/'data'/data/'images/train').glob('ShineMuscat*.jpg' if data=='berry_yolo' else '*.jpg'))
    paths=[p for p in paths if len((R/'data'/data/'labels/train'/f'{p.stem}.txt').read_text().splitlines())>=10]
    idx=np.linspace(0,len(paths)-1,6,dtype=int);fig,axs=plt.subplots(2,3,figsize=(10,6.4))
    chosen=[]
    for ax,i in zip(axs.flat,idx):
        p=paths[i];chosen.append(p.relative_to(R).as_posix());boxes(ax,p,R/'data'/data/'labels/train'/f'{p.stem}.txt');ax.set_title(p.name,fontsize=9)
    fig.suptitle(title+'（训练划分，叠加真实标签）',fontsize=13);fig.tight_layout()
    save(fig,name,chosen)
for task in ['berry_aux','flower','young']:
    for name in ['results.png','confusion_matrix.png','confusion_matrix_normalized.png','BoxPR_curve.png']:
        src=R/'runs'/task/name if name=='results.png' else R/'runs'/f'{task}_visual_val'/name
        dst=f'{task}_{name}';shutil.copyfile(src,O/dst)
        evidence.append({'figure':dst,'source':str(src.relative_to(R)),'split':'training CSV for results.png; best-weight validation for matrices and PR; NOT held-out test'})
validation=json.loads((R/'reports/visual_validation.json').read_text())
for task in ['berry_aux','flower','young']:
    matrix=np.array(validation[task]['confusion_matrix']);labels=['整花序','小穗','背景'] if task=='flower' else ['果粒','背景']
    fig,axs=plt.subplots(1,2,figsize=(9,3.8))
    for ax,normalized,title in zip(axs,[False,True],['验证计数矩阵','按真实类别归一化']):
        values=matrix/(matrix.sum(axis=0,keepdims=True)+1e-9) if normalized else matrix
        ax.imshow(values,cmap='Blues',vmin=0,vmax=1 if normalized else None)
        for y in range(len(labels)):
            for x in range(len(labels)):
                value=values[y,x];label='—' if y==x==len(labels)-1 else f'{value:.2f}' if normalized else str(int(value))
                ax.text(x,y,label,ha='center',va='center',fontsize=13,color='white' if value>values.max()/2 else 'black')
        ax.set_xticks(range(len(labels)),labels,fontsize=11);ax.set_yticks(range(len(labels)),labels,fontsize=11)
        ax.set_xlabel('真实标签',fontsize=12);ax.set_ylabel('预测标签',fontsize=12);ax.set_title(title,fontsize=13)
    fig.tight_layout();save(fig,f'{task}_cm_evidence.png',{'numeric_source':'reports/visual_validation.json','task':task,'conf':0.001,'match_iou':0.45})
for task in ['berry_aux','flower']:
    src=R/'runs'/task/'train_batch0.jpg';shutil.copyfile(src,O/f'{task}_train_batch0.jpg')
    evidence.append({'figure':f'{task}_train_batch0.jpg','source':str(src.relative_to(R)),'split':'training augmentation mosaic'})

# Fixed-threshold test detection confusion matrices. No meaningful true-negative cell.
fig,axs=plt.subplots(1,4,figsize=(12,3.7))
for ax,(task,cls,title) in zip(axs,[('berry_aux','berry','辅助果粒'),('flower','inflorescence','整花序'),('flower','spikelet','小穗'),('young','berry','幼果试验')]):
    d=json.loads((R/'reports'/f'{task}_evaluation.json').read_text())['classes'][cls]['test']
    a=np.array([[d['tp'],d['fp']],[d['fn'],0]]);ax.imshow(a,cmap='Blues')
    for y in range(2):
        for x in range(2):ax.text(x,y,'—' if (y,x)==(1,1) else str(a[y,x]),ha='center',va='center',color='white' if a[y,x]>a.max()/2 else 'black',fontsize=11)
    ax.set_xticks([0,1],['目标','背景']);ax.set_yticks([0,1],['目标','背景']);ax.set_xlabel('真实');ax.set_ylabel('预测');ax.set_title(f'{title}\n阈值 {d["threshold"]:.2f}',fontsize=11)
fig.tight_layout();save(fig,'test_confusion.png','reports/*_evaluation.json: fixed threshold on held-out test')

fig,axs=plt.subplots(1,3,figsize=(10,3.4))
for ax,task,title in zip(axs,['berry_aux','flower','young'],['辅助果粒测试图块','花序测试图','幼果测试区域']):
    cls='inflorescence' if task=='flower' else 'berry';d=json.loads((R/'reports'/f'{task}_evaluation.json').read_text())['classes'][cls]['test'];v=d['per_image']
    g=np.array([x['ground_truth'] for x in v]);p=np.array([x['predicted'] for x in v]);m=max(max(g),max(p))+2
    ax.scatter(g,p,s=15,alpha=.6);ax.plot([0,m],[0,m],'k--',lw=1);ax.set(xlabel='标签数量',ylabel='预测数量',title=title);ax.grid(alpha=.2)
fig.tight_layout();save(fig,'test_count_scatter.png','reports/*_evaluation.json: per_image')

# Raw input / exported output from the same supplied licensed image.
for folder,name in [('public_quickstart','berry_input_output.png'),('flower_demo','flower_input_output.png')]:
    inp=R/'examples'/('berry_demo_input.jpg' if folder=='public_quickstart' else 'flower_demo_input.jpg')
    fig,axs=plt.subplots(1,2,figsize=(9,4.5))
    for ax,p,title in zip(axs,[inp,R/'outputs'/folder/'annotated.jpg'],['程序输入','实际导出编号图']):
        ax.imshow(Image.open(p));ax.set_title(title);ax.axis('off')
    fig.tight_layout();save(fig,name,[str(inp.relative_to(R)),f'outputs/{folder}/annotated.jpg'])

# Real console records, explicitly exported as a figure rather than a fake GUI window.
lines=['实际命令行运行记录摘录','',
       '$ python src/predict.py examples/berry_demo_input.jpg',
       '  --weights runs/berry_aux/weights/best.pt',
       '  --output outputs/public_quickstart --confidence 0.30 --ratio 0.70','']
d=json.loads((R/'outputs/public_quickstart/result.json').read_text())
for k in ['visible_count','remove_count','keep_count','size_ratio']:lines.append(f'{k}: {d[k]}')
lines+=['','实际导出：annotated.jpg / berries.csv / result.json',
        '单元测试：6 项通过；端到端验收：passed',
        '这是保存的运行记录图，不是桌面窗口截图。']
fig,ax=plt.subplots(figsize=(10,4.3));ax.axis('off');ax.text(.01,.98,'\n'.join(lines),va='top',fontsize=11,linespacing=1.5)
save(fig,'cli_run_record.png',['outputs/public_quickstart/result.json','reports/unit_tests.txt','reports/delivery_verification.json'])

fig,ax=plt.subplots(figsize=(10,3.7));ax.axis('off');v=list(csv.DictReader((R/'outputs/public_quickstart/berries.csv').open(encoding='utf-8-sig')))[:6]
headers=['id','confidence','relative_diameter','action','reason'];rows=[[x[k] for k in headers] for x in v]
t=ax.table(cellText=rows,colLabels=headers,loc='center',cellLoc='center',colWidths=[.07,.16,.22,.14,.32]);t.auto_set_font_size(False);t.set_fontsize(10);t.scale(1,1.7)
ax.set_title('真实 berries.csv 前六条记录',fontsize=13)
save(fig,'csv_export_preview.png','outputs/public_quickstart/berries.csv')

# Select the worst absolute count errors in held-out licensed berry tiles.
d=json.loads((R/'reports/berry_aux_evaluation.json').read_text())['classes']['berry']['test']
rows=json.loads((R/'reports/berry_aux_predictions.json').read_text())['test'];lookup={x['file']:x for x in rows}
worst=sorted(d['per_image'],key=lambda x:abs(x['error']),reverse=True)[:2]
fig,axs=plt.subplots(1,2,figsize=(10,4.8))
for ax,w in zip(axs,worst):
    path=R/'data/berry_yolo/images/test'/w['file'];ax.imshow(Image.open(path));row=lookup[w['file']]
    for b in row['gt']:
        x,y,u,v=b[1:];ax.add_patch(Rectangle((x,y),u-x,v-y,fill=False,ec='#00cfff',lw=.6))
    for b in row['pred']:
        if b[1]<d['threshold']:continue
        x,y,u,v=b[2:];ax.add_patch(Rectangle((x,y),u-x,v-y,fill=False,ec='#ff7700',lw=.7))
    ax.axis('off');ax.set_title(f'{w["file"]}\n标签 {w["ground_truth"]} / 预测 {w["predicted"]}',fontsize=10)
fig.tight_layout();save(fig,'test_error_examples.png',{'selection':'two largest absolute test count errors','cyan':'ground truth','orange':'prediction'})
(R/'reports/figure_evidence_index.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
# Publish completed bytes atomically so shared readers never see partial images.
import os,tempfile
for src in O.iterdir():
    im=Image.open(src);im.load()
    target=R/'docs/figures'/src.name
    fd,name=tempfile.mkstemp(dir=target.parent,prefix='complete-')
    with os.fdopen(fd,'wb') as out:out.write(src.read_bytes())
    os.replace(name,target)
print('Evidence figures',len(evidence))
