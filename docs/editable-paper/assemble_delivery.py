"""Join the public v02 archive parts and verify SHA-256 (Python 3.9+)."""
import hashlib
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    destination = root / manifest['archive']
    temporary = destination.with_suffix('.zip.partial')
    whole = hashlib.sha256()
    try:
        with temporary.open('wb') as output:
            for item in manifest['parts']:
                part = root / item['name']
                digest = hashlib.sha256()
                size = 0
                with part.open('rb') as source:
                    while chunk := source.read(1024 * 1024):
                        output.write(chunk)
                        whole.update(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                if size != item['size'] or digest.hexdigest() != item['sha256']:
                    raise ValueError('Part checksum mismatch: ' + part.name)
                print('OK', part.name)
        if whole.hexdigest() != manifest['sha256']:
            raise ValueError('Archive checksum mismatch')
        temporary.replace(destination)
        print('Verified:', destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


if __name__ == '__main__':
    main()
