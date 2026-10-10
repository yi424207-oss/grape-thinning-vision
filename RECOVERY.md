# 恢复索引

优先使用最新 grape-thinning-delivery.zip，可直接恢复代码、论文、3组权重、日志和审计。旧 checkpoint-001 → 002 → 003 按顺序覆盖；其早期统计与评测如与最终包冲突，以最终包和纠正记录为准。

原始CC BY数据在checkpoint-001 Release的flower-original-ccby4.zip、gbisc-original-ccby4.zip。移动项目后重跑prepare_data.py与prepare_flower.py，更新绝对数据路径。

幼果原件私人备份文件名young_photo_private_checkpoint.zip；公开reports/young_source_candidates.json及recover_young_photos.py可重新获取。训练37张、伪标签1571；验证1区36框、测试2区78框，AI视觉辅助标签需专家复核。不得把网络候选99文件当有效幼果训练数。

已完成：三组25轮训练、分组与重复审计、统一填充后的评测、幼果适配前后对照、CLI端到端测试、论文排版和源代码。保留的限制：GUI事件循环未经当前环境实际运行；无田间疏除真值，幼果独立场景很少。下一步若继续提高质量，应优先扩大独立幼果专家标注集并在目标电脑验收GUI。
