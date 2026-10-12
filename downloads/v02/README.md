> **新版下载入口：[v0.2.0-visual](https://github.com/yi424207-oss/grape-thinning-vision/releases/tag/v0.2.0-visual)。优先下载 Release 中的完整 ZIP，无需合并分卷。以下分卷保留为原始备份；Release 附件同步了较新的文字说明，其校验值请使用 Release 的 RELEASE_SHA256SUMS.txt。**

# 第二版完整交付包

完整包共 269,087,545 字节，包含设计程序、三组模型权重、训练与评价日志、论文 DOCX/PDF、结果图，以及 1123 张有公开再分发许可的实际数据图片和配套标签。训练划分共 729 张。未获得明确再分发许可的私人幼果照片不在公开包内。

## 下载与解压

1. 在仓库首页选择 **Code → Download ZIP**，解压仓库下载包。
2. 进入 `downloads/v02`，保留所有 `.partNNN` 文件、`manifest.json` 和合并脚本。
3. 在此目录运行 `python assemble_delivery.py`（Windows 也可以运行 `py assemble_delivery.py`）。只需要 Python 3.9 或更新版本，不需要第三方依赖。
4. 脚本会逐卷核验 SHA-256，合并生成 `grape-thinning-delivery-v02.zip`。解压它后，进入里面的 `grape-thinning-vision` 目录，按 `docs/使用说明.md` 安装运行。
5. 运行 `python scripts/relink_datasets.py` 更新数据路径。

也可以使用 `git clone` 下载仓库。不能把某一个分卷单独当作 ZIP 解压；全部分卷缺一不可。分卷为原始 ZIP 的连续字节，未改变其中的任何文件。

## 样本和证据的位置

- `data/berry_yolo/images/{train,val,test}`：360 / 120 / 120 张辅助果粒图块。
- `data/flower_yolo/images/{train,val,test}`：369 / 75 / 79 张花序照片。
- 同级 `labels` 目录：逐图 YOLO 标签。
- `runs`：训练曲线、`results.png`、权重和日志。
- `docs/figures`：论文图；`reports/figure_evidence_index.json`：图的来源记录。
- `docs/课程设计论文.docx`、`docs/课程设计论文.pdf`：15 页、19 组图的第二版论文。

原始完整包保留生成时的文档。包内提及新版 Release 的下载位置，以本页为准：本次第二版通过仓库分卷发布，旧版 Release 不代表第二版。

完整包 SHA-256：`b1e358184b8537b9e4f1db3c49b549c8b406c0813ccbdac6d66ee042320092b4`。每卷的校验值见 `manifest.json`。

公开包移除了幼果逐图标注、来源定位清单和相关备份恢复脚本。幼果模型的重新训练需要另备合法数据。
