"""Private recovery of the actual young-fruit inputs; never a public release asset."""
from pathlib import Path
import zipfile,json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    temp=Path('/tmp/young-training-private-complete.zip')
    manifest=json.loads((ROOT/'reports/young_manifest.json').read_text())
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT/'data/young_yolo').rglob('*')):
            if p.is_file() and p.suffix in {'.jpg','.txt','.yaml'}:z.write(p,p.relative_to(ROOT))
        for m in manifest:
            p=ROOT/'data/young_candidates'/m['file'];z.write(p,p.relative_to(ROOT))
        for rel in ['reports/young_manifest.json','reports/young_source_candidates.json','annotations/young_review.json','docs/数据交付索引.md','DATA_SOURCES.md','scripts/relink_datasets.py']:
            z.write(ROOT/rel,rel)
        z.writestr('README-private.txt','私人幼果样本附件：40个实际输入和原始来源照片。按data目录合并到公开交付包。37训练图为弱标注；1验证和2测试区域为AI视觉辅助标签。未经专家复核，未获明确公开再分发许可，请勿上传公开仓库。')
    with zipfile.ZipFile(temp) as z:assert z.testzip() is None
    dest=ROOT.parent/'young-training-private-complete.zip';shutil.copyfile(temp,dest)
    print(dest,dest.stat().st_size,hashlib.sha256(dest.read_bytes()).hexdigest())
