"""Course paper built from saved actual evaluation records; anonymous cover."""
from pathlib import Path
import json,csv
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
R=Path(__file__).resolve().parents[1];O=R/'docs';O.mkdir(exist_ok=True)
D=Document();sec=D.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11);sec.top_margin=sec.bottom_margin=Inches(.82);sec.left_margin=sec.right_margin=Inches(.9)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Caption']:
 s=D.styles[name];s.font.name='Noto Serif CJK SC';s.font.color.rgb=RGBColor(0,0,0);s._element.rPr.rFonts.set(qn('w:eastAsia'),'Noto Serif CJK SC');s.font.size=Pt(11 if name=='Normal' else 16 if name=='Heading 1' else 12 if name in ['Heading 2','Caption'] else 22 if name=='Title' else 15)
 s.paragraph_format.space_after=Pt(7);s.paragraph_format.line_spacing=Pt(19 if name=='Normal' else 14 if name=='Caption' else 25 if name in ['Title','Subtitle'] else 22)
 s.font.italic=False
 for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
  s._element.rPr.rFonts.attrib.pop(qn('w:'+attr),None)
# Remove inherited Word title borders and theme overrides.
for style in D.styles:
 if style.type == 1:
  pp=style._element.find(qn('w:pPr'))
  if pp is not None:
   for b in list(pp.findall(qn('w:pBdr'))):pp.remove(b)
D.styles['Normal'].paragraph_format.first_line_indent=Pt(22)
D.styles['Caption'].font.size=Pt(9);D.styles['Caption'].paragraph_format.first_line_indent=Pt(0)
header=sec.header.paragraphs[0];header.text='生物生产机器人设计  课程设计论文';header.alignment=WD_ALIGN_PARAGRAPH.RIGHT;header.runs[0].font.size=Pt(9)
f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');f._p.append(fld)
md=[]
def p(text):D.add_paragraph(text);md.append(text+'\n')
def h(text,level=1):D.add_heading(text,level);md.append('#'*level+' '+text+'\n')
def table(caption,headers,rows):
 cap=D.add_paragraph(caption,'Caption');cap.paragraph_format.keep_with_next=True;md.append(caption+'\n')
 t=D.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
 for i,v in enumerate(headers):t.rows[0].cells[i].text=str(v)
 for row in rows:
  cells=t.add_row().cells
  for c,v in zip(cells,row):c.text=str(v)
 for ri,row in enumerate(t.rows):
  no=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(no)
  for c in row.cells:
   c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER;tcPr=c._tc.get_or_add_tcPr();b=OxmlElement('w:tcBorders')
   for edge in ['top','left','bottom','right']:
    e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');b.append(e)
   tcPr.append(b)
   if ri==0:
    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8E8E8');tcPr.append(shade)
   for para in c.paragraphs:
    para.paragraph_format.keep_with_next=(ri<len(t.rows)-1);para.paragraph_format.first_line_indent=Pt(0);para.paragraph_format.space_after=Pt(4);para.paragraph_format.space_before=Pt(4);para.paragraph_format.line_spacing=Pt(14)
    for run in para.runs:run.font.size=Pt(9)
  if ri==0:rep=OxmlElement('w:tblHeader');row._tr.get_or_add_trPr().append(rep)
 D.add_paragraph().paragraph_format.space_after=Pt(0)
 md.append('| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n')
def fig(file,caption,width=6.3):
 a=D.add_paragraph();a.alignment=WD_ALIGN_PARAGRAPH.CENTER;a.paragraph_format.first_line_indent=Pt(0);a.paragraph_format.keep_with_next=True;a.paragraph_format.line_spacing=1.0;a.add_run().add_picture(str(O/'figures'/file),width=Inches(width));b=D.add_paragraph(caption,'Caption');b.alignment=WD_ALIGN_PARAGRAPH.CENTER;md.append(f'![{caption}](figures/{file})\n')

t=D.add_paragraph('生物生产机器人设计','Title');t.alignment=WD_ALIGN_PARAGRAPH.CENTER;t.paragraph_format.space_before=Pt(65)
t=D.add_paragraph('基于 YOLO 与相对尺度判别的\n葡萄疏果识别系统的设计','Subtitle');t.alignment=WD_ALIGN_PARAGRAPH.CENTER;t.paragraph_format.space_after=Pt(50)
for text in ['课程设计选题  3 葡萄疏果识别图像处理算法','姓名  ____________________','学号  ____________________','专业班级  ____________________','指导教师  ____________________','完成日期  2026年10月']:
 a=D.add_paragraph(text);a.alignment=WD_ALIGN_PARAGRAPH.CENTER;a.paragraph_format.first_line_indent=Pt(0)
D.add_page_break();h('摘要')
p('针对阳光玫瑰葡萄疏果过程中果粒查数和小果筛选的需求，设计了由目标检测、单穗区域选择、相对尺度判别及结果导出组成的图像处理系统。系统以 YOLOv8n 为检测基础，分别训练花序与小穗模型、辅助果粒模型，并使用疏果期网络实拍照片进行幼果弱标注适配。果粒筛选采用检测框面积平方根与中位尺度的比值，在不提供实际物理标尺的情况下生成可复核的疏除建议。程序输出编号图、CSV 与 JSON，记录检测数量、建议去除数量及可见保留数量。')
berry=json.loads((R/'reports/berry_aux_evaluation.json').read_text());flower=json.loads((R/'reports/flower_evaluation.json').read_text());young=json.loads((R/'reports/young_evaluation.json').read_text());base=json.loads((R/'reports/young_baseline_evaluation.json').read_text());ym=young['classes']['berry']['test'];bm=berry['classes']['berry']['test']
p(f"辅助果粒测试集包含30张原图划分的120个图块，其 mAP50 为{berry['test_AP']['metrics/mAP50(B)']:.4f}，固定置信度下 F1 为{bm['f1']:.4f}，计数平均绝对误差为{bm['count_mae']:.2f}粒。花序测试集79张图像的双类别平均 mAP50 为{flower['test_AP']['metrics/mAP50(B)']:.4f}。幼果外部试验仅有2张图像和78个可辨识果粒，适配后 F1 为{ym['f1']:.4f}、计数平均绝对误差为{ym['count_mae']:.2f}粒。幼果训练标签由辅助模型生成，外部评测框由视觉辅助检查形成，均未经农业专家独立复核，因此该结果仅用于验证算法流程，不足以推断田间泛化能力。工程测试确认数量守恒、尺度缩放、异常输入与导出一致性；桌面界面的交互运行仍需在目标电脑上验收。")
p('关键词：阳光玫瑰；葡萄疏果；YOLOv8；可见果粒计数；相对尺度；弱标注')
h('1 研究背景与设计目标')
p('疏果并非简单地把一穗葡萄剪到某个固定数量。操作还要考虑果穗结构、果粒朝向、大小整齐程度和后续膨大空间。对课程设计而言，首先需要解决的是照片上能否稳定找到果粒，以及每一次筛选建议是否能够解释和复查。若只有最终计数而没有具体位置，出现漏检时难以判断问题来自识别还是筛选规则。')
p('现有方法大致包括基于颜色与形状的传统图像处理、基于检测框的识别以及分割或密度图计数。传统方法实现直接，但幼果、叶片和果梗常有相近颜色，复杂背景容易产生误检。Mask-GK 研究采用实例掩膜构造高斯核，实现田间果粒分割和计数[1]；MVDNet 采用计数与果穗分割双分支，为疏果期整穗计数提供了研究思路[2]。这些方法的评价数据、标签形式和计数对象不同，不能将文献精度直接作为本设计的实验结果。')
p('本设计选用 YOLOv8n，是为了在普通 CPU 条件下形成可运行的检测程序[3]。工作重点放在数据阶段辨别、原图分组、可解释筛选和过程归档，而不是提出新的网络结构。系统目标是辅助观察单张图像中的可见果粒，不执行机械剪切，也不估算完全遮挡的果粒。')
h('2 农艺依据与需求分析')
p('马陆葡萄2024年精品果标准的公开报道给出了阳光玫瑰45至50粒每串、单粒重12至14克的质量指标[4]。该指标对应特定产区和精品果要求，不宜当作所有果园、所有疏果时期的统一阈值。网络栽培资料也显示，实际疏果强调小粒、内向粒和上下向粒的取舍[5]。仅凭单幅二维图片，本程序能提供相对大小和图像内拥挤程度，尚不能可靠推断果梗空间朝向。')
p('因此，小果阈值设置为可调整的工程参数，默认相对尺度比0.70；保留数量设置为用户输入的“当前区域可见果粒上限”，默认留空。留空时只按相对大小筛选，输入上限时再执行拥挤筛选。界面要求用户先框选一穗，以减少多穗混计。对于花序照片，识别对象为整花序和小穗，不能把小穗框的数量写成果粒或单花数量。')
table('表1 课程任务与程序实现对应关系',['任务要求','本设计实现','适用范围'],[
 ['花或小果图像','花序数据训练与幼果实拍适配','花序与幼果分开建模'],['识别小果','相对尺度比及可调阈值','二维投影尺度'],['给出去除阈值','默认0.70并提供敏感性结果','工程启发式规则'],['给出留下数量','可见数减建议去除数','不含完全遮挡果粒'],['设计程序附件','CLI 桌面源代码 模型 导出样例','离线图像处理']])
h('3 数据来源与预处理')
h('3.1 花序与辅助果粒数据',2)
p('花序数据来自 Wensheng Du 公开发布的数据包，采用 CC BY 4.0 许可[6]。包内除原始 IMG 文件外还含数字命名的增强图。本设计不把增强图当作独立原图使用。恢复审计发现，原始命名文件共有567条目，其中44条为图片和标注均完全一致的重复，实际独立文件为523张；同名重复不存在标注冲突。此前检查点中的567统计已在审计记录中纠正。')
p('GBISC 数据随 Mask-GK 项目公开，包含巨峰、阳光玫瑰和夏黑各50张高分辨率图片[1]。其果粒主要处于较大果粒阶段，不能代替疏果期幼果样本。本设计把它用于辅助检测能力训练。COCO 中不同划分类别编号先统一为一个 berry 类，再依据原始图片编号每5张组成一组；每个品种的组按固定随机种子分为6组训练、2组验证和2组测试。先划分原图，再制作图块，避免同一原图的不同图块同时出现在训练集和测试集中。')
p('辅助果粒原图被划分为四个不重叠图块，图块最长边缩放至768像素。检测框与图块相交面积不足原框65%的目标不纳入该图块标签，这一边缘政策使评测对象偏向可完整观察的果粒，计数误差不能直接解释为整幅原图误差。花序图像按连续拍摄编号的十位分组，分组后拆分为369张训练、75张验证和79张测试。序号分组只是一种减少近邻泄漏的办法，不能证明不同果穗或不同场景已经完全独立。')
table('表2 实際使用数据量与标签性质',['数据','训练图像','验证图像','测试图像','标签'],[
 ['辅助果粒','90原图 360图块','30原图 120图块','30原图 120图块','数据集实例框'],['花序','369','75','79','整花序与小穗框'],['幼果试验','37','1区域','2区域','训练伪标签 评测视觉框']])
h('3.2 幼果实拍筛选与弱标注',2)
manifest=json.loads((R/'reports/young_source_candidates.json').read_text());count=len({m['file'] for m in manifest})
p(f'网络采集共保存{count}个候选图片文件及对应来源链接，其中包括药剂器具、成品果、广告和部分损坏图像。候选数量不等于有效训练样本数。结合正文的品种描述和拍摄阶段，选择 Tom 家阳光玫瑰疏果记录中的37张实拍图片用于适配，其中含同一果穗的处理前后照片，均保留在训练侧。辅助果粒模型以640像素输入、0.25置信度产生1571个伪标签。伪标签可提高流程完整性，但会继承教师模型的漏检和误检，不能当作专家真值。')
p('验证区域来自やくも果树研究所的阳光玫瑰摘粒文章；测试区域来自葡萄栽培记录中明确配文为阳光玫瑰的两张照片。品种核对十分必要：同一网页前面的照片实际上介绍另一个品种，不能因为文章提到阳光玫瑰就把全部图片赋为该品种。评测框在图像坐标上通过视觉辅助逐框检查形成，不使用待测检测器的预测框直接充当真值；可辨识边界不清的遮挡小粒仍可能遗漏，标签可靠性有限。验证区域36个框、测试区域78个框。')
p('三部分按网站来源隔离：训练来源为 tomtom1ono.hatenablog.com，验证来源为 kaju-fruits.com，测试来源为 grapetopia.hatenablog.com。这样可以避免同一网页前后处理照片跨入训练和测试。该试验仍只有极少数独立场景，未覆盖不同果园和光照条件。未明确许可转载的照片只作私人恢复档案，公开资料保留下载地址、筛选记录、坐标标注和训练代码，不重新公开原图。')
h('4 系统与算法设计')
fig('system_design.png','图1 葡萄疏果识别系统的功能关系')
h('4.1 检测与坐标处理',2)
p('检测器采用 COCO 预训练的 YOLOv8n。花序模型具有两个类别；辅助果粒和幼果适配模型均只识别果粒。训练统一采用25轮、384像素输入和 CPU，冻结前10层，在有限时间内完成迁移学习。幼果模型从已训练的辅助模型继续适配，而不是从随机参数开始训练。其学习率降低至0.0003，防止小样本过快改变已有特征。')
p('推理时用户给出图像路径和单穗 ROI。对于较大区域，以1024像素窗口、768像素步长生成重叠图块，再把检测坐标换回原图坐标，最后以0.45的 NMS 阈值去除跨图块重复框。窗口输入固定填充到384像素尺寸。在开发中发现默认的单图矩形填充和混合尺寸批量评测会产生数量差异，现已显式关闭矩形填充，并在统一设置后重跑评测。高分辨率滑窗演示与数据集图块 AP 评测仍是不同的使用场景，演示计数不冒充标准测试分数。')
h('4.2 小果阈值与拥挤筛选',2)
p('设第 i 个检测框的宽、高为 wᵢ 和 hᵢ，定义投影尺度 dᵢ = √(wᵢhᵢ)，相对尺度 rᵢ = dᵢ / median(d)。当 rᵢ 小于比例阈值 τ 时，将其标为 relative_small。默认 τ 为0.70，该参数仅是对同一 ROI 中检测框大小的比较。距离镜头较远的果粒、被遮挡而框较小的果粒，可能被误判为小果；拍摄时应尽量靠近单穗并避免严重透视。')
p('若用户输入可见保留上限 K，且第一步筛选后的保留数量仍大于 K，则计算任意两粒中心距离与平均投影尺度之比。每轮找到归一化距离最小的一对，优先去除尺度较小者；同尺度时再按置信度和索引确定顺序。删除后重新计算，直到数量不超过 K。这个规则提供可重复的图像内拥挤处理，不等于农艺上对内向粒、果梗位置或穗型的判断。K 大于当前检测数量时，不凭空补出缺失果粒。')
p('输出中每个果粒保留编号、边界框、置信度、相对尺度、动作和理由。可见数量 N、建议去除数量 Nᵣ、保留数量 Nₖ 满足 N = Nᵣ + Nₖ。绿色框表示保留，红色框表示建议去除。建议去除的对象由观察者复查后决定，系统没有连接机器人执行器。')
h('4.3 程序组织与操作',2)
p('命令行入口 src/predict.py 负责果粒检测和导出，src/flower_predict.py 负责花序检测，src/thinning.py 负责独立筛选规则。src/app.py 提供本地桌面入口，可打开图像、拖动选择 ROI、切换模型、调整参数并显示导出结果。识别线程在后台运行，结果通过队列交回界面，避免界面线程直接承担模型推理。论文附带的使用说明给出 Python 环境安装、命令行示例和数据复现步骤。')
h('5 实验设置与结果')
table('表3 训练配置',['参数','辅助果粒与花序','幼果适配'],[['初始权重','COCO YOLOv8n','辅助果粒 best.pt'],['轮次与图像输入','25轮 384像素','25轮 384像素'],['批量与设备','16 CPU','8 CPU'],['优化器与初始学习率','AdamW 0.001','AdamW 0.0003'],['冻结层与随机种子','10层 20261010','10层 20261010']])
fig('training_curves.png','图2 实际训练记录生成的验证平均精度曲线')
p('固定阈值评价采用 IoU 不小于0.50的逐框匹配。预测框按置信度降序排列，每个真实框最多匹配一次，计算 precision、recall 和 F1；每幅图预测数减真实数用于计算 MAE、RMSE 和有符号偏差。置信度在验证集的0.05至0.50候选范围内选择 F1 最大者，再用于测试集。AP 来自 Ultralytics 测试流程，统计方式与单个固定阈值下的 P、R 不同，因此两套结果分别保存。')
rows=[]
for name,d,key in [('辅助果粒',berry,'berry'),('花序',flower,'inflorescence'),('小穗',flower,'spikelet'),('幼果试验',young,'berry')]:
 q=d['classes'][key]['test'];rows.append([name,str(q['images']),f"{q['threshold']:.2f}",f"{q['precision']:.3f}",f"{q['recall']:.3f}",f"{q['f1']:.3f}",f"{q['count_mae']:.2f}"])
table('表4 固定验证阈值下的测试结果',['对象','图数','阈值','P','R','F1','MAE 粒或穗'],rows)
p(f"辅助果粒共有9612个测试标签，固定阈值0.30下真阳性{bm['tp']}、误检{bm['fp']}、漏检{bm['fn']}，计数平均偏差{bm['count_bias']:.2f}粒，主要问题是漏检。这个结果表明模型可用于给出可见位置提示，但稠密果穗上的计数仍偏低。花序整体定位的 F1 高于小穗识别；小穗密集、细小且相互接近，漏检和重复识别更明显。花序双类别平均 mAP50-95 为{flower['test_AP']['metrics/mAP50-95(B)']:.4f}，不能将整花序定位成绩代替小穗成绩。")
q=base['classes']['berry']['test'];table('表5 同一外部幼果区域的适配前后试验',['模型','验证阈值','测试 F1','测试 MAE','测试 mAP50'],[
 ['辅助模型直接预测',f"{q['threshold']:.2f}",f"{q['f1']:.3f}",f"{q['count_mae']:.2f}",f"{base['test_AP']['metrics/mAP50(B)']:.3f}"],['幼果弱标注适配',f"{ym['threshold']:.2f}",f"{ym['f1']:.3f}",f"{ym['count_mae']:.2f}",f"{young['test_AP']['metrics/mAP50(B)']:.3f}"]])
p('表5的两个模型各自仅利用同一验证区域选择阈值，测试区域未用于训练。它用于观察适配是否改变检测行为，不构成充分的泛化结论。两张测试照片可能来自同一栽培园、相近条件，且标注未经专家复核；即使 F1 较高，也不能报告为“阳光玫瑰幼果普遍识别准确率”。准确率、F1 和 mAP 是不同指标，本文不将它们相互替换。')
fig('public_examples.png','图3 实际程序输出示例 左为GBISC阳光玫瑰较大果粒 右为Du花序数据 CC BY 4.0',6.1)
demo=json.loads((R/'outputs/berry_demo/result.json').read_text());p(f"图3左侧示例的原图为 ShineMuscat_5.jpg，ROI 为(1100,500,2300,2300)，识别到{demo['visible_count']}个可见果粒，比例阈值0.70下建议去除{demo['remove_count']}个、保留{demo['keep_count']}个。该图是较大果粒的功能演示，并不属于新增幼果测试集。右侧结果显示整花序与小穗检测框；两类数量的生物学含义不同。")
sens=json.loads((R/'reports/threshold_sensitivity.json').read_text());table('表6 同一演示图像的比例阈值敏感性',['τ','识别数量','建议去除','保留'],[[f"{x['size_ratio']:.2f}",x['visible_count'],x['remove_count'],x['keep_count']] for x in sens])
p('阈值变化只影响已经检测到的对象，不会修复漏检。比例越高，标为小果的对象通常越多，但中位尺度本身受检测框质量影响。表6仅用于检查规则响应和数量守恒，未与农业专家的实际疏果选择比较，因此不能称为最优农艺阈值。')
h('6 验证记录与误差分析')
p('数据审计检查了花序同名重复文件、原图跨划分哈希以及低分辨率感知哈希候选。辅助果粒150张和花序523张未发现跨划分的完全相同图片，也没有感知距离不大于8的候选。感知哈希没有发现近重复，不意味着场景绝对独立，仍需更完整的果穗编号和采集批次信息。')
p('筛选规则通过6项单元测试，覆盖空输入、比例筛选、整体缩放不变、上限大于检测量、零上限以及无效输入。端到端测试另外核对真实照片导出、中文文件名、空白图像、越界 ROI、缺失图像、原图坐标范围和 CSV/JSON 数量一致性。所有模型均实际完成25轮训练，并保存 CSV、权重及日志；评测结果可由程序重新生成。')
p('桌面界面已通过语法与模块导入检查，但当前执行环境无法建立图形服务器监听连接，未完成真实窗口的拖框与按钮交互验收。命令行入口和核心推理导出已实际运行。交付说明据此把桌面界面列为需在目标电脑验收的附件，而不填写虚假的“全部界面通过”记录。运行速度在当前 CPU 上记录于具体样例 JSON，不视为任何电脑都能达到的性能保证。')
p('本设计仍有三类主要误差。第一是识别误差：叶片、果梗和遮挡导致误检漏检，幼果伪标签会继承这些问题。第二是尺度误差：二维检测框不是果实直径，透视和遮挡会改变相对尺寸。第三是决策误差：按大小和距离删除的对象未必符合果穗朝向与穗型要求。后续应先补充跨果园的独立幼果样本并请人工双人标注复核，再结合果梗方向或实例分割改进决策。')
h('7 结论')
p('本课程设计形成了可运行的葡萄图像识别与疏果建议程序，完成了公开数据清洗、三组实际训练、外部幼果试验和结果导出。程序能够记录每个可见目标的位置、相对大小和筛选原因，并给出保留数量；设计文件包含源码、模型、参数、日志、测试报告和使用说明。实验同时暴露出稠密果粒漏检与幼果真值不足的问题，说明数据与评价口径比单一分数更重要。')
p('本设计可作为课程算法原型和进一步采集验证的基础。其结论限定于当前可见目标、当前数据和已运行的命令行流程；对于整穗隐藏果粒数量、真实田间疏除正确率和机器人剪切精度，尚无实验依据。')
h('参考文献')
refs=[
 '[1] YANG C, GENG T, PENG J, et al. Mask-GK An efficient method based on mask Gaussian kernel for segmentation and counting of grape berries in field[J]. Computers and Electronics in Agriculture, 2025, 234:110286. DOI:10.1016/j.compag.2025.110286. 数据与代码:https://github.com/volcanoYcc/Mask-GK.',
 '[2] DU W, QIN W, CUI X, et al. A precise berry counting method for in-cluster grapes to guide berry thinning[J]. Frontiers in Plant Science, 2026, 16:1739688. DOI:10.3389/fpls.2025.1739688. 该研究完整数据需向作者申请 本设计未取得其779张数据.',
 '[3] ULTRALYTICS. Explore Ultralytics YOLOv8[EB/OL]. https://docs.ultralytics.com/models/yolov8. 访问日期2026-10-10.',
 '[4] 上海市人民政府新闻办公室. 精品果按串销售每串售价100元 马陆葡萄品牌价值再创新高[EB/OL]. https://www.shio.gov.cn/TrueCMS/shxwbgs/ywts/content/94f32927-3c25-4f87-82c2-1cf6438d6cc2.htm. 访问日期2026-10-10.',
 '[5] やくも果樹研究所. シャインマスカット栽培 摘房 摘粒 1回目[EB/OL]. https://kaju-fruits.com/シャインマスカット　粗摘房・粗摘粒/. 访问日期2026-10-10.',
 '[6] DU W. Grape inflorescence dataset[DB/OL]. Mendeley Data, 2022, V1. DOI:10.17632/skwbr5k9gg.1. CC BY 4.0.',
 '[7] Tom. シャインマスカットのジベレリン処理後の予備摘粒[EB/OL]. https://tomtom1ono.hatenablog.com/entry/2026/06/19/225730. 2026-06-19.',
 '[8] Grapetopia. 粒間引き 摘粒 荒間引き[EB/OL]. https://grapetopia.hatenablog.com/entry/2020/06/06/222016. 2020-06-06.'
]
for text in refs:
 a=D.add_paragraph(text);a.paragraph_format.first_line_indent=Pt(0);a.paragraph_format.line_spacing=Pt(14)
 for run in a.runs:run.font.size=Pt(9)
md+=refs
h('附录 程序与实验文件索引')
p('src 为设计程序；scripts 为数据准备、训练、评测与报告生成程序；runs 下各模型目录保存训练记录和 best.pt；reports 为指标、源数据审计和验收结果；outputs 为实际导出样例；annotations 为幼果评测坐标及标注方法说明。运行和恢复命令见 README 与 docs/使用说明.md。全部数据集、下载候选、伪标签和独立原图数量按实际记录表述，未将增强次数当作原始照片数量。')
D.core_properties.author='';D.core_properties.last_modified_by='';D.core_properties.title='葡萄疏果识别系统的设计';D.core_properties.subject='生物生产机器人设计课程论文';D.core_properties.keywords='葡萄 疏果 YOLO 可见果粒';D.core_properties.comments=''
D.save(O/'课程设计论文.docx');(O/'论文正文.md').write_text('\n\n'.join(md),encoding='utf-8');print('saved',O/'课程设计论文.docx','characters',len('\n'.join(md)))
