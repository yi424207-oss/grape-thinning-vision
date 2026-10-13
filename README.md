# 葡萄疏果识别图像处理算法

《生物生产机器人设计》选题3课程原型。提供设计源码、已训练权重、可编辑论文与PDF、实际日志、评测、数据审计及复现步骤。姓名学号等个人字段留空。

## 新版材料与样本位置

第三版论文有21组图，含实际训练样本、批次、三组results.png、同口径验证和测试TP/FP/FN、PR曲线、导出与失败案例。完整交付包直接包含1123张许可图片及标签，其中训练侧729张；幼果40个实际输入未获明确再分发许可，不在公开包中，见docs/数据交付索引.md。

## 当前交付状态

命令行识别、单穗ROI、相对大小阈值、可见保留上限、编号图和CSV/JSON导出已实际运行。三组主实验各完成25轮CPU训练，本轮另完成每模型3种子共9次25轮重训。8项单元测试和两组实际CLI导出检查通过。桌面界面源码已完成，但受当前环境图形连接限制，只验证了导入和语法，尚未完成窗口交互验收。

幼果训练使用37张真实疏果期照片的1571个伪标签；外部验证1个区域、测试2个区域78个AI视觉辅助检查框，未经专家复核。这是小规模探索试验，不能声称已达到田间应用水平。大果粒结果与幼果结果分开。

| 任务 | 测试规模 | 固定阈值F1 | 计数MAE |
| --- | --- | --- | --- |
| 辅助果粒 | 30原图的120图块 | 0.7467 | 21.72粒/图块 |
| 花序与小穗 | 79图 | 见分类评测 | 见分类评测 |
| 幼果试验 | 2图 78框 | 0.8800 | 3.00粒/区域 |

## 下载与运行

优先从 [第三版 Release](https://github.com/yi424207-oss/grape-thinning-vision/releases/tag/v0.3.1-writing) 下载 **grape-thinning-delivery-v031.zip**，直接解压即可。完整包包含代码、原模型、9次重复训练权重与记录、1123张许可图片及标签、更新论文和所有过程证据。独立附件提供Word、PDF、源码、图表与实验记录，以及重复训练档案。downloads/v02与旧Release仅作历史备份，不用于当前版本运行。

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
- 完整包内 runs/：三组 best.pt、last.pt、训练CSV和配置。
- reports/：真实评测JSON、日志、数据审计、验收记录。
- examples/ 与 outputs/：有许可的演示输入与实际输出。
- PUBLIC_PACKAGE_SCOPE.md：公开包包含的材料及复现限制。
- DATA_SOURCES.md 与 LICENSE：来源署名、数据范围和许可。

设计源码、文本说明与评测记录按目录保存在仓库；完整包同时包含图片、论文DOCX/PDF、数据和模型。根目录source-code.zip和downloads/v02是历史版本；第三版运行请使用v0.3.1-writing完整包。

## 农艺与评价边界

默认相对尺度0.70是工程启发式参数，未经专家疏果选择验证。输出仅为检测到的可见果粒，隐藏果粒不推算；不能把45–50粒整穗指标直接填作照片可见目标。花序中的 spikelet 是小穗，不能当单花或果粒。幼果训练标签是伪标签，外部框是AI辅助检查框；禁止把小样本F1写成普遍识别准确率。

网络幼果照片未明确许可再分发；公开包不包含这些照片、对应逐图标注和来源定位清单，也不包含相关备份恢复脚本。仅靠公开包无法重新训练幼果模型，但可检查保存的权重与统计结果。CC BY 4.0 原始花序/GBISC附件位于checkpoint-001 Release，署名见DATA_SOURCES.md。

本项目代码与YOLO模型按AGPL-3.0发布。所有实验结论以本仓库实际日志为依据，未使用生成图像冒充训练照片。

## 审阅修订与验证

[逐项核对与修订记录](docs/审阅意见核对与修订.md)区分真实问题和误读：原F1为0.746668，统一显示0.7467；原表“33”是保留数，去除数本来就是单调的3、7、15、17、19。

新增统一匹配IoU=0.50的TP/FP/FN图、同阈值适配比较、三品种分布、按编号组bootstrap条件区间、三种子复验、漏检扰动和CPU实测。原主实验保持独立，未用新种子较高分数覆盖原值。幼果样本量没有因重复训练而增加；专家复核、田间真值及GUI交互验收仍未完成。

- [可编辑论文正文](docs/论文正文.md)与[PDF](docs/课程设计论文.pdf)
- [当前Word分卷](docs/editable-paper-v031)
- [论文图表](docs/figures)与[来源索引](reports/figure_evidence_index.json)
- [重复训练原始结果](reports/seed_repeats.json)
- [同口径复评与条件区间](reports/review_statistics.json)
- [CPU原始计时](reports/cpu_benchmark.json)
- [第三版下载说明](RELEASE_DOWNLOAD.md)

## 文字与结构修订

v0.3.1-writing按文字审阅建议压缩重复说明，补充实施条件下的设计取舍，幼果移出主结果表，强化结论的研究优先级。实验数值、模型与配图未修改。逐项评判见[修订记录](docs/文字审阅意见评判与修订.md)。
