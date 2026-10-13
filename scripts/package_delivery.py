"""Build and verify v03 public archives; private datasets stay outside the project."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def permitted(p):
    rel=p.relative_to(ROOT);top=rel.parts[0]
    if '__pycache__' in rel.parts or p.suffix in {'.pyc','.cache'}:return False
    if top=='data':return len(rel.parts)>2 and rel.parts[1] in {'berry_yolo','flower_yolo'} and p.suffix in {'.jpg','.txt','.yaml'}
    if top in {'src','scripts','tests','reports','examples','models'}:return True
    if top=='docs':return len(rel.parts)==2 or rel.parts[1]=='figures'
    if top=='outputs':return len(rel.parts)>1 and 'young' not in rel.parts[1]
    if top=='runs':
        if len(rel.parts)>1 and rel.parts[1]=='repeats':return p.suffix in {'.pt','.csv','.yaml'}
        return p.suffix in {'.pt','.csv','.yaml','.png'} or (len(rel.parts)>1 and rel.parts[1] in {'berry_aux','flower'} and p.suffix=='.jpg')
    return len(rel.parts)==1 and p.name in {'README.md','RECOVERY.md','RELEASE_DOWNLOAD.md','PUBLIC_PACKAGE_SCOPE.md','DATA_SOURCES.md','LICENSE','requirements.txt','requirements-report.txt','requirements-lock-cpu.txt','.gitignore'}
def archive(path,files,root_prefix='grape-thinning-vision/'):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,root_prefix+p.relative_to(ROOT).as_posix())
        z.writestr(root_prefix+'SHA256SUMS.txt',''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files))
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for p in files:assert hashlib.sha256(z.read(root_prefix+p.relative_to(ROOT).as_posix())).hexdigest()==digest(p)
    print(path.name,path.stat().st_size,digest(path),flush=True)
def main(dest):
    dest.mkdir(parents=True,exist_ok=True)
    seeds=json.loads((ROOT/'reports/seed_repeats.json').read_text());assert len(seeds['runs'])==9
    counts={}
    for task in ['berry_yolo','flower_yolo']:
        counts[task]={}
        for split in ['train','val','test']:
            files=list((ROOT/'data'/task/'images'/split).glob('*.jpg'));counts[task][split]=len(files)
            for p in files:
                with Image.open(p) as im:im.load()
                assert (ROOT/'data'/task/'labels'/split/p.with_suffix('.txt').name).is_file()
    assert counts=={'berry_yolo':{'train':360,'val':120,'test':120},'flower_yolo':{'train':369,'val':75,'test':79}}
    for task in seeds['runs']:
        run=ROOT/'runs/repeats'/f"{task['task']}_seed{task['seed']}"
        assert len((run/'results.csv').read_text().splitlines())==26
        assert not list(run.rglob('*.jpg')) and not list(run.rglob('*.png'))
    validation={'public_dataset_images_fully_decoded':counts,'public_images':1123,'training_images':729,'seed_runs':9,'epochs_per_seed_run':25,'unit_tests':8,'gui_interaction':'unverified','young_labels':'weak; no expert review','private_dataset_included':False}
    (ROOT/'reports/delivery_v03_validation.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and permitted(p))
    for p in files:
        if p.suffix.lower() in {'.jpg','.png'}:
            with Image.open(p) as im:im.load()
    (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT).as_posix()}\n' for p in files))
    archive(dest/'grape-thinning-delivery-v03.zip',files)
    source=[p for p in files if p.relative_to(ROOT).parts[0] in {'src','scripts','tests'} or len(p.relative_to(ROOT).parts)==1 or (p.relative_to(ROOT).parts[0]=='docs' and p.suffix=='.md')]
    archive(dest/'source-code-v03.zip',source)
    evidence=[p for p in files if p.relative_to(ROOT).parts[0]=='reports' or (p.relative_to(ROOT).parts[0]=='docs' and 'figures' in p.relative_to(ROOT).parts) or (p.relative_to(ROOT).parts[0]=='runs' and p.suffix in {'.csv','.yaml'})]
    archive(dest/'figures-and-evidence-v03.zip',evidence)
    repeat=[p for p in files if p.relative_to(ROOT).parts[:2]==('runs','repeats') or p.name=='seed_repeats.json']
    archive(dest/'repeat-training-v03.zip',repeat)
    for original,name in [('课程设计论文.docx','course-paper-v03.docx'),('课程设计论文.pdf','course-paper-v03.pdf')]:shutil.copyfile(ROOT/'docs'/original,dest/name)
    selected=sorted(p for p in dest.iterdir() if p.is_file() and p.name!='RELEASE_SHA256SUMS.txt')
    (dest/'RELEASE_SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in selected))
    print('ZIP CRC and per-entry SHA-256 passed',flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT.parent/'release-v03');main(parser.parse_args().output)
