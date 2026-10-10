"""Visual course paper; figures are tied to saved real files by an evidence index."""
from paper_layout import *
from docx.enum.text import WD_BREAK
berry=json.loads((R/'reports/berry_aux_evaluation.json').read_text())
flower=json.loads((R/'reports/flower_evaluation.json').read_text())
young=json.loads((R/'reports/young_evaluation.json').read_text())
base=json.loads((R/'reports/young_baseline_evaluation.json').read_text())
def page(title):
 D.add_page_break();h(title)
def note(text):
 a=D.add_paragraph(text);a.paragraph_format.first_line_indent=Pt(0)
 a.paragraph_format.line_spacing=Pt(15)
 for r in a.runs:r.font.size=Pt(9)
 md.append(text)
def pair(files,captions,width=2.8):
 a=D.add_paragraph();a.alignment=WD_ALIGN_PARAGRAPH.CENTER;a.paragraph_format.first_line_indent=Pt(0);a.paragraph_format.line_spacing=1.0;a.paragraph_format.keep_with_next=True
 for i,file in enumerate(files):
  if i:a.add_run('  ')
  a.add_run().add_picture(str(O/'figures'/file),width=Inches(width))
 cap=D.add_paragraph('；'.join(captions),'Caption');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
 md.extend(f'![{c}](figures/{f})' for f,c in zip(files,captions))
# Cover
for text,style,before,after in [('生物生产机器人设计','Title',65,20),('基于 YOLO 与相对尺度判别的\n葡萄疏果识别系统的设计','Subtitle',0,38)]:
 a=D.add_paragraph(text,style);a.alignment=WD_ALIGN_PARAGRAPH.CENTER;a.paragraph_format.space_before=Pt(before);a.paragraph_format.space_after=Pt(after)
for text in ['课程设计选题  3 葡萄疏果识别图像处理算法','姓名  ____________________','学号  ____________________','专业班级  ____________________','指导教师  ____________________','完成日期  2026年10月']:
 a=D.add_paragraph(text);a.alignment=WD_ALIGN_PARAGRAPH.CENTER;a.paragraph_format.first_line_indent=Pt(0)
page('摘要与设计目标')
p('针对阳光玫瑰葡萄疏果中的查数与小果筛选需求，设计目标检测、单穗区域选择、相对尺度判别和结果导出程序。系统以YOLOv8n为基础，分别训练花序与小穗、辅助果粒及幼果弱标注模型；按检测框投影尺度产生可复查的疏除建议，输出编号图、CSV和JSON。')
p('三组模型各实际训练25轮。辅助果粒独立测试120图块的固定阈值F1为0.7467；幼果试验仅2个区域78个视觉辅助检查框，F1为0.8800，计数MAE为3.00粒。幼果标签未经专家复核，结果仅支持小规模算法流程试验。程序能够守恒统计可见保留数量，但不估算隐藏果粒，也不直接控制机械剪切。')
p('关键词：阳光玫瑰；疏果；YOLOv8；可见果粒计数；相对尺度')
h('1 研究背景与任务要求')
p('传统颜色和形状方法容易把绿色叶片、果梗与幼果混淆。Mask-GK采用实例掩膜高斯核进行果粒分割计数[1]；MVDNet利用计数与果穗分割双分支研究疏果期计数[2]。本设计不提出新网络结构，而是在普通CPU上完成真实数据清洗、检测、阈值筛选与可追溯导出[3]。')
p('公开精品果指标中，马陆阳光玫瑰为45—50粒每串[4]，但它不是照片可见果粒的统一目标。栽培记录强调小粒、内向粒等取舍[5]。二维照片难以判断果梗朝向，因此默认只比较相对大小，保留上限由用户按所框区域设置。')
table('表1 课程要求与实现',['要求','实现及边界'],[['花或小果图像','花序与幼果分别训练，较大果粒只作辅助'],['小果与去除阈值','相对尺度默认0.70，可调工程参数'],['留下数量','可见数减建议去除数，不含遮挡果粒'],['设计程序','CLI、桌面源码、模型及实际导出样例']])
page('2 数据样本与划分')
p('Du花序包采用CC BY 4.0许可[6]。原始命名条目567份含44份图片与标签完全相同的重复，实际523张；原包增强图不作独立样本。GBISC含巨峰、阳光玫瑰和夏黑各50张[1]，本设计先按原图组划分，再切为不重叠图块，避免一张原图的不同图块跨入测试集。')
fig('berry_samples.png','图1 阳光玫瑰训练图块与标签 GBISC CC BY 4.0',4.3)
h('2.1 花序训练样本',2)
p('花序模型包含整花序与小穗两类。下图保留实际文件名，分别显示不同穗型、背景与视角的标注。清洗后按拍摄序号分组，原包的重复文件和已有旋转增强不参与独立原图计数。')
fig('flower_samples.png','图2 花序训练原图与标签 Du CC BY 4.0',4.3)
page('2.2 预处理与幼果适配')
table('表2 实际划分与标签性质',['数据','训练','验证','测试','标签'],[['辅助果粒','360图块','120图块','120图块','原实例框'],['花序','369图','75图','79图','花序及小穗框'],['幼果','37图','1区域','2区域','训练伪标签 评测视觉框']])
p('辅助果粒图块对应90/30/30张原图。裁切目标保留规则为可见框面积不少于原框65%，最长边缩至768像素。花序按连续拍摄编号分组再划分。哈希审计未发现跨划分完全重复，但不能据此证明所有场景绝对独立。')
p('幼果从网络候选中按品种配文及疏果阶段筛出37张真实照片[7]，辅助模型生成1571个伪标签。同一网页处理前后图全部留在训练侧；验证与测试分别来自另外两个网站[5,8]。评测区域由AI视觉辅助逐框检查，不使用待测模型预测直接充当真值。未获明确再分发许可的幼果照片单独提供私人附件，公开包保留来源与坐标。')
pair(['berry_aux_train_batch0.jpg','flower_train_batch0.jpg'],['图3a 辅助果粒实际训练批次','图3b 花序实际训练批次'],2.75)
note('批次图由训练器实际保存，展示缩放、拼接等数据增强。它是训练过程证据，不是独立测试结果；幼果同样存在伪标签噪声，不能据此宣称已完成专家标注。')
page('3 算法结构与设计程序')
fig('system_design.png','图4 检测 筛选及结果导出的功能关系',6.0)
p('输入图像先由用户框选单穗。大区域使用1024像素窗口和768像素步长，坐标回到原图后以NMS消除重复框。模型输入固定填充到384像素，避免单图与批量填充方式不同造成计数差异。花序分支直接输出整花序与小穗数量，果粒分支继续筛选。')
p('第i个检测框宽高为wᵢ、hᵢ，投影尺度dᵢ=√(wᵢhᵢ)，相对尺度rᵢ=dᵢ/median(d)。当rᵢ<τ时建议去除，默认τ=0.70。它衡量二维框大小，透视与遮挡会影响判断，不能视作真实直径。')
p('若设置可见保留上限K，则在大小筛选后，从中心距离除以平均尺度最小的一对中优先去除较小者，迭代至数量不超过K。输出保持N=Nᵣ+Nₖ，不推算不存在的对象。每粒保存编号、位置、尺度、动作和原因供人工复查。')
table('表3 实际训练配置',['参数','辅助果粒 花序','幼果适配'],[['初始权重','COCO YOLOv8n','辅助best.pt'],['轮次 输入','25轮 384像素','25轮 384像素'],['批量 设备','16 CPU','8 CPU'],['优化器 学习率','AdamW 0.001','AdamW 0.0003'],['冻结 随机种子','10层 20261010','10层 20261010']])
for task,title,num,detail in [
 ('berry_aux','4 辅助果粒模型训练结果',5,'该模型学习较大果粒，稠密场景仍存在漏检。验证曲线不能代替幼果性能，也不能作为独立测试结论。'),
 ('flower','4.1 花序与小穗模型训练结果',7,'整花序尺度较大，定位较容易；小穗密集且相似，定位与类别混淆更明显。spikelet指小穗，不能当作单花。'),
 ('young','4.2 幼果弱标注模型训练结果',9,'训练37张、验证仅1个区域，因此曲线波动和较高分数缺乏稳健性。验证标签未经专家复核，不能报告为普遍识别准确率。')]:
 page(title)
 fig(f'{task}_results.png',f'图{num} 实际results.csv对应的训练损失及验证指标 results.png',6.25)
 fig(f'{task}_cm_evidence.png',f'图{num+1} 最佳权重验证计数矩阵及归一化矩阵 按实际数值重绘',6.1)
 p(detail)
 note('results.png来自训练CSV；矩阵由最佳权重重跑验证生成，位于runs/'+task+'_visual_val。横轴为真实标签，纵轴为预测标签；background表示误检或漏检。验证矩阵置信度0.001、匹配IoU为0.45，低阈值会计入更多误检，与下一节按验证选定阈值、IoU为0.50的测试矩阵区分。辅助results.png由保存的实际CSV重新绘制，未重训或修改指标。')
page('5 独立测试结果与计数误差')
p('预测按置信度排序，以IoU≥0.50逐框匹配，每个真实框最多匹配一次。阈值仅由验证集候选值的最高F1选定，再用于测试；P、R、F1与AP分别记录。图11汇总真阳性、误检和漏检；检测任务没有可定义的背景真阴性，右下格以横线表示。')
fig('test_confusion.png','图11 已保存测试记录生成的固定阈值检测矩阵',6.3)
rows=[]
for name,d,key in [('辅助果粒',berry,'berry'),('整花序',flower,'inflorescence'),('小穗',flower,'spikelet'),('幼果试验',young,'berry')]:
 q=d['classes'][key]['test'];rows.append([name,str(q['images']),f"{q['threshold']:.2f}",f"{q['precision']:.3f}",f"{q['recall']:.3f}",f"{q['f1']:.3f}",f"{q['count_mae']:.2f}"])
table('表4 固定阈值测试结果 MAE为每图粒或穗',['对象','图数','阈值','P','R','F1','MAE'],rows)
fig('test_count_scatter.png','图12 测试图标签数量与预测数量 虚线为理想一致关系',6.1)
note('辅助果粒测试120图块对应30原图；花序79图；幼果仅2区域78框。幼果散点不具有充分统计代表性。不同阶段、不同对象的成绩不能混为一个识别准确率。')
page('5.1 PR曲线与适配对照')
fig('flower_BoxPR_curve.png','图13 花序最佳权重重跑验证PR曲线 整花序与小穗分开显示',5.5)
pair(['berry_aux_BoxPR_curve.png','young_BoxPR_curve.png'],['图14a 辅助最佳权重验证PR','图14b 幼果最佳权重验证PR'],2.9)
q=base['classes']['berry']['test'];y=young['classes']['berry']['test']
table('表5 同一幼果外部测试区域上的对照',['模型','阈值','F1','MAE','mAP50'],[['辅助直接预测',f"{q['threshold']:.2f}",f"{q['f1']:.3f}",f"{q['count_mae']:.2f}",f"{base['test_AP']['metrics/mAP50(B)']:.3f}"],['弱标注适配',f"{y['threshold']:.2f}",f"{y['f1']:.3f}",f"{y['count_mae']:.2f}",f"{young['test_AP']['metrics/mAP50(B)']:.3f}"]])
note('两模型各自利用验证区域选阈值。适配后的固定阈值F1和MAE略有改善，mAP50反而降低，不能称为全面或显著提升；相近拍摄条件和标签不确定性仍限制结论。')
page('6 程序输入与实际输出')
fig('berry_input_output.png','图15 阳光玫瑰示例的输入与果粒导出 GBISC CC BY 4.0',5.1)
p('果粒命令行入口为src/predict.py，绿色框为保留，红色框为建议去除。所有数量只覆盖检测到的可见对象。多穗照片应先框选单穗，否则统计的是整个输入区域。')
fig('flower_input_output.png','图16 花序示例的输入与检测导出 Du CC BY 4.0',5.1)
p('花序入口为src/flower_predict.py，整花序与小穗计数分别输出。本页来自实际导出的annotated.jpg，展示花序分支的功能。')
page('6.1 运行记录与结构化导出')
fig('cli_run_record.png','图17 已实际执行的命令行运行记录摘录图',6.1)
fig('csv_export_preview.png','图18 实际CSV文件前六条记录的可读预览',6.1)
p('导出目录同时包含annotated.jpg、berries.csv和result.json。CSV使用UTF-8 BOM；JSON记录输入尺寸、ROI、模型、阈值、耗时和逐粒决策。图17与图18由保存的真实记录导出，属于命令行与结构化输出的运行证据。')
p('桌面入口src/app.py提供打开照片、拖框选ROI、切换模型和参数输入，推理线程异步回传结果。当前环境无法建立图形服务连接，尚未完成窗口交互验收，窗口操作仍需在目标电脑验收。已实际验证的入口是命令行。')
page('7 阈值响应与失败样例')
fig('test_error_examples.png','图19 独立测试中计数误差最大的两个辅助果粒图块 青色标签 橙色预测',6.1)
p('失败图主动选取绝对计数误差最大的测试样本，避免只展示好看的结果。密集果粒在384像素输入下目标很小，遮挡导致漏检，叶片及果梗也可能产生误检；提高小果比例阈值不会修复检测漏检。')
sens=json.loads((R/'reports/threshold_sensitivity.json').read_text())
table('表6 同一40粒演示ROI的小果比例敏感性',['比例τ','检测数','建议去除','保留'],[[f"{x['size_ratio']:.2f}",x['visible_count'],x['remove_count'],x['keep_count']] for x in sens])
p('默认0.70下建议去除15粒、保留25粒。该表只验证规则响应与数量守恒，未与农艺专家疏除选择对照，不能据此称默认比例最优。工程验收通过6项单元测试及真实照片导出、中文路径、空白图像、缺失文件、越界ROI和CSV/JSON一致性检查。')
page('8 结论与交付复现')
p('本设计完成三组实际训练及可见目标识别、相对大小筛选、可调上限和结构化导出。训练数据、曲线、混淆矩阵与失败案例均保留来源路径，便于检查“样本—训练—验证—测试—程序输出”的对应关系。当前可作为课程算法原型，尚无整穗隐藏粒数、田间疏除正确率或机械剪切精度的证据。')
p('后续应优先扩大跨果园、跨光照的独立幼果样本，并由双人或专家复核标签，再考虑实例分割与果梗朝向。继续追求更高小样本分数不足以消除上述限制。')
table('表7 交付包可直接查找的材料',['目录','内容'],[['data/berry_yolo images labels','实际辅助果粒训练360 验证120 测试120图块'],['data/flower_yolo images labels','实际花序训练369 验证75 测试79原图'],['私人幼果附件','37训练 1验证 2测试图片及标签 来源与恢复说明'],['runs 各模型目录','best last权重 results.csv results.png 矩阵 PR'],['docs figures','论文图及图像来源证据索引'],['src scripts tests reports','程序 复现脚本 单元测试 实际评测与日志']])
p('完整包解压后先按使用说明安装依赖，再运行提供的两张有许可的示例；模型已训练，无需重训才能识别。公开幼果照片恢复依赖原网页，可能失效；私人附件保存此次实际使用文件。更换路径后应重新生成dataset.yaml或运行prepare脚本。')
page('参考文献')
refs=[
'[1] YANG C, GENG T, PENG J, et al. Mask-GK An efficient method based on mask Gaussian kernel for segmentation and counting of grape berries in field[J]. Computers and Electronics in Agriculture, 2025, 234:110286. DOI:10.1016/j.compag.2025.110286.',
'[2] DU W, QIN W, CUI X, et al. A precise berry counting method for in-cluster grapes to guide berry thinning[J]. Frontiers in Plant Science, 2026,16:1739688. DOI:10.3389/fpls.2025.1739688. 本设计未取得其完整779张数据.',
'[3] ULTRALYTICS. Explore Ultralytics YOLOv8[EB/OL]. https://docs.ultralytics.com/models/yolov8. 访问日期2026-10-10.',
'[4] 上海市人民政府新闻办公室. 精品果按串销售每串售价100元 马陆葡萄品牌价值再创新高[EB/OL]. https://www.shio.gov.cn/TrueCMS/shxwbgs/ywts/content/94f32927-3c25-4f87-82c2-1cf6438d6cc2.htm. 访问日期2026-10-10.',
'[5] やくも果樹研究所. シャインマスカット栽培 摘房 摘粒 1回目[EB/OL]. https://kaju-fruits.com/シャインマスカット　粗摘房・粗摘粒/. 访问日期2026-10-10.',
'[6] DU W. Grape inflorescence dataset[DB/OL]. Mendeley Data,2022,V1. DOI:10.17632/skwbr5k9gg.1. CC BY 4.0.',
'[7] Tom. シャインマスカットのジベレリン処理後の予備摘粒[EB/OL]. https://tomtom1ono.hatenablog.com/entry/2026/06/19/225730. 2026-06-19.',
'[8] Grapetopia. 粒間引き 摘粒 荒間引き[EB/OL]. https://grapetopia.hatenablog.com/entry/2020/06/06/222016. 2020-06-06.'
]
for text in refs:
 a=D.add_paragraph(text);a.paragraph_format.first_line_indent=Pt(0);a.paragraph_format.line_spacing=Pt(13)
 for run in a.runs:run.font.size=Pt(8.5)
md+=refs
D.core_properties.author='';D.core_properties.last_modified_by='';D.core_properties.title='葡萄疏果识别系统的设计';D.core_properties.subject='生物生产机器人设计课程论文';D.core_properties.comments=''
D.save('/tmp/grape-paper-complete.docx');import shutil;shutil.copyfile('/tmp/grape-paper-complete.docx',O/'课程设计论文.docx');(O/'论文正文.md').write_text('\n\n'.join(md),encoding='utf-8');print('saved characters',len('\n'.join(md)),'figures',len(D.inline_shapes))
