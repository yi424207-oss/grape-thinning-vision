# 中断后恢复工作

更新：2026-10-10，检查点 001。

## 任务约束

完成课程第3题“葡萄疏果识别图像处理算法”：明确农艺；小果识别；去除阈值；留下的果粒数；品种阳光玫瑰/巨峰；搜集花、小果照片。论文至少1500字，有意义、现状、目标、设计、图表、参考文献。姓名学号留空。用户已授权公开GitHub发布；不发送邮件、不透露私人信息。不可伪造测试、数据阶段或田间采集。

## 环境

Linux CPU，9逻辑核，无GPU。Python3.11；训练运行用 `PYTHONPATH=/tmp/grape_ml`。可迁移机器安装 `requirements.txt`，不依赖该临时路径。

当前源码目录名 `grape_thinning`。运行：

```bash
python scripts/prepare_data.py
python scripts/train.py
```

训练输出 `runs/berry_aux/`；`weights/last.pt` 可用 Ultralytics `YOLO(path).train(resume=True)` 续训。若检查点未包含 last.pt，说明创建快照时还没产生；可从已归档官方 yolov8n.pt 重跑。先查看 reports/training.log、runs/berry_aux/results.csv，不要假设完成。

## 数据还原

1. 花序 Mendeley： https://data.mendeley.com/datasets/skwbr5k9gg/1 ，Download all；外层压缩包内还有 `grape inflorescence dataset.zip`。解压到 `data/flower_original/grape inflorescence dataset/`。
2. GBISC： https://drive.google.com/file/d/12uQKaTwmN2bCmxDNfjvCWAdFuz8W-qPd/view ，解压到 `data/gbisc_original/`，直接包含 images、annotations_COCO_train.json、annotations_COCO_val.json、annotations_COCO_test.json。
3. GBISC COCO train 类别1而val/test类别0，脚本统一为berry0。去除裁剪后可见面积不足65%的跨边界框，报告必须说明这个局限。
4. 原始花序只取 `IMG_*.jpg` 共567张；大写JPG数字命名820张为已有增强，应排除以避免泄漏。原始类0共676框、类1共11440框，需叠加检查语义，疑似整花序/小穗，不能冒充单朵花或果粒。

## 接下来按顺序完成

- [ ] 训练结束检查曲线、记录真实时长与环境；不要提前查看测试集调参。
- [ ] 按图像感知哈希及接触表审计近重复，必要时重新分组和训练。
- [ ] 补充真正幼果图像并标注，保留来源、许可、标注方式和独立来源测试。GBISC是辅助果粒数据，不足以证明疏果期适用。
- [ ] 花序分支训练或阶段辅助识别，确认标签语义。
- [ ] 程序：单穗ROI、模型推理、相对尺寸/拥挤阈值、去除理由、可见保留计数、CSV/JSON/标注图、可使用界面。
- [ ] OpenCV基线与模型比较；验证集选择阈值，独立测试给P/R/AP及计数MAE/RMSE；失败案例。
- [ ] 有意义的边界测试、真实图像端到端测试，保存命令和输出。
- [ ] 论文DOCX/PDF，实际渲染检查；README、运行指南、数据授权、复现实验、答辩要点。
- [ ] 每个阶段GitHub提交或Release归档；大数据与模型另存分卷，记录SHA256。不要把未经授权网站照片公开再分发。

## 已找到但无可直接用完整幼果数据的来源

- AS-SwinT: https://github.com/AWEN975/AS-SwinT ，代码zip无数据；论文 DOI10.34133/plantphenomics.0085，公开附图/补充材料可检查。
- MVDNet: https://github.com/AWEN975/MVDNet_code ，代码无数据；论文 https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2025.1739688/full ，779张2021年5月阳光玫瑰幼果，完整数据须向作者申请，尚未获得。可合法检查CC BY附图；勿当已获取779张。
- GrapeSAM: https://github.com/tong-xz/GrapeSAM ，ViViD-5K可继续检查阶段/品种与下载权限。
- 日本种植日志 young fruit 示例： https://tomtom1ono.hatenablog.com/entry/2025/06/24/222657 、 https://grapetopia.hatenablog.com/entry/2020/06/10/210438 。未下载未标注，版权待查。

## 农艺来源

上海马陆标准： https://www.shio.gov.cn/TrueCMS/shxwbgs/ywts/content/94f32927-3c25-4f87-82c2-1cf6438d6cc2.htm ，阳光玫瑰45–50粒/穗。需结合拍摄覆盖说明，不能直接约束单面可见数量。阈值例如0.7倍中位等效直径只能称工程启发式。

## 工作记录原则

如实记载失败、修改原因和限制，以实际工作细节让论文自然。不要伪造“人工采集”“专家标注”或成熟度、试验次数、精度。下载公开代码不等于该论文实验已经复现。
