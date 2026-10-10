"""Build public archives from an explicit allow-list; never include private photos."""
from pathlib import Path
import hashlib
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT.parent

def permitted(p):
    rel = p.relative_to(ROOT)
    if '__pycache__' in rel.parts or p.suffix == '.pyc':
        return False
    top = rel.parts[0]
    if top in {'src', 'scripts', 'tests', 'annotations', 'reports', 'examples', 'models'}:
        return True
    if top == 'docs':
        return len(rel.parts) == 2 or rel.parts[1] == 'figures'
    if top == 'outputs':
        return 'young' not in rel.parts[1] or p.suffix in {'.json', '.csv'}
    if top == 'runs':
        return p.suffix in {'.pt', '.csv', '.yaml', '.png'}
    return len(rel.parts) == 1 and p.name in {
        'README.md', 'RECOVERY.md', 'DATA_SOURCES.md', 'LICENSE',
        'requirements.txt', 'requirements-report.txt', '.gitignore'}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

if __name__ == '__main__':
    # Coordinates and pseudo-labels are public; the corresponding RGB photos are not.
    labels = ROOT / 'data/young_yolo/labels'
    if labels.exists():
        shutil.copytree(labels, ROOT / 'annotations/young_yolo_labels', dirs_exist_ok=True)
    files = sorted(p for p in ROOT.rglob('*') if p.is_file() and permitted(p))
    manifest = ROOT / 'SHA256SUMS.txt'
    manifest.write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files), encoding='utf-8')
    files.append(manifest)
    for name, source_only in [('grape-thinning-delivery.zip', False), ('source-code.zip', True)]:
        with zipfile.ZipFile(DEST / name, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            for p in files:
                if source_only and (p.suffix == '.pt' or p.relative_to(ROOT).parts[0] == 'models'):
                    continue
                z.write(p, 'grape-thinning-vision/' + p.relative_to(ROOT).as_posix())
    checks = [DEST / 'grape-thinning-delivery.zip', DEST / 'source-code.zip',
              ROOT / 'docs/课程设计论文.docx', ROOT / 'docs/课程设计论文.pdf']
    (DEST / 'DELIVERY_SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in checks), encoding='utf-8')
    print('\n'.join(f'{p.name}: {p.stat().st_size} bytes, {digest(p)}' for p in checks))
