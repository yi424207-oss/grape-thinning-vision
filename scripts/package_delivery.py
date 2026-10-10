"""Build public archives from an explicit allow-list; never include private photos."""
from pathlib import Path
import hashlib
import shutil
import zipfile
import json
import io
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT.parent

def permitted(p):
    rel = p.relative_to(ROOT)
    if '__pycache__' in rel.parts or p.suffix == '.pyc':
        return False
    top = rel.parts[0]
    if top == 'data':
        return len(rel.parts) > 2 and rel.parts[1] in {'berry_yolo', 'flower_yolo'} and p.suffix in {'.jpg', '.txt', '.yaml'}
    if top in {'src', 'scripts', 'tests', 'annotations', 'reports', 'examples', 'models'}:
        return True
    if top == 'docs':
        return len(rel.parts) == 2 or rel.parts[1] == 'figures'
    if top == 'outputs':
        return 'young' not in rel.parts[1] or p.suffix in {'.json', '.csv'}
    if top == 'runs':
        return p.suffix in {'.pt', '.csv', '.yaml', '.png'} or (len(rel.parts)>1 and rel.parts[1] in {'berry_aux','flower'} and p.suffix=='.jpg')
    return len(rel.parts) == 1 and p.name in {
        'README.md', 'RECOVERY.md', 'DATA_SOURCES.md', 'LICENSE',
        'requirements.txt', 'requirements-report.txt', '.gitignore'}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

if __name__ == '__main__':
    labels = ROOT / 'data/young_yolo/labels'
    if labels.exists():
        shutil.copytree(labels, ROOT / 'annotations/young_yolo_labels', dirs_exist_ok=True)
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and permitted(p))
    counts = {}
    for task in ['berry_yolo', 'flower_yolo', 'young_yolo']:
        counts[task] = {}
        for split in ['train', 'val', 'test']:
            images = sorted((ROOT/'data'/task/'images'/split).glob('*.jpg'))
            for im in images:
                with Image.open(im) as pic: pic.load()
                assert (ROOT/'data'/task/'labels'/split/(im.stem+'.txt')).is_file(), im
            counts[task][split] = len(images)
    assert counts == {'berry_yolo': {'train':360,'val':120,'test':120}, 'flower_yolo':{'train':369,'val':75,'test':79}, 'young_yolo':{'train':37,'val':1,'test':2}}
    for p in files:
        if p.suffix.lower() in {'.png','.jpg'}:
            with Image.open(p) as im: im.load()
    check = ROOT/'reports/delivery_v02_validation.json'
    check.write_text(json.dumps({'dataset_images_fully_decoded':counts, 'public_images':1123, 'public_training_images':729, 'private_young_images':40, 'label_pairing':'passed', 'public_rgb_allowlist':['berry_yolo','flower_yolo'], 'paper_figure_groups':19, 'paper_image_objects':21, 'gui_runtime':'not verified; actual CLI records supplied'},ensure_ascii=False,indent=2))
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and permitted(p))
    full_manifest = ''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files)
    (ROOT/'SHA256SUMS.txt').write_text(full_manifest)
    checks = []
    for name, source_only in [('grape-thinning-delivery-v02.zip', False), ('source-code-v02.zip', True)]:
        selected = [p for p in files if not source_only or (p.relative_to(ROOT).parts[0] not in {'models','data','runs'} and not (p.relative_to(ROOT).parts[0]=='docs' and (p.suffix in {'.docx','.pdf'} or 'figures' in p.relative_to(ROOT).parts)))]
        tmp = Path('/tmp')/name
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for p in selected: z.write(p, 'grape-thinning-vision/'+p.relative_to(ROOT).as_posix())
            z.writestr('grape-thinning-vision/SHA256SUMS.txt', ''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in selected))
        with zipfile.ZipFile(tmp) as z:
            assert z.testzip() is None
            for p in selected:
                payload=z.read('grape-thinning-vision/'+p.relative_to(ROOT).as_posix())
                assert hashlib.sha256(payload).hexdigest()==digest(p)
        dest=DEST/name
        shutil.copyfile(tmp,dest)
        assert digest(dest)==digest(tmp)
        checks.append(dest)
    for original,name in [('课程设计论文.docx','course-paper-v02.docx'),('课程设计论文.pdf','course-paper-v02.pdf')]:
        dest=DEST/name; shutil.copyfile(ROOT/'docs'/original,dest);checks.append(dest)
    (DEST/'V02_SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in checks))
    print('All archive CRC and entry SHA-256 checks passed')
    print('\n'.join(f'{p.name}: {p.stat().st_size} bytes, {digest(p)}' for p in checks))
