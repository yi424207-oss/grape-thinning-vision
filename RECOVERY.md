# 第三版恢复与留档

当前完整交付由v0.3.0-review Release的grape-thinning-delivery-v03.zip恢复，直接解压。代码、论文、评测与过程文字保存在main；v03-review分支保留审阅修订检查点。辅助果粒三种子中间档案与最终九次训练档案均保留于同一Release。

每次重复训练的runs/repeats目录保存best.pt、last.pt、args.yaml和25轮results.csv，统计见reports/seed_repeats.json。移位后运行python scripts/relink_datasets.py，再按docs/使用说明.md运行。

旧v0.2.0-visual、downloads/v02与早期Release保留原始过程。原始CC BY 4.0花序与GBISC附件仍在checkpoint-001 Release。

幼果输入及标注未取得明确再分发许可，保持非公开。专家复核、田间验证及桌面窗口交互验收尚未完成。
