# 第二版公开材料恢复索引

第二版完整包发布位置：downloads/v02。进入该目录，运行 python assemble_delivery.py，逐卷校验并生成 grape-thinning-delivery-v02.zip，然后解压。完整包包括代码、论文、三组模型权重、训练日志、1123张许可图片及标签、评测和审计记录。

旧版 Release 保留早期开发检查点。若早期统计或评测与第二版不一致，以第二版和纠正记录为准。原始 CC BY 数据在 checkpoint-001 Release 的 flower-original-ccby4.zip 与 gbisc-original-ccby4.zip；署名和许可见 DATA_SOURCES.md。

移动项目后运行 python scripts/relink_datasets.py 更新数据路径。未获明确再分发许可的照片不在公开交付包内，因此不能仅靠本公开包重现幼果训练；已训练幼果权重、日志及标注方法记录仍可检查。辅助果粒和花序的实际图片、标签可直接检查和复用。

已完成：三组25轮训练、分组与重复审计、统一填充后的评测、幼果适配前后对照、CLI端到端测试、论文排版和源代码。限制：GUI窗口交互尚未实测；无田间疏除真值；幼果独立场景很少，训练标签为伪标签，外部框未经专家复核。
