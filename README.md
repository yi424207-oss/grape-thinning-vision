# 葡萄疏果识别图像处理算法

《生物生产机器人设计》选题3课程原型。提供设计源码、已训练权重、可编辑论文与PDF、实际日志、评测、数据审计及复现步骤。姓名学号等个人字段留空。

## 新版材料与样本位置

新版论文有19组图，含实际训练样本、批次、三组results.png、验证和测试矩阵、PR曲线、导出与失败案例。完整交付包直接包含1123张许可图片及标签，其中训练侧729张；幼果40个实际输入另作私人附件，见docs/数据交付索引.md。

## 当前交付状态

命令行识别、单穗ROI、相对大小阈值、可见保留上限、编号图和CSV/JSON导出已实际运行。三组模型实际完成25轮CPU训练。6项单元测试与端到端导出检查通过。桌面界面源码已完成，但受当前环境图形连接限制，只验证了导入和语法，尚未完成窗口交互验收。

幼果训练使用37张真实疏果期照片的1571个伪标签；外部验证1个区域、测试2个区域78个AI视觉辅助检查框，未经专家复核。这是小规模探索试验，不能声称已达到田间应用水平。大果粒结果与幼果结果分开。

| 任务 | 测试规模 | 固定阈值F1 | 计数MAE |
| --- | --- | --- | --- |
| 辅助果粒 | 30原图的120图块 | 0.7467 | 21.72粒/图块 |
| 花序与小穗 | 79图 | 见分类评测 | 见分类评测 |
| 幼果试验 | 2图 78框 | 0.8800 | 3.00粒/区域 |

## 下载与运行

下载本仓库后，按 [第二版下载说明](downloads/v02/README.md) 合并分卷，得到 **grape-thinning-delivery-v02.zip** 并解压。此包是可运行课程原型，保留了上述验证范围和不足。若只下载仓库源码压缩包，请另下载模型交付附件。

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python src/predict.py examples/berry_demo_input.jpg --weights runs/berry_aux/weights/best.pt --output outputs/demo --confidence 0.30 --ratio 0.70
python src/flower_predict.py examples/flower_demo_input.jpg --weights runs/flower/weights/best.pt --output outputs/flower
python src/app.py
```

激活虚拟环境后再安装。CPU torch/torchvision 使用官方索引 https://download.pytorch.org/whl/cpu 。详细安装、ROI、幼果模型和复现方法见 docs/使用说明.md。

## 文件索引

- src/：设计程序，检测与相对尺度/拥挤筛选。
- scripts/：采集、数据准备、训练、评价、去重和文档生成。
- docs/：论文DOCX、PDF、正文和使用说明。
- runs/：三组 best.pt、last.pt、训练CSV和配置。
- reports/：真实评测JSON、日志、数据审计、验收记录。
- examples/ 与 outputs/：有许可的演示输入与实际输出。
- annotations/：幼果外部评价坐标与方法说明。
- DATA_SOURCES.md 与 LICENSE：来源署名、数据范围和许可。

source-code-v02.zip 保存带目录的设计源码、文本说明与评测记录；图片、论文DOCX/PDF、数据和模型在完整交付包中。设计程序，源码也按目录直接放入仓库。第二版模型和完整过程档案在 downloads/v02 分卷中；旧版 Release 保留历史检查点。

## 农艺与评价边界

默认相对尺度0.70是工程启发式参数，未经专家疏果选择验证。输出仅为检测到的可见果粒，隐藏果粒不推算；不能把45–50粒整穗指标直接填作照片可见目标。花序中的 spikelet 是小穗，不能当单花或果粒。幼果训练标签是伪标签，外部框是AI辅助检查框；禁止把小样本F1写成普遍识别准确率。

网络幼果照片未明确许可再分发，公开包保留来源与下载脚本，原件另作私人恢复档案。CC BY 4.0 原始花序/GBISC附件位于checkpoint-001 Release，署名见DATA_SOURCES.md。

本项目代码与YOLO模型按AGPL-3.0发布。所有实验结论以本仓库实际日志为依据，未使用生成图像冒充训练照片。
