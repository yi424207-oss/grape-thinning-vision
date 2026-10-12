"""Visual course paper; figures are tied to saved real files by an evidence index."""
from paper_layout import *
from docx.enum.text import WD_BREAK
berry=json.loads((R/'reports/berry_aux_evaluation.json').read_text())
flower=json.loads((R/'reports/flower_evaluation.json').read_text())
young=json.loads((R/'reports/young_evaluation.json').read_text())
base=json.loads((R/'reports/young_baseline_evaluation.json').read_text())
review=json.loads((R/'reports/review_statistics.json').read_text())
cpu=json.loads((R/'reports/cpu_benchmark.json').read_text())
import yaml
configs={task:yaml.safe_load((R/'runs'/task/'args.yaml').read_text()) for task in ['berry_aux','flower','young']}
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
for text,style,before,after in [('生物生产机器人设计','Title',65,20),('基于 YOLO 与相对尺度判别的\n葡萄可见果粒检测与尺度筛选算法原型设计','Subtitle',0,38)]:
 a=D.add_paragraph(text,style);a.alignment=WD_ALIGN_PARAGRAPH.CENTER;a.paragraph_format.space_before=Pt(before);a.paragraph_format.space_after=Pt(after)
for text in ['课程设计选题  3 葡萄疏果识别图像处理算法','姓名  ____________________','学号  ____________________','专业班级  ____________________','指导教师  ____________________','完成日期  2026年10月']:
 a=D.add_paragraph(text);a.alignment=WD_ALIGN_PARAGRAPH.CENTER;a.paragraph_format.first_line_indent=Pt(0)
page('摘要与设计目标')
p('针对阳光玫瑰葡萄疏果中的查数与小果筛选需求，设计目标检测、单穗区域选择、相对尺度判别和结果导出程序。系统以YOLOv8n为基础，分别训练花序与小穗、辅助果粒及幼果弱标注模型；按检测框投影尺度产生可复查的疏除建议，输出编号图、CSV和JSON。')
p('三组模型各实际训练25轮。辅助果粒独立测试120图块的固定阈值F1为0.7467；幼果试验仅2个区域78个视觉辅助检查框，F1为0.8800，计数MAE为3.00粒。幼果标签未经专家复核，结果仅支持小规模算法流程试验。已验收入口为命令行；桌面窗口交互未验收。程序守恒统计检测到的可见对象，不估算隐藏果粒。筛选结果仅供人工复查，不是完整农艺疏果决策。')
p('关键词：阳光玫瑰；疏果；YOLOv8；可见果粒计数；相对尺度')
h('1 研究背景与任务要求')
p('传统颜色和形状方法容易把绿色叶片、果梗与幼果混淆。Mask-GK采用实例掩膜高斯核进行果粒分割计数[1]；MVDNet利用计数与果穗分割双分支研究疏果期计数[2]。本设计采用YOLOv8n[3]，不提出新网络结构。数据清洗、检测、阈值筛选与导出由本项目程序完成；CPU耗时由实际测量报告支撑。')
p('同行评议研究指出，疏果效应受到品种、生育期、生理状态及环境条件影响[9]，不能仅用二维检测框大小决定。公开精品果指标中，马陆阳光玫瑰为45—50粒每串[4]，它不是照片可见果粒的统一目标。网页栽培记录[5]仅用作照片来源和背景，不用来证明默认阈值具有农艺最优性。二维照片不能充分识别朝向、病虫害、机械损伤或穗形均匀度；本原型只按投影尺度生成待复查建议。')
table('表1 课程要求与实现',['要求','实现及边界'],[['花或小果图像','花序与幼果分别训练，较大果粒只作辅助'],['小果与去除阈值','相对尺度默认0.70，可调工程参数'],['留下数量','可见数减建议去除数，不含遮挡果粒'],['设计程序','CLI、桌面源码、模型及实际导出样例']])
page('2 数据样本与划分')
p('Du花序包采用CC BY 4.0许可[6]。原始命名条目567份含44份图片与标签完全相同的重复，实际523张；原包增强图不作独立样本。GBISC含巨峰、阳光玫瑰和夏黑各50张[1]，辅助模型混合使用三品种。每品种按原图编号连续5张为一组，以20261010随机种子将10组分为6训练、2验证、2测试；每品种原图数为30/10/10。每原图切为四个不重叠象限，同组全部留在一个划分。三品种都参与训练和测试，不属于未见品种泛化试验。')
fig('berry_samples.png','图1 三品种辅助果粒训练图块与标签 GBISC CC BY 4.0',4.3)
table('表2 三品种原图划分与固定阈值测试',['品种','训练 验证 测试原图','测试F1'],[[name,'30 10 10',f"{review['cultivar_results'][key]['f1']:.4f}"] for name,key in [('巨峰','Kyoho'),('阳光玫瑰','ShineMuscat'),('夏黑','SummerBlack')]])
page('2.1 花序训练样本')
p('花序模型包含整花序与小穗两类。下图保留实际文件名，分别显示不同穗型、背景与视角的标注。清洗后按拍摄序号分组，原包的重复文件和已有旋转增强不参与独立原图计数。')
fig('flower_samples.png','图2 花序训练原图与标签 Du CC BY 4.0',4.3)
page('2.2 预处理与幼果适配')
table('表3 实际划分与标签性质',['数据','训练','验证','测试','标签'],[['辅助果粒','360图块','120图块','120图块','原实例框'],['花序','369图','75图','79图','花序及小穗框'],['幼果','37图','1区域','2区域','训练伪标签 评测视觉框']])
p('辅助果粒图块对应90/30/30张原图。裁切目标保留规则为可见框面积不少于原框65%，最长边缩至768像素。花序组号为拍摄编号整除10，以20261010随机种子打乱组号后按组划分。逐组样本数见reports/split_group_distribution.json。来源未提供植株、果园身份，编号相邻分组和去重只能控制已知泄漏风险，不能证明植株或场景完全独立。')
p('幼果从网络候选中按品种配文及疏果阶段筛出37张真实照片[7]，辅助模型生成1571个伪标签。同一网页处理前后图全部留在训练侧；验证与测试分别来自另外两个网站[5,8]。评测区域由AI视觉辅助逐框检查，不使用待测模型预测直接充当真值。未获明确再分发许可的幼果照片不包含于公开包，对应逐图标注与来源定位清单也不公开。公开包可核查权重与汇总结果，不能独立重新训练幼果模型；来源网页可能失效。标签未进行双人一致性评估或专家复核。')
pair(['berry_aux_train_batch0.jpg','flower_train_batch0.jpg'],['图3a 辅助果粒实际训练批次','图3b 花序实际训练批次'],2.75)
note('批次图由训练器实际保存，展示缩放、拼接等数据增强。它是训练过程证据，不是独立测试结果；幼果同样存在伪标签噪声，不能据此宣称已完成专家标注。')
page('3 算法结构与设计程序')
fig('system_design.png','图4 检测 筛选及结果导出的功能关系',6.0)
p('输入图像先由用户框选单穗。大区域使用1024像素窗口和768像素步长，坐标回到原图后以NMS消除重复框。模型输入固定填充到384像素，避免单图与批量填充方式不同造成计数差异。花序分支用于定位整花序、统计小穗及保存框坐标，不自动决定疏花或疏小穗；其计数不换算成果粒数，也不与果粒去除动作相加。果粒分支才继续执行尺度筛选。')
p('第i个检测框宽高为wᵢ、hᵢ，投影尺度dᵢ=√(wᵢhᵢ)，相对尺度rᵢ=dᵢ/median(d)。当rᵢ<τ时建议去除，默认τ=0.70。它衡量二维框大小，透视与遮挡会影响判断，不能视作真实直径。')
p('若设置可见保留上限K，则在大小筛选后，从中心距离除以平均尺度最小的一对中优先去除较小者，迭代至数量不超过K。数量满足N_total=N_keep+N_remove，分别表示检测总数、保留数和建议去除数，不推算漏检或遮挡对象。每粒保存编号、位置、尺度、动作和原因供人工复查。')
rows=[['初始权重','COCO YOLOv8n','COCO YOLOv8n','辅助 best.pt']]
for label,key in [('轮次','epochs'),('输入边长 px','imgsz'),('批量','batch'),('设备','device'),('优化器','optimizer'),('初始学习率','lr0'),('冻结层数','freeze'),('随机种子','seed')]:
 rows.append([label]+[str(configs[t][key]) for t in ['berry_aux','flower','young']])
page('3.1 原始模型训练配置')
table('表4 各模型独立训练配置',['参数','辅助果粒','花序与小穗','幼果适配'],rows)
note('原训练日志记录Python 3.12.14、PyTorch 2.14.1+cpu、Ultralytics 8.4.175。依赖已固定在requirements.txt，补充的完整CPU依赖锁定文件为requirements-lock-cpu.txt。三组训练各只有一个随机种子，尚未评估训练种子变异。')
for task,title,num,detail in [
 ('berry_aux','4 辅助果粒模型训练结果',5,'该模型学习较大果粒，稠密场景仍存在漏检。验证曲线不能代替幼果性能，也不能作为独立测试结论。'),
 ('flower','4.1 花序与小穗模型训练结果',7,'整花序尺度较大，定位较容易；小穗密集且相似，定位与类别混淆更明显。spikelet指小穗，不能当作单花。'),
 ('young','4.2 幼果弱标注模型训练结果',9,'训练37张、验证仅1个区域，因此曲线波动和较高分数缺乏稳健性。验证标签未经专家复核，不能报告为普遍识别准确率。')]:
 page(title)
 fig(f'{task}_results.png',f'图{num} 实际results.csv对应的训练损失及验证指标 results.png',6.25)
 fig(f'{task}_cm_evidence.png',f'图{num+1} 同一置信度与匹配IoU下验证和测试的TP FP FN',6.1)
 p(detail)
 note('results.png来自保存的训练CSV，保留原训练器AP口径（NMS IoU=0.70，最多300框），不用于工作阈值比较。下方图按已保存预测重新匹配：IoU≥0.50，每类置信度仅由验证集选定并固定用于测试。TP为一对一正确匹配，FP为未匹配预测，FN为未检出标签；没有背景真阴性。原保存的conf=0.001、匹配IoU=0.45验证矩阵仅作过程档案，其未匹配预测数不能解释成背景标签数，也不能与工作阈值图直接比较。')
page('5 独立测试结果与计数误差')
p('预测按置信度排序，以IoU≥0.50逐框匹配，每个真实框最多匹配一次。阈值仅由验证集候选值的最高F1选定，再用于测试；P、R、F1与AP分别记录。图11仅列TP、FP、FN，不设真实背景类别或真阴性格。固定阈值F1=2TP/(2TP+FP+FN)，与AP曲线积分不是同一个量。')
fig('test_confusion.png','图11 固定阈值测试的TP FP FN及统一精度F1',6.3)
rows=[]
for name,d,key in [('辅助果粒',berry,'berry'),('整花序',flower,'inflorescence'),('小穗',flower,'spikelet'),('幼果试验',young,'berry')]:
 q=d['classes'][key]['test'];rows.append([name,str(q['images']),f"{q['threshold']:.2f}",f"{q['precision']:.3f}",f"{q['recall']:.3f}",f"{q['f1']:.4f}",f"{q['count_mae']:.2f}"])
table('表5 固定阈值测试结果',['对象','图数','阈值','P','R','F1','MAE'],rows)
fig('test_count_scatter.png','图12 测试图标签数量与预测数量 虚线为理想一致关系',6.1)
note('MAE单位：辅助果粒为粒每图块；整花序为穗每图；小穗为小穗每图；幼果为粒每区域。辅助120图块对应30原图，不能将图块MAE称为每原图或每果穗误差。幼果只有2区域，其结果仅为流程试验。')
page('5.1 PR曲线与适配对照')
fig('flower_BoxPR_curve.png','图13 花序最佳权重重跑验证PR曲线 整花序与小穗分开显示',4.4)
pair(['berry_aux_BoxPR_curve.png','young_BoxPR_curve.png'],['图14a 辅助最佳权重验证PR','图14b 幼果最佳权重验证PR'],2.45)
rows=[]
for c in review['young_common_threshold_comparison']:
 for key,label in [('baseline','辅助直接预测'),('adapted','弱标注适配')]:
  q=c[key];rows.append([label,f"{c['common_threshold']:.2f}",f"{q['f1']:.4f}",f"{q['count_mae']:.2f}"])
table('表6 同一幼果测试区域的同阈值对照',['模型','共同阈值','F1','MAE 粒每区域'],rows)
note('同阈值0.40下适配模型的MAE较小；0.50下反而更大，不能笼统声称适配全面改善。测试仅2区域且来自同一来源，标签未经专家复核，不进行总体显著性检验。原分别选阈值的比较保留在原始记录中，不作为因果改善证据。')
page('6 程序输入与实际输出')
fig('berry_input_output.png','图15 阳光玫瑰示例的输入与果粒导出 GBISC CC BY 4.0',5.1)
p('果粒命令行入口为src/predict.py，绿色框为保留，红色框为建议去除。所有数量只覆盖检测到的可见对象。多穗照片应先框选单穗，否则统计的是整个输入区域。')
fig('flower_input_output.png','图16 花序示例的输入与检测导出 Du CC BY 4.0',5.1)
p('花序入口为src/flower_predict.py，整花序与小穗计数分别输出。本页来自实际导出的annotated.jpg，展示花序分支的功能。')
page('6.1 运行记录与结构化导出')
fig('cli_run_record.png','图17 修订后实际命令行记录 ASCII双连字符参数',6.1)
fig('csv_export_preview.png','图18 实际导出记录中的保留和建议去除样例',6.1)
p('导出目录同时包含annotated.jpg、berries.csv和result.json。CSV使用UTF-8 BOM。修订schema_version为2.0，将relative_diameter改名为relative_scale；该值是相对投影尺度，不是真实直径。JSON记录ROI、模型、阈值、耗时和逐粒决策；旧版记录保留旧字段作为历史档案。图17与图18由保存的真实记录导出，属于命令行与结构化输出的运行证据。')
p('桌面入口src/app.py提供打开照片、拖框选ROI、切换模型和参数输入，推理线程异步回传结果。当前环境无法建立图形服务连接，尚未完成窗口交互验收，窗口操作仍需在目标电脑验收。已实际验证的入口是命令行。')
page('7 阈值响应与失败样例')
fig('test_error_examples.png','图19 独立测试中计数误差最大的两个辅助果粒图块 青色标签 橙色预测',6.1)
p('失败图主动选取绝对计数误差最大的测试样本，避免只展示好看的结果。密集果粒在384像素输入下目标很小，遮挡导致漏检，叶片及果梗也可能产生误检；提高小果比例阈值不会修复检测漏检。')
sens=json.loads((R/'reports/threshold_sensitivity.json').read_text())
table('表7 同一40粒演示ROI的小果比例敏感性',['比例τ','检测数','建议去除','保留'],[[f"{x['size_ratio']:.2f}",x['visible_count'],x['remove_count'],x['keep_count']] for x in sens])
p('默认0.70下建议去除15粒、保留25粒。该表只验证规则响应与数量守恒，未与农艺专家疏除选择对照，不能据此称默认比例最优。工程验收通过6项单元测试及真实照片导出、中文路径、空白图像、缺失文件、越界ROI和CSV/JSON一致性检查。')
page('7.1 选择性漏检与规则敏感性')
fig('scale_missingness_sensitivity.png','图20 删除最小框的模拟对剩余对象建议的影响',6.1)
note('在保存的40框示例上模拟删除最小的10%、20%、30%检测框，中位尺度由106.70 px增至110.02、116.72、121.71 px；剩余对象建议分别改变0、1、2个。这是检测结果上的扰动分析，不是新检测性能实验。中位数归一化也会受选择性漏检影响；分位数或空间分层需另行验证，当前建议必须由人工复查。')
page('7.2 指标不确定性与CPU性能')
rows=[]
for task,name,label in [('berry_aux','berry','辅助果粒'),('flower','inflorescence','整花序'),('flower','spikelet','小穗')]:
 q=review['models'][task]['classes'][name]['conditional_group_bootstrap'];a=q['f1_percentile_95'];b=q['mae_percentile_95']
 rows.append([label,q['groups'],f'{a[0]:.4f} 至 {a[1]:.4f}',f'{b[0]:.2f} 至 {b[1]:.2f}'])
table('表8 按编号组重采样的条件百分位区间',['对象','组数','F1 95%区间','MAE 95%区间'],rows)
note('重采样10000次，随机种子20261012；辅助按连续5张原图组，花序按编号整除10组。区间以标签和当前模型为条件，并假设编号组独立；来源缺少植株身份，不能据此证明场景独立。重采样不能替代多种子重训，也不覆盖标注偏差。幼果只有两个同来源区域，不给出具有总体解释的置信区间。')
ap=json.loads((R/'reports/review_test_AP.json').read_text())
rows=[]
for task in ['berry_aux','flower']:
 for name,q in ap[task]['class_AP'].items():rows.append([task+' '+name,f"{q['AP50']:.4f}",f"{q['AP50_95']:.4f}"])
rows.append(['幼果 流程试验',f"{young['test_AP']['metrics/mAP50(B)']:.4f}",f"{young['test_AP']['metrics/mAP50-95(B)']:.4f}"])
table('表9 独立测试AP与固定阈值指标分开报告',['对象','AP50','AP50至95'],rows)
note('辅助及花序AP已以原权重重新验证；幼果AP引用保存的原始评测，未重新取得图片。AP50匹配IoU为0.50；AP50至95为IoU 0.50至0.95步长0.05的平均。AP评测候选置信度下限0.001、NMS IoU 0.50，不能把该下限称作固定工作阈值。')
page('7.3 运行测量和导出字段')
rows=[]
for q in cpu['tasks']:
 rows.append([q['model'],q['batch'],f"{q['mean_per_image_seconds']*1000:.2f}",f"{q['throughput_images_per_second']:.1f}",f"{q['process_peak_rss_mib']:.1f}"])
table('表10 当前CPU预热推理测量',['模型','批量','ms每图','图每秒','峰值RSS MiB'],rows)
note('硬件为'+cpu['cpu']+'，固定8线程、384像素方形填充。预热3次后测20次；同一已解码许可图重复输入，包含预处理、前向与NMS，不包含模型加载、磁盘读取、ROI切窗和结果导出。吞吐量不是交互界面的端到端FPS，峰值RSS为进程累计峰值，不是独立模型内存。原训练硬件为AMD EPYC 9V74，不能与当前测量混同。原始时间序列与标准差见reports/cpu_benchmark.json。')
table('表11 CSV及JSON逐粒字段',['字段','含义和取值'],[['id','当前结果内从1开始的编号 对应编号图 不保证跨图一致'],['box','原图像素坐标 x1 y1 x2 y2'],['confidence','检测置信度 0至1 不表示农艺正确概率'],['relative_scale','sqrt(框面积)除以当前检测框尺度中位数 无量纲'],['action','keep 保留 或 remove 建议去除'],['reason','keep 未触发规则 relative_small 低于尺度阈值 crowding_target 因可见上限去除']])
note('只有设置visible_target时才使用crowding_target；花序分支仅输出定位与类别计数，不输出果粒去除动作。8项单元测试通过；新版CLI实测39个检测对象，建议去除12、保留27，字段与编号图可对应。')
page('8 结论与交付复现')
p('本设计完成三组实际训练及可见目标识别、相对大小筛选、可调上限和结构化导出。训练数据、曲线、混淆矩阵与失败案例均保留来源路径，便于检查“样本—训练—验证—测试—程序输出”的对应关系。当前可作为课程算法原型，尚无整穗隐藏粒数、田间疏除正确率或机械剪切精度的证据。')
p('后续应优先扩大跨果园、跨光照的独立幼果样本，并由双人或专家复核标签，再考虑实例分割与果梗朝向。继续追求更高小样本分数不足以消除上述限制。')
table('表12 交付包可直接查找的材料',['目录','内容'],[['data/berry_yolo images labels','实际辅助果粒训练360 验证120 测试120图块'],['data/flower_yolo images labels','实际花序训练369 验证75 测试79原图'],['幼果模型与汇总记录','公开包不包含幼果原图及逐图标注 无法仅依公开包重训'],['runs 各模型目录','best last权重 results.csv results.png 矩阵 PR'],['docs figures','论文图及图像来源证据索引'],['src scripts tests reports','程序 复现脚本 单元测试 实际评测与日志']])
p('完整包解压后先按使用说明安装依赖，再运行提供的两张有许可的示例；模型已训练，无需重训才能识别。幼果网络来源可能失效，公开包也不包含对应原图和逐图标注，其复现只能核查汇总记录及已训练权重。更换路径后运行scripts/relink_datasets.py。未完成双人或专家复核、田间验证、多随机种子重训和桌面窗口交互验收。')
page('参考文献')
refs=[
'[1] YANG C, GENG T, PENG J, et al. Mask-GK An efficient method based on mask Gaussian kernel for segmentation and counting of grape berries in field[J]. Computers and Electronics in Agriculture, 2025, 234:110286. DOI:10.1016/j.compag.2025.110286.',
'[2] DU W, QIN W, CUI X, et al. A precise berry counting method for in-cluster grapes to guide berry thinning[J]. Frontiers in Plant Science, 2026,16:1739688. DOI:10.3389/fpls.2025.1739688. 本设计未取得其完整779张数据.',
'[3] ULTRALYTICS. Explore Ultralytics YOLOv8[EB/OL]. https://docs.ultralytics.com/models/yolov8. 访问日期2026-10-10.',
'[4] 上海市人民政府新闻办公室. 精品果按串销售每串售价100元 马陆葡萄品牌价值再创新高[EB/OL]. https://www.shio.gov.cn/TrueCMS/shxwbgs/ywts/content/94f32927-3c25-4f87-82c2-1cf6438d6cc2.htm. 访问日期2026-10-10.',
'[5] やくも果樹研究所. シャインマスカット栽培 摘房 摘粒 1回目[EB/OL]. https://kaju-fruits.com/シャインマスカット　粗摘房・粗摘粒/. 访问日期2026-10-10.',
'[6] DU W. Grape inflorescence dataset[DB/OL]. Mendeley Data,2022,V1. DOI:10.17632/skwbr5k9gg.1. CC BY 4.0.',
'[7] Tom. シャインマスカットのジベレリン処理後の予備摘粒[EB/OL]. https://tomtom1ono.hatenablog.com/entry/2026/06/19/225730. 2026-06-19.',
'[8] Grapetopia. 粒間引き 摘粒 荒間引き[EB/OL]. https://grapetopia.hatenablog.com/entry/2020/06/06/222016. 2020-06-06.',
'[9] DOMINGOS S, SCAFIDI P, CARDOSO V, et al. Flower abscission in Vitis vinifera L. triggered by gibberellic acid and shade discloses differences in the underlying metabolic pathways[J]. Frontiers in Plant Science, 2015,6:457. DOI:10.3389/fpls.2015.00457.'
]
for text in refs:
 a=D.add_paragraph(text);a.paragraph_format.first_line_indent=Pt(0);a.paragraph_format.line_spacing=Pt(13)
 for run in a.runs:run.font.size=Pt(8.5)
md+=refs
D.core_properties.author='';D.core_properties.last_modified_by='';D.core_properties.title='葡萄可见果粒检测与尺度筛选算法原型设计';D.core_properties.subject='生物生产机器人设计课程论文';D.core_properties.comments=''
import tempfile,shutil
with tempfile.TemporaryDirectory() as temporary:
 staged=Path(temporary)/'paper.docx';D.save(staged);shutil.copyfile(staged,O/'课程设计论文.docx')
(O/'论文正文.md').write_text('\n\n'.join(md),encoding='utf-8');print('saved characters',len('\n'.join(md)),'figures',len(D.inline_shapes))
