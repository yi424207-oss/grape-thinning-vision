# 数据来源与署名

## 公开原始数据

1. Wensheng Du. Grape inflorescence dataset, Mendeley Data, V1, 2022. DOI https://doi.org/10.17632/skwbr5k9gg.1 ，CC BY 4.0（https://creativecommons.org/licenses/by/4.0/）。原件附件仅重命名。处理包括去重、原图分组、缩放和YOLO标签整理。523个独立原始命名文件；整花序和小穗两个类别。567是含44份完全相同重复的文件条目数。下载包还含增强图片，未计入独立训练样本。
2. Canchen Yang, Tianyu Geng, Jian Peng, Chun Xu, Zichen Song. Mask-GK: An efficient method based on mask Gaussian kernel for segmentation and counting of grape berries in field. Computers and Electronics in Agriculture 234 (2025), 110286. DOI https://doi.org/10.1016/j.compag.2025.110286 。GBISC 数据与许可见 https://github.com/volcanoYcc/Mask-GK ，数据 CC BY 4.0，原项目代码 MIT。GBISC 150张原图，巨峰、阳光玫瑰、夏黑各50张。处理为COCO框统一类别、分组拆分、四块裁剪与缩放，边界可见面积小于65%者不计入块标签。

本项目示例 examples/berry_demo_input.jpg 是 GBISC ShineMuscat_5.jpg 的 ROI 裁剪；examples/flower_demo_input.jpg 是花序数据 IMG_1964.jpg 的缩放图。docs/figures/public_examples.png 由以上许可数据的程序检测结果形成，包含框、编号和裁剪。请继续保留上述署名与变更说明。

## 幼果候选网络实拍

候选地址见 reports/young_source_candidates.json，筛选与划分见 reports/young_manifest.json。37张训练图来自阳光玫瑰疏果记录，训练标签由辅助模型生成。验证1个区域来自やくも果树研究所，测试2个区域来自Grapetopia的阳光玫瑰图。其他品种、成熟成品、药瓶、广告、损坏图像未当作幼果训练样本。

- https://tomtom1ono.hatenablog.com/entry/2025/06/24/222657
- https://tomtom1ono.hatenablog.com/entry/2026/06/25/205921
- https://tomtom1ono.hatenablog.com/entry/2026/06/19/225730
- https://kaju-fruits.com/シャインマスカット　粗摘房・粗摘粒/
- https://grapetopia.hatenablog.com/entry/2020/06/06/222016

这些原图没有明确的公开再分发许可，公开仓库不放原图、带原图的标注预览或幼果示例照片。原件保存为私人恢复档案。下载脚本记录失败和图像损坏，不保证第三方链接永久有效。评测坐标由AI视觉辅助检查形成，不是农业专家标注，也不是田间实测真值。annotations/young_review.json说明方法与ROI；AI辅助导致的标注不确定性需要再次人工复核。

## 模型与代码

Ultralytics YOLOv8 使用 AGPL-3.0，本项目代码和提供的模型按 AGPL-3.0 发布，见 LICENSE。官方 COCO 预训练权重来自 Ultralytics，不冒称为从零训练。Mask-GK、AS-SwinT、MVDNet 作为参考；本设计未取得 MVDNet 完整779张原始数据，也未运行其作者完整模型，不借用其结果作为本项目指标。
